from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

#am i sure i want a user id here or somewhere else? 
class UserProfile:
    def __init__(self, userid: str, age: int, gender: str, race: str, city: str):
        """
        Initialize a UserProfile object.

        Args:
            id: The identification of the user.
            age (int): The age of the user.
            gender (str): The gender of the user.
            race (str): The race of the user.
            city (str): The city where the user resides.
        """
        self.id = id
        self.age = age
        self.gender = gender
        self.race = race
        self.city = city
    
    #demographics (copy from above)\
    #self defined
    #other defined

    def to_dict(self) -> dict:
        """
        Convert the user profile to a dictionary.

        Returns:
            dict: The user profile as a dictionary.
        """
        return {
            "id": self.id,
            "Age": self.age,
            "Gender": self.gender,
            "Race": self.race,
            "City": self.city,
        }
