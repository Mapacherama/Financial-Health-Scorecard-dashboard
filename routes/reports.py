from flask import Blueprint, send_file
from fpdf import FPDF
from db import connect_db
from routes.insights import get_summary
from routes.historical import get_historical_data

# Create the Blueprint for reports
reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/api/generate_report", methods=["GET"])
def generate_report():
    summary = get_summary()
    historical_data = get_historical_data()
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Financial Health Report", ln=True, align="C")
    pdf.ln(10)

    # Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "📊 Financial Summary", ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 8, f"Total Income: ${summary['total_income']:.2f}", ln=True)
    pdf.cell(200, 8, f"Total Expenses: ${summary['total_expenses']:.2f}", ln=True)
    pdf.cell(200, 8, f"Net Balance: ${summary['net_balance']:.2f}", ln=True)
    
    pdf.ln(10)

    # Historical Data Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "📅 Historical Data (Monthly Breakdown)", ln=True)
    
    pdf.set_font("Arial", "", 11)
    for data in historical_data:
        pdf.cell(200, 8, f"{data['month']} - Income: ${data['total_income']:.2f} | Expenses: ${data['total_expenses']:.2f} | Savings: ${data['net_savings']:.2f}", ln=True)

    pdf.ln(10)

    # Save PDF
    pdf_path = "financial_report.pdf"
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True, mimetype="application/pdf")