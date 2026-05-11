import sqlite3
import os
import argparse
import sys

def init_db(db_path, schema_path):
    if not os.path.exists(schema_path):
        print(f"Error: Schema file not found at {schema_path}")
        sys.exit(1)
    
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    try:
        conn = sqlite3.connect(db_path)
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        print(f"Successfully initialized database at {db_path}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize acellorator index database.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--schema", default="registry/db/schema.sql", help="Path to SQL schema file.")
    
    args = parser.parse_args()
    init_db(args.db, args.schema)
