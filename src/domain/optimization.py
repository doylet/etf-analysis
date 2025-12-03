"""
Optimization Domain Models

Models for portfolio optimization requests and results.
"""

from typing import List, Dict, Optional
from enum import Enum
from pydantic import Field, field_validator
from datetime import datetime
from src.domain import DomainModel


class OptimizationObjective(str, Enum):
    """Portfolio optimization objectives."""
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    MAX_RETURN = "max_return"
    EFFICIENT_FRONTIER = "efficient_frontier"


class OptimizationRequest(DomainModel):
    """
    Request for portfolio optimization.
    
    Specifies objective, constraints, and time period for historical data.
    """
    
    symbols: List[str] = Field(
        ...,
        min_length=2,
        description="List of instrument symbols to optimize"
    )
    
    objective: OptimizationObjective = Field(
        ...,
        description="Optimization objective (max_sharpe, min_volatility, etc.)"
    )
    
    constraints: Dict[str, float] = Field(
        default_factory=dict,
        description="Optimization constraints (e.g., {'min_weight': 0.05, 'max_weight': 0.4})"
    )
    
    # Time period for historical data
    start_date: Optional[datetime] = Field(
        None,
        description="Start date for historical returns (None = default lookback)"
    )
    
    end_date: Optional[datetime] = Field(
        None,
        description="End date for historical returns (None = today)"
    )
    
    # Risk-free rate for Sharpe calculation
    risk_free_rate: float = Field(
        0.02,
        ge=0,
        le=0.2,
        description="Annual risk-free rate (e.g., 0.02 = 2%)"
    )
    
    # For efficient frontier
    num_points: int = Field(
        50,
        ge=10,
        le=200,
        description="Number of points on efficient frontier"
    )
    
    @field_validator('constraints')
    @classmethod
    def validate_constraints(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate constraint values."""
        if 'min_weight' in v and 'max_weight' in v:
            if v['min_weight'] > v['max_weight']:
                raise ValueError("min_weight cannot exceed max_weight")
        
        if 'target_return' in v and (v['target_return'] < -0.5 or v['target_return'] > 2.0):
            raise ValueError("target_return must be between -0.5 and 2.0")
        
        return v


class OptimizationResults(DomainModel):
    """
    Results from portfolio optimization.
    
    Contains optimal weights, expected metrics, and efficient frontier (if requested).
    """
    
    optimal_weights: Dict[str, float] = Field(
        ...,
        description="Optimal portfolio weights by symbol"
    )
    
    expected_return: float = Field(
        ...,
        description="Expected annual return for optimal portfolio"
    )
    
    volatility: float = Field(
        ...,
        description="Expected annual volatility (standard deviation)"
    )
    
    sharpe_ratio: float = Field(
        ...,
        description="Sharpe ratio (return / volatility, risk-adjusted)"
    )
    
    # Efficient frontier (if objective was EFFICIENT_FRONTIER)
    efficient_frontier: Optional[List[Dict[str, float]]] = Field(
        None,
        description="List of {return, volatility, sharpe} points on frontier"
    )
    
    # Metadata
    request: OptimizationRequest = Field(
        ...,
        description="Original optimization request"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When optimization was performed"
    )
    
    @field_validator('optimal_weights')
    @classmethod
    def weights_sum_to_one(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate optimal weights sum to 1.0."""
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Optimal weights must sum to 1.0, got {total}")
        return v
