from flask import Flask
from config.database import db, validate_config

def test_db_connection():
    try:
        # Create a test Flask app
        app = Flask(__name__)
        
        # Configure the test app
        app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
        db.init_app(app)
        
        # Try to connect
        with app.app_context():
            db.engine.connect()
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    # First validate environment variables
    try:
        validate_config()
        print("✅ Environment variables validated!")
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        exit(1)
    
    # Then test connection
    test_db_connection() 