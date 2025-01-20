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

@app.route('/api/top_transactions', methods=['GET'])
def get_top_transactions():
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch largest income
    cursor.execute("""
        SELECT * FROM financials
        WHERE amount > 0
        ORDER BY amount DESC
        LIMIT 1
    """)
    top_income = dict(cursor.fetchone())

    # Fetch largest expense
    cursor.execute("""
        SELECT * FROM financials
        WHERE amount < 0
        ORDER BY amount ASC
        LIMIT 1
    """)
    top_expense = dict(cursor.fetchone())

    conn.close()

    return jsonify({"top_income": top_income, "top_expense": top_expense})


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

@app.route('/api/trends', methods=['GET'])
def get_trends():
    conn = connect_db()
    cursor = conn.cursor()

    # Aggregate amounts by month
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, 
               SUM(amount) as total
        FROM financials
        GROUP BY month
        ORDER BY month
    """)
    trends = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(trends)

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

@app.route('/api/recurring_transactions', methods=['GET'])
def get_recurring_transactions():
    conn = connect_db()
    cursor = conn.cursor()

    # Group by category and count occurrences
    cursor.execute("""
        SELECT category, COUNT(*) as occurrences, SUM(amount) as total
        FROM financials
        GROUP BY category
        HAVING occurrences > 1
        ORDER BY occurrences DESC
    """)
    recurring = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(recurring)


@app.route('/api/savings_rate', methods=['GET'])
def get_savings_rate():
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch income and expenses
    cursor.execute("SELECT SUM(amount) as total_income FROM financials WHERE amount > 0")
    total_income = cursor.fetchone()['total_income'] or 0

    cursor.execute("SELECT SUM(amount) as total_expenses FROM financials WHERE amount < 0")
    total_expenses = abs(cursor.fetchone()['total_expenses'] or 0)

    # Calculate savings rate
    savings_rate = 0
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * 100

    conn.close()
    return jsonify({"savings_rate": savings_rate})

if __name__ == '__main__':
    # Initialize the database before starting the app
    initialize_db()
    app.run(debug=True)
