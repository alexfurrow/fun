from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return "Welcome to the Flask Backend!"

# Set your OpenAI API key from the .env file
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/api/generate', methods=['POST'])
def generate():
    client = OpenAI()
    data = request.get_json()
    user_input = data.get('message', '')

    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Choose your model
            response_format = { "type": "json_object" },
            messages = [
                {"role":"system", "content": "You are a helpful assistant. reply in json"},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100,
            temperature=1
        )
        reply = response.choices[0].message.content
        return jsonify({"reply":reply})
        # return reply

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
