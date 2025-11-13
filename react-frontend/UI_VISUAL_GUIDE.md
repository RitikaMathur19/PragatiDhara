# Green Credits Frontend - Visual Guide

## 🎨 What Users Will See

### 1. Header with Wallet (Top of Page)
```
╔═══════════════════════════════════════════════════════════════════════╗
║  🌱 PragatiDhara                    ┌──────────────────────────────┐  ║
║  Smart Route Planning & Fuel Savings│🌟 YOUR GREEN CREDITS         │  ║
║                                     │   125.5      15 eco trips    │  ║
║                                     │           35.2 kg CO₂ saved  │  ║
║                                     └──────────────────────────────┘  ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### 2. Route Cards with Credits
```
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│  🌱 ECO-FRIENDLY ROUTE │  │  ⚖️ BALANCED ROUTE     │  │  🚀 FASTEST ROUTE      │
│  ┌──────────────────┐  │  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │
│  │ Distance: 25.3 km│  │  │  │ Distance: 23.5 km│  │  │  │ Distance: 20.1 km│  │
│  │ Duration: 45 mins│  │  │  │ Duration: 35 mins│  │  │  │ Duration: 28 mins│  │
│  │ Trip Cost: ₹125  │  │  │  │ Trip Cost: ₹138  │  │  │  │ Trip Cost: ₹155  │  │
│  └──────────────────┘  │  │  └──────────────────┘  │  │  └──────────────────┘  │
│  ┌──────────────────┐  │  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │
│  │🌟 Green Credits  │  │  │  │🌟 Green Credits  │  │  │  │⚪ Green Credits  │  │
│  │Great reward! +12.5│  │  │  │Good reward! +7.5│  │  │  │No credits    0.0│  │
│  └──────────────────┘  │  │  └──────────────────┘  │  │  └──────────────────┘  │
└────────────────────────┘  └────────────────────────┘  └────────────────────────┘
      Emerald green              Blue theme                 Gray (no reward)
```

### 3. Green Credits Tab View
```
╔════════════════════════════════════════════════════════════════════════╗
║                    🌟 Green Credits Comparison                         ║
║              Earn credits by choosing eco-friendly routes              ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   ║
║  │  ⭐ Best Choice  │  │                  │  │                  │   ║
║  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤   ║
║  │      🌱 Eco      │  │   ⚖️ Balanced    │  │   🚀 Fastest     │   ║
║  │                  │  │                  │  │                  │   ║
║  │      🌟          │  │      🌟          │  │      ⚪          │   ║
║  │      12.5        │  │      7.5         │  │      0.0         │   ║
║  │     credits      │  │     credits      │  │     credits      │   ║
║  │                  │  │                  │  │                  │   ║
║  │ +12.5 to wallet! │  │ +7.5 to wallet!  │  │ No credits for   │   ║
║  │                  │  │                  │  │   this route     │   ║
║  └──────────────────┘  └──────────────────┘  └──────────────────┘   ║
║                                                                        ║
║  ┌────────────────────────────────────────────────────────────────┐  ║
║  │ 💡 How to earn more credits:                                   │  ║
║  │  • Choose eco-friendly routes for maximum credits              │  ║
║  │  • Balanced routes earn 60% credits                           │  ║
║  │  • Fastest routes earn no credits                             │  ║
║  │  • Credits based on distance + CO₂ savings                    │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════════════════════╝
```

### 4. Tab Navigation
```
┌──────────────────────────────────────────────────────────────────┐
│  [📍 Route Details] [🌟 Green Credits] [💰 Savings] [🚗 Compare] │
└──────────────────────────────────────────────────────────────────┘
    Active tab (blue)    New tab!       Existing     Existing
```

## 🎨 Color Scheme

### Credits Badge Colors
| Credits Range | Color    | Background  | Message         | Icon |
|--------------|----------|-------------|-----------------|------|
| 0            | Gray     | bg-gray-100 | No credits      | ⚪   |
| 0-5          | Yellow   | bg-yellow-50| Small reward    | 🌟   |
| 5-10         | Green    | bg-green-50 | Good reward!    | 🌟   |
| 10+          | Emerald  | bg-emerald-50| Great reward!  | 🌟   |

### Route Type Colors
| Route Type    | Primary Color | Background   | Border          |
|---------------|---------------|--------------|-----------------|
| Eco-Friendly  | #006400       | #F0FFF0      | #006400         |
| Balanced      | #000080       | #F0F5FF      | #000080         |
| Fastest       | #FF6B00       | #FFF1E0      | #FF6B00         |

## 📱 Responsive Design

### Desktop (> 768px)
- Wallet visible in header
- Three route cards side by side
- Full tab navigation
- Credits comparison in 3 columns

### Mobile (< 768px)
- Wallet moves to separate section below header
- Route cards stack vertically
- Tabs scrollable horizontally
- Credits comparison stacks to 1 column

## ✨ Interactive Features

### Hover Effects
- Route cards scale up (transform: scale(1.05))
- Credits badges glow on hover
- Tab buttons change color

### Visual Feedback
- Selected route card has blue ring (ring-4 ring-blue-300)
- Best choice has yellow ring (ring-4 ring-yellow-300)
- Loading states with skeleton animations

### Animations
- Smooth transitions (duration-200)
- Fade in effects for new data
- Pulse animation for loading states

## 🔄 Data Flow Visualization

```
User Searches Route
        ↓
Backend Calculates Routes
        ↓
Each Route Gets green_credits_earned
        ↓
Frontend Displays:
  ├─ Credits Badge on Each Card
  ├─ Credits Comparison Tab
  └─ Wallet Updates (after completion)
```

## 💻 Example JSON Response

```json
{
  "routes": [
    {
      "type": "eco-friendly",
      "distance": "25.3",
      "duration": "45",
      "green_credits_earned": 12.5,
      "fuel_analysis": {...}
    },
    {
      "type": "balanced",
      "distance": "23.5",
      "duration": "35",
      "green_credits_earned": 7.5,
      "fuel_analysis": {...}
    },
    {
      "type": "fastest",
      "distance": "20.1",
      "duration": "28",
      "green_credits_earned": 0.0,
      "fuel_analysis": {...}
    }
  ]
}
```

## 🎯 Key UX Improvements

1. **Immediate Visibility**: Credits shown on every route card
2. **Clear Comparison**: Dedicated tab for credits comparison
3. **Motivation**: Color coding and messages encourage eco choices
4. **Progress Tracking**: Wallet in header shows total achievements
5. **Educational**: Info box explains how to earn more
6. **Visual Hierarchy**: Best choice clearly highlighted
