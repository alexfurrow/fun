from flask import Blueprint, request, jsonify, session, current_app
from flask_jwt_extended import (
    jwt_required, 
    create_access_token,
    get_jwt_identity,
    decode_token
)
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, UserProfile
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .email import send_password_reset_email, send_verification_email, verify_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
bcrypt = Bcrypt()

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

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

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
            
        # Check if account is locked
        is_locked, seconds_remaining = user.is_locked()
        if is_locked:
            return jsonify({
                'error': f'Account is locked. Try again in {seconds_remaining} seconds'
            }), 401
            
        if user.check_password(data['password']):
            login_user(user)
            session['user_id'] = user.user_id
            user.reset_failed_attempts()
            
            # Create the JWT token
            access_token = create_access_token(identity=user.user_id)
            
            return jsonify({
                'message': 'Logged in successfully',
                'access_token': access_token,  # Include the token in response
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200
            
        # Failed login attempt
        user.increment_failed_attempts()
        return jsonify({'error': 'Invalid username or password'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/logout', methods=['POST'])
@login_required
def user_logout():
    user_id = session.get('user_id')
    if user_id:
        session.pop('user_id', None)  # Clear from session
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

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
def verify_email():
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

# User profile routes
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()  # Requires valid JWT token
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        'username': user.username,
        'email': user.email,
        # Add other profile fields as needed
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    data = request.get_json()
    
    # Update allowed fields
    if 'username' in data:
        user.username = data['username']
    # Add other updatable fields
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

# Session management
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

@auth_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user with password
        new_user = User(
            username=data['username'],
            email=data['email'],
            email_verified=False  # Start as unverified
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send verification email
        send_verification_email(new_user)
        
        # Create profile
        profile = UserProfile(
            user_id=new_user.user_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            gender=data.get('gender'),
            race=data.get('race'),
            city=data.get('city')
        )
        db.session.add(profile)
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