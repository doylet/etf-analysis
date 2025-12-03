"""
Simulation Domain Models

Models for Monte Carlo simulation parameters and results.
"""

from typing import List, Dict, Optional
from pydantic import Field, field_validator
import numpy as np
from datetime import datetime
from src.domain import DomainModel


class SimulationParameters(DomainModel):
    """
    Configuration for Monte Carlo portfolio simulation.
    
    Validates that weights sum to 1.0, positive values, and reasonable constraints.
    """
    
    symbols: List[str] = Field(
        ...,
        min_length=1,
        description="List of instrument symbols to simulate"
    )
    
    weights: List[float] = Field(
        ...,
        min_length=1,
        description="Portfolio weights for each symbol (must sum to 1.0)"
    )
    
    years: int = Field(
        ...,
        ge=1,
        le=50,
        description="Time horizon in years"
    )
    
    num_simulations: int = Field(
        ...,
        ge=100,
        le=50000,
        description="Number of Monte Carlo paths to simulate"
    )
    
    initial_value: float = Field(
        ...,
        gt=0,
        description="Initial portfolio value"
    )
    
    # Contribution settings
    contribution_amount: float = Field(
        0.0,
        ge=0,
        description="Regular contribution amount"
    )
    
    contribution_frequency: str = Field(
        "monthly",
        pattern="^(monthly|quarterly|annually|none)$",
        description="Frequency of contributions"
    )
    
    # Rebalancing settings
    rebalancing_enabled: bool = Field(
        False,
        description="Whether to rebalance portfolio"
    )
    
    rebalancing_threshold: float = Field(
        0.05,
        ge=0,
        le=0.5,
        description="Drift threshold to trigger rebalancing (e.g., 0.05 = 5%)"
    )
    
    rebalancing_frequency: str = Field(
        "quarterly",
        pattern="^(monthly|quarterly|annually)$",
        description="Maximum rebalancing frequency"
    )
    
    transaction_costs: float = Field(
        0.001,
        ge=0,
        le=0.1,
        description="Transaction cost as fraction (e.g., 0.001 = 0.1%)"
    )
    
    @field_validator('weights')
    @classmethod
    def weights_must_sum_to_one(cls, v: List[float]) -> List[float]:
        """Validate that weights sum to 1.0 (within tolerance)."""
        total = sum(v)
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return v
    
    @field_validator('symbols', 'weights')
    @classmethod
    def same_length(cls, v, info):
        """Validate symbols and weights have same length."""
        if info.field_name == 'weights' and 'symbols' in info.data:
            if len(v) != len(info.data['symbols']):
                raise ValueError("symbols and weights must have same length")
        return v


class SimulationResults(DomainModel):
    """
    Results from Monte Carlo portfolio simulation.
    
    Contains simulation paths, percentiles, risk metrics, and recommendations.
    """
    
    # Simulation paths and time points
    paths: List[List[float]] = Field(
        ...,
        description="All simulation paths (2D array: [num_sims x time_points])"
    )
    
    time_points: List[float] = Field(
        ...,
        description="Time points in years (e.g., [0, 0.25, 0.5, ...])"
    )
    
    # Percentile bands
    percentiles: Dict[str, List[float]] = Field(
        ...,
        description="Percentile bands (5th, 10th, 25th, 50th, 75th, 90th, 95th)"
    )
    
    # Final portfolio values
    final_values: List[float] = Field(
        ...,
        description="Final portfolio values across all simulations"
    )
    
    # Risk metrics
    var_95: float = Field(
        ...,
        description="Value at Risk at 95% confidence (5th percentile loss)"
    )
    
    cvar_95: float = Field(
        ...,
        description="Conditional VaR at 95% (expected loss beyond VaR)"
    )
    
    max_drawdown_median: float = Field(
        ...,
        description="Median maximum drawdown across simulations"
    )
    
    # Return metrics
    cagr_median: float = Field(
        ...,
        description="Median compound annual growth rate"
    )
    
    cagr_5th: float = Field(
        ...,
        description="5th percentile CAGR (pessimistic scenario)"
    )
    
    cagr_95th: float = Field(
        ...,
        description="95th percentile CAGR (optimistic scenario)"
    )
    
    # Historical metrics (from input data)
    historical_sharpe: float = Field(
        ...,
        description="Sharpe ratio from historical returns"
    )
    
    historical_volatility: float = Field(
        ...,
        description="Annualized volatility from historical returns"
    )
    
    # Optional rebalancing recommendations
    rebalancing_dates: Optional[List[datetime]] = Field(
        None,
        description="Dates when rebalancing occurred (if enabled)"
    )
    
    avg_rebalancing_drift: Optional[float] = Field(
        None,
        description="Average portfolio drift at rebalancing (if enabled)"
    )
    
    # Metadata
    parameters: SimulationParameters = Field(
        ...,
        description="Parameters used for this simulation"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When simulation was run"
    )
