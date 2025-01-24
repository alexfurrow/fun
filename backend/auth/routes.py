from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, 
    create_access_token,
    get_jwt_identity,
    decode_token
)
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

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
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token}), 200
        
    return jsonify({'error': 'Invalid credentials'}), 401



# Password reset routes
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user:
        # Generate password reset token
        reset_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
        # In production, you'd send this via email
        return jsonify({
            'message': 'Password reset instructions sent',
            'token': reset_token  # In production, remove this and send via email
        }), 200
    return jsonify({'error': 'Email not found'}), 404

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    try:
        user_id = decode_token(data['reset_token'])['sub']
        user = User.query.get(user_id)
        
        if user:
            hashed_password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
            user.password_hash = hashed_password
            db.session.commit()
            return jsonify({'message': 'Password updated successfully'}), 200
    except:
        return jsonify({'error': 'Invalid or expired reset token'}), 400

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
    new_token = create_access_token(identity=current_user_id)
    return jsonify({'token': new_token}), 200

# Optional: Email verification
@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    try:
        user_id = decode_token(token)['sub']
        user = User.query.get(user_id)
        if user:
            user.email_verified = True
            db.session.commit()
            return jsonify({'message': 'Email verified successfully'}), 200
    except:
        return jsonify({'error': 'Invalid verification token'}), 400

@auth_bp.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
        
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201