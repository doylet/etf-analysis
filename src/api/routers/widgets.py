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
from src.api.widgets.benchmark_comparison import BenchmarkComparisonAdapter
from src.api.widgets.dividend_analysis import DividendAnalysisAdapter
from src.api.widgets.performance import PerformanceAdapter
from src.api.widgets.timeseries_analysis import TimeseriesAnalysisAdapter
from src.api.widgets.portfolio_transition import PortfolioTransitionAdapter
from src.api.widgets.news_event_analysis import NewsEventAnalysisAdapter
from src.api.widgets.portfolio_optimizer import PortfolioOptimizerAdapter
from src.api.widgets.constrained_optimization import ConstrainedOptimizationAdapter

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
            },
            {
                "name": "benchmark_comparison",
                "endpoint": "/api/widgets/benchmark-comparison",
                "description": "Compare portfolio performance against market benchmarks",
                "category": "analysis"
            },
            {
                "name": "dividend_analysis",
                "endpoint": "/api/widgets/dividend-analysis",
                "description": "Analyze dividend income and yield metrics",
                "category": "analysis"
            },
            {
                "name": "performance",
                "endpoint": "/api/widgets/performance",
                "description": "Analyze portfolio performance metrics and statistics",
                "category": "analysis"
            },
            {
                "name": "timeseries_analysis",
                "endpoint": "/api/widgets/timeseries-analysis",
                "description": "Analyze portfolio value over time with trends",
                "category": "analysis"
            },
            {
                "name": "portfolio_transition",
                "endpoint": "/api/widgets/portfolio-transition",
                "description": "Analyze portfolio transitions and rebalancing",
                "category": "analysis"
            },
            {
                "name": "news_event_analysis",
                "endpoint": "/api/widgets/news-event-analysis",
                "description": "Analyze impact of news and events on portfolio",
                "category": "analysis"
            },
            {
                "name": "portfolio_optimizer",
                "endpoint": "/api/widgets/portfolio-optimizer",
                "description": "Optimize portfolio allocation for risk/return",
                "category": "optimization"
            },
            {
                "name": "constrained_optimization",
                "endpoint": "/api/widgets/constrained-optimization",
                "description": "Optimize portfolio with custom constraints",
                "category": "optimization"
            }
        ],
        "total_widgets": 12,
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


@router.get("/benchmark-comparison",
    response_model=WidgetResponse,
    summary="Get benchmark comparison analysis",
    description="Compare portfolio performance against market benchmarks"
)
async def get_benchmark_comparison(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    time_period: Optional[str] = Query('1Y', description="Time period (1W, 1M, 3M, 6M, 1Y, 2Y, 5Y)"),
    benchmark: Optional[str] = Query('SPY', description="Benchmark symbol (SPY, QQQ, DIA, IWM, VTI, EFA, AGG, GLD)")
) -> WidgetResponse:
    """Get benchmark comparison analysis."""
    try:
        adapter = BenchmarkComparisonAdapter(db)
        return await adapter.execute(
            portfolio_id=portfolio_id,
            time_period=time_period,
            benchmark=benchmark
        )
        
    except Exception as e:
        logger.error(f"Error in benchmark comparison endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate benchmark comparison: {str(e)}"
        )


@router.get("/dividend-analysis",
    response_model=WidgetResponse,
    summary="Get dividend analysis",
    description="Analyze dividend income and yield metrics"
)
async def get_dividend_analysis(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    time_period: Optional[str] = Query('All', description="Time period (All, 1Y, 2Y, 5Y)"),
    symbol: Optional[str] = Query(None, description="Filter by symbol")
) -> WidgetResponse:
    """Get dividend analysis."""
    try:
        adapter = DividendAnalysisAdapter(db)
        return await adapter.execute(
            portfolio_id=portfolio_id,
            time_period=time_period,
            symbol=symbol
        )
        
    except Exception as e:
        logger.error(f"Error in dividend analysis endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate dividend analysis: {str(e)}"
        )


@router.get("/performance",
    response_model=WidgetResponse,
    summary="Get performance analysis",
    description="Analyze portfolio performance metrics and statistics"
)
async def get_performance_analysis(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    time_period: Optional[str] = Query('1Y', description="Time period (1W, 1M, 3M, 6M, 1Y, 2Y, 5Y)")
) -> WidgetResponse:
    """Get performance analysis."""
    try:
        adapter = PerformanceAdapter(db)
        return await adapter.execute(
            portfolio_id=portfolio_id,
            time_period=time_period
        )
        
    except Exception as e:
        logger.error(f"Error in performance analysis endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate performance analysis: {str(e)}"
        )


@router.get("/timeseries-analysis",
    response_model=WidgetResponse,
    summary="Get timeseries analysis",
    description="Analyze portfolio value over time with trends"
)
async def get_timeseries_analysis(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    time_period: Optional[str] = Query('1Y', description="Time period"),
    analysis_type: Optional[str] = Query('Portfolio Overview', description="Analysis type"),
    symbol: Optional[str] = Query(None, description="Symbol to analyze")
) -> WidgetResponse:
    """Get timeseries analysis."""
    try:
        adapter = TimeseriesAnalysisAdapter(db)
        return await adapter.execute(
            portfolio_id=portfolio_id,
            time_period=time_period,
            analysis_type=analysis_type,
            symbol=symbol
        )
        
    except Exception as e:
        logger.error(f"Error in timeseries analysis endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate timeseries analysis: {str(e)}"
        )


@router.get("/portfolio-transition",
    response_model=WidgetResponse,
    summary="Get portfolio transition analysis",
    description="Analyze portfolio transitions and rebalancing"
)
async def get_portfolio_transition(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    transition_method: Optional[str] = Query('Gradual', description="Transition method"),
    optimization_priority: Optional[str] = Query('Balance', description="Optimization priority")
) -> WidgetResponse:
    """Get portfolio transition analysis."""
    try:
        adapter = PortfolioTransitionAdapter(db)
        return await adapter.execute(
            portfolio_id=portfolio_id,
            transition_method=transition_method,
            optimization_priority=optimization_priority
        )
        
    except Exception as e:
        logger.error(f"Error in portfolio transition endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate portfolio transition: {str(e)}"
        )


@router.get("/news-event-analysis",
    response_model=WidgetResponse,
    summary="Get news and event analysis",
    description="Analyze impact of news and events on portfolio"
)
async def get_news_event_analysis(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    lookback_days: Optional[int] = Query(30, description="Lookback days"),
    surprise_threshold: Optional[float] = Query(5.0, description="Surprise threshold percentage")
) -> WidgetResponse:
    """Get news and event analysis."""
    try:
        adapter = NewsEventAnalysisAdapter(db)
        return await adapter.execute(
            portfolio_id=portfolio_id,
            lookback_days=lookback_days,
            surprise_threshold=surprise_threshold
        )
        
    except Exception as e:
        logger.error(f"Error in news event analysis endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate news event analysis: {str(e)}"
        )


@router.get("/portfolio-optimizer",
    response_model=WidgetResponse,
    summary="Get portfolio optimization",
    description="Optimize portfolio allocation for risk/return"
)
async def get_portfolio_optimizer(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    mode: Optional[str] = Query('Max Sharpe', description="Optimization mode"),
    time_period: Optional[str] = Query('1Y', description="Historical data period"),
    target_return: Optional[float] = Query(None, description="Target return"),
    include_dividends: Optional[bool] = Query(True, description="Include dividends")
) -> WidgetResponse:
    """Get portfolio optimization."""
    try:
        adapter = PortfolioOptimizerAdapter(db)
        return await adapter.execute(
            portfolio_id=portfolio_id,
            mode=mode,
            time_period=time_period,
            target_return=target_return,
            include_dividends=include_dividends
        )
        
    except Exception as e:
        logger.error(f"Error in portfolio optimizer endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate portfolio optimization: {str(e)}"
        )


@router.get("/constrained-optimization",
    response_model=WidgetResponse,
    summary="Get constrained optimization",
    description="Optimize portfolio with custom constraints"
)
async def get_constrained_optimization(
    db = Depends(get_database),
    portfolio_id: Optional[str] = Query(None, description="Portfolio identifier"),
    objective: Optional[str] = Query('Max Sharpe', description="Optimization objective"),
    max_weight: Optional[float] = Query(30.0, description="Max weight percentage"),
    min_weight: Optional[float] = Query(0.0, description="Min weight percentage"),
    target_return: Optional[float] = Query(None, description="Target return")
) -> WidgetResponse:
    """Get constrained optimization."""
    try:
        adapter = ConstrainedOptimizationAdapter(db)
        return await adapter.execute(
            portfolio_id=portfolio_id,
            objective=objective,
            max_weight=max_weight,
            min_weight=min_weight,
            target_return=target_return
        )
        
    except Exception as e:
        logger.error(f"Error in constrained optimization endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate constrained optimization: {str(e)}"
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
        "widgets_available": 12,
        "message": "Widget service is operational with all 12 widgets"
    }