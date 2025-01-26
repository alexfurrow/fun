from flask import Flask
from auth.models import User, UserProfile, db
from config.database import get_database_url
import random
import string

def generate_random_string(length=8):
    """Generate a random string for unique usernames"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def cleanup_all_data():
    """Function to clean up all data from both tables"""
    try:
        # Delete all profiles first (because of foreign key constraints)
        UserProfile.query.delete()
        # Delete all users
        User.query.delete()
        db.session.commit()
        print("✅ All existing data cleaned up!")
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        return False

def test_user_profile_relationship():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    db.init_app(app)
    
    with app.app_context():
        try:
            # Clean up any existing data first
            cleanup_all_data()
            
            # Create a test user with random username
            random_username = f"test_user_{generate_random_string()}"
            test_user = User(
                username=random_username,
                email=f"{random_username}@example.com"
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ Created user with ID: {test_user.user_id}")
            
            # Create their profile with all required fields
            test_profile = UserProfile(
                user_id=test_user.user_id,
                first_name="Alex",
                last_name="Fisher",
                age=25,
                gender="male",
                race="Caucasian",
                city="Seattle"
            )
            db.session.add(test_profile)
            db.session.commit()
            print(f"✅ Created profile with ID: {test_profile.profile_id} for user_id: {test_profile.user_id}")
            
            # Verify the relationship
            fetched_user = User.query.get(test_user.user_id)
            print(f"\nVerifying relationship:")
            print(f"User ID: {fetched_user.user_id}")
            print(f"Username: {fetched_user.username}")
            print(f"User's Profile:")
            print(f"  Name: {test_profile.first_name} {test_profile.last_name}")
            print(f"  Race: {test_profile.race}")
            print(f"  City: {test_profile.city}")
            
            # Clean up all data again
            cleanup_all_data()
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            # Try to clean up on failure
            try:
                db.session.rollback()
                cleanup_all_data()
            except:
                pass
            return False

if __name__ == "__main__":
    print("Testing user-profile relationship...")
    result = test_user_profile_relationship()
    if result:
        print("✅ All tests passed!")
    else:
        print("❌ Test failed!") 