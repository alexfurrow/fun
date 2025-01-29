from flask import Blueprint, request, jsonify, session, current_app
from flask_jwt_extended import (
    jwt_required, 
    create_access_token,
    get_jwt_identity,
    decode_token
)
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from ..models.models import db, User, UserProfile
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ..auth.email import send_password_reset_email, send_verification_email, verify_token
from ..extensions import bcrypt  # Import bcrypt from extensions

auth_bp = Blueprint('auth', __name__)

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


