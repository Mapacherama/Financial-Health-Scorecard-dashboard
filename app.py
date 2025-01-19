from flask import Flask, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

# Connect to the SQLite database
def connect_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

# API to fetch financial data
@app.route('/api/financial_data', methods=['GET'])
def get_financial_data():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Fetch data from the database
    cursor.execute("SELECT * FROM financials")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    
    return jsonify(data)

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
    app.run(debug=True)
