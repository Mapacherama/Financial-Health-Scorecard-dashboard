# routes/forecasting.py
from flask import Blueprint, jsonify
from db import connect_db
import pandas as pd
from sklearn.linear_model import LinearRegression

forecasting_bp = Blueprint("forecasting", __name__)

@forecasting_bp.route('/api/forecast', methods=['GET'])
def forecast():
    conn = connect_db()
    try:
        df = pd.read_sql_query("""
            SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
            FROM financials
            GROUP BY month
            ORDER BY month
        """, conn)

        if df.empty:
            return jsonify({"error": "No data available for forecasting"}), 400

        df['month_num'] = range(1, len(df) + 1)
        X = df[['month_num']]
        y = df['total']

        model = LinearRegression().fit(X, y)
        future_months = [[len(df) + i] for i in range(1, 7)]
        predictions = model.predict(future_months)

        forecast = [{"month": f"Month {i}", "predicted_total": round(p, 2)} for i, p in enumerate(predictions, 1)]
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
