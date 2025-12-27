import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found in environment variables.")
    exit(1)

genai.configure(api_key=api_key)

print(f"🔍 Checking available models for key ending in ...{api_key[-4:]}")

try:
    print("\n📋 Available Models:")
    found = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} (DisplayName: {m.displayName})")
            found = True
    
    if not found:
        print("❌ No models found that support 'generateContent'.")
    else:
        print("\n✅ List complete.")
        
except Exception as e:
    print(f"❌ Error listing models: {e}")
