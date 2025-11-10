#!/usr/bin/env python3
"""
Check .env configuration
"""

import os
from dotenv import load_dotenv

print("🔧 Checking .env configuration...")

# Load from current directory
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...{api_key[-8:]}")
    print("✅ Configuration is correct!")
    
    # Test if we can import Gemini
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
        
        # Configure and test basic access
        genai.configure(api_key=api_key)
        
        # Try to list models (light test)
        print("🤖 Testing API access...")
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content("Hello! Just say 'Hello back!' to test the API.")
        
        print("🎉 SUCCESS! Gemini API is working!")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
else:
    print("❌ GEMINI_API_KEY not found!")
    print("💡 Edit .env file and remove the # from the GEMINI_API_KEY line")
    print("💡 Current line should look like: GEMINI_API_KEY=AIzaSy...")
    print("💡 NOT like: # GEMINI_API_KEY=AIzaSy...")