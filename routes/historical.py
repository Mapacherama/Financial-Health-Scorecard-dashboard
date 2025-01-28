from flask import Blueprint, jsonify
from db import connect_db

# Create the Blueprint for historical data
historical_bp = Blueprint("historical", __name__)

@historical_bp.route('/api/historical_data', methods=['GET'])
def get_historical_data():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, 
               SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
               SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as total_expenses,
               SUM(amount) as net_savings
        FROM financials
        GROUP BY month
        ORDER BY month
    """)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"historical_data": results})
