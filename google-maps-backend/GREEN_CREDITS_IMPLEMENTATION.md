# Green Credits System Implementation

## Overview
Successfully implemented a comprehensive green credits system that rewards users for choosing eco-friendly routes.

## Features Implemented

### 1. **Green Credits Calculation**
- **Eco-Friendly Routes**: 100% credits (0.5 per km + 5.0 per kg CO2 saved)
- **Balanced Routes**: 60% credits (60% of eco-friendly calculation)
- **Shortest Routes**: 40% credits (40% of eco-friendly calculation)
- **Fastest Routes**: 0 credits (no reward for fastest routes)

### 2. **Route Response Enhancement**
All route options now include a `green_credits_earned` field showing:
- How many credits the user will earn for selecting that route
- Calculated based on distance and CO2 savings
- 0 credits for fastest routes as requested

### 3. **Green Credits API Endpoints**

#### Get User Wallet
```
GET /api/v1/routes/green-credits/{user_id}
```
Returns:
- Total credits balance
- Lifetime credits earned
- Credits redeemed
- Number of eco routes taken
- Total CO2 saved

#### Earn Credits
```
POST /api/v1/routes/green-credits/earn
```
Body:
```json
{
  "user_id": "user_001",
  "route_distance_km": 15.2,
  "co2_saved_kg": 2.3,
  "route_type": "eco_friendly"
}
```

#### Transaction History
```
GET /api/v1/routes/green-credits/{user_id}/transactions?limit=10
```

#### Redeem Credits
```
POST /api/v1/routes/green-credits/{user_id}/redeem?amount=50
```

## Files Created/Modified

### New Files:
1. **`app/models/green_credits_models.py`** - Data models for credits system
2. **`app/services/green_credits_service.py`** - Business logic for credits
3. **`app/api/green_credits_routes.py`** - API endpoints

### Modified Files:
1. **`app/models/route_models.py`** - Added `green_credits_earned` field to Route model
2. **`app/services/green_credits_service.py`** - Added `calculate_credits_for_route()` method
3. **`app/api/routes.py`** - Integrated credits calculation into route optimization
4. **`app/main.py`** - Registered green credits router

## How It Works

### Frontend Display
When the user requests routes, each option (eco-friendly, balanced, fastest) will now show:
- Route details (distance, duration, etc.)
- **Green Credits Earned**: The number of credits they'll receive
- Environmental impact

Example response:
```json
{
  "primary_route": {
    "total_distance": {"text": "15.3 km", "value": 15300},
    "total_duration": {"text": "25 mins", "value": 1500},
    "green_credits_earned": 12.5,
    "emissions": {
      "co2_emissions_kg": 3.2,
      "eco_score": 8.5
    }
  },
  "alternatives": [
    {
      "route": {
        "total_distance": {"text": "14.2 km", "value": 14200},
        "total_duration": {"text": "18 mins", "value": 1080},
        "green_credits_earned": 0.0,
        "emissions": {
          "co2_emissions_kg": 4.5,
          "eco_score": 5.2
        }
      }
    }
  ]
}
```

### Credit Calculation Rules
- **Base Credits**: 0.5 credits per kilometer
- **CO2 Bonus**: 5.0 credits per kg of CO2 saved vs fastest route
- **Route Type Multipliers**:
  - Eco-Friendly: 100% (full credits)
  - Balanced: 60% (partial credits)
  - Shortest: 40% (minimal credits)
  - Fastest: 0% (no credits)

### User Wallet
- Tracks total credits balance
- Records all transactions
- Shows environmental impact (total CO2 saved)
- Supports redemption (for future rewards system)

## Testing

To test the implementation:

1. **Get route options with credits**:
```bash
POST http://localhost:8000/api/v1/routes/optimize
{
  "origin": {"address": "Katraj, Pune"},
  "destination": {"address": "Hinjewadi, Pune"},
  "optimization_mode": "eco_friendly",
  "alternatives": true
}
```

2. **Check user wallet**:
```bash
GET http://localhost:8000/api/v1/routes/green-credits/user_001
```

3. **Award credits after route completion**:
```bash
POST http://localhost:8000/api/v1/routes/green-credits/earn
{
  "user_id": "user_001",
  "route_distance_km": 15.3,
  "co2_saved_kg": 1.3,
  "route_type": "eco_friendly"
}
```

## Future Enhancements
- Database persistence (currently in-memory)
- Rewards catalog for redeeming credits
- Leaderboards and achievements
- Credits multipliers for consistent eco-friendly choices
- Integration with payment/loyalty systems
