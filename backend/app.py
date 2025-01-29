from flask import Flask
from flask_cors import CORS
from .models.models import db
from flask_migrate import Migrate
from .routes.auth_routes import auth_bp
from .routes.yap_routes import yap_bp
from .routes.text_routes import text_bp
from .routes.profile_routes import profile_bp
from .extensions import init_extensions
from .config import Config
import os

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Get config name from environment or use default
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Load the config
    app.config.from_object(config[config_name])

    # Initialize extensions
    init_extensions(app)

    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": app.config['CORS_METHODS'],
            "allow_headers": app.config['CORS_HEADERS'],
            "supports_credentials": True,
            "expose_headers": ["Content-Range", "X-Content-Range"]
        }
    })

    # Initialize database
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(yap_bp)
    app.register_blueprint(text_bp)
    app.register_blueprint(profile_bp)

    @app.route('/')
    def home():
        return "Welcome to the Flask Backend!"

    return app

# Usage:
app = create_app()  # Will use FLASK_ENV or default to 'development'

if __name__ == '__main__':
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
    app.run(debug=True)
