import os
import random
import time
import logging
import psycopg2
from datetime import datetime, timedelta
from faker import Faker
from prometheus_client import start_http_server, Summary, Gauge

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('load-test')

fake = Faker()

QUERY_TIME = Summary(
    'query_duration_seconds', 
    'Time spent processing query',
    ['query_name']
)
ERROR_COUNT = Gauge('query_errors_total', 'Total query errors', ['query_name'])
ACTIVE_QUERIES = Gauge('active_queries', 'Current active queries')

class PastebinLoadTester:
    def __init__(self):
        self.conn = None
        self.user_ids = []
        self.paste_ids = []
        self.tag_names = []
        self.folder_ids = []
        self.category_ids = []
        
        self.interval = float(os.getenv("LOAD_TEST_INTERVAL", 1.0))
        self.duration = float(os.getenv("LOAD_TEST_DURATION", 60.0))
        
    def connect(self):
        """Установка соединения с БД и загрузка справочных данных"""
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        logger.info("Connected to PostgreSQL database")
        
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM users")
            self.user_ids = [row[0] for row in cur.fetchall()]
            
            cur.execute("SELECT id FROM pastes WHERE privacy_level = 'public'")
            self.paste_ids = [row[0] for row in cur.fetchall()]
            
            cur.execute("SELECT name FROM tags")
            self.tag_names = [row[0] for row in cur.fetchall()]
            
            cur.execute("SELECT id FROM folders")
            self.folder_ids = [row[0] for row in cur.fetchall()]
            
            cur.execute("SELECT id FROM categories")
            self.category_ids = [row[0] for row in cur.fetchall()]
            
        logger.info(f"Loaded: {len(self.user_ids)} users, {len(self.paste_ids)} pastes, "
                    f"{len(self.tag_names)} tags, {len(self.folder_ids)} folders")
        logger.info(f"Test configuration: interval={self.interval}s, duration={self.duration}s")

    def run_query(self, query_spec):
        """Выполнение запроса с замером времени и обработкой ошибок"""
        ACTIVE_QUERIES.inc()
        start_time = time.perf_counter()
        error = False
        
        try:
            with self.conn.cursor() as cursor:
                params = query_spec["params"]()
                cursor.execute(query_spec["sql"], params)
                
                if query_spec.get("fetch", True):
                    cursor.fetchall()
        except Exception as e:
            logger.error(f"Error in '{query_spec['name']}': {str(e)}")
            ERROR_COUNT.labels(query_name=query_spec['name']).inc()
            error = True
            self.conn.rollback()
        finally:
            duration = (time.perf_counter() - start_time) * 1000
            ACTIVE_QUERIES.dec()
            
            if not error:
                QUERY_TIME.labels(query_name=query_spec['name']).observe(duration / 1000)
            
            return duration

    def generate_load(self):
        """Основной цикл генерации нагрузки (только SELECT-запросы)"""
        QUERIES = [
            {
                "name": "user_pastes_with_stats",
                "sql": """
                    SELECT p.id, p.name, p.created_at, 
                           COUNT(c.id) AS comment_count,
                           COUNT(l.user_id) AS like_count,
                           COUNT(DISTINCT f.id) AS folder_count,
                           STRING_AGG(t.name, ', ') AS tags
                    FROM pastes p
                    LEFT JOIN comments c ON p.id = c.paste_id
                    LEFT JOIN likes l ON p.id = l.paste_id
                    LEFT JOIN paste_tags pt ON p.id = pt.paste_id
                    LEFT JOIN tags t ON pt.tag_id = t.id
                    LEFT JOIN paste_folders pf ON p.id = pf.paste_id
                    LEFT JOIN folders f ON pf.folder_id = f.id
                    WHERE p.user_id = %s
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
                    LIMIT 10
                """,
                "params": lambda: (random.choice(self.user_ids),),
                "weight": 35
            },
            {
                "name": "popular_pastes_by_category",
                "sql": """
                    SELECT c.name AS category,
                           p.name AS paste_name,
                           COUNT(l.user_id) AS like_count,
                           COUNT(DISTINCT v.id) AS view_count,
                           COUNT(DISTINCT cm.id) AS comment_count
                    FROM pastes p
                    JOIN categories c ON p.category_id = c.id
                    LEFT JOIN likes l ON p.id = l.paste_id
                    LEFT JOIN paste_views v ON p.id = v.paste_id
                    LEFT JOIN comments cm ON p.id = cm.paste_id
                    WHERE p.privacy_level = 'public'
                    GROUP BY c.name, p.name
                    ORDER BY like_count DESC, view_count DESC
                    LIMIT 10
                """,
                "params": lambda: (),
                "weight": 25
            },
            {
                "name": "user_activity_stats",
                "sql": """
                    SELECT u.username,
                           COUNT(DISTINCT p.id) AS paste_count,
                           COUNT(DISTINCT c.id) AS comment_count,
                           COUNT(DISTINCT l.paste_id) AS likes_given,
                           COUNT(DISTINCT v.paste_id) AS pastes_viewed,
                           COUNT(DISTINCT f.id) AS folder_count
                    FROM users u
                    LEFT JOIN pastes p ON u.id = p.user_id
                    LEFT JOIN comments c ON u.id = c.user_id
                    LEFT JOIN likes l ON u.id = l.user_id
                    LEFT JOIN paste_views v ON u.id = v.user_id
                    LEFT JOIN folders f ON u.id = f.user_id
                    WHERE u.id = %s
                    GROUP BY u.username
                """,
                "params": lambda: (random.choice(self.user_ids),),
                "weight": 20
            },
            {
                "name": "tag_analysis",
                "sql": """
                    SELECT t.name AS tag,
                           COUNT(DISTINCT p.id) AS paste_count,
                           COUNT(DISTINCT u.id) AS user_count,
                           AVG(CHAR_LENGTH(p.name)) AS avg_name_length,
                           MAX(p.created_at) AS last_used
                    FROM tags t
                    JOIN paste_tags pt ON t.id = pt.tag_id
                    JOIN pastes p ON pt.paste_id = p.id
                    JOIN users u ON p.user_id = u.id
                    WHERE t.name = %s
                    GROUP BY t.name
                """,
                "params": lambda: (random.choice(self.tag_names),),
                "weight": 20
            }
        ]
        
        weights = [q["weight"] for q in QUERIES]
        total_weight = sum(weights)
        
        logger.info("Starting READ-ONLY load generation")
        
        start_time = time.time()
        end_time = start_time + self.duration if self.duration > 0 else float('inf')
        
        try:
            while time.time() < end_time:
                r = random.uniform(0, total_weight)
                index = 0
                for i, weight in enumerate(weights):
                    r -= weight
                    if r <= 0:
                        index = i
                        break
                
                query_spec = QUERIES[index]
                duration = self.run_query(query_spec)
                
                if duration:
                    logger.debug(f"Executed '{query_spec['name']}' in {duration:.2f} ms")
                
                if self.interval > 0:
                    delay = random.expovariate(1.0 / self.interval)
                    time.sleep(delay)
        except KeyboardInterrupt:
            logger.info("Stopping load generation")
        except Exception as e:
            logger.error(f"Critical error: {str(e)}")
        finally:
            if self.conn:
                self.conn.close()
            logger.info(f"Load test completed. Total duration: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    start_http_server(8000)
    logger.info("Prometheus metrics server started on port 8000")
    
    tester = PastebinLoadTester()
    tester.connect()
    tester.generate_load()