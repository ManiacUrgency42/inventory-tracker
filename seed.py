"""
Run once to populate the database with sample items.
Usage: python seed.py
"""

from dotenv import load_dotenv
load_dotenv()

import database

database.init_db()

samples = [
    ("0123456789012", "Widget A",                   "Small blue widget",           17, "Shelf 4"),
    ("9780131101630", "The C Programming Language",  "Kernighan & Ritchie, 2nd ed",  2, "Bookshelf 1"),
    ("0000000000001", "Test Item",                   "For testing the scanner",     99, "Lab"),
]

conn = database.get_connection()
cur = database.get_cursor(conn)
cur.executemany(
    """
    INSERT INTO items (barcode, name, description, quantity, location)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (barcode) DO NOTHING
    """,
    samples,
)
conn.commit()
cur.close()
conn.close()

print(f"Seeded {len(samples)} items.")
