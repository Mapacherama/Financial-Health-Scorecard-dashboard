import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Backend API URL
API_BASE_URL = "http://127.0.0.1:5000/api"

# Fetch financial data
@st.cache
def fetch_financial_data():
    response = requests.get(f"{API_BASE_URL}/financial_data")
    return pd.DataFrame(response.json())

# Fetch summary data
def fetch_summary():
    response = requests.get(f"{API_BASE_URL}/summary")
    return response.json()

# Title
st.title("Financial Health Dashboard")

# Fetch and display financial data
st.header("Transaction Data")
financial_data = fetch_financial_data()
st.dataframe(financial_data)

# Display summary
st.header("Summary")
summary = fetch_summary()
st.metric("Total Income", f"${summary['total_income']:.2f}")
st.metric("Total Expenses", f"${summary['total_expenses']:.2f}")
st.metric("Net Balance", f"${summary['net_balance']:.2f}")

# Visualize category-wise expenses
st.header("Category Breakdown")
if not financial_data.empty:
    category_chart = px.pie(financial_data, names="category", values="amount", title="Expenses by Category")
    st.plotly_chart(category_chart)

# Visualize trends over time
st.header("Trends Over Time")
if not financial_data.empty:
    financial_data["date"] = pd.to_datetime(financial_data["date"])
    trend_chart = px.line(financial_data, x="date", y="amount", color="category", title="Spending Trends")
    st.plotly_chart(trend_chart)
