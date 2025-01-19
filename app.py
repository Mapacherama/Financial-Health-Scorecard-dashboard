from flask import Flask, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

# Connect to the SQLite database
def connect_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database and create the table if it doesn't exist
def initialize_db():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        # Create the table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT
        )
        """)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# API to fetch financial data with optional date filtering
@app.route('/api/financial_data', methods=['GET'])
def get_financial_data():
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch query parameters for date filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = "SELECT * FROM financials"
    params = []

    # Apply date filters if provided
    if start_date and end_date:
        query += " WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    
    return jsonify(data)

# API to fetch summary data
@app.route('/api/summary', methods=['GET'])
def get_summary():
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch total income (categories like 'Income')
    cursor.execute("SELECT SUM(amount) as total_income FROM financials WHERE amount > 0")
    total_income = cursor.fetchone()['total_income'] or 0

    # Fetch total expenses (categories like 'Expense')
    cursor.execute("SELECT SUM(amount) as total_expenses FROM financials WHERE amount < 0")
    total_expenses = cursor.fetchone()['total_expenses'] or 0

    # Calculate net balance
    net_balance = total_income + total_expenses

    summary = {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance
    }

    conn.close()
    return jsonify(summary)

# API to add data (for manual input or testing)
@app.route('/api/add_data', methods=['POST'])
def add_data():
    conn = connect_db()
    cursor = conn.cursor()
    data = request.json

    cursor.execute("""
        INSERT INTO financials (category, amount, date)
        VALUES (?, ?, ?)
    """, (data['category'], data['amount'], data['date']))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Data added successfully!"})

if __name__ == '__main__':
    # Initialize the database before starting the app
    initialize_db()
    app.run(debug=True)
