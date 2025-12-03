"""
API schemas for portfolio optimization endpoints.

Request/response models for optimization operations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class OptimizationObjectiveEnum(str, Enum):
    """Optimization objective types."""
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    MAX_RETURN = "max_return"
    TARGET_RETURN = "target_return"


class OptimizationRequest(BaseModel):
    """Request schema for portfolio optimization."""
    
    symbols: List[str] = Field(..., description="List of ticker symbols to optimize")
    objective: OptimizationObjectiveEnum = Field(..., description="Optimization objective")
    risk_free_rate: float = Field(0.04, ge=0, le=1.0, description="Annual risk-free rate")
    target_return: Optional[float] = Field(None, description="Target return (for target_return objective)")
    constraints: Optional[Dict] = Field(None, description="Additional constraints (min/max weights)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbols": ["VTI", "BND", "VEA", "VWO"],
                "objective": "max_sharpe",
                "risk_free_rate": 0.04,
                "constraints": {
                    "min_weights": {"VTI": 0.2},
                    "max_weights": {"BND": 0.4}
                }
            }
        }


class OptimizationResponse(BaseModel):
    """Response schema for portfolio optimization."""
    
    optimal_weights: List[float] = Field(..., description="Optimal portfolio weights")
    symbols: List[str] = Field(..., description="Symbols corresponding to weights")
    expected_return: float = Field(..., description="Expected annualized return")
    volatility: float = Field(..., description="Expected annualized volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio of optimal portfolio")
    objective_value: float = Field(..., description="Optimization objective function value")
    success: bool = Field(..., description="Whether optimization converged successfully")
    
    class Config:
        json_schema_extra = {
            "example": {
                "optimal_weights": [0.45, 0.35, 0.15, 0.05],
                "symbols": ["VTI", "BND", "VEA", "VWO"],
                "expected_return": 0.089,
                "volatility": 0.142,
                "sharpe_ratio": 0.627,
                "objective_value": 0.627,
                "success": True
            }
        }


class EfficientFrontierPoint(BaseModel):
    """Single point on the efficient frontier."""
    
    return_value: float = Field(..., description="Expected return at this point")
    volatility: float = Field(..., description="Volatility at this point")
    sharpe_ratio: float = Field(..., description="Sharpe ratio at this point")
    weights: List[float] = Field(..., description="Portfolio weights at this point")


class EfficientFrontierResponse(BaseModel):
    """Response schema for efficient frontier calculation."""
    
    frontier_points: List[EfficientFrontierPoint] = Field(..., description="Points on efficient frontier")
    symbols: List[str] = Field(..., description="Symbols corresponding to weights")
    min_volatility_point: EfficientFrontierPoint = Field(..., description="Minimum volatility portfolio")
    max_sharpe_point: EfficientFrontierPoint = Field(..., description="Maximum Sharpe ratio portfolio")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbols": ["VTI", "BND", "VEA"],
                "frontier_points": [
                    {
                        "return_value": 0.065,
                        "volatility": 0.08,
                        "sharpe_ratio": 0.50,
                        "weights": [0.2, 0.6, 0.2]
                    },
                    {
                        "return_value": 0.085,
                        "volatility": 0.12,
                        "sharpe_ratio": 0.625,
                        "weights": [0.6, 0.3, 0.1]
                    }
                ],
                "min_volatility_point": {
                    "return_value": 0.065,
                    "volatility": 0.08,
                    "sharpe_ratio": 0.50,
                    "weights": [0.2, 0.6, 0.2]
                },
                "max_sharpe_point": {
                    "return_value": 0.085,
                    "volatility": 0.12,
                    "sharpe_ratio": 0.625,
                    "weights": [0.6, 0.3, 0.1]
                }
            }
        }
