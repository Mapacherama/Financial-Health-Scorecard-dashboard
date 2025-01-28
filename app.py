from flask import Flask
from flask_cors import CORS
from db import initialize_db

# Import Blueprints from the routes folder
from routes.financials import financials_bp
from routes.forecasting import forecasting_bp
from routes.historical import historical_bp
from routes.insights import insights_bp
from routes.investments import investments_bp

app = Flask(__name__)
CORS(app)

# Initialize the database before running the app
initialize_db()

# Registering Blueprints
app.register_blueprint(financials_bp)
app.register_blueprint(forecasting_bp)
app.register_blueprint(historical_bp)
app.register_blueprint(insights_bp)
app.register_blueprint(investments_bp)

if __name__ == '__main__':
    app.run(debug=True)
