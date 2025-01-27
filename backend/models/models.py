from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re
import datetime
from datetime import datetime, timedelta

db = SQLAlchemy()
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    profile = db.relationship('UserProfile', backref='user', uselist=False)

    def get_id(self):
        """Override get_id from UserMixin"""
        return str(self.user_id)

    @staticmethod
    def is_password_valid(password):
        """Check if password meets security requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        return True, "Password is valid"

    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        db.session.commit()

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True, (self.locked_until - datetime.utcnow()).seconds
        self.locked_until = None
        return False, 0

    def set_password(self, password):
        """Set password with validation"""
        is_valid, message = self.is_password_valid(password)
        if not is_valid:
            raise ValueError(message)
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    race = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100))

    def __repr__(self):
        return f'<Profile for {self.user.username}>'

    def to_dict(self):
        return {
            "userid": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "race": self.race,
            "city": self.city
        }
    
class YapEntry(db.Model):
    __tablename__ = 'yap_entries'
    
    entry_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    raw_text = db.Column(db.Text, nullable=False)  # Raw text content
    refined_text = db.Column(db.Text)  # New column for AI-refined text
    title = db.Column(db.String(255))
    source_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('yap_entries', lazy=True))
    
    def __repr__(self):
        return f'<YapEntry {self.entry_id} by User {self.user_id}>' 