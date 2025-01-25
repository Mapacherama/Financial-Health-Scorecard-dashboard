from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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


# API to fetch financial data with optional date filtering
@app.route('/api/financial_data', methods=['GET'])
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

@app.route('/api/investment_portfolio', methods=['GET', 'POST'])
def investment_portfolio():
    conn = connect_db()
    cursor = conn.cursor()

    # Create the investments table if it doesn't exist
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

    if request.method == 'POST':
        # Add a new investment
        data = request.json
        cursor.execute("""
            INSERT INTO investments (name, category, amount, purchase_date, current_value)
            VALUES (?, ?, ?, ?, ?)
        """, (data['name'], data['category'], data['amount'], data['purchase_date'], data['current_value']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Investment added successfully!"}), 201

    elif request.method == 'GET':
        # Retrieve portfolio data
        cursor.execute("""
            SELECT name, category, amount, purchase_date, current_value, 
                   ROUND(((current_value - amount) / amount) * 100, 2) AS roi
            FROM investments
        """)
        investments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"investments": investments})
    
@app.route('/api/compound_growth', methods=['POST'])
def compound_growth():
    data = request.json
    principal = data.get('principal', 0)
    rate = data.get('rate', 0) / 100  # Convert percentage to decimal
    years = data.get('years', 1)
    contribution = data.get('contribution', 0)  # Optional yearly contribution

    # Calculate compound growth
    results = []
    for year in range(1, years + 1):
        # Compound formula with annual contributions
        principal = principal * (1 + rate) + contribution
        results.append({"year": year, "value": round(principal, 2)})

    return jsonify({"growth": results})

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

@app.route('/api/forecast', methods=['GET'])
def forecast():
    conn = connect_db()
    try:
        # Fetch and process financial data
        df = pd.read_sql_query("""
            SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
            FROM financials
            GROUP BY month
            ORDER BY month
        """, conn)

        if df.empty:
            return jsonify({"error": "No data available for forecasting"}), 400

        # Prepare data for linear regression
        df['month_num'] = range(1, len(df) + 1)  # Add numerical month index
        X = df[['month_num']]
        y = df['total']

        # Train linear regression model
        from sklearn.linear_model import LinearRegression
        model = LinearRegression().fit(X, y)

        # Predict for the next 6 months
        future_months = [[len(df) + i] for i in range(1, 7)]
        predictions = model.predict(future_months)

        # Format the response
        forecast = [{"month": f"Month {i}", "predicted_total": round(p, 2)} for i, p in enumerate(predictions, 1)]
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    # Initialize the database before starting the app
    initialize_db()
    app.run(debug=True)
