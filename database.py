import os

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn


def get_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    conn = get_connection()
    cur = get_cursor(conn)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id          SERIAL PRIMARY KEY,
            barcode     TEXT UNIQUE NOT NULL,
            name        TEXT NOT NULL,
            description TEXT,
            quantity    INTEGER DEFAULT 0,
            location    TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
