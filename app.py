import os
import logging
import random
import string
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
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
from models import User, Driver, Setting

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
    
    # Create default settings if they don't exist
    if not Setting.query.filter_by(key='support_whatsapp').first():
        support_whatsapp = Setting(
            key='support_whatsapp',
            value='+77082836678',
            description='WhatsApp number for customer support'
        )
        db.session.add(support_whatsapp)
        db.session.commit()
        logging.info("Default settings created")

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
# Check and set locale before each request
@app.before_request
def before_request():
    if 'locale' not in session:
        if current_user.is_authenticated and current_user.locale:
            session['locale'] = current_user.locale
        else:
            session['locale'] = 'ru'  # Default to Russian
    
    # Set the language code in Flask's g object for templates to use
    g.lang_code = session.get('locale', 'ru')

@app.context_processor
def utility_processor():
    # Get support WhatsApp number from settings
    support_whatsapp = Setting.query.filter_by(key='support_whatsapp').first()
    whatsapp_number = support_whatsapp.value if support_whatsapp else '+77082836678'
    
    return {
        '_': _, 
        'current_locale': session.get('locale', 'ru'),
        'support_whatsapp': whatsapp_number
    }

# Routes for language switching
@app.route('/set_language/<language>')
def set_language(language):
    if language in ['en', 'ru', 'kk', 'zh']:
        session['locale'] = language
    
    # Redirect back to the referring page
    next_page = request.args.get('next') or request.referrer or '/'
    return redirect(next_page)

@app.route('/language')
def language_page():
    # Get the next page URL from query parameters
    next_url = request.args.get('next') or request.referrer or '/'
    return render_template('language_selector.html', next_url=next_url)

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/driver_form', methods=['GET', 'POST'])
def driver_form():
    if request.method == 'POST':
        try:
            # Get form data
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
                whatsapp=data['whatsapp']
            )
            
            db.session.add(new_driver)
            db.session.commit()
            
            return jsonify({
                "message": _('driver_added'), 
                "id": new_driver.id,
                "driver_code": new_driver.driver_code
            }), 201
        
        except Exception as e:
            logging.error(f"Error adding driver from form: {e}")
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
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
            
            # Do not override user's selected language
            # Keep previous session['locale'] value
            
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

# Admin profile route
@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if not current_user.is_admin:
        flash(_('admin_access_required'))
        return redirect(url_for('index'))
    
    # Create a form instance (using WTForms)
    class ProfileForm:
        def hidden_tag(self):
            return ''
    
    form = ProfileForm()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Check current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash(_('incorrect_password'), 'danger')
            return render_template('admin_profile.html', form=form)
        
        # Update user profile
        current_user.username = username
        current_user.email = email
        
        # If new password provided, update it
        if new_password:
            if new_password != confirm_password:
                flash(_('passwords_dont_match'), 'danger')
                return render_template('admin_profile.html', form=form)
            
            current_user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        flash(_('profile_updated'), 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_profile.html', form=form)

# Admin settings route
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        flash(_('admin_access_required'))
        return redirect(url_for('index'))
    
    # Get support WhatsApp setting
    support_whatsapp = Setting.query.filter_by(key='support_whatsapp').first()
    
    if request.method == 'POST':
        # Update WhatsApp number
        whatsapp_number = request.form.get('support_whatsapp')
        
        if whatsapp_number:
            if support_whatsapp:
                support_whatsapp.value = whatsapp_number
            else:
                support_whatsapp = Setting(
                    key='support_whatsapp',
                    value=whatsapp_number,
                    description='WhatsApp number for customer support'
                )
                db.session.add(support_whatsapp)
            
            db.session.commit()
            flash(_('settings_updated'), 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash(_('invalid_whatsapp'), 'danger')
    
    return render_template('admin_settings.html', support_whatsapp=support_whatsapp.value if support_whatsapp else '')

# API endpoints
@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    try:
        # Get filters from query parameters
        gender = request.args.get('gender')
        search_query = request.args.get('search')
        
        query = Driver.query
        
        # Apply gender filter if provided
        if gender and gender != 'all':
            query = query.filter_by(gender=gender)
            
        # Apply search filter if provided (search by name, code, or phone)
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                db.or_(
                    Driver.name.ilike(search_pattern),
                    Driver.driver_code.ilike(search_pattern),
                    Driver.phone.ilike(search_pattern)
                )
            )
            
        drivers = query.all()
        
        return jsonify([{
            'id': driver.id,
            'driver_code': driver.driver_code,
            'name': driver.name,
            'age': driver.age,
            'gender': driver.gender,
            'phone': driver.phone,
            'whatsapp': driver.whatsapp
        } for driver in drivers])
    except Exception as e:
        logging.error(f"Error getting drivers: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drivers', methods=['POST'])
@login_required
def add_driver():
    try:
        # Only admins can add drivers via API
        if not current_user.is_admin:
            return jsonify({"error": _('admin_access_required')}), 403
            
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
            whatsapp=data['whatsapp']
        )
        
        db.session.add(new_driver)
        db.session.commit()
        
        return jsonify({
            "message": _('driver_added'), 
            "id": new_driver.id,
            "driver_code": new_driver.driver_code
        }), 201
    
    except Exception as e:
        logging.error(f"Error adding driver: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/drivers/<int:driver_id>', methods=['PUT'])
@login_required
def update_driver(driver_id):
    try:
        # Only admins can update drivers
        if not current_user.is_admin:
            return jsonify({"error": _('admin_access_required')}), 403
            
        data = request.get_json()
        driver = Driver.query.get_or_404(driver_id)
        
        # Update driver fields
        if 'name' in data:
            driver.name = data['name']
        if 'age' in data:
            driver.age = data['age']
        if 'gender' in data:
            driver.gender = data['gender']
        if 'phone' in data:
            driver.phone = data['phone']
        if 'whatsapp' in data:
            driver.whatsapp = data['whatsapp']
            
        db.session.commit()
        
        return jsonify({
            "message": _('driver_updated'),
            "id": driver.id
        })
    
    except Exception as e:
        logging.error(f"Error updating driver {driver_id}: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/drivers/<int:driver_id>', methods=['DELETE'])
@login_required
def delete_driver(driver_id):
    try:
        # Only admins can delete drivers
        if not current_user.is_admin:
            return jsonify({"error": _('admin_access_required')}), 403
            
        driver = Driver.query.get_or_404(driver_id)
        db.session.delete(driver)
        db.session.commit()
        
        return jsonify({
            "message": _('driver_deleted')
        })
    
    except Exception as e:
        logging.error(f"Error deleting driver {driver_id}: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
