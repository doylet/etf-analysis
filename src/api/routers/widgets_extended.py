"""FastAPI router for portfolio widget endpoints - Extended Version."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from ..dependencies import get_database
from ..schemas.widgets import (
    WidgetResponse, 
    PortfolioSummaryResponse,
    HoldingsBreakdownResponse, 
    CorrelationMatrixResponse,
    MonteCarloResponse,
    MonteCarloParameters,
    CorrelationParameters
)

# Import widget adapters
from ..widgets.portfolio_summary import PortfolioSummaryAdapter
from ..widgets.holdings_breakdown import HoldingsBreakdownAdapter
from ..widgets.correlation_matrix import CorrelationMatrixAdapter
from ..widgets.monte_carlo import MonteCarloAdapter
from ..widgets.benchmark_comparison import BenchmarkComparisonAdapter
from ..widgets.dividend_analysis import DividendAnalysisAdapter
from ..widgets.performance import PerformanceAdapter

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/widgets",
    tags=["widgets"],
    responses={
        404: {"description": "Widget not found"},
        422: {"description": "Invalid widget parameters"},
        500: {"description": "Internal server error"}
    }
)

# Available widgets registry
AVAILABLE_WIDGETS = {
    "portfolio_summary": {
        "name": "Portfolio Summary",
        "description": "Overview of portfolio performance and key metrics",
        "adapter": PortfolioSummaryAdapter,
        "enabled": True
    },
    "holdings_breakdown": {
        "name": "Holdings Breakdown", 
        "description": "Detailed breakdown of portfolio holdings and allocations",
        "adapter": HoldingsBreakdownAdapter,
        "enabled": True
    },
    "correlation_matrix": {
        "name": "Correlation Matrix",
        "description": "Asset correlation analysis and heatmap visualization", 
        "adapter": CorrelationMatrixAdapter,
        "enabled": True
    },
    "monte_carlo": {
        "name": "Monte Carlo Simulation",
        "description": "Portfolio return simulations and risk analysis",
        "adapter": MonteCarloAdapter,
        "enabled": True
    },
    "benchmark_comparison": {
        "name": "Benchmark Comparison",
        "description": "Portfolio performance vs benchmark analysis",
        "adapter": BenchmarkComparisonAdapter,
        "enabled": True
    },
    "dividend_analysis": {
        "name": "Dividend Analysis",
        "description": "Dividend income tracking and projections",
        "adapter": DividendAnalysisAdapter,
        "enabled": True
    },
    "performance": {
        "name": "Performance Analysis",
        "description": "Comprehensive performance metrics and statistics",
        "adapter": PerformanceAdapter,
        "enabled": True
    }
}

@router.get("/", response_model=dict)
async def list_widgets():
    """List all available portfolio widgets."""
    try:
        return {
            "widgets": {
                widget_id: {
                    "name": info["name"],
                    "description": info["description"],
                    "enabled": info["enabled"]
                }
                for widget_id, info in AVAILABLE_WIDGETS.items()
            },
            "total_count": len(AVAILABLE_WIDGETS)
        }
    except Exception as e:
        logger.error(f"Error listing widgets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list widgets")

# Original 4 widget endpoints (working)
@router.get("/portfolio-summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    time_period: Optional[str] = Query("1Y", description="Time period for analysis"),
    database: str = Depends(get_database)
):
    """Get portfolio summary widget data."""
    try:
        adapter = PortfolioSummaryAdapter(database)
        return await adapter.get_data(portfolio_id, time_period=time_period)
    except Exception as e:
        logger.error(f"Error in portfolio summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/holdings-breakdown", response_model=HoldingsBreakdownResponse)
async def get_holdings_breakdown(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    group_by: Optional[str] = Query("asset_type", description="Grouping method"),
    database: str = Depends(get_database)
):
    """Get holdings breakdown widget data."""
    try:
        adapter = HoldingsBreakdownAdapter(database)
        return await adapter.get_data(portfolio_id, group_by=group_by)
    except Exception as e:
        logger.error(f"Error in holdings breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlation-matrix", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    params: CorrelationParameters = Depends(),
    database: str = Depends(get_database)
):
    """Get correlation matrix widget data."""
    try:
        adapter = CorrelationMatrixAdapter(database)
        return await adapter.get_data(portfolio_id, **params.dict())
    except Exception as e:
        logger.error(f"Error in correlation matrix: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monte-carlo", response_model=MonteCarloResponse)
async def get_monte_carlo(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    params: MonteCarloParameters = Depends(),
    database: str = Depends(get_database)
):
    """Get Monte Carlo simulation widget data."""
    try:
        adapter = MonteCarloAdapter(database)
        return await adapter.get_data(portfolio_id, **params.dict())
    except Exception as e:
        logger.error(f"Error in Monte Carlo simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# New widget endpoints (3 additional)
@router.get("/benchmark-comparison")
async def get_benchmark_comparison(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    benchmark: Optional[str] = Query("SPY", description="Benchmark symbol"),
    time_period: Optional[str] = Query("1Y", description="Time period for analysis"),
    database: str = Depends(get_database)
):
    """Get benchmark comparison widget data."""
    try:
        adapter = BenchmarkComparisonAdapter(database)
        return await adapter.get_data(
            portfolio_id=portfolio_id,
            benchmark=benchmark,
            time_period=time_period
        )
    except Exception as e:
        logger.error(f"Error in benchmark comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dividend-analysis")
async def get_dividend_analysis(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    time_period: Optional[str] = Query("1Y", description="Time period for analysis"),
    database: str = Depends(get_database)
):
    """Get dividend analysis widget data."""
    try:
        adapter = DividendAnalysisAdapter(database)
        return await adapter.get_data(
            portfolio_id=portfolio_id,
            time_period=time_period
        )
    except Exception as e:
        logger.error(f"Error in dividend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_analysis(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    time_period: Optional[str] = Query("1Y", description="Time period for analysis"),
    database: str = Depends(get_database)
):
    """Get performance analysis widget data."""
    try:
        adapter = PerformanceAdapter(database)
        return await adapter.get_data(
            portfolio_id=portfolio_id,
            time_period=time_period
        )
    except Exception as e:
        logger.error(f"Error in performance analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))