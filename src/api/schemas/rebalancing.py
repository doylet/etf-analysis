"""
API schemas for rebalancing analysis endpoints.

Request/response models for rebalancing recommendations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RebalancingRequest(BaseModel):
    """Request schema for rebalancing analysis."""
    
    symbols: List[str] = Field(..., description="List of ticker symbols in portfolio")
    current_weights: List[float] = Field(..., description="Current portfolio weights")
    target_weights: List[float] = Field(..., description="Target portfolio weights")
    drift_threshold: float = Field(0.05, gt=0, le=1.0, description="Drift threshold to trigger rebalancing")
    transaction_cost_pct: float = Field(0.001, ge=0, description="Transaction cost percentage")
    max_rebalances_per_year: Optional[int] = Field(None, ge=0, description="Maximum rebalances per year")
    years: int = Field(10, gt=0, le=50, description="Analysis time horizon in years")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbols": ["VTI", "BND", "VEA"],
                "current_weights": [0.65, 0.25, 0.10],
                "target_weights": [0.60, 0.30, 0.10],
                "drift_threshold": 0.05,
                "transaction_cost_pct": 0.001,
                "max_rebalances_per_year": 4,
                "years": 10
            }
        }


class InstrumentRebalanceAction(BaseModel):
    """Rebalancing action for a single instrument."""
    
    symbol: str = Field(..., description="Ticker symbol")
    current_weight: float = Field(..., description="Current weight")
    target_weight: float = Field(..., description="Target weight")
    drift: float = Field(..., description="Drift from target (absolute)")
    action: str = Field(..., description="Action: BUY, SELL, or HOLD")
    shares_to_trade: Optional[float] = Field(None, description="Number of shares to buy/sell")
    value_to_trade: Optional[float] = Field(None, description="Dollar amount to buy/sell")


class RebalancingResponse(BaseModel):
    """Response schema for rebalancing analysis."""
    
    should_rebalance: bool = Field(..., description="Whether rebalancing is recommended")
    trigger_threshold: float = Field(..., description="Drift threshold used")
    max_drift: float = Field(..., description="Maximum drift from target")
    avg_drift: float = Field(..., description="Average drift across portfolio")
    instruments_to_rebalance: List[InstrumentRebalanceAction] = Field(..., description="Rebalancing actions per instrument")
    estimated_transaction_cost: float = Field(..., description="Estimated total transaction cost")
    estimated_benefit: float = Field(..., description="Estimated benefit from rebalancing")
    cost_benefit_ratio: float = Field(..., description="Ratio of benefit to cost")
    sharpe_improvement: float = Field(..., description="Expected Sharpe ratio improvement")
    recommended_rebalance_dates: List[datetime] = Field(..., description="Recommended rebalancing dates")
    
    class Config:
        json_schema_extra = {
            "example": {
                "should_rebalance": True,
                "trigger_threshold": 0.05,
                "max_drift": 0.08,
                "avg_drift": 0.045,
                "instruments_to_rebalance": [
                    {
                        "symbol": "VTI",
                        "current_weight": 0.65,
                        "target_weight": 0.60,
                        "drift": 0.05,
                        "action": "SELL",
                        "shares_to_trade": 12,
                        "value_to_trade": 2650.00
                    },
                    {
                        "symbol": "BND",
                        "current_weight": 0.25,
                        "target_weight": 0.30,
                        "drift": 0.05,
                        "action": "BUY",
                        "shares_to_trade": 35,
                        "value_to_trade": 2650.00
                    }
                ],
                "estimated_transaction_cost": 53.00,
                "estimated_benefit": 425.00,
                "cost_benefit_ratio": 8.02,
                "sharpe_improvement": 0.03,
                "recommended_rebalance_dates": []
            }
        }
