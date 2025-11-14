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

def seed_users(cur, count):
    for _ in range(count):
        username = faker.unique.user_name()
        email = faker.unique.email()
        password_hash = faker.sha256()
        avatar_url = faker.image_url()
        cur.execute("""
            INSERT INTO users (username, email, password_hash, avatar_url, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW());
        """, (username, email, password_hash, avatar_url))

def seed_categories(cur, count):
    for _ in range(count):
        name = faker.unique.word().capitalize()
        description = faker.sentence()
        cur.execute("""
            INSERT INTO categories (name, description)
            VALUES (%s, %s)
            ON CONFLICT (name) DO NOTHING;
        """, (name, description))

def seed_tags(cur, count):
    for _ in range(count):
        name = faker.unique.word().lower()
        cur.execute("""
            INSERT INTO tags (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING;
        """, (name,))

def seed_pastes(cur, count, user_ids, category_ids):
    privacy_levels = ['public', 'private']
    for _ in range(count):
        user_id = random.choice(user_ids)
        object_key = f"pastes/{faker.unique.uuid4()}.txt"
        name = faker.sentence(nb_words=3)
        language = random.choice(['Python', 'JavaScript', 'C#', 'Go', 'Java'])
        privacy_level = random.choice(privacy_levels)
        expiration = datetime.utcnow() + timedelta(days=random.randint(1, 365)) if random.random() < 0.5 else None
        category_id = random.choice(category_ids) if category_ids and random.random() < 0.7 else None
        cur.execute("""
            INSERT INTO pastes (user_id, object_key, name, language, privacy_level, expiration, category_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (object_key) DO NOTHING;
        """, (user_id, object_key, name, language, privacy_level, expiration, category_id))

def seed_paste_tags(cur, paste_ids, tag_ids):
    for paste_id in paste_ids:
        tags_sample = random.sample(tag_ids, k=random.randint(1, min(3, len(tag_ids))))
        for tag_id in tags_sample:
            cur.execute("""
                INSERT INTO paste_tags (paste_id, tag_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (paste_id, tag_id))

def seed_folders(cur, user_ids, count_per_user=2):
    for user_id in user_ids:
        for _ in range(count_per_user):
            name = faker.word().capitalize() + " Folder"
            cur.execute("""
                INSERT INTO folders (user_id, name, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT DO NOTHING;
            """, (user_id, name))

def seed_paste_folders(cur, paste_ids, folder_ids):
    for paste_id in paste_ids:
        folder_sample = random.sample(folder_ids, k=random.randint(0, min(2, len(folder_ids))))
        for folder_id in folder_sample:
            cur.execute("""
                INSERT INTO paste_folders (paste_id, folder_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (paste_id, folder_id))

def main():
    seed_count = int(os.getenv("SEED_COUNT", 100))
    conn = get_conn()
    cur = conn.cursor()

    seed_users(cur, seed_count)
    seed_categories(cur, seed_count // 5)
    seed_tags(cur, seed_count // 2)

    user_ids = get_all_ids(cur, "users")
    category_ids = get_all_ids(cur, "categories")
    tag_ids = get_all_ids(cur, "tags")

    seed_pastes(cur, seed_count * 2, user_ids, category_ids)

    paste_ids = get_all_ids(cur, "pastes")
    seed_paste_tags(cur, paste_ids, tag_ids)

    seed_folders(cur, user_ids, 2)

    folder_ids = get_all_ids(cur, "folders")
    seed_paste_folders(cur, paste_ids, folder_ids)

    conn.commit()
    cur.close()
    conn.close()
    print("Seeding V1 (core tables) complete.")

if __name__ == "__main__":
    main()
