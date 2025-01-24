from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_config():
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Database Configuration
DB_CONFIG = {
    'NAME': os.environ['DB_NAME'],  # Will raise error if not set
    'USER': os.environ['DB_USER'],
    'PASSWORD': os.environ['DB_PASSWORD'],
    'HOST': os.environ.get('DB_HOST', 'localhost'),  # Fallback for optional vars
    'PORT': os.environ.get('DB_PORT', '5432'),
}

# Create database URI
def get_database_url():
    return f"postgresql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['NAME']}"

# Initialize SQLAlchemy instance
db = SQLAlchemy() 