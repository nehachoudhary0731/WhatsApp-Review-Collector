import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    conn = sqlite3.connect('whatsapp_reviews.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_number TEXT NOT NULL,
            user_name TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_review TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()