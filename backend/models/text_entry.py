from datetime import datetime
from models.models import User  # Update this import
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Make sure db is accessible

class TextEntry(db.Model):
    __tablename__ = 'text_entries'
    
    entry_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # For storing text content
    title = db.Column(db.String(255))  # Optional title
    source_type = db.Column(db.String(50), nullable=False)  # 'txt_upload', 'manual', 'voice', 'audio'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('text_entries', lazy=True))
    
    def __repr__(self):
        return f'<TextEntry {self.entry_id} by User {self.user_id}>' 