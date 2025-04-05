import os
import logging
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Setup database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "driver_service_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///drivers.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Enable CORS
CORS(app)

# Initialize the app with the extension
db.init_app(app)

# Import models after db initialization to avoid circular imports
from models import Driver

# Create all tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/driver_form')
def driver_form():
    return render_template('driver_form.html')

@app.route('/user_view')
def user_view():
    return render_template('user_view.html')

# API endpoints
@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    try:
        drivers = Driver.query.all()
        return jsonify([{
            'id': driver.id,
            'name': driver.name,
            'age': driver.age,
            'gender': driver.gender,
            'phone': driver.phone,
            'whatsapp': driver.whatsapp,
            'available': driver.available
        } for driver in drivers])
    except Exception as e:
        logging.error(f"Error getting drivers: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drivers', methods=['POST'])
def add_driver():
    try:
        data = request.get_json()
        logging.debug(f"Received data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'age', 'gender', 'phone', 'whatsapp', 'available']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create new driver
        new_driver = Driver(
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            phone=data['phone'],
            whatsapp=data['whatsapp'],
            available=data['available']
        )
        
        db.session.add(new_driver)
        db.session.commit()
        
        return jsonify({"message": "Driver added successfully", "id": new_driver.id}), 201
    
    except Exception as e:
        logging.error(f"Error adding driver: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
