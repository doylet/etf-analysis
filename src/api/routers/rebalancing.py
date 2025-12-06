"""
Rebalancing analysis API router.

Endpoints for portfolio rebalancing recommendations.
"""

from fastapi import APIRouter, HTTPException, Depends
import numpy as np
from datetime import datetime

from api.schemas.rebalancing import (
    RebalancingRequest,
    RebalancingResponse,
    InstrumentRebalanceAction,
)
from services.rebalancing_service import RebalancingService
from services.storage_adapter import DataStorageAdapter
from repositories.price_data_repository import PriceDataRepository
from api.auth import get_current_user, User


router = APIRouter(prefix="/rebalancing", tags=["Rebalancing"])


def get_rebalancing_service() -> RebalancingService:
    """Get rebalancing service with repository."""
    storage = DataStorageAdapter()
    price_repo = PriceDataRepository(storage)
    return RebalancingService(price_data_repository=price_repo)


@router.post("/analyze", response_model=RebalancingResponse)
async def analyze_rebalancing(request: RebalancingRequest):
    """
    Analyze portfolio rebalancing needs.
    
    Determines if rebalancing is needed based on drift threshold,
    calculates required trades, and estimates costs vs benefits.
    """
    # Validate inputs
    if len(request.symbols) != len(request.current_weights):
        raise HTTPException(
            status_code=400,
            detail="Number of symbols must match number of current weights"
        )
    
    if len(request.symbols) != len(request.target_weights):
        raise HTTPException(
            status_code=400,
            detail="Number of symbols must match number of target weights"
        )
    
    if abs(sum(request.current_weights) - 1.0) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Current weights must sum to 1.0"
        )
    
    if abs(sum(request.target_weights) - 1.0) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Target weights must sum to 1.0"
        )
    
    try:
        service = get_rebalancing_service()
        
        # Analyze rebalancing timing
        results = service.analyze_timing(
            symbols=request.symbols,
            target_weights=np.array(request.target_weights),
            years=request.years,
            drift_threshold=request.drift_threshold,
            transaction_cost_pct=request.transaction_cost_pct,
            mu=0.08,  # Default expected return
            sigma=0.15,  # Default volatility
            max_rebalances_per_year=request.max_rebalances_per_year
        )
        
        # Calculate drift and determine actions
        current_weights_array = np.array(request.current_weights)
        target_weights_array = np.array(request.target_weights)
        drifts = np.abs(current_weights_array - target_weights_array)
        max_drift = float(np.max(drifts))
        avg_drift = float(np.mean(drifts))
        
        # Determine if rebalancing is needed
        should_rebalance = max_drift > request.drift_threshold
        
        # Create instrument rebalancing actions
        instrument_actions = []
        for i, symbol in enumerate(request.symbols):
            current_weight = request.current_weights[i]
            target_weight = request.target_weights[i]
            drift = abs(current_weight - target_weight)
            
            # Determine action
            if drift > request.drift_threshold:
                if current_weight > target_weight:
                    action = "SELL"
                    weight_change = current_weight - target_weight
                else:
                    action = "BUY"
                    weight_change = target_weight - current_weight
            else:
                action = "HOLD"
                weight_change = 0.0
            
            instrument_actions.append(InstrumentRebalanceAction(
                symbol=symbol,
                current_weight=current_weight,
                target_weight=target_weight,
                drift=drift,
                action=action,
                shares_to_trade=None,  # Would need current portfolio value to calculate
                value_to_trade=None
            ))
        
        return RebalancingResponse(
            should_rebalance=should_rebalance,
            trigger_threshold=request.drift_threshold,
            max_drift=max_drift,
            avg_drift=avg_drift,
            instruments_to_rebalance=instrument_actions,
            estimated_transaction_cost=results.total_transaction_costs,
            estimated_benefit=0.0,  # Would need more context to estimate
            cost_benefit_ratio=results.cost_benefit_ratio,
            sharpe_improvement=results.sharpe_improvement,
            recommended_rebalance_dates=[
                datetime.fromisoformat(date) if isinstance(date, str) else date
                for date in results.rebalance_dates[:5]  # Return up to 5 dates
            ]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebalancing analysis failed: {str(e)}")
