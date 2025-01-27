from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..extensions import bcrypt  # Import from extensions instead

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