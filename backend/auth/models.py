from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

#am i sure i want a user id here or somewhere else? 
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    race = db.Column(db.String(50))
    city = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            "userid": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "race": self.race,
            "city": self.city
        }
