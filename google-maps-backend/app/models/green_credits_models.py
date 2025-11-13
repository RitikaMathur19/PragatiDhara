"""
Pydantic models for green credits system
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GreenCreditTransaction(BaseModel):
    """Represents a single green credit transaction"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    user_id: str = Field(..., description="User identifier")
    credits_earned: float = Field(..., ge=0, description="Credits earned in this transaction")
    route_distance_km: Optional[float] = Field(None, description="Route distance in kilometers")
    co2_saved_kg: Optional[float] = Field(None, description="CO2 saved in kilograms")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")
    route_type: str = Field(default="eco_friendly", description="Type of route selected")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_123456",
                "user_id": "user_001",
                "credits_earned": 10.5,
                "route_distance_km": 15.2,
                "co2_saved_kg": 2.3,
                "timestamp": "2025-11-12T10:30:00Z",
                "route_type": "eco_friendly"
            }
        }


class UserWallet(BaseModel):
    """Represents a user's green credits wallet"""
    user_id: str = Field(..., description="User identifier")
    total_credits: float = Field(default=0.0, ge=0, description="Total green credits balance")
    credits_earned_all_time: float = Field(default=0.0, ge=0, description="Lifetime credits earned")
    credits_redeemed: float = Field(default=0.0, ge=0, description="Total credits redeemed")
    eco_routes_count: int = Field(default=0, ge=0, description="Number of eco routes taken")
    total_co2_saved_kg: float = Field(default=0.0, ge=0, description="Total CO2 saved in kilograms")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last wallet update")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "total_credits": 125.5,
                "credits_earned_all_time": 150.0,
                "credits_redeemed": 24.5,
                "eco_routes_count": 15,
                "total_co2_saved_kg": 35.2,
                "last_updated": "2025-11-12T10:30:00Z"
            }
        }


class EarnCreditsRequest(BaseModel):
    """Request to earn green credits for taking eco route"""
    user_id: str = Field(..., description="User identifier")
    route_distance_km: float = Field(..., gt=0, description="Route distance in kilometers")
    co2_saved_kg: Optional[float] = Field(None, ge=0, description="CO2 saved compared to regular route")
    route_type: str = Field(default="eco_friendly", description="Type of eco route")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "route_distance_km": 15.2,
                "co2_saved_kg": 2.3,
                "route_type": "eco_friendly"
            }
        }


class EarnCreditsResponse(BaseModel):
    """Response after earning green credits"""
    success: bool = Field(..., description="Whether credits were awarded successfully")
    credits_earned: float = Field(..., description="Credits earned in this transaction")
    new_balance: float = Field(..., description="New total credits balance")
    transaction_id: str = Field(..., description="Transaction identifier")
    message: str = Field(..., description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "credits_earned": 10.5,
                "new_balance": 136.0,
                "transaction_id": "txn_123456",
                "message": "Successfully earned 10.5 green credits!"
            }
        }


class WalletResponse(BaseModel):
    """Response containing user wallet information"""
    success: bool = Field(..., description="Whether request was successful")
    wallet: UserWallet = Field(..., description="User wallet data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "wallet": {
                    "user_id": "user_001",
                    "total_credits": 125.5,
                    "credits_earned_all_time": 150.0,
                    "credits_redeemed": 24.5,
                    "eco_routes_count": 15,
                    "total_co2_saved_kg": 35.2,
                    "last_updated": "2025-11-12T10:30:00Z"
                }
            }
        }
