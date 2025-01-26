from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.text_entry import TextEntry  # Update this import
from models.models import User  # If needed
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

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