"""FastAPI router for portfolio widget endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from src.api.dependencies import get_database
from src.api.schemas.widgets import (
    WidgetResponse, 
    PortfolioSummaryResponse,
    HoldingsBreakdownResponse, 
    CorrelationMatrixResponse,
    MonteCarloResponse,
    MonteCarloParameters,
    CorrelationParameters
)
from src.api.widgets.portfolio_summary import PortfolioSummaryAdapter
from src.api.widgets.holdings_breakdown import HoldingsBreakdownAdapter
from src.api.widgets.correlation_matrix import CorrelationMatrixAdapter
from src.api.widgets.monte_carlo import MonteCarloAdapter

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/widgets",
    tags=["widgets"],
    responses={
        404: {"description": "Widget not found"},
        422: {"description": "Invalid widget parameters"}, 
        500: {"description": "Widget calculation error"}
    }
)


@router.get("/", 
    summary="List available widgets",
    description="Get list of all available portfolio analysis widgets"
)
async def list_widgets() -> dict:
    """List all available widget endpoints."""
    return {
        "available_widgets": [
            {
                "name": "portfolio_summary",
                "endpoint": "/api/widgets/portfolio/summary", 
                "description": "Portfolio performance metrics and summary",
                "category": "overview"
            },
            {
                "name": "holdings_breakdown", 
                "endpoint": "/api/widgets/portfolio/holdings",
                "description": "Detailed breakdown of portfolio positions",
                "category": "overview"
            },
            {
                "name": "correlation_matrix",
                "endpoint": "/api/widgets/portfolio/correlation",
                "description": "Asset correlation analysis",
                "category": "analysis"
            },
            {
                "name": "monte_carlo",
                "endpoint": "/api/widgets/portfolio/monte-carlo", 
                "description": "Monte Carlo risk simulation",
                "category": "analysis"
            }
        ],
        "total_widgets": 4,
        "status": "ready"
    }


@router.get("/portfolio/summary",
    response_model=PortfolioSummaryResponse,
    summary="Get portfolio summary",
    description="Retrieve portfolio performance metrics including total value, returns, and position count"
)
async def get_portfolio_summary(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier")
) -> PortfolioSummaryResponse:
    """Get portfolio summary metrics."""
    try:
        # Create portfolio summary adapter
        adapter = PortfolioSummaryAdapter(db)
        
        # Execute widget calculation
        result = adapter.execute(portfolio_id=portfolio_id)
        
        # Return typed response
        return PortfolioSummaryResponse(
            widget_name=result["widget_name"],
            success=result["success"],
            data=result["data"],
            metadata=result["metadata"],
            error=result["error"]
        )
        
    except Exception as e:
        logger.error(f"Error in portfolio summary endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate portfolio summary: {str(e)}"
        )


@router.get("/portfolio/holdings",
    response_model=HoldingsBreakdownResponse,
    summary="Get holdings breakdown",
    description="Detailed breakdown of portfolio holdings by sector, geography, or asset class"
)
async def get_holdings_breakdown(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    breakdown_type: str = Query("sector", description="Type of breakdown (sector, geography, asset_class, all)")
) -> HoldingsBreakdownResponse:
    """Get detailed holdings breakdown."""
    try:
        # Create holdings breakdown adapter
        adapter = HoldingsBreakdownAdapter(db)
        
        # Execute widget calculation
        result = adapter.execute(portfolio_id=portfolio_id, breakdown_type=breakdown_type)
        
        # Return typed response
        return HoldingsBreakdownResponse(
            widget_name=result["widget_name"],
            success=result["success"],
            data=result["data"],
            metadata=result["metadata"],
            error=result["error"]
        )
        
    except Exception as e:
        logger.error(f"Error in holdings breakdown endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate holdings breakdown: {str(e)}"
        )


@router.get("/portfolio/correlation", 
    response_model=CorrelationMatrixResponse,
    summary="Get correlation matrix",
    description="Calculate correlation matrix between portfolio assets and benchmarks"
)
async def get_correlation_matrix(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    time_window_days: int = Query(252, description="Time window for correlation analysis (default 1 year)"),
    additional_symbols: Optional[str] = Query("SPY,QQQ", description="Additional benchmark symbols (comma-separated)"),
    include_holdings: bool = Query(True, description="Include portfolio holdings in analysis")
) -> CorrelationMatrixResponse:
    """Get asset correlation matrix analysis."""
    try:
        # Parse additional symbols
        additional_symbols_list = []
        if additional_symbols:
            additional_symbols_list = [s.strip().upper() for s in additional_symbols.split(',') if s.strip()]
        
        # Create correlation matrix adapter
        adapter = CorrelationMatrixAdapter(db)
        
        # Execute widget calculation
        result = adapter.execute(
            portfolio_id=portfolio_id,
            time_window_days=time_window_days,
            additional_symbols=additional_symbols_list,
            include_holdings=include_holdings
        )
        
        # Return typed response
        return CorrelationMatrixResponse(
            widget_name=result["widget_name"],
            success=result["success"],
            data=result["data"],
            metadata=result["metadata"],
            error=result["error"]
        )
        
    except Exception as e:
        logger.error(f"Error in correlation matrix endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate correlation matrix: {str(e)}"
        )


@router.get("/portfolio/monte-carlo",
    response_model=MonteCarloResponse,
    summary="Get Monte Carlo simulation",
    description="Run Monte Carlo simulation for portfolio risk analysis"
)
async def get_monte_carlo_simulation(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    num_simulations: int = Query(10000, description="Number of simulation runs"),
    time_horizon_days: int = Query(252, description="Investment horizon in days (default 1 year)"),
    confidence_level: float = Query(0.95, description="Confidence level for VaR calculation"),
    initial_value: Optional[float] = Query(None, description="Initial portfolio value (uses current if not provided)"),
    include_dividends: bool = Query(True, description="Include dividend payments in simulation"),
    estimation_method: str = Query("historical", description="Return estimation method (historical, monte_carlo)")
) -> MonteCarloResponse:
    """Get Monte Carlo risk simulation."""
    try:
        # Validate inputs
        if num_simulations < 100 or num_simulations > 100000:
            raise HTTPException(status_code=400, detail="Number of simulations must be between 100 and 100,000")
        
        if confidence_level <= 0 or confidence_level >= 1:
            raise HTTPException(status_code=400, detail="Confidence level must be between 0 and 1")
            
        if time_horizon_days < 1 or time_horizon_days > 5*252:  # Max 5 years
            raise HTTPException(status_code=400, detail="Time horizon must be between 1 and 1260 days")
        
        # Create Monte Carlo adapter
        adapter = MonteCarloAdapter(db)
        
        # Execute widget calculation
        result = adapter.execute(
            portfolio_id=portfolio_id,
            num_simulations=num_simulations,
            time_horizon_days=time_horizon_days,
            confidence_level=confidence_level,
            initial_value=initial_value,
            include_dividends=include_dividends,
            estimation_method=estimation_method
        )
        
        # Return typed response
        return MonteCarloResponse(
            widget_name=result["widget_name"],
            success=result["success"],
            data=result["data"],
            metadata=result["metadata"],
            error=result["error"]
        )
        
    except Exception as e:
        logger.error(f"Error in Monte Carlo endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run Monte Carlo simulation: {str(e)}"
        )


@router.get("/health",
    summary="Widget service health check",
    description="Check if widget service is operational"
)
async def health_check():
    """Health check endpoint for widget service."""
    return {
        "status": "healthy",
        "service": "portfolio_widgets", 
        "widgets_available": 4,
        "message": "Widget service is operational with basic 4 widgets"
    }