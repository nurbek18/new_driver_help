from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    locale = db.Column(db.String(2), default='ru')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<Driver {self.name}>'

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Setting {self.key}>'