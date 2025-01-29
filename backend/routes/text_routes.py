from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from ..models.models import db, TextEntry, User  # Import db from models
import os

text_bp = Blueprint('text', __name__, url_prefix='/api/text')

ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@text_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            # Get current user
            current_user_id = get_jwt_identity()
            
            # Read and decode the file content
            content = file.read().decode('utf-8')
            
            # Create new text entry
            new_entry = TextEntry(
                user_id=current_user_id,
                content=content,
                title=secure_filename(file.filename),
                source_type='txt_upload'
            )
            
            db.session.add(new_entry)
            db.session.commit()
            
            return jsonify({
                'message': 'File uploaded successfully',
                'entry_id': new_entry.entry_id
            }), 201
            
        return jsonify({'error': 'File type not allowed'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@text_bp.route('/text', methods=['POST'])
@jwt_required()
def save_text():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        new_text = TextEntry(
            user_id=current_user_id,
            content=data.get('content'),
            entry_type=data.get('type', 'general')
        )
        
        db.session.add(new_text)
        db.session.commit()
        
        return jsonify({
            "message": "Text saved successfully",
            "entry_id": new_text.entry_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@text_bp.route('/text', methods=['GET'])
@jwt_required()
def get_texts():
    try:
        current_user_id = get_jwt_identity()
        texts = TextEntry.query.filter_by(user_id=current_user_id).all()
        
        return jsonify([{
            "entry_id": text.entry_id,
            "content": text.content,
            "type": text.entry_type,
            "created_at": text.created_at
        } for text in texts]), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 