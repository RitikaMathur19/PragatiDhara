# Gemini LLM POC Project

A simple proof-of-concept to test Google Gemini API integration for the PragatiDhara project.

## 🎯 Purpose

Test Gemini LLM access and functionality for:
- Traffic advice generation
- Conversational AI capabilities
- Sustainable transportation recommendations
- Integration feasibility with PragatiDhara backend

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Navigate to POC directory
cd gemini-poc

# Install required packages
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key (free tier available)
3. Copy the API key

### 3. Configure Environment

```bash
# Copy template to .env file
copy config.template .env

# Edit .env file and add your API key:
# GEMINI_API_KEY=your-actual-api-key-here
```

### 4. Run Tests

```bash
# Run comprehensive test (requires rich library)
python gemini_test.py

# Or run simple test (minimal dependencies)
python simple_gemini_test.py
```

## 📁 Files

- `requirements.txt` - Python dependencies
- `config.template` - Environment configuration template
- `gemini_test.py` - Full-featured test with rich output
- `simple_gemini_test.py` - Minimal test with basic output
- `README.md` - This file

## 🧪 Test Coverage

### Basic Tests
- ✅ API connection and authentication
- ✅ Simple text generation
- ✅ Model response validation

### Traffic-Specific Tests
- ✅ Route recommendation scenarios
- ✅ Traffic condition analysis
- ✅ Sustainable transport advice

### Conversation Tests
- ✅ Multi-turn conversations
- ✅ Context awareness
- ✅ Follow-up questions

### Performance Tests
- ✅ Response time measurement
- ✅ Rate limiting behavior
- ✅ Error handling

## 🔧 Configuration Options

```bash
# Model Settings
GEMINI_MODEL=gemini-1.5-flash-latest    # Fast, efficient model
GEMINI_TEMPERATURE=0.7                  # Creativity vs consistency
GEMINI_MAX_TOKENS=1000                  # Response length limit

# Safety Settings
GEMINI_SAFETY_THRESHOLD=BLOCK_MEDIUM_AND_ABOVE

# Rate Limits (Free Tier)
MAX_REQUESTS_PER_MINUTE=15              # Gemini Flash limit
MAX_REQUESTS_PER_DAY=1500               # Daily free quota
```

## 📊 Expected Output

```
🚀 GEMINI LLM POC TEST
Testing Google Gemini API for PragatiDhara
==================================================
🔧 Loading configuration...
✅ Configuration loaded: gemini-1.5-flash-latest
🔑 API Key: AIzaSyBm...xyz1
🤖 Initializing Gemini API...
✅ Gemini API initialized successfully

==================================================
🧪 Testing basic text generation...
📝 Prompt: Explain sustainable transportation in one sentence.
🤖 Response: Sustainable transportation prioritizes eco-friendly modes like walking, cycling, public transit, and electric vehicles to reduce environmental impact while meeting mobility needs.
⏱️  Processing time: 1.23s
✅ Basic generation test PASSED

==================================================
📊 FINAL TEST SUMMARY
==================================================
  Basic Generation: ✅ PASSED
  Traffic Scenario: ✅ PASSED  
  Conversation: ✅ PASSED
  Rate Limits: ✅ PASSED

📈 Overall Result: 4/4 tests passed
🎉 ALL TESTS PASSED! Gemini integration is working.
```

## 🔗 Integration with PragatiDhara

Once tests pass, you can integrate Gemini into PragatiDhara backend:

1. **Copy configuration** to main project
2. **Adapt prompts** for specific traffic scenarios
3. **Add caching** for sustainability 
4. **Implement rate limiting** for production use
5. **Create fallback** to local models when API unavailable

## 🌱 Sustainability Features

- **Efficient model selection** (Flash vs Pro)
- **Response caching** to reduce API calls
- **Rate limiting** to stay within free tier
- **Fallback mechanisms** when API unavailable
- **Token optimization** to minimize costs

## 🚨 Troubleshooting

### Common Issues

1. **Import Error**: `pip install google-generativeai`
2. **API Key Error**: Check API key format and permissions
3. **Rate Limit**: Wait between requests, implement caching
4. **Network Error**: Check internet connection and firewall

### Debug Mode

Set environment variable for verbose output:
```bash
export GEMINI_DEBUG=true
```

## 🔄 Next Steps

1. ✅ Test basic Gemini functionality
2. ✅ Validate traffic-specific use cases
3. 🔄 Integrate into PragatiDhara backend
4. 🔄 Add production-ready error handling
5. 🔄 Implement cost optimization strategies

## 📝 License

This POC is part of the PragatiDhara project - sustainable AI for transportation.