from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Initialize without app
bcrypt = Bcrypt()
jwt = JWTManager()

def init_extensions(app):
    # Initialize with app
    bcrypt.init_app(app)
    jwt.init_app(app)