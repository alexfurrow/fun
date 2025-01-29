from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import bcrypt  # Import from extensions instead
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ..models.models import db, User, UserProfile
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, request, jsonify, session, current_app

auth_bp = Blueprint('auth', __name__)

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting for login attempts
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt - Email: {email}")
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        print(f"User found: {user is not None}")
        
        if not user:
            return jsonify({'error': 'No account found with this email'}), 401
        
        password_check = bcrypt.check_password_hash(user.password_hash, password)
        print(f"Password check result: {password_check}")
        
        if not password_check:
            return jsonify({'error': 'Incorrect password'}), 401

        # Create JWT token with user_id as identity
        access_token = create_access_token(identity=user.user_id)
        print("Access token created successfully")
        
        return jsonify({
            'access_token': access_token,
            'user_id': user.user_id,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 400


def create_auth_routes():  # Remove bcrypt parameter
    auth_bp = Blueprint('auth', __name__)

    @auth_bp.route('/auth/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            print(f"Login attempt - Email: {email}")
            
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            user = User.query.filter_by(email=email).first()
            print(f"User found: {user is not None}")
            
            if not user:
                return jsonify({'error': 'No account found with this email'}), 401
            
            password_check = bcrypt.check_password_hash(user.password_hash, password)
            print(f"Password check result: {password_check}")
            
            if not password_check:
                return jsonify({'error': 'Incorrect password'}), 401

            access_token = create_access_token(identity=user.user_id)
            print("Access token created successfully")
            
            return jsonify({
                'access_token': access_token,
                'user_id': user.user_id
            }), 200
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({'error': str(e)}), 400

    return auth_bp


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
        
    # Hash password and create user
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], 
                   email=data['email'], 
                   password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a more complex setup, you might want to blacklist the token
    return jsonify({'message': 'Logged out successfully'}), 200

# Token refresh
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({
        'access_token': new_access_token
    }), 200

# Add a route to check login status
@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'user_id': current_user.user_id,
                'username': current_user.username
            }
        }), 200
    return jsonify({'authenticated': False}), 401

# Password reset routes
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user:
            send_password_reset_email(user)
        # Always return success to prevent email enumeration
        return jsonify({'message': 'If an account exists with that email, a reset link has been sent.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = verify_token(data['token'], 'reset')
        if not email:
            return jsonify({'error': 'Invalid or expired token'}), 400
            
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.set_password(data['password'])
        db.session.commit()
        return jsonify({'message': 'Password reset successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/verify-email', methods=['POST'])
def process_email_verification():
    try:
        data = request.get_json()
        email = verify_token(data['token'], 'verify')
        if not email:
            return jsonify({'error': 'Invalid or expired token'}), 400
            
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.email_verified = True
        db.session.commit()
        return jsonify({'message': 'Email verified successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    try:
        email = verify_token(token, 'verify')
        if not email:
            return jsonify({'error': 'Invalid or expired token'}), 400
            
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.email_verified = True
        db.session.commit()
        return jsonify({'message': 'Email verified successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Token refresh
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({
        'access_token': new_access_token
    }), 200

# Session management
@auth_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            email_verified=False,
            active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'user_id': new_user.user_id,
                'username': new_user.username,
                'email': new_user.email,
                'profile': profile.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        print(f"Found {len(users)} users")
        return jsonify([{
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'profile': user.profile.to_dict() if user.profile else None
        } for user in users]), 200
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
# Get specific user
@auth_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'profile': user.profile.to_dict() if user.profile else None
    }), 200

# Add this new protected route
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()  # This decorator requires a valid JWT
def protected():
    # get_jwt_identity() gets the user_id we stored in the token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        'message': f'Protected route accessed by {user.username}',
        'user_id': current_user_id
    }), 200