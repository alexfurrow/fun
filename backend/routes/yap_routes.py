from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.models import db, YapEntry
from ..services.services import Prompt
from openai import OpenAI

yap_bp = Blueprint('yap', __name__, url_prefix='/api')

@yap_bp.route('/generate', methods=['POST'])
def generate_page():
    client = OpenAI()
    data = request.get_json()
    user_input = data.get('message','')
    
    prompt_instance = Prompt(
        style="poetic", 
        author_to_emulate="Maya Angelou",
        user_profile={"age":37, "gender":"male","race":"white","city":"Houston"},
        orientation = "refinement"
    )
    system_prompt = prompt_instance.system_prompt(orientation = 'refinement')
    formatted_prompt = prompt_instance.generate_prompt(orientation = 'refinement', user_input = user_input)

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
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

@yap_bp.route('/yap', methods=['POST'])
@jwt_required()
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