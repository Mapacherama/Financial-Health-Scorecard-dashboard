from db import connect_db

def create_budget(user_id: int, category: str, allocated_amount: float, month_year: str):
    """
    Create a new budget for a specific category and month.
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO budgets (user_id, category, allocated_amount, month_year)
        VALUES (?, ?, ?, ?)
    """, (user_id, category, allocated_amount, month_year))
    
    conn.commit()
    conn.close()
    
    return {"message": f"Budget for {category} in {month_year} created successfully"}

def check_budget_status(category: str, month_year: str):
    """
    Check if the budget is exceeded.
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT allocated_amount, spent_amount FROM budgets 
        WHERE category = ? AND month_year = ?
    """, (category, month_year))
    
    budget = cursor.fetchone()
    conn.close()
    
    if not budget:
        return {"message": f"No budget found for {category} in {month_year}"}
    
      
    allocated, spent = budget
    status = "✅ Within Budget" if spent <= allocated else "⚠️ Over Budget"
    
    return {
        "category": category,
        "month_year": month_year,
        "allocated_amount": allocated,
        "spent_amount": spent,
        "status": status
    }