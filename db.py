# db.py
import sqlite3

def connect_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount REAL,
                date TEXT
            )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            allocated_amount REAL NOT NULL,
            spent_amount REAL DEFAULT 0.0,
            month_year TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT,
                amount REAL,
                purchase_date TEXT,
                current_value REAL
            )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compound_growth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            principal REAL,
            rate REAL,
            years INTEGER,
            contribution REAL,
            growth_data TEXT
            )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0.0,
            due_date TEXT,
            category TEXT
        )
    """)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
