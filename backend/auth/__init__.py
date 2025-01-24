# This __init__.py file:
# Initializes JWT, Bcrypt, and LoginManager
# Provides a function to initialize auth with your Flask app
# Sets up user loading for Flask-Login
# Registers the auth blueprint
# 5. Adds JWT error handlers

# Initialize extensions
jwt = JWTManager()
bcrypt = Bcrypt()
login_manager = LoginManager()

def init_auth(app):
    """Initialize authentication modules with the Flask app"""
    # Initialize extensions
    jwt.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Import models here to avoid circular imports
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Set login view
    login_manager.login_view = 'auth.login'
    
    # Import and register blueprint
    from .routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Optional: JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'message': 'The token has expired',
            'error': 'token_expired'
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'message': 'Signature verification failed',
            'error': 'invalid_token'
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'message': 'Request does not contain an access token',
            'error': 'authorization_required'
        }, 401 