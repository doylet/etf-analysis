"""FastAPI router for portfolio widget endpoints."""

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
from ..widgets.portfolio_summary import PortfolioSummaryAdapter

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
                "description": "Portfolio performance metrics and summary"
            },
            {
                "name": "holdings_breakdown", 
                "endpoint": "/api/widgets/portfolio/holdings",
                "description": "Detailed breakdown of portfolio positions"
            },
            {
                "name": "correlation_matrix",
                "endpoint": "/api/widgets/portfolio/correlation",
                "description": "Asset correlation analysis"
            },
            {
                "name": "monte_carlo",
                "endpoint": "/api/widgets/portfolio/monte-carlo", 
                "description": "Monte Carlo risk simulation"
            }
        ],
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
        result = await adapter.execute(portfolio_id=portfolio_id)
        
        # Return typed response
        return PortfolioSummaryResponse(
            widget_name=result.widget_name,
            success=result.success,
            data=result.data,
            metadata=result.metadata,
            error=result.error
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
    description="Retrieve detailed breakdown of all portfolio positions with weights and performance"
)
async def get_holdings_breakdown(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier") 
) -> HoldingsBreakdownResponse:
    """Get detailed holdings breakdown."""
    # This will be implemented in Phase 3 User Story tasks
    raise HTTPException(
        status_code=501,
        detail="Holdings breakdown widget implementation pending"
    )


@router.get("/portfolio/correlation", 
    response_model=CorrelationMatrixResponse,
    summary="Get correlation matrix",
    description="Calculate correlation matrix between portfolio assets"
)
async def get_correlation_matrix(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    lookback_days: int = Query(252, description="Historical data lookback period"),
    method: str = Query("pearson", description="Correlation calculation method")
) -> CorrelationMatrixResponse:
    """Get asset correlation matrix."""
    # This will be implemented in Phase 3 User Story tasks  
    raise HTTPException(
        status_code=501,
        detail="Correlation matrix widget implementation pending"
    )


@router.get("/portfolio/monte-carlo",
    response_model=MonteCarloResponse,
    summary="Run Monte Carlo simulation", 
    description="Perform Monte Carlo risk simulation for portfolio performance scenarios"
)
async def get_monte_carlo_simulation(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    num_simulations: int = Query(1000, description="Number of simulation runs"),
    time_horizon_days: int = Query(252, description="Time horizon in days"), 
    confidence_level: float = Query(0.95, description="Confidence level for VaR")
) -> MonteCarloResponse:
    """Run Monte Carlo simulation for portfolio."""
    # This will be implemented in Phase 3 User Story tasks
    raise HTTPException(
        status_code=501,
        detail="Monte Carlo widget implementation pending"
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
        "message": "Widget service is operational"
    }