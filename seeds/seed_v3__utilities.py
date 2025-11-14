#!/usr/bin/env python3
import os
import uuid
import random
from datetime import datetime, timedelta
from utils import *

import psycopg2
from faker import Faker

faker = Faker()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def seed_paste_templates(cur, count, user_ids):
    for _ in range(count):
        cur.execute("""
            INSERT INTO paste_templates (user_id, name, content, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (
            random.choice(user_ids),
            faker.word().capitalize() + " Template",
            faker.text(max_nb_chars=1000)
        ))

def seed_export_formats(cur):
    formats = [
        ('PDF', 'application/pdf', 'pdf'),
        ('Markdown', 'text/markdown', 'md'),
        ('Text', 'text/plain', 'txt'),
        ('HTML', 'text/html', 'html')
    ]
    cur.executemany("""
        INSERT INTO export_formats (name, mime_type, file_extension)
        VALUES (%s, %s, %s)
        ON CONFLICT (name) DO NOTHING
    """, formats)

def seed_exports(cur, count, user_ids, paste_ids, format_ids):
    for _ in range(count):
        cur.execute("""
            INSERT INTO exports (paste_id, user_id, format_id, paste_name, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (
            random.choice(paste_ids),
            random.choice(user_ids),
            random.choice(format_ids),
            faker.word().capitalize() + " Export"
        ))

def seed_export_logs(cur, export_ids):
    for export_id in export_ids:
        status = random.choices(['success', 'failed'], weights=[0.8, 0.2])[0]
        cur.execute("""
            INSERT INTO export_logs (export_id, status, error_message, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (
            export_id,
            status,
            faker.sentence() if status == 'failed' else None
        ))

def seed_notification_types(cur):
    types = [
        ('System',),
        ('New comment',),
        ('New like',),
        ('Export completed',)
    ]
    cur.executemany("""
        INSERT INTO notification_types (name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
    """, types)

def seed_notifications(cur, count, user_ids, type_ids):
    for _ in range(count):
        cur.execute("""
            INSERT INTO notifications (
                user_id, type_id, message, 
                related_id, is_read, delivery_status
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            random.choice(user_ids),
            random.choice(type_ids),
            faker.sentence(),
            random.randint(1, 1000) if random.random() > 0.5 else None,
            faker.boolean(chance_of_getting_true=60),
            random.choices(['pending', 'delivered', 'failed'], weights=[0.2, 0.7, 0.1])[0]
        ))

def seed_user_sessions(cur, user_ids):
    for user_id in user_ids:
        cur.execute("""
            INSERT INTO user_sessions (
                user_id, session_token, 
                expires_at, ip_address, user_agent
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            uuid.uuid4().hex,
            datetime.now() + timedelta(days=30),
            faker.ipv4(),
            faker.user_agent()
        ))

def seed_password_reset_tokens(cur, user_ids):
    for user_id in user_ids:
        cur.execute("""
            INSERT INTO password_reset_tokens (
                user_id, token, expires_at, used
            ) VALUES (%s, %s, %s, %s)
        """, (
            user_id,
            uuid.uuid4().hex,
            datetime.now() + timedelta(hours=1),
            faker.boolean(chance_of_getting_true=20)
        ))

def main():
    seed_count = int(os.getenv("SEED_COUNT", 100))
    conn = get_conn()
    cur = conn.cursor()

    user_ids = get_all_ids(cur, "users")
    paste_ids = get_all_ids(cur, "pastes")

    seed_paste_templates(cur, seed_count // 2, user_ids)
    seed_export_formats(cur)
    
    format_ids = get_all_ids(cur, "export_formats")
    seed_exports(cur, seed_count, user_ids, paste_ids, format_ids)
    
    export_ids = get_all_ids(cur, "exports")
    seed_export_logs(cur, export_ids)
    
    seed_notification_types(cur)
    type_ids = get_all_ids(cur, "notification_types")
    seed_notifications(cur, seed_count * 2, user_ids, type_ids)
    
    seed_user_sessions(cur, random.sample(user_ids, k=seed_count // 5))
    seed_password_reset_tokens(cur, random.sample(user_ids, k=seed_count // 10))

    conn.commit()
    cur.close()
    conn.close()
    print("Seeding V3 (utility tables) complete.")

if __name__ == "__main__":
    main()