from flask_mail import Mail, Message
from flask import current_app, url_for
import jwt
from datetime import datetime, timedelta

mail = Mail()

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

def send_password_reset_email(user):
    token = generate_token(user.email, 'reset')
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
    
    template = f"""
    <h1>Password Reset Request</h1>
    <p>To reset your password, click the following link:</p>
    <a href="{reset_url}">Reset Password</a>
    <p>If you did not request this reset, please ignore this email.</p>
    <p>This link will expire in 30 minutes.</p>
    """
    
    send_email(user.email, 'Password Reset Request', template)

def send_verification_email(user):
    token = generate_token(user.email, 'verify')
    verify_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={token}"
    
    template = f"""
    <h1>Verify Your Email</h1>
    <p>To verify your email address, click the following link:</p>
    <a href="{verify_url}">Verify Email</a>
    <p>If you did not create an account, please ignore this email.</p>
    <p>This link will expire in 24 hours.</p>
    """
    
    send_email(user.email, 'Verify Your Email', template)

def generate_token(email, type='reset'):
    expiry = datetime.utcnow() + timedelta(hours=24 if type == 'verify' else 0.5)
    return jwt.encode(
        {
            'email': email,
            'type': type,
            'exp': expiry.timestamp()
        },
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

def verify_token(token, type='reset'):
    try:
        data = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        if data['type'] != type:
            return None
        return data['email']
    except:
        return None 