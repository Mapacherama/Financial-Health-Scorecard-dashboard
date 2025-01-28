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
    
@investments_bp.route('/api/compound_growth', methods=['POST'])
def compound_growth():
    # Ensure the table exists
    conn = connect_db()
    cursor = conn.cursor()
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
    conn.commit()

    # Process the request
    data = request.json
    principal = data.get('principal', 0)
    rate = data.get('rate', 0) / 100  
    years = data.get('years', 1)
    contribution = data.get('contribution', 0)  

    # Calculate compound growth
    results = []
    original_principal = principal  
    for year in range(1, years + 1):
        principal = principal * (1 + rate) + contribution
        results.append({"year": year, "value": round(principal, 2)})

    # Save the results into the database
    cursor.execute("""
        INSERT INTO compound_growth (principal, rate, years, contribution, growth_data)
        VALUES (?, ?, ?, ?, ?)
    """, (original_principal, rate * 100, years, contribution, str(results)))  # Convert results to string for storage
    conn.commit()

    conn.close()
    return jsonify({"growth": results, "message": "Compound growth saved successfully!"})
