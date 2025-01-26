from flask import Flask
from backend.models.models import User, db
from config.database import get_database_url

def test_create_user():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            
            # Create a test user
            test_user = User(
                username="test_user",
                email="test@example.com"
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully!")
            
            # Clean up
            db.session.delete(test_user)
            db.session.commit()
            print("✅ Test user cleaned up!")
            
            # Drop all tables
            db.drop_all()
            print("✅ Database tables cleaned up!")
            return True
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False

if __name__ == "__main__":
    # Run the test when file is executed
    print("Running user creation test...")
    result = test_create_user()
    if result:
        print("✅ All tests passed!")
    else:
        print("❌ Test failed!") 