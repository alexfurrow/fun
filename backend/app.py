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
def generate():
    client = OpenAI()
    data = request.get_json()
    user_input = data.get('message','')
    
    prompt_instance = Prompt(
        style="poetic", 
        author_to_emulate="Maya Angelou",
        user_profile={"age":37, "gender":"male","race":"whaite","city":"Houston"}
        )
    system_prompt = prompt_instance.system_prompt()
    formatted_prompt = prompt_instance.generate_prompt(user_input)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format = { "type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_prompt}
        ],
        max_tokens=100,
        temperature=1.0
    )
    reply = response.choices[0].message.content
    return jsonify({"reply":reply})
if __name__ == '__main__':
    app.run(debug=True)

# def generate():
#     client = OpenAI()
#     data = request.get_json()
#     user_input = data.get('message', '')

#     try:
#         # Call the OpenAI API
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",  # Choose your model
#             response_format = { "type": "json_object" },
#             messages = [
#                 {"role":"system", "content": f"Write a poem in the style of {poet}"},
#                 {"role": "user", "content": user_input}
#             ],
#             max_tokens=100,
#             temperature=1
#             )
#         reply = response.choices[0].message.content
#         return jsonify({"reply":reply})
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#user_input = "hey so I was having an awesome day today. I woke up and played 3 games of dota, won 2, but played well in all 3. I had my coffee and I was able to sleep in but I did wake up in the middle of the night with some heart burn. I had eating that bread, I think maybe I have a gluten alergy because it straight up was giving me nightmares. I don't remember the nightmare, what was it, it was something like. well, i don't remember, but people were mad at me. my mouth felt gross so i went to the bathroom and rinsed out. i was able to fall back asleep and eventually woke up at 930, which isn't ideal but i realized i could probably get away with a later schedule because i generally dont have to be in before 9 during the work week anwyay. its not like i need to get up at 630. it's all about finding my rythym. so anyway, i spent the rest of the day working on my side projects and i plan to work on my interview prep, at least 30 minutes, but the side projects longer. i have a new theme, which is 'no fun', which is like a reminder that the impulse to have fun almost always makes my life worse later. and instead, it's way more fun when i am doing the things that make me happy, like eating a healthy meal and feeling energized by that because my body naturally feels more energy, or like working out because its fun and stuff, or at least it feels good. and the discipline to do that rather than like, thinking 'oh i have some time off, let me go get icecream or play videogames all morning', there's something to that, you know, but basically delaying gratification and if you want, call it type 2 fun, wehre you look back on it and youre like yeah that was awesome, rather than going for immediate gratification. thesee are old ideas but they are applying freshly to my life now. anyway, i am just writing up my app and doing my pomodoro, which is good. i feel really good about where i am, as long as im taking advantage of the time to prepare, i will be okay. i do want to spend more time building things socially, but this weekend was really about proving something to myself in terms of the things i want to do with my life, and doing them. its a resume weekend, not an obituary weekend. so many things i want to do. anyway, gotta get back to work, bye."
