"""
Simple Gemini LLM POC - Minimal Version
Tests Google Gemini API access without external dependencies
"""

import os
import time
import json
from typing import Dict, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class SimpleGeminiPOC:
    """Minimal Gemini API test class."""
    
    def __init__(self):
        """Initialize Gemini POC."""
        self.api_key: Optional[str] = None
        self.model = None
        self.model_name = "gemini-1.5-flash-latest"
        self.request_count = 0
        
    def load_config(self) -> bool:
        """Load configuration from environment."""
        print("🔧 Loading configuration...")
        
        # Try to load from .env file if it exists
        if os.path.exists(".env"):
            try:
                with open(".env", "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key] = value
                print("✅ Loaded .env file")
            except Exception as e:
                print(f"⚠️  Error reading .env file: {e}")
        
        # Get API key
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("❌ No GEMINI_API_KEY found in environment")
            print("\n📝 Setup Instructions:")
            print("1. Get API key from: https://aistudio.google.com/app/apikey")
            print("2. Create .env file with: GEMINI_API_KEY=your-api-key-here")
            print("3. Or set environment variable: set GEMINI_API_KEY=your-key")
            return False
        
        # Get model configuration
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
        
        print(f"✅ Configuration loaded: {self.model_name}")
        print(f"🔑 API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
        return True
    
    def initialize_gemini(self) -> bool:
        """Initialize Gemini API."""
        print("🤖 Initializing Gemini API...")
        
        if not GEMINI_AVAILABLE:
            print("❌ Google GenerativeAI library not installed")
            print("Run: pip install google-generativeai")
            return False
        
        try:
            # Configure API key
            genai.configure(api_key=self.api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel(self.model_name)
            
            print("✅ Gemini API initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            return False
    
    def test_basic_generation(self) -> bool:
        """Test basic text generation."""
        print("\n" + "="*50)
        print("🧪 Testing basic text generation...")
        
        try:
            prompt = "Explain sustainable transportation in one sentence."
            print(f"📝 Prompt: {prompt}")
            
            start_time = time.time()
            response = self.model.generate_content(prompt)
            end_time = time.time()
            
            self.request_count += 1
            
            print(f"🤖 Response: {response.text}")
            print(f"⏱️  Processing time: {(end_time - start_time):.2f}s")
            print("✅ Basic generation test PASSED")
            
            return True
            
        except Exception as e:
            print(f"❌ Basic generation FAILED: {e}")
            return False
    
    def test_traffic_scenario(self) -> bool:
        """Test traffic-related scenario."""
        print("\n" + "="*50)
        print("🚦 Testing traffic scenario...")
        
        try:
            prompt = """
            You are a traffic advisor for Bangalore. A user needs to travel from 
            Koramangala to Electronic City during rush hour (6 PM) with a petrol car.
            They want to minimize travel time and emissions. Give 2 specific recommendations.
            """
            
            print("📝 Prompt: Traffic scenario for PragatiDhara app")
            
            start_time = time.time()
            response = self.model.generate_content(prompt)
            end_time = time.time()
            
            self.request_count += 1
            
            print(f"🤖 Traffic Advice:\n{response.text}")
            print(f"⏱️  Processing time: {(end_time - start_time):.2f}s")
            print("✅ Traffic scenario test PASSED")
            
            return True
            
        except Exception as e:
            print(f"❌ Traffic scenario FAILED: {e}")
            return False
    
    def test_conversation(self) -> bool:
        """Test conversational capabilities."""
        print("\n" + "="*50)
        print("💬 Testing conversation mode...")
        
        try:
            # Start a chat session
            chat = self.model.start_chat(history=[])
            
            # Test conversation
            messages = [
                "I want eco-friendly transport options.",
                "Compare electric vehicles vs public transport.",
            ]
            
            for i, message in enumerate(messages, 1):
                print(f"\n👤 User {i}: {message}")
                
                start_time = time.time()
                response = chat.send_message(message)
                end_time = time.time()
                
                self.request_count += 1
                
                print(f"🤖 Gemini: {response.text}")
                print(f"⏱️  Time: {(end_time - start_time):.2f}s")
            
            print("✅ Conversation test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Conversation test FAILED: {e}")
            return False
    
    def test_rate_limits(self) -> bool:
        """Test rate limiting."""
        print("\n" + "="*50)
        print("⏱️  Testing rate limits...")
        
        try:
            print("Sending 2 rapid requests...")
            
            for i in range(2):
                prompt = f"Quick test {i+1}: Name one benefit of carpooling."
                
                start_time = time.time()
                response = self.model.generate_content(prompt)
                end_time = time.time()
                
                self.request_count += 1
                
                print(f"📍 Request {i+1}: {(end_time - start_time):.2f}s")
                print(f"   Response: {response.text[:60]}...")
                
                # Be respectful with API
                time.sleep(1)
            
            print("✅ Rate limit test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Rate limit test FAILED: {e}")
            return False
    
    def get_summary(self) -> Dict:
        """Get test summary."""
        return {
            "model_name": self.model_name,
            "total_requests": self.request_count,
            "api_key_configured": bool(self.api_key),
            "gemini_library_available": GEMINI_AVAILABLE,
            "status": "ready" if self.model else "not_initialized"
        }

def main():
    """Main POC execution."""
    print("🚀 GEMINI LLM POC TEST")
    print("Testing Google Gemini API for PragatiDhara")
    print("="*50)
    
    # Initialize POC
    poc = SimpleGeminiPOC()
    
    # Load configuration
    if not poc.load_config():
        return
    
    # Initialize Gemini
    if not poc.initialize_gemini():
        return
    
    # Run all tests
    tests = [
        ("Basic Generation", poc.test_basic_generation),
        ("Traffic Scenario", poc.test_traffic_scenario),
        ("Conversation", poc.test_conversation),
        ("Rate Limits", poc.test_rate_limits)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
            results[test_name] = False
    
    # Final Summary
    print("\n" + "="*50)
    print("📊 FINAL TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Gemini integration is working.")
    elif passed > 0:
        print("⚠️  Some tests passed. Check failed tests above.")
    else:
        print("❌ All tests failed. Check API key and network connection.")
    
    # Summary info
    summary = poc.get_summary()
    print(f"\n🔍 Summary: {json.dumps(summary, indent=2)}")
    
    if passed > 0:
        print("\n✨ Next steps:")
        print("1. Integrate this into PragatiDhara backend")
        print("2. Add error handling and rate limiting")
        print("3. Implement caching for sustainability")
        print("4. Create specific prompts for traffic scenarios")

if __name__ == "__main__":
    main()