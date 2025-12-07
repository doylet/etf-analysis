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
    sector: str = Field(..., description="Sector classification")
    geography: str = Field(..., description="Geographic region")
    asset_class: str = Field(..., description="Asset class type")


class CategoryBreakdown(BaseModel):
    """Breakdown by category (sector, geography, asset class)."""
    
    name: str = Field(..., description="Category name")
    value: float = Field(..., description="Total value in category")
    weight: float = Field(..., description="Weight as decimal (0-1)")
    positions: int = Field(..., description="Number of positions in category")


class HoldingsBreakdownData(BaseModel):
    """Holdings breakdown calculation results."""
    
    holdings: List[HoldingPosition] = Field(..., description="List of individual positions")
    total_positions: int = Field(..., description="Total number of positions")
    total_value: float = Field(..., description="Total portfolio value")
    breakdown_by_sector: List[CategoryBreakdown] = Field(..., description="Breakdown by sector")
    breakdown_by_geography: List[CategoryBreakdown] = Field(..., description="Breakdown by geography")
    breakdown_by_asset_class: List[CategoryBreakdown] = Field(..., description="Breakdown by asset class")
    concentration_risk_score: float = Field(..., description="Concentration risk score (0-1)")
    last_updated: datetime = Field(..., description="Last data update timestamp")


class HoldingsBreakdownResponse(WidgetResponse):
    """Typed response for holdings breakdown widget."""
    
    data: Optional[HoldingsBreakdownData] = None


# Correlation Matrix Widget Schemas
class CorrelationPair(BaseModel):
    """Correlation between two assets."""
    
    symbol1: str = Field(..., description="First asset symbol")
    symbol2: str = Field(..., description="Second asset symbol")
    correlation: float = Field(..., description="Correlation coefficient (-1 to 1)")


class CorrelationPairs(BaseModel):
    """Correlation pairs data."""
    
    asset1: str = Field(..., description="First asset symbol") 
    asset2: str = Field(..., description="Second asset symbol")
    correlation: float = Field(..., description="Correlation coefficient (-1 to 1)")


class BenchmarkComparison(BaseModel):
    """Benchmark correlation comparison."""
    
    benchmark: str = Field(..., description="Benchmark symbol")
    correlations: Dict[str, Optional[float]] = Field(..., description="Correlations with portfolio assets")


class CorrelationStatistics(BaseModel):
    """Correlation matrix summary statistics."""
    
    avg_correlation: float = Field(..., description="Average correlation coefficient")
    max_correlation: float = Field(..., description="Maximum correlation coefficient") 
    min_correlation: float = Field(..., description="Minimum correlation coefficient")
    num_days: int = Field(..., description="Number of trading days analyzed")


class AnalysisPeriod(BaseModel):
    """Analysis time period information."""
    
    start_date: str = Field(..., description="Analysis start date (ISO format)")
    end_date: str = Field(..., description="Analysis end date (ISO format)")
    days_analyzed: int = Field(..., description="Number of days with data")


class CorrelationMatrixData(BaseModel):
    """Correlation matrix calculation results."""
    
    symbols: List[str] = Field(..., description="Asset symbols in the matrix")
    correlation_matrix: List[CorrelationPair] = Field(..., description="Correlation matrix data")
    correlation_pairs: List[CorrelationPairs] = Field(..., description="Strongest correlation pairs")
    benchmark_comparison: List[Dict[str, Any]] = Field(..., description="Benchmark correlation comparison")
    statistics: CorrelationStatistics = Field(..., description="Summary statistics")
    analysis_period: AnalysisPeriod = Field(..., description="Analysis time period")
    last_updated: str = Field(..., description="Last calculation timestamp")


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