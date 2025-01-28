# routes/investments.py
from flask import Blueprint, request, jsonify
from db import connect_db

investments_bp = Blueprint("investments", __name__)

@investments_bp.route('/api/investment_portfolio', methods=['GET', 'POST'])
def investment_portfolio():
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.json
        cursor.execute("""
            INSERT INTO investments (name, category, amount, purchase_date, current_value)
            VALUES (?, ?, ?, ?, ?)
        """, (data['name'], data['category'], data['amount'], data['purchase_date'], data['current_value']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Investment added successfully!"}), 201

    elif request.method == 'GET':
        cursor.execute("""
            SELECT name, category, amount, purchase_date, current_value, 
                   ROUND(((current_value - amount) / amount) * 100, 2) AS roi
            FROM investments
        """)
        investments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"investments": investments})