#!/usr/bin/env python3
"""
Ultra-Simple Gemini Test (No External Dependencies)
Tests Gemini API with just the basic google-generativeai library
"""

import os
import sys
from dotenv import load_dotenv

def test_gemini_basic():
    """Test basic Gemini functionality"""
    print("🚀 ULTRA-SIMPLE GEMINI TEST")
    print("=" * 50)
    
    # Load environment variables
    print("🔧 Loading configuration...")
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        print("\n📝 Setup Instructions:")
        print("1. Get API key from: https://aistudio.google.com/app/apikey")
        print("2. Add to .env file: GEMINI_API_KEY=your-api-key-here")
        return False
    
    try:
        # Import here to avoid early failures
        import google.generativeai as genai
        
        print("✅ Google Generative AI library loaded successfully")
        print(f"✅ API Key configured (ends with: ...{api_key[-8:]})")
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Test basic model access
        print("\n🤖 Testing model access...")
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Simple test prompt
        print("📝 Sending test prompt...")
        response = model.generate_content("Hello! Please respond with 'Gemini is working!'")
        
        print("✅ SUCCESS! Gemini API Response:")
        print(f"🎯 {response.text}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Try: pip install google-generativeai python-dotenv")
        return False
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        print("💡 Check your API key and internet connection")
        return False

if __name__ == "__main__":
    success = test_gemini_basic()
    if success:
        print("\n🎉 Gemini integration test PASSED!")
    else:
        print("\n💥 Gemini integration test FAILED!")
        sys.exit(1)