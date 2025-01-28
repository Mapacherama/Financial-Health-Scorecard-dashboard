# routes/insights.py
from flask import Blueprint, jsonify
from db import connect_db

insights_bp = Blueprint("insights", __name__)

@insights_bp.route('/api/summary', methods=['GET'])
def get_summary():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) as total_income FROM financials WHERE amount > 0")
    total_income = cursor.fetchone()['total_income'] or 0

    cursor.execute("SELECT SUM(amount) as total_expenses FROM financials WHERE amount < 0")
    total_expenses = cursor.fetchone()['total_expenses'] or 0

    net_balance = total_income + total_expenses

    conn.close()
    return jsonify({"total_income": total_income, "total_expenses": total_expenses, "net_balance": net_balance})


@insights_bp.route('/api/savings_rate', methods=['GET'])
def get_savings_rate():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) as total_income FROM financials WHERE amount > 0")
    total_income = cursor.fetchone()['total_income'] or 0

    cursor.execute("SELECT SUM(amount) as total_expenses FROM financials WHERE amount < 0")
    total_expenses = abs(cursor.fetchone()['total_expenses'] or 0)

    savings_rate = ((total_income - total_expenses) / total_income) * 100 if total_income > 0 else 0

    conn.close()
    return jsonify({"savings_rate": savings_rate})

@insights_bp.route('/api/recurring_transactions', methods=['GET'])
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
