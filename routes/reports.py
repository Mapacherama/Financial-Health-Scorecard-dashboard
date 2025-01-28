from flask import Blueprint, send_file
from fpdf import FPDF
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
    
    # Check if the data is nested under a key
    if isinstance(historical_data_json, dict):
        data_to_iterate = historical_data_json.get('data', [])
    else:
        data_to_iterate = historical_data_json

    for data in data_to_iterate:
        if isinstance(data, dict):
            pdf.cell(200, 8, 
                f"{data.get('month', 'N/A')} - "
                f"Income: ${data.get('total_income', 0):.2f} | "
                f"Expenses: ${data.get('total_expenses', 0):.2f} | "
                f"Savings: ${data.get('net_savings', 0):.2f}", 
                ln=True)

    pdf.ln(10)

    # Save PDF
    pdf_path = "financial_report.pdf"
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True, mimetype="application/pdf")