import os
import logging
import random
import string
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from translations import translations

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Setup database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "driver_service_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Needed for url_for to generate with https

# Configure database
db_url = os.environ.get("DATABASE_URL")
if db_url is None:
    logging.warning("DATABASE_URL not found, using SQLite")
    db_url = "sqlite:///drivers.db"
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after app and db are defined to avoid circular imports
from models import User, Driver

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and admin user
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Admin user created")

# Generate driver code function
def generate_driver_code():
    letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
    numbers = ''.join(random.choice(string.digits) for _ in range(4))
    return f"{letters}{numbers}"

# Translation helper
def _(text):
    locale = session.get('locale', 'en')
    if locale in translations and text in translations[locale]:
        return translations[locale][text]
    return text

# Make translation function available in templates
@app.context_processor
def utility_processor():
    return {'_': _}

# Routes for language switching
@app.route('/set_language/<language>')
def set_language(language):
    if language in ['en', 'ru', 'kk', 'zh']:
        session['locale'] = language
    
    # Redirect back to the referring page
    next_page = request.args.get('next') or request.referrer or '/'
    return redirect(next_page)

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/driver_form')
def driver_form():
    return render_template('driver_form.html')

@app.route('/user_view')
def user_view():
    return render_template('user_view.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Use Flask-Login to log in the user
            login_user(user)
            # Set user locale in session if not already set
            if not session.get('locale'):
                session['locale'] = user.locale
            
            flash(_('login_successful'))
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        
        flash(_('invalid_credentials'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('logout_successful'))
    return redirect(url_for('index'))

# Admin dashboard route
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash(_('admin_access_required'))
        return redirect(url_for('index'))
    
    drivers = Driver.query.all()
    return render_template('admin.html', drivers=drivers)

# API endpoints
@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    try:
        drivers = Driver.query.all()
        return jsonify([{
            'id': driver.id,
            'driver_code': driver.driver_code,
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
        required_fields = ['name', 'age', 'gender', 'phone', 'whatsapp']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create new driver
        new_driver = Driver(
            driver_code=generate_driver_code(),
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            phone=data['phone'],
            whatsapp=data['whatsapp'],
            available=data.get('available', True)
        )
        
        db.session.add(new_driver)
        db.session.commit()
        
        return jsonify({
            "message": "Driver added successfully", 
            "id": new_driver.id,
            "driver_code": new_driver.driver_code
        }), 201
    
    except Exception as e:
        logging.error(f"Error adding driver: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
