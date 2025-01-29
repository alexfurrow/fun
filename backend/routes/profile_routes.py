from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.models import db, User, UserProfile

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        profile = user.profile
        
        return jsonify({
            'username': user.username,
            'email': user.email,
            'profile': {
                'first_name': profile.first_name if profile else None,
                'last_name': profile.last_name if profile else None,
                'age': profile.age if profile else None,
                'gender': profile.gender if profile else None,
                'race': profile.race if profile else None,
                'city': profile.city if profile else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        data = request.get_json()
        
        # Update or create profile
        if not user.profile:
            user.profile = UserProfile()
            
        profile = user.profile
        profile.first_name = data.get('first_name', profile.first_name)
        profile.last_name = data.get('last_name', profile.last_name)
        profile.age = data.get('age', profile.age)
        profile.gender = data.get('gender', profile.gender)
        profile.race = data.get('race', profile.race)
        profile.city = data.get('city', profile.city)
        
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
