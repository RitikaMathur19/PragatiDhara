"""
Gemini LLM POC - Simple Test Script
Tests Google Gemini API access and basic functionality
"""

import os
import time
from typing import Dict, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Initialize rich console for pretty output
console = Console()

class GeminiPOC:
    """Simple Gemini API test class."""
    
    def __init__(self):
        """Initialize Gemini POC."""
        self.api_key: Optional[str] = None
        self.model = None
        self.model_name = "gemini-1.5-flash-latest"
        self.request_count = 0
        
    def load_config(self) -> bool:
        """Load configuration from environment."""
        # Load .env file if it exists
        if os.path.exists(".env"):
            load_dotenv(".env")
            console.print("✅ Loaded .env file", style="green")
        else:
            console.print("⚠️  No .env file found, using environment variables", style="yellow")
        
        # Get API key
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            console.print("❌ No GEMINI_API_KEY found in environment", style="red")
            return False
        
        # Get model configuration
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
        
        console.print(f"✅ Configuration loaded: {self.model_name}", style="green")
        return True
    
    def initialize_gemini(self) -> bool:
        """Initialize Gemini API."""
        if not GEMINI_AVAILABLE:
            console.print("❌ Google GenerativeAI library not installed", style="red")
            console.print("Run: pip install google-generativeai", style="yellow")
            return False
        
        try:
            # Configure API key
            genai.configure(api_key=self.api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel(self.model_name)
            
            console.print("✅ Gemini API initialized successfully", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to initialize Gemini: {e}", style="red")
            return False
    
    def test_basic_generation(self) -> bool:
        """Test basic text generation."""
        console.print("\n🧪 Testing basic text generation...", style="blue")
        
        try:
            prompt = "Explain sustainable transportation in one sentence."
            
            start_time = time.time()
            response = self.model.generate_content(prompt)
            end_time = time.time()
            
            self.request_count += 1
            
            # Display results
            console.print(Panel(
                f"[bold]Prompt:[/bold] {prompt}\n\n"
                f"[bold]Response:[/bold] {response.text}\n\n"
                f"[dim]Processing time: {(end_time - start_time):.2f}s[/dim]",
                title="✅ Basic Generation Test",
                border_style="green"
            ))
            
            return True
            
        except Exception as e:
            console.print(f"❌ Basic generation failed: {e}", style="red")
            return False
    
    def test_traffic_scenario(self) -> bool:
        """Test traffic-related scenario (relevant to PragatiDhara)."""
        console.print("\n🚦 Testing traffic scenario...", style="blue")
        
        try:
            prompt = """
            Scenario: A user is traveling from Koramangala to Electronic City in Bangalore 
            during evening rush hour (6 PM) on a weekday. They have a petrol car and 
            want to minimize both travel time and carbon emissions.
            
            Provide 3 specific actionable recommendations.
            """
            
            start_time = time.time()
            response = self.model.generate_content(prompt)
            end_time = time.time()
            
            self.request_count += 1
            
            # Display results
            console.print(Panel(
                f"[bold]Traffic Scenario Test:[/bold]\n\n"
                f"{response.text}\n\n"
                f"[dim]Processing time: {(end_time - start_time):.2f}s[/dim]",
                title="🚦 Traffic Scenario Test",
                border_style="blue"
            ))
            
            return True
            
        except Exception as e:
            console.print(f"❌ Traffic scenario failed: {e}", style="red")
            return False
    
    def test_conversation_mode(self) -> bool:
        """Test conversational capabilities."""
        console.print("\n💬 Testing conversation mode...", style="blue")
        
        try:
            # Start a chat session
            chat = self.model.start_chat(history=[])
            
            # Test conversation flow
            messages = [
                "I'm looking for eco-friendly transportation options in my city.",
                "What about electric vehicles vs public transport?",
                "How can I calculate my carbon footprint?"
            ]
            
            for i, message in enumerate(messages, 1):
                console.print(f"\n[bold]User {i}:[/bold] {message}", style="cyan")
                
                start_time = time.time()
                response = chat.send_message(message)
                end_time = time.time()
                
                self.request_count += 1
                
                console.print(f"[bold]Gemini:[/bold] {response.text}", style="green")
                console.print(f"[dim]Time: {(end_time - start_time):.2f}s[/dim]", style="dim")
            
            console.print("\n✅ Conversation test completed", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Conversation test failed: {e}", style="red")
            return False
    
    def test_rate_limits(self) -> bool:
        """Test rate limiting behavior."""
        console.print("\n⏱️  Testing rate limits...", style="blue")
        
        try:
            console.print("Sending 3 rapid requests...", style="yellow")
            
            for i in range(3):
                prompt = f"Quick test {i+1}: What's a benefit of carpooling?"
                
                start_time = time.time()
                response = self.model.generate_content(prompt)
                end_time = time.time()
                
                self.request_count += 1
                
                console.print(f"Request {i+1}: {(end_time - start_time):.2f}s - {response.text[:50]}...")
                
                # Small delay to be respectful
                time.sleep(0.5)
            
            console.print("✅ Rate limit test passed", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Rate limit test failed: {e}", style="red")
            return False
    
    def get_model_info(self) -> Dict:
        """Get model information."""
        if not self.model:
            return {}
        
        return {
            "model_name": self.model_name,
            "requests_made": self.request_count,
            "api_configured": bool(self.api_key),
            "status": "ready" if self.model else "not_initialized"
        }
    
    def interactive_mode(self):
        """Run interactive mode for custom testing."""
        console.print("\n🎯 Interactive Mode - Type 'quit' to exit", style="magenta")
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]Enter your prompt[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("👋 Goodbye!", style="green")
                    break
                
                start_time = time.time()
                response = self.model.generate_content(user_input)
                end_time = time.time()
                
                self.request_count += 1
                
                console.print(Panel(
                    f"{response.text}\n\n"
                    f"[dim]Time: {(end_time - start_time):.2f}s | Request #{self.request_count}[/dim]",
                    title="🤖 Gemini Response",
                    border_style="green"
                ))
                
            except KeyboardInterrupt:
                console.print("\n👋 Exiting...", style="yellow")
                break
            except Exception as e:
                console.print(f"❌ Error: {e}", style="red")


def main():
    """Main POC execution."""
    console.print(Panel(
        "[bold]Gemini LLM POC Test[/bold]\n"
        "Testing Google Gemini API integration for PragatiDhara",
        title="🚀 Gemini POC",
        border_style="blue"
    ))
    
    # Initialize POC
    poc = GeminiPOC()
    
    # Load configuration
    if not poc.load_config():
        console.print("\n📝 Setup Instructions:", style="bold yellow")
        console.print("1. Get API key from: https://aistudio.google.com/app/apikey")
        console.print("2. Copy config.template to .env")
        console.print("3. Add your API key to .env file")
        console.print("4. Install dependencies: pip install -r requirements.txt")
        return
    
    # Initialize Gemini
    if not poc.initialize_gemini():
        return
    
    # Run tests
    tests = [
        ("Basic Generation", poc.test_basic_generation),
        ("Traffic Scenario", poc.test_traffic_scenario),
        ("Conversation Mode", poc.test_conversation_mode),
        ("Rate Limits", poc.test_rate_limits)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        console.print(f"\n{'='*50}", style="dim")
        try:
            results[test_name] = test_func()
        except Exception as e:
            console.print(f"❌ {test_name} crashed: {e}", style="red")
            results[test_name] = False
    
    # Summary
    console.print(f"\n{'='*50}", style="dim")
    console.print("\n📊 Test Summary:", style="bold blue")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        console.print(f"  {test_name}: {status}")
    
    console.print(f"\nOverall: {passed}/{total} tests passed", 
                 style="green" if passed == total else "yellow")
    
    # Model info
    info = poc.get_model_info()
    console.print(f"\n🔍 Model Info: {info}")
    
    # Interactive mode option
    if passed > 0:
        continue_interactive = Prompt.ask(
            "\n💬 Run interactive mode?", 
            choices=["yes", "no"], 
            default="no"
        )
        
        if continue_interactive.lower() == "yes":
            poc.interactive_mode()


if __name__ == "__main__":
    main()