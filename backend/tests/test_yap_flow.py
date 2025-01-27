from flask import Flask
from backend.models.models import User, db, YapEntry
from backend.services.services import Prompt
from config.database import get_database_url
import json

def test_yap_flow():
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
            print("✅ Test user created!")
            
            # Create a test yap entry
            test_yap = YapEntry(
                user_id=test_user.user_id,
                content="This is a test yap entry. I had a great day today!",
                source_type="manual"
            )
            db.session.add(test_yap)
            db.session.commit()
            print("✅ Test yap entry created!")
            
            # Verify the entry exists
            entry = YapEntry.query.filter_by(user_id=test_user.user_id).first()
            if entry and entry.content:
                print("✅ Successfully retrieved yap entry!")
                print(f"Content: {entry.content}")
                print(f"Refined text: {entry.refined_text}")
            
            # Clean up
            db.session.delete(test_yap)
            db.session.delete(test_user)
            db.session.commit()
            print("✅ Test data cleaned up!")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False

if __name__ == "__main__":
    print("Running yap flow test...")
    result = test_yap_flow()
    if result:
        print("✅ All tests passed!")
    else:
        print("❌ Test failed!") 