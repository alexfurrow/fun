from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask Backend!"

# Set your OpenAI API key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_input = data.get('message', '')

    try:
        # Call the OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",  # Choose your model
            prompt=user_input,
            max_tokens=100,
        )
        reply = response.choices[0].text.strip()
        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
