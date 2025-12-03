"""
Rebalancing Domain Models

Models for portfolio rebalancing analysis and recommendations.
"""

from typing import List, Dict, Optional
from pydantic import Field, field_validator
from datetime import datetime
from src.domain import DomainModel


class RebalancingRecommendation(DomainModel):
    """
    Recommendation for portfolio rebalancing.
    
    Includes rebalancing dates, drift analysis, and cost-benefit metrics.
    """
    
    # Rebalancing schedule
    rebalance_dates: List[datetime] = Field(
        ...,
        description="Dates when rebalancing should occur"
    )
    
    drift_at_rebalance: List[float] = Field(
        ...,
        description="Portfolio drift (%) at each rebalancing date"
    )
    
    # Trigger analysis
    trigger_threshold: float = Field(
        ...,
        ge=0,
        le=0.5,
        description="Drift threshold that triggered rebalancing (e.g., 0.05 = 5%)"
    )
    
    avg_drift: float = Field(
        ...,
        ge=0,
        description="Average drift across all rebalancing events"
    )
    
    max_drift: float = Field(
        ...,
        ge=0,
        description="Maximum drift observed"
    )
    
    # Per-instrument rebalancing actions
    instruments_to_rebalance: List[Dict[str, any]] = Field(
        ...,
        description="List of {symbol, current_weight, target_weight, action, shares} for each date"
    )
    
    # Cost-benefit analysis
    total_transaction_costs: float = Field(
        ...,
        ge=0,
        description="Total transaction costs for all rebalancing"
    )
    
    cost_benefit_ratio: float = Field(
        ...,
        description="Ratio of rebalancing benefit to costs"
    )
    
    sharpe_improvement: float = Field(
        ...,
        description="Expected Sharpe ratio improvement from rebalancing"
    )
    
    # Portfolio metrics
    portfolio_value_at_dates: List[float] = Field(
        ...,
        description="Portfolio value at each rebalancing date"
    )
    
    # Constraints
    max_rebalances_per_year: Optional[int] = Field(
        None,
        ge=0,
        le=12,
        description="Maximum allowed rebalancing frequency"
    )
    
    # Metadata
    analysis_period: Dict[str, datetime] = Field(
        ...,
        description="Start and end dates for analysis period"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When analysis was performed"
    )
    
    @field_validator('rebalance_dates', 'drift_at_rebalance')
    @classmethod
    def same_length(cls, v, info):
        """Validate dates and drift have same length."""
        if info.field_name == 'drift_at_rebalance' and 'rebalance_dates' in info.data:
            if len(v) != len(info.data['rebalance_dates']):
                raise ValueError("drift_at_rebalance must match length of rebalance_dates")
        return v
