import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API key found")
    exit(1)

genai.configure(api_key=api_key, transport='rest')

print(f"Using API Key: {api_key[:5]}...")

try:
    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-09-2025')
    print("Invoking model directly...")
    response = model.generate_content("Hello, are you working?")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
