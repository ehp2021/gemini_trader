import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=api_key)

print("Available Gemini models:")
try:
    for model in client.models.list():
        print(f"  - {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying simple model names:")
    for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-flash']:
        print(f"  Testing: {model_name}")
