# Backend for Extension
# pip install google-genai

from google import genai
import os
import dotenv


dotenv.load_dotenv()

def get_response(prompt):
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    response = client.models.generate_content(
        model='gemini-2.0-flash-lite',
        contents=prompt
    )
     
    return response.text
