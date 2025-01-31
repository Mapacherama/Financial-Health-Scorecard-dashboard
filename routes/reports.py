from flask import Blueprint, send_file
from fpdf import FPDF
from routes.insights import get_recurring_transactions, get_summary
from routes.historical import get_historical_data
from routes.financials import get_top_transactions
from routes.investments import get_investment_portfolio

# Create the Blueprint for reports
reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/api/generate_report", methods=["GET"])
def generate_report():
    summary = get_summary()
    historical_data = get_historical_data()
    recurring_transactions = get_recurring_transactions()
    top_transactions = get_top_transactions()
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Financial Health Report", ln=True, align="C")
    pdf.ln(10)

    # Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Financial Summary", ln=True)
    
    pdf.set_font("Arial", "", 11)
    # Get the JSON data from the summary response
    summary_data = summary.get_json()  # Convert Response to dictionary

    # Now use the dictionary to access the values
    pdf.cell(200, 8, f"Total Income: ${summary_data['total_income']:.2f}", ln=True)
    pdf.cell(200, 8, f"Total Expenses: ${summary_data['total_expenses']:.2f}", ln=True)
    pdf.cell(200, 8, f"Net Balance: ${summary_data['net_balance']:.2f}", ln=True)
    
    pdf.ln(10)

    # Historical Data Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Historical Data (Monthly Breakdown)", ln=True)
    
    pdf.set_font("Arial", "", 11)
    historical_data_json = historical_data.get_json()
    
    # Access the historical_data array directly
    data_to_iterate = historical_data_json.get('historical_data', [])

    for data in data_to_iterate:
        pdf.cell(200, 8, 
            f"{data.get('month', 'N/A')} - "
            f"Income: ${data.get('total_income', 0):.2f} | "
            f"Expenses: ${data.get('total_expenses', 0):.2f} | "
            f"Net Savings: ${data.get('net_savings', 0):.2f}", 
            ln=True)

    pdf.ln(10)
    
    # Top Transactions Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Top Transactions", ln=True)
    
    pdf.set_font("Arial", "", 11)
    top_transactions_json = top_transactions.get_json()
    pdf.cell(200, 8, f"Largest Income: ${top_transactions_json.get('top_income', {}).get('amount', 0):.2f}", ln=True)
    pdf.cell(200, 8, f"Largest Expense: ${top_transactions_json.get('top_expense', {}).get('amount', 0):.2f}", ln=True)
    pdf.ln(10)
    
    # Recurring Transactions Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Recurring Transactions", ln=True)
    
    pdf.set_font("Arial", "", 11)
    recurring_transactions_json = recurring_transactions.get_json()
    for transaction in recurring_transactions_json:
        pdf.cell(200, 8, f"{transaction.get('category', 'N/A')}: ${transaction.get('total', 0):.2f}", ln=True)
    pdf.ln(10)
    
    # Investment Portfolio Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Investment Portfolio", ln=True)
    
    pdf.set_font("Arial", "", 11)
    investment_portfolio_json = get_investment_portfolio().json
    investments = investment_portfolio_json.get("investments", [])
    # Display total investment amount
    total_investment = sum(item.get("amount", 0) for item in investments)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 8, f"Total Investments: ${total_investment:,.2f}", ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", "B", 11)
    pdf.cell(50, 8, "Investment Name", border=1)
    pdf.cell(40, 8, "Category", border=1)
    pdf.cell(30, 8, "Amount ($)", border=1, align="R")
    pdf.cell(35, 8, "Current Value ($)", border=1, align="R")
    pdf.cell(25, 8, "ROI (%)", border=1, align="R")
    pdf.ln()

    # Investment Details
    pdf.set_font("Arial", "", 10)
    for investment in investments:
        pdf.cell(50, 8, investment.get("name", "N/A"), border=1)
        pdf.cell(40, 8, investment.get("category", "N/A"), border=1)
        pdf.cell(30, 8, f"${investment.get('amount', 0):,.2f}", border=1, align="R")
        pdf.cell(35, 8, f"${investment.get('current_value', 0):,.2f}", border=1, align="R")
        pdf.cell(25, 8, f"{investment.get('roi', 0):,.2f}%", border=1, align="R")
        pdf.ln()

    # Save PDF
    pdf_path = "financial_report.pdf"
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True, mimetype="application/pdf")