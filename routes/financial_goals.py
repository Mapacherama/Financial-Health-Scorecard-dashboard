from flask import Blueprint, request, jsonify
from db import connect_db

financial_goals_bp = Blueprint('financial_goals', __name__)

# Model for Financial Goals (if using SQLAlchemy)
@financial_goals_bp.route('/api/financial_goals', methods=['GET'])
def get_financial_goals():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM financial_goals WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])

@financial_goals_bp.route('/api/financial_goals', methods=['POST'])
def create_financial_goal():
    data = request.json
    if not all(key in data for key in ['user_id', 'goal_name', 'target_amount']):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO financial_goals (user_id, goal_name, target_amount, current_amount, due_date, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data['user_id'], data['goal_name'], data['target_amount'], data.get('current_amount', 0.0), data.get('due_date'), data.get('category')))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Financial goal added successfully!"}), 201

@financial_goals_bp.route('/api/financial_goals/<int:goal_id>', methods=['PUT'])
def update_financial_goal(goal_id):
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM financial_goals WHERE id = ?", (goal_id,))
    goal = cursor.fetchone()
    if not goal:
        conn.close()
        return jsonify({"error": "Goal not found"}), 404
    
    cursor.execute("""
        UPDATE financial_goals 
        SET goal_name = ?, target_amount = ?, current_amount = ?, due_date = ?, category = ? 
        WHERE id = ?
    """, (data.get('goal_name', goal['goal_name']), data.get('target_amount', goal['target_amount']), data.get('current_amount', goal['current_amount']), data.get('due_date', goal['due_date']), data.get('category', goal['category']), goal_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Financial goal updated successfully!"})

@financial_goals_bp.route('/api/financial_goals/<int:goal_id>', methods=['DELETE'])
def delete_financial_goal(goal_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM financial_goals WHERE id = ?", (goal_id,))
    goal = cursor.fetchone()
    if not goal:
        conn.close()
        return jsonify({"error": "Goal not found"}), 404
    
    cursor.execute("DELETE FROM financial_goals WHERE id = ?", (goal_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Financial goal deleted successfully!"})
