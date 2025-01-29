import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""
    # Common settings for all environments
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    CORS_ORIGINS = ["http://localhost:3000"]
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"]
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Useful for debugging
    CORS_ORIGINS = ["http://localhost:3000"]  # Development frontend

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Production DB URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Better performance
    CORS_ORIGINS = [os.getenv("PRODUCTION_FRONTEND_URL")]  # Production frontend
    JWT_COOKIE_SECURE = True  # Only send cookies over HTTPS

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing

# Dictionary to map environment names to config classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 