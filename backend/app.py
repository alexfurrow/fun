from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
from .auth import init_auth
from .models.models import db, User, UserProfile, YapEntry
from .routes.auth_routes import auth_bp, limiter
from flask_migrate import Migrate
from flask_session import Session
from datetime import timedelta
from flask_mail import Mail
from .auth.email import mail
from .services.services import Prompt
from .utils.utils import InitialText
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
import redis
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager
from .routes.yap_routes import yap_bp
from .extensions import bcrypt, jwt, init_extensions

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

# Initialize extensions
init_extensions(app)

# Configure CORS more explicitly
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        "supports_credentials": True,
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }
})

# Add session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configure Redis for rate limiting
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

# Initialize limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    storage_options={"connection_pool": redis.ConnectionPool.from_url("redis://localhost:6379")}
)

# Database Configuration
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'another-secret-key')   # For Flask-Login
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Add email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['FRONTEND_URL'] = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
init_auth(app)

# Import and register blueprints
from .routes.auth_routes import create_auth_routes
from .routes.yap_routes import yap_bp

# Create and register blueprints
auth_bp = create_auth_routes(bcrypt)
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(yap_bp, url_prefix='/api')

# Initialize mail
mail.init_app(app)

# Add OPTIONS handler for the specific endpoint
@app.route('/api/yap', methods=['OPTIONS'])
def handle_options():
    response = jsonify({'message': 'OK'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
    app.run(debug=True)

@app.route('/')
def home():
    return "Welcome to the Flask Backend!"

# Set your OpenAI API key from the .env file
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/api/generate', methods=['POST'])
def generate_page():
    client = OpenAI()
    data = request.get_json()
    user_input = data.get('message','')
    
    prompt_instance = Prompt(
        style="poetic", 
        author_to_emulate="Maya Angelou",
        user_profile={"age":37, "gender":"male","race":"whaite","city":"Houston"},
        orientation = "refinement"
        )
    system_prompt = prompt_instance.system_prompt(orientation = 'refinement')
    formatted_prompt = prompt_instance.generate_prompt(orientation = 'refinement', user_input = user_input)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format = { "type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_prompt}
        ],
        max_tokens=4000,
        temperature=1
    )
    reply = response.choices[0].message.content
    return jsonify({"reply":reply})

# def generate_poem():
#     client = OpenAI()
#     data = request.get_json()
#     user_input = data.get('message','')
    
#     prompt_instance = Prompt(
#         style="poetic", 
#         author_to_emulate="Maya Angelou",
#         user_profile={"age":37, "gender":"male","race":"whaite","city":"Houston"}
#         )
#     system_prompt = prompt_instance.system_prompt('poem')
#     formatted_prompt = prompt_instance.generate_prompt(user_input)

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         response_format = { "type": "json_object"},
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": formatted_prompt}
#         ],
#         max_tokens=100,
#         temperature=1.0
#     )
#     reply = response.choices[0].message.content
#     return jsonify({"reply":reply})

@app.route('/api/yap', methods=['POST'])
@jwt_required()  # Ensure user is authenticated
def process_yap():
    try:
        data = request.get_json()
        raw_text = data.get('content')
        current_user_id = get_jwt_identity()
        
        # Create new YapEntry with raw text
        new_yap = YapEntry(
            user_id=current_user_id,
            content=raw_text,
            source_type='manual'
        )
        
        # Process text through Prompt service
        prompt_instance = Prompt(
            orientation="refinement",
            style="poetic",
            author_to_emulate="Maya Angelou",
            user_profile={"age":37, "gender":"male","race":"white","city":"Houston"}
        )
        
        # Get refined text from OpenAI
        client = OpenAI()
        system_prompt = prompt_instance.system_prompt(orientation='refinement')
        formatted_prompt = prompt_instance.generate_prompt(orientation='refinement', user_input=raw_text)
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ],
            max_tokens=4000,
            temperature=1
        )
        
        refined_text = response.choices[0].message.content
        new_yap.refined_text = refined_text
        
        # Save to database
        db.session.add(new_yap)
        db.session.commit()
        
        return jsonify({
            "message": "Yap processed successfully",
            "entry_id": new_yap.entry_id,
            "refined_text": refined_text
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
