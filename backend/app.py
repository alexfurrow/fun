from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

from classes import Prompt
#from user import UserProfile

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



if __name__ == '__main__':
    app.run(debug=True)
