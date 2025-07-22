import json
import os
import sys
import re
import requests
from PIL import Image
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Use free API endpoints that don't require authentication
BLIP_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
LLM_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"  # Free alternative

def generate_image_caption(image_path):
    """Generate image caption using BLIP model via API"""
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        
        response = requests.post(BLIP_API_URL, data=data)
        
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        elif response.status_code == 503:  # Model loading
            print("Model is loading, waiting 10 seconds...")
            time.sleep(10)
            return generate_image_caption(image_path)  # Retry
        else:
            print(f"Caption API error: {response.status_code} - {response.text}")
            return "Visual content"
    
    except Exception as e:
        print(f"Caption error: {e}")
        return "Image"

def generate_question(question_data):
    """Generate AI question using free APIs without authentication"""
    # Generate image captions
    image_descriptions = []
    for img_path in question_data['images']:
        caption = generate_image_caption(img_path)
        image_descriptions.append(caption)
        print(f"Generated caption: {caption}")
    
    # Prepare prompt
    prompt = f"""You are a math olympiad question generator for Class 1 students.
Generate a multiple-choice question based on this content:

Page {question_data['page']} Question {question_data['number']}:
{question_data['text']}

Image descriptions:
{'; '.join(image_descriptions)}

Create a multiple-choice question with 4 options (A, B, C, D). 
Format your response as JSON with these keys:
- "question": the question text
- "options": dictionary with keys A, B, C, D
- "answer": the correct option letter (A, B, C, or D)

Example:
{{
  "question": "How many apples are in the basket?",
  "options": {{
    "A": "2",
    "B": "3",
    "C": "4",
    "D": "5"
  }},
  "answer": "C"
}}

JSON response:"""
    
    # Generate question with LLM API
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        response = requests.post(LLM_API_URL, json=payload)
        
        if response.status_code == 200:
            response_text = response.json()[0]['generated_text']
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                print("Couldn't find JSON in response, using fallback")
                return create_fallback_question(question_data)
                
        elif response.status_code == 503:  # Model loading
            print("LLM model is loading, waiting 15 seconds...")
            time.sleep(15)
            return generate_question(question_data)  # Retry
        else:
            print(f"LLM API error: {response.status_code} - {response.text}")
            return create_fallback_question(question_data)
            
    except Exception as e:
        print(f"Question generation error: {e}")
        return create_fallback_question(question_data)

def create_fallback_question(question_data):
    """Create a simple fallback question when API fails"""
    return {
        "question": f"Math question about: {question_data['text'][:50]}...",
        "options": {
            "A": "Option 1",
            "B": "Option 2",
            "C": "Option 3",
            "D": "Option 4"
        },
        "answer": "C"
    }

def process_extracted_content(json_path):
    """Process extracted content and generate questions"""
    if not os.path.exists(json_path):
        print(f"Error: File not found - {json_path}")
        sys.exit(1)
    
    try:
        with open(json_path) as f:
            content = json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in extracted_content.json")
        sys.exit(1)
    
    all_questions = []
    
    # Process each page and generate questions
    for page in content:
        if not page.get('text') or not page.get('images'):
            continue
            
        # Split page text into individual questions
        questions_text = re.split(r'\n(\d+\.)\s', page['text'])
        q_num = 1
        
        for i in range(1, len(questions_text), 2):
            if i+1 >= len(questions_text):
                break
                
            question_text = questions_text[i] + questions_text[i+1]
            if len(question_text.strip()) < 10:  # Skip short fragments
                continue
                
            question_data = {
                "page": page["page"],
                "number": q_num,
                "text": question_text,
                "images": page["images"]
            }
            
            print(f"Generating question for page {page['page']} question {q_num}...")
            ai_question = generate_question(question_data)
            ai_question.update({
                "source_page": page["page"],
                "source_question": q_num,
                "images": page["images"]
            })
            all_questions.append(ai_question)
            q_num += 1
    
    # Save generated questions
    output_path = "output/questions.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(all_questions, f, indent=2)
    
    print(f"Successfully generated {len(all_questions)} questions")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    input_json = "output/extracted_content.json"
    process_extracted_content(input_json)