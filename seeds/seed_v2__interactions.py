#!/usr/bin/env python3
import os
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

def seed_comments(cur, count, user_ids, paste_ids):
    for _ in range(count):
        user_id = random.choice(user_ids)
        paste_id = random.choice(paste_ids)
        content = faker.text(max_nb_chars=500)
        parent_comment = random.choice([None, random.choice(get_all_ids(cur, "comments")) if random.random() < 0.2 else None])
        
        cur.execute("""
            INSERT INTO comments (user_id, paste_id, content, parent_comment_id, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT DO NOTHING;
        """, (user_id, paste_id, content, parent_comment))

def seed_likes(cur, user_ids, paste_ids):
    for user_id in user_ids:
        paste_sample = random.sample(paste_ids, k=random.randint(0, len(paste_ids)//4))
        for paste_id in paste_sample:
            cur.execute("""
                INSERT INTO likes (user_id, paste_id, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT DO NOTHING;
            """, (user_id, paste_id))

def seed_paste_views(cur, paste_ids, user_ids):
    for paste_id in paste_ids:
        views_count = random.randint(0, 50)
        for _ in range(views_count):
            user_id = random.choice(user_ids + [None])
            cur.execute("""
                INSERT INTO paste_views (paste_id, user_id, viewed_at, ip_address)
                VALUES (%s, %s, NOW(), %s)
            """, (paste_id, user_id, faker.ipv4()))

def seed_paste_proposals(cur, count, user_ids, paste_ids):
    statuses = ['pending', 'approved', 'rejected']
    for _ in range(count):
        original_id = random.choice(paste_ids)
        user_id = random.choice(user_ids)
        cur.execute("""
            INSERT INTO paste_proposals (
                original_paste_id, proposed_content, status, 
                created_by, created_at, resolved_at
            ) VALUES (%s, %s, %s, %s, NOW(), 
                CASE WHEN %s THEN NOW() - INTERVAL '1 day' ELSE NULL END)
        """, (
            original_id,
            faker.text(max_nb_chars=2000),
            random.choice(statuses),
            user_id,
            random.random() < 0.3
        ))

def seed_proposal_comments(cur, proposal_ids, user_ids):
    for proposal_id in proposal_ids:
        comments_count = random.randint(0, 5)
        for _ in range(comments_count):
            cur.execute("""
                INSERT INTO proposal_comments (proposal_id, user_id, content, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (
                proposal_id,
                random.choice(user_ids),
                faker.sentence()
            ))

def seed_reports(cur, count, user_ids, paste_ids):
    statuses = ['pending', 'resolved']
    for _ in range(count):
        cur.execute("""
            INSERT INTO reports (paste_id, reporter_id, reason, status, resolved_at)
            VALUES (%s, %s, %s, %s, 
                CASE WHEN %s THEN NOW() ELSE NULL END)
        """, (
            random.choice(paste_ids),
            random.choice(user_ids),
            faker.paragraph(),
            random.choice(statuses),
            random.random() < 0.4
        ))

def main():
    seed_count = int(os.getenv("SEED_COUNT", 100))
    conn = get_conn()
    cur = conn.cursor()

    user_ids = get_all_ids(cur, "users")
    paste_ids = get_all_ids(cur, "pastes")

    seed_comments(cur, seed_count * 3, user_ids, paste_ids)
    seed_likes(cur, user_ids, paste_ids)
    seed_paste_views(cur, paste_ids, user_ids)
    seed_paste_proposals(cur, seed_count // 2, user_ids, paste_ids)
    
    proposal_ids = get_all_ids(cur, "paste_proposals")
    seed_proposal_comments(cur, proposal_ids, user_ids)
    
    seed_reports(cur, seed_count // 4, user_ids, paste_ids)

    conn.commit()
    cur.close()
    conn.close()
    print("Seeding V2 (interaction tables) complete.")

if __name__ == "__main__":
    main()