"""
Green Credits API endpoints
"""

from fastapi import APIRouter, HTTPException
import logging

from ..models.green_credits_models import (
    EarnCreditsRequest, EarnCreditsResponse, WalletResponse
)
from ..services.green_credits_service import GreenCreditsService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/routes/green-credits",
    tags=["green-credits"],
    responses={404: {"description": "Not found"}}
)


@router.get("/{user_id}", response_model=WalletResponse)
async def get_user_wallet(user_id: str):
    """
    Get user's green credits wallet
    
    Returns the current balance and statistics for a user's green credits wallet.
    This includes:
    - Total credits available
    - Lifetime credits earned
    - Credits redeemed
    - Number of eco routes taken
    - Total CO2 saved
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        WalletResponse containing wallet details
    """
    try:
        wallet = GreenCreditsService.get_wallet(user_id)
        return WalletResponse(success=True, wallet=wallet)
    except Exception as e:
        logger.error(f"Error fetching wallet for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch wallet: {str(e)}"
        )


@router.post("/earn", response_model=EarnCreditsResponse)
async def earn_green_credits(request: EarnCreditsRequest):
    """
    Award green credits for taking an eco-friendly route
    
    Users earn credits when they choose eco-friendly routes. Credits are calculated based on:
    - Route distance (0.5 credits per kilometer)
    - CO2 saved compared to regular route (5 credits per kg of CO2)
    
    The credits are automatically added to the user's wallet.
    
    Args:
        request: EarnCreditsRequest with user_id, route details, and CO2 savings
        
    Returns:
        EarnCreditsResponse with credits earned and new balance
    """
    try:
        response = GreenCreditsService.earn_credits(request)
        logger.info(
            f"User {request.user_id} earned {response.credits_earned} credits. "
            f"New balance: {response.new_balance}"
        )
        return response
    except Exception as e:
        logger.error(f"Error awarding credits to user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to award credits: {str(e)}"
        )


@router.get("/{user_id}/transactions")
async def get_transaction_history(user_id: str, limit: int = 10):
    """
    Get user's green credits transaction history
    
    Returns recent transactions showing how credits were earned.
    
    Args:
        user_id: Unique identifier for the user
        limit: Maximum number of transactions to return (default: 10)
        
    Returns:
        List of recent transactions
    """
    try:
        transactions = GreenCreditsService.get_transaction_history(user_id, limit)
        return {
            "success": True,
            "user_id": user_id,
            "transaction_count": len(transactions),
            "transactions": [t.dict() for t in transactions]
        }
    except Exception as e:
        logger.error(f"Error fetching transactions for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch transaction history: {str(e)}"
        )


@router.post("/{user_id}/redeem")
async def redeem_credits(user_id: str, amount: float):
    """
    Redeem green credits (future feature for rewards)
    
    Allows users to spend their earned credits on rewards or benefits.
    
    Args:
        user_id: Unique identifier for the user
        amount: Number of credits to redeem
        
    Returns:
        Redemption confirmation and new balance
    """
    try:
        if amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Redemption amount must be greater than 0"
            )
        
        result = GreenCreditsService.redeem_credits(user_id, amount)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        logger.info(f"User {user_id} redeemed {amount} credits")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redeeming credits for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to redeem credits: {str(e)}"
        )
