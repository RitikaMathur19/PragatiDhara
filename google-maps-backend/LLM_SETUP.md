# LLM Integration Setup Guide

## Overview
The backend now supports AI-powered route recommendations using OpenAI-compatible APIs with automatic fallback to Ollama for local inference.

## Setup Instructions

### 1. Install Required Dependencies

```bash
cd google-maps-backend
pip install -r requirements.txt
```

This will install:
- `openai>=1.0.0` - For OpenAI-compatible API
- `python-dotenv>=1.0.0` - For loading environment variables

### 2. Configure Environment Variables

Create a `.env` file in the `google-maps-backend` directory:

```bash
# Copy the template
cp env.template .env
```

Edit the `.env` file with your configuration:

```env
# LLM Configuration
USE_OPENAI=false  # Set to true to try OpenAI-compatible endpoint first, false to use Ollama directly

# OpenAI-Compatible API Configuration (Primary)
OPENAI_API_BASE_URL=http://34.67.10.255/api/v1
OPENAI_API_KEY=pass
MODEL_NAME=Qwen/Qwen2.5-Math-1.5B-Instruct
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=1000

# Google Maps API
GOOGLE_MAPS_API_KEY=AIzaSyC4F-XYYRo_VpYVg7fkezgTHo6rNwW6wcY

# Ollama Fallback Configuration (Required if USE_OPENAI=false)
OLLAMA_API_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL_NAME=gemma3:1b
OLLAMA_API_KEY=ollama

# Application Configuration
APP_TITLE=Pragati Dhara
```

**Important:** 
- Set `USE_OPENAI=true` to try the OpenAI-compatible endpoint first (with Ollama as fallback)
- Set `USE_OPENAI=false` to skip OpenAI and use Ollama directly (faster startup, no external API calls)

### 3. (Optional) Install Ollama for Local Fallback

If you want local fallback capability when the primary API is unavailable:

1. **Install Ollama** from [https://ollama.ai](https://ollama.ai)

2. **Pull the gemma3:1b model**:
   ```bash
   ollama pull gemma3:1b
   ```

3. **Verify Ollama is running**:
   ```bash
   ollama list
   ```

### 4. Start the Backend Server

```bash
python enhanced_server.py
```

The server will:
- ✅ Load environment variables from `.env`
- ✅ Check `USE_OPENAI` flag to determine LLM strategy
- ✅ If `USE_OPENAI=true`: Try OpenAI-compatible endpoint → Ollama fallback → Rule-based
- ✅ If `USE_OPENAI=false`: Skip OpenAI, use Ollama directly → Rule-based fallback
- ✅ Use rule-based recommendations if all LLM endpoints fail

## How It Works

### LLM Integration Flow

The system uses a tiered approach with three fallback levels:

**When USE_OPENAI=true** (Default):
1. **Primary**: Calls OpenAI-compatible API at `OPENAI_API_BASE_URL` with model `MODEL_NAME`
2. **Fallback**: If primary fails, tries Ollama at `OLLAMA_API_BASE_URL` with model `OLLAMA_MODEL_NAME`
3. **Final Fallback**: If both fail, uses intelligent rule-based recommendations

**When USE_OPENAI=false** (Local-only mode):
1. **Primary**: Ollama at `OLLAMA_API_BASE_URL` with model `OLLAMA_MODEL_NAME`
2. **Fallback**: Rule-based recommendations if Ollama unavailable

**Why use USE_OPENAI=false?**
- **Privacy**: Keep all LLM inference local, no external API calls
- **Speed**: Skip external API timeout delays, faster startup
- **Cost**: Avoid API usage charges
- **Development**: Test with local models during development

**Why use USE_OPENAI=true?**
- **Quality**: Try higher-quality external models first
- **Reliability**: External APIs often more stable than local setups
- **Flexibility**: Automatic fallback to local models if external fails

### Response Structure

The AI recommendations include:
```json
{
  "source": "openai_compatible",
  "model": "Qwen/Qwen2.5-Math-1.5B-Instruct",
  "timestamp": "2025-11-12T10:30:00",
  "recommended_route": "eco_friendly",
  "reasoning": "Brief explanation why this route is best",
  "key_insights": [
    "Insight 1 about the routes",
    "Insight 2 about savings",
    "Insight 3 about efficiency"
  ],
  "best_for_scenarios": {
    "time_critical": "fastest",
    "cost_conscious": "eco_friendly",
    "eco_conscious": "eco_friendly"
  }
}
```

### Frontend Display

The `app.html` now shows:
- 🤖 AI-powered recommendation card
- Highlighted recommended route with reasoning
- 💡 Key insights about all routes
- Scenario-based recommendations (time-critical, cost-conscious, eco-conscious)
- Model attribution (shows which AI model generated the recommendation)

## Testing

### Test with Primary API
```bash
curl -X POST http://127.0.0.1:8001/api/v1/routes/three-strategies \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"address": "Mumbai"},
    "destination": {"address": "Pune"},
    "travel_mode": "driving",
    "vehicle_type": "petrol"
  }'
```

Look for the `ai_recommendations` field in the response.

### Test Fallback Behavior

1. **Test with invalid primary URL** (to trigger Ollama fallback):
   ```env
   OPENAI_API_BASE_URL=http://invalid-url/api/v1
   ```

2. **Test with both APIs down** (to trigger rule-based):
   - Set invalid URLs for both primary and Ollama
   - The system will fall back to intelligent rule-based recommendations

## Troubleshooting

### Issue: "LLM unavailable, using rule-based recommendations"
**Solution**: Check your `.env` configuration and ensure the API endpoint is accessible.

### Issue: "ImportError: No module named 'openai'"
**Solution**: 
```bash
pip install openai python-dotenv
```

### Issue: "Connection refused" to Ollama
**Solution**: 
1. Ensure Ollama is installed and running
2. Check that Ollama is listening on port 11434:
   ```bash
   curl http://localhost:11434/api/tags
   ```

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_BASE_URL` | Primary LLM API endpoint | `http://34.67.10.255/api/v1` | Yes |
| `OPENAI_API_KEY` | API key for authentication | `pass` | Yes |
| `MODEL_NAME` | Model to use for inference | `Qwen/Qwen2.5-Math-1.5B-Instruct` | Yes |
| `DEFAULT_TEMPERATURE` | Creativity level (0.0-2.0) | `0.7` | No |
| `DEFAULT_MAX_TOKENS` | Max response length | `1000` | No |
| `OLLAMA_API_BASE_URL` | Ollama fallback endpoint | `http://localhost:11434/v1` | No |
| `OLLAMA_MODEL_NAME` | Ollama model name | `gemma3:1b` | No |
| `OLLAMA_API_KEY` | Ollama API key | `ollama` | No |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | - | Yes |

## Features

✅ **Dual LLM Support**: Primary + Fallback architecture
✅ **Smart Fallback**: Graceful degradation to rule-based recommendations
✅ **Environment-based Config**: Easy configuration via `.env` files
✅ **Model Attribution**: Frontend shows which model generated recommendations
✅ **Async Implementation**: Non-blocking LLM calls
✅ **Error Handling**: Robust error handling at all levels
✅ **JSON Validation**: Parses and validates LLM JSON responses
✅ **Flexible**: Works with any OpenAI-compatible API

## Next Steps

1. Test the integration with real routes in `app.html`
2. Monitor LLM response quality and adjust prompts if needed
3. Fine-tune `temperature` and `max_tokens` for optimal results
4. Consider adding user preferences to personalize recommendations further
