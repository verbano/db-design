def column_exists(cur, table_name, column_name):
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        );
    """, (table_name, column_name))
    return cur.fetchone()[0]

def get_all_ids(cur, table):
    cur.execute(f"SELECT id FROM {table};")
    return [row[0] for row in cur.fetchall()]