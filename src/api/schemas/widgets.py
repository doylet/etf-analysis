"""Widget API response schemas using Pydantic v2."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field


class WidgetError(BaseModel):
    """Error information for widget API responses."""
    
    code: str = Field(..., description="Error code (VALIDATION_ERROR, CALCULATION_ERROR, etc.)")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class WidgetResponse(BaseModel):
    """Standard response format for all widget API endpoints."""
    
    widget_name: str = Field(..., description="Name of the widget")
    success: bool = Field(..., description="Whether the calculation succeeded")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Widget calculation results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    error: Optional[WidgetError] = Field(default=None, description="Error information if failed")


# Portfolio Summary Widget Schemas
class PortfolioSummaryData(BaseModel):
    """Portfolio summary calculation results."""
    
    total_value: float = Field(..., description="Total portfolio value")
    total_return: float = Field(..., description="Total return amount")
    total_return_percent: float = Field(..., description="Total return percentage")
    day_change: float = Field(..., description="Daily change amount")
    day_change_percent: float = Field(..., description="Daily change percentage") 
    positions: int = Field(..., description="Number of positions")
    allocated_cash: float = Field(..., description="Amount of allocated cash")
    last_updated: datetime = Field(..., description="Last data update timestamp")


class PortfolioSummaryResponse(WidgetResponse):
    """Typed response for portfolio summary widget."""
    
    data: Optional[PortfolioSummaryData] = None


# Holdings Breakdown Widget Schemas  
class HoldingPosition(BaseModel):
    """Individual holding position data."""
    
    symbol: str = Field(..., description="Stock/ETF symbol")
    name: str = Field(..., description="Company/Fund name")
    quantity: float = Field(..., description="Number of shares/units")
    current_price: float = Field(..., description="Current price per share")
    market_value: float = Field(..., description="Total market value")
    weight: float = Field(..., description="Portfolio weight percentage")
    day_change: float = Field(..., description="Daily price change")
    day_change_percent: float = Field(..., description="Daily change percentage")
    total_return: float = Field(..., description="Total return on position")
    total_return_percent: float = Field(..., description="Total return percentage")


class HoldingsBreakdownData(BaseModel):
    """Holdings breakdown calculation results."""
    
    positions: List[HoldingPosition] = Field(..., description="List of portfolio positions")
    total_value: float = Field(..., description="Total portfolio value")
    cash_position: float = Field(..., description="Cash position")
    last_updated: datetime = Field(..., description="Last data update timestamp")


class HoldingsBreakdownResponse(WidgetResponse):
    """Typed response for holdings breakdown widget."""
    
    data: Optional[HoldingsBreakdownData] = None


# Correlation Matrix Widget Schemas
class CorrelationMatrixData(BaseModel):
    """Correlation matrix calculation results."""
    
    correlation_matrix: Dict[str, Dict[str, float]] = Field(
        ..., description="Correlation coefficients between assets"
    )
    symbols: List[str] = Field(..., description="Asset symbols in the matrix")
    time_period: str = Field(..., description="Analysis time period") 
    calculation_date: datetime = Field(..., description="When analysis was performed")
    data_quality_score: float = Field(..., description="Data completeness score 0-1")


class CorrelationMatrixResponse(WidgetResponse):
    """Typed response for correlation matrix widget."""
    
    data: Optional[CorrelationMatrixData] = None


# Monte Carlo Widget Schemas
class MonteCarloScenario(BaseModel):
    """Individual Monte Carlo simulation scenario."""
    
    final_value: float = Field(..., description="Final portfolio value")
    return_percent: float = Field(..., description="Total return percentage")
    max_drawdown: float = Field(..., description="Maximum drawdown during period")


class MonteCarloData(BaseModel):
    """Monte Carlo simulation results."""
    
    scenarios: List[MonteCarloScenario] = Field(..., description="Simulation scenarios")
    statistics: Dict[str, float] = Field(..., description="Summary statistics")
    percentiles: Dict[str, float] = Field(..., description="Value percentiles")
    var_95: float = Field(..., description="95% Value at Risk")
    var_99: float = Field(..., description="99% Value at Risk")
    simulation_params: Dict[str, Any] = Field(..., description="Simulation parameters")
    execution_time_seconds: float = Field(..., description="Calculation duration")


class MonteCarloResponse(WidgetResponse):
    """Typed response for Monte Carlo widget."""
    
    data: Optional[MonteCarloData] = None


# Generic schemas for other widgets
class PerformanceData(BaseModel):
    """Generic performance analysis data."""
    
    metrics: Dict[str, float] = Field(..., description="Performance metrics")
    time_series: Optional[List[Dict[str, Any]]] = Field(default=None, description="Time series data")
    benchmarks: Optional[Dict[str, float]] = Field(default=None, description="Benchmark comparisons")
    

class GenericWidgetData(BaseModel):
    """Generic widget data structure."""
    
    results: Dict[str, Any] = Field(..., description="Widget-specific results")
    parameters: Dict[str, Any] = Field(..., description="Input parameters used")
    calculation_metadata: Dict[str, Any] = Field(..., description="Calculation metadata")


# Widget parameter schemas
class WidgetParameters(BaseModel):
    """Base parameters for widget requests."""
    
    portfolio_id: Optional[str] = Field(default=None, description="Portfolio identifier")
    date_range: Optional[str] = Field(default=None, description="Date range for analysis")
    

class MonteCarloParameters(WidgetParameters):
    """Parameters for Monte Carlo simulation."""
    
    num_simulations: int = Field(default=1000, description="Number of simulation runs")
    time_horizon_days: int = Field(default=252, description="Time horizon in days")
    confidence_level: float = Field(default=0.95, description="Confidence level for VaR")


class CorrelationParameters(WidgetParameters):
    """Parameters for correlation analysis."""
    
    lookback_days: int = Field(default=252, description="Historical data lookback period")
    method: str = Field(default="pearson", description="Correlation calculation method")