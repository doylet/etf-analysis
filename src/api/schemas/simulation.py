"""
API schemas for Monte Carlo simulation endpoints.

Request/response models that wrap domain models for API layer.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class SimulationRequest(BaseModel):
    """Request schema for Monte Carlo simulation."""
    
    symbols: List[str] = Field(..., description="List of ticker symbols to simulate")
    weights: List[float] = Field(..., description="Portfolio weights (must sum to 1.0)")
    initial_investment: float = Field(..., gt=0, description="Initial investment amount")
    years: int = Field(..., gt=0, le=50, description="Simulation time horizon in years")
    num_simulations: int = Field(1000, gt=0, le=10000, description="Number of simulation paths")
    confidence_level: int = Field(90, ge=80, le=99, description="Confidence level for percentiles")
    estimation_method: str = Field("Historical Mean", description="Mean estimation method")
    enable_rebalancing_analysis: bool = Field(False, description="Analyze rebalancing timing")
    drift_threshold: float = Field(0.10, gt=0, le=1.0, description="Drift threshold for rebalancing")
    transaction_cost_pct: float = Field(0.001, ge=0, description="Transaction cost percentage")
    max_rebalances_per_year: Optional[int] = Field(None, ge=0, description="Max rebalances per year")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbols": ["VTI", "BND", "VEA"],
                "weights": [0.6, 0.3, 0.1],
                "initial_investment": 10000,
                "years": 10,
                "num_simulations": 1000,
                "confidence_level": 90,
                "estimation_method": "Historical Mean",
                "enable_rebalancing_analysis": False,
                "drift_threshold": 0.10,
                "transaction_cost_pct": 0.001
            }
        }


class SimulationResponse(BaseModel):
    """Response schema for completed Monte Carlo simulation."""
    
    median_outcome: float = Field(..., description="Median final portfolio value")
    best_case: float = Field(..., description="Best case outcome (95th percentile)")
    worst_case: float = Field(..., description="Worst case outcome (5th percentile)")
    percentiles: Dict[int, float] = Field(..., description="Outcome percentiles")
    probability_of_loss: float = Field(..., description="Probability portfolio loses value")
    expected_return: float = Field(..., description="Expected annualized return")
    expected_volatility: float = Field(..., description="Expected annualized volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio of simulated portfolio")
    max_drawdown: float = Field(..., description="Maximum drawdown in simulation")
    value_at_risk_95: float = Field(..., description="Value at Risk (5th percentile)")
    simulation_paths: Optional[List[List[float]]] = Field(None, description="Individual simulation paths (optional)")
    rebalancing_analysis: Optional[Dict] = Field(None, description="Rebalancing timing analysis (if enabled)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "median_outcome": 25840.50,
                "best_case": 45230.75,
                "worst_case": 12450.20,
                "percentiles": {
                    5: 12450.20,
                    25: 18750.30,
                    50: 25840.50,
                    75: 33210.80,
                    95: 45230.75
                },
                "probability_of_loss": 0.12,
                "expected_return": 0.087,
                "expected_volatility": 0.15,
                "sharpe_ratio": 0.58,
                "max_drawdown": 0.32,
                "value_at_risk_95": 12450.20
            }
        }


class TaskStatusResponse(BaseModel):
    """Response schema for asynchronous task tracking."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status: pending, running, completed, failed")
    progress: Optional[float] = Field(None, ge=0, le=1.0, description="Task progress (0.0-1.0)")
    created_at: datetime = Field(..., description="Task creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    result: Optional[SimulationResponse] = Field(None, description="Task result (if completed)")
    error: Optional[str] = Field(None, description="Error message (if failed)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "running",
                "progress": 0.65,
                "created_at": "2023-12-04T10:30:00Z",
                "started_at": "2023-12-04T10:30:02Z",
                "completed_at": None,
                "result": None,
                "error": None
            }
        }
