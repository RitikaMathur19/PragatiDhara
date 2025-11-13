"""
Service layer for managing green credits system
"""

from typing import Dict, Optional
from datetime import datetime
import uuid
from app.models.green_credits_models import (
    UserWallet,
    GreenCreditTransaction,
    EarnCreditsRequest,
    EarnCreditsResponse,
    WalletResponse
)


class GreenCreditsService:
    """Service for managing user green credits and rewards"""
    
    # In-memory storage for demonstration (use database in production)
    _wallets: Dict[str, UserWallet] = {}
    _transactions: Dict[str, list] = {}
    
    # Credits calculation constants
    CREDITS_PER_KM = 0.5  # Base credits per kilometer of eco route
    CREDITS_PER_KG_CO2 = 5.0  # Bonus credits per kg of CO2 saved
    
    @classmethod
    def get_wallet(cls, user_id: str) -> UserWallet:
        """
        Get user's wallet, creating one if it doesn't exist
        
        Args:
            user_id: User identifier
            
        Returns:
            UserWallet object
        """
        if user_id not in cls._wallets:
            cls._wallets[user_id] = UserWallet(user_id=user_id)
            cls._transactions[user_id] = []
        
        return cls._wallets[user_id]
    
    @classmethod
    def calculate_credits(cls, route_distance_km: float, co2_saved_kg: Optional[float] = None) -> float:
        """
        Calculate green credits based on route parameters
        
        Args:
            route_distance_km: Distance of eco route in kilometers
            co2_saved_kg: CO2 saved compared to regular route (optional)
            
        Returns:
            Calculated credits amount
        """
        # Base credits from distance
        credits = route_distance_km * cls.CREDITS_PER_KM
        
        # Bonus credits from CO2 savings
        if co2_saved_kg:
            credits += co2_saved_kg * cls.CREDITS_PER_KG_CO2
        
        return round(credits, 2)
    
    @classmethod
    def calculate_credits_for_route(
        cls, 
        route_distance_km: float, 
        optimization_mode: str,
        co2_emissions_kg: Optional[float] = None,
        fastest_route_emissions_kg: Optional[float] = None
    ) -> float:
        """
        Calculate green credits for a route based on optimization mode
        
        Args:
            route_distance_km: Distance of route in kilometers
            optimization_mode: Route optimization mode (eco_friendly, balanced, fastest, shortest)
            co2_emissions_kg: CO2 emissions for this route
            fastest_route_emissions_kg: CO2 emissions for fastest route (for comparison)
            
        Returns:
            Calculated credits amount (0 for fastest routes)
        """
        # No credits for fastest route
        if optimization_mode == "fastest":
            return 0.0
        
        # Base credits calculation
        credits = 0.0
        
        if optimization_mode == "eco_friendly":
            # Full credits for eco-friendly routes
            credits = route_distance_km * cls.CREDITS_PER_KM
            
            # Bonus for CO2 savings vs fastest route
            if co2_emissions_kg and fastest_route_emissions_kg:
                co2_saved = fastest_route_emissions_kg - co2_emissions_kg
                if co2_saved > 0:
                    credits += co2_saved * cls.CREDITS_PER_KG_CO2
        
        elif optimization_mode == "balanced":
            # 60% credits for balanced routes
            credits = route_distance_km * cls.CREDITS_PER_KM * 0.6
            
            # Partial bonus for CO2 savings
            if co2_emissions_kg and fastest_route_emissions_kg:
                co2_saved = fastest_route_emissions_kg - co2_emissions_kg
                if co2_saved > 0:
                    credits += co2_saved * cls.CREDITS_PER_KG_CO2 * 0.5
        
        elif optimization_mode == "shortest":
            # 40% credits for shortest routes
            credits = route_distance_km * cls.CREDITS_PER_KM * 0.4
        
        return round(credits, 2)
    
    @classmethod
    def earn_credits(cls, request: EarnCreditsRequest) -> EarnCreditsResponse:
        """
        Award green credits to user for taking eco route
        
        Args:
            request: EarnCreditsRequest containing user and route info
            
        Returns:
            EarnCreditsResponse with transaction details
        """
        # Get or create user wallet
        wallet = cls.get_wallet(request.user_id)
        
        # Calculate credits earned
        credits_earned = cls.calculate_credits(
            request.route_distance_km,
            request.co2_saved_kg
        )
        
        # Create transaction record
        transaction = GreenCreditTransaction(
            transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
            user_id=request.user_id,
            credits_earned=credits_earned,
            route_distance_km=request.route_distance_km,
            co2_saved_kg=request.co2_saved_kg,
            route_type=request.route_type,
            timestamp=datetime.utcnow()
        )
        
        # Update wallet
        wallet.total_credits += credits_earned
        wallet.credits_earned_all_time += credits_earned
        wallet.eco_routes_count += 1
        if request.co2_saved_kg:
            wallet.total_co2_saved_kg += request.co2_saved_kg
        wallet.last_updated = datetime.utcnow()
        
        # Store transaction
        if request.user_id not in cls._transactions:
            cls._transactions[request.user_id] = []
        cls._transactions[request.user_id].append(transaction)
        
        # Return response
        return EarnCreditsResponse(
            success=True,
            credits_earned=credits_earned,
            new_balance=wallet.total_credits,
            transaction_id=transaction.transaction_id,
            message=f"Successfully earned {credits_earned} green credits!"
        )
    
    @classmethod
    def get_transaction_history(cls, user_id: str, limit: int = 10) -> list:
        """
        Get user's recent transaction history
        
        Args:
            user_id: User identifier
            limit: Maximum number of transactions to return
            
        Returns:
            List of recent transactions
        """
        if user_id not in cls._transactions:
            return []
        
        transactions = cls._transactions[user_id]
        # Return most recent transactions
        return sorted(transactions, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    @classmethod
    def redeem_credits(cls, user_id: str, amount: float) -> Dict:
        """
        Redeem green credits (for future use - rewards system)
        
        Args:
            user_id: User identifier
            amount: Credits to redeem
            
        Returns:
            Dictionary with redemption status
        """
        wallet = cls.get_wallet(user_id)
        
        if wallet.total_credits < amount:
            return {
                "success": False,
                "message": f"Insufficient credits. Available: {wallet.total_credits}, Required: {amount}"
            }
        
        wallet.total_credits -= amount
        wallet.credits_redeemed += amount
        wallet.last_updated = datetime.utcnow()
        
        return {
            "success": True,
            "message": f"Successfully redeemed {amount} credits",
            "new_balance": wallet.total_credits
        }
    
    @classmethod
    def reset_wallet(cls, user_id: str) -> None:
        """Reset a user's wallet (for testing purposes)"""
        if user_id in cls._wallets:
            del cls._wallets[user_id]
        if user_id in cls._transactions:
            del cls._transactions[user_id]
