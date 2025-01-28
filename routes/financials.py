# routes/financials.py
from flask import Blueprint, request, jsonify
from db import connect_db

financials_bp = Blueprint("financials", __name__)

@financials_bp.route('/api/financial_data', methods=['GET'])
def get_financial_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')

    query = "SELECT * FROM financials WHERE 1=1"
    params = []

    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    
    if category:
        query += " AND category = ?"
        params.append(category)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

@financials_bp.route('/api/top_transactions', methods=['GET'])
def get_top_transactions():
    conn = connect_db()
    cursor = conn.cursor()

    # Initialize with None
    top_income = None
    top_expense = None

    # Fetch largest income
    cursor.execute("""
        SELECT * FROM financials
        WHERE amount > 0
        ORDER BY amount DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        top_income = dict(result)

    # Fetch largest expense
    cursor.execute("""
        SELECT * FROM financials
        WHERE amount < 0
        ORDER BY amount ASC
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        top_expense = dict(result)

    conn.close()

    return jsonify({
        "top_income": top_income,
        "top_expense": top_expense
    })

@financials_bp.route('/api/add_data', methods=['POST'])
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