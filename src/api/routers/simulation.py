"""
Monte Carlo simulation API router.

Endpoints for running portfolio simulations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Union
from datetime import datetime

from api.schemas.simulation import SimulationRequest, SimulationResponse, TaskStatusResponse
from services.monte_carlo_service import MonteCarloService
from services.storage_adapter import DataStorageAdapter
from repositories.price_data_repository import PriceDataRepository
from domain.simulation import SimulationParameters
from api.auth import get_current_user, User
from api.tasks import monte_carlo_simulation_task, get_task_status as get_celery_task_status
from api.exceptions import BusinessLogicError, SimulationError


router = APIRouter(prefix="/simulation", tags=["Simulation"])

# Threshold for async processing (simulations with more paths will be async)
ASYNC_THRESHOLD = 1000


def get_simulation_service() -> MonteCarloService:
    """Get Monte Carlo service with repository."""
    storage = DataStorageAdapter()
    price_repo = PriceDataRepository(storage)
    return MonteCarloService(price_data_repository=price_repo)


@router.post("/monte-carlo", response_model=Union[SimulationResponse, TaskStatusResponse])
async def run_monte_carlo_simulation(
    request: SimulationRequest
):
    """
    Run Monte Carlo portfolio simulation.
    
    For simulations with >1000 paths, returns task ID for async processing.
    For smaller simulations, returns results immediately.
    """
    # Convert request to domain parameters
    params = SimulationParameters(
        symbols=request.symbols,
        weights=request.weights,
        initial_investment=request.initial_investment,
        years=request.years,
        num_simulations=request.num_simulations
    )
    
    # Validate weights sum to 1
    if abs(sum(request.weights) - 1.0) > 0.01:
        raise BusinessLogicError("Portfolio weights must sum to 1.0")
    
    # Validate symbols and weights match
    if len(request.symbols) != len(request.weights):
        raise BusinessLogicError("Number of symbols must match number of weights")
    
    # For large simulations, use Celery background task
    if request.num_simulations > ASYNC_THRESHOLD:
        # Convert parameters to serializable dict for Celery
        params_dict = {
            'symbols': params.symbols,
            'start_date': params.start_date,
            'end_date': params.end_date,
            'num_simulations': params.num_simulations,
            'time_horizon': params.time_horizon,
            'initial_investment': params.initial_investment,
            'risk_free_rate': getattr(params, 'risk_free_rate', 0.02),
            'confidence_level': getattr(params, 'confidence_level', 0.95),
            'rebalancing_frequency': getattr(params, 'rebalancing_frequency', 'monthly')
        }
        
        # Start Celery task
        task = monte_carlo_simulation_task.delay(params_dict)
        
        return TaskStatusResponse(
            task_id=task.id,
            status="pending",
            progress=0.0,
            message=f"Monte Carlo simulation queued for {request.num_simulations} paths"
        )
    
    # For smaller simulations, run synchronously
    try:
        service = get_simulation_service()
        results = service.run_simulation(params)
        
        # Convert results to response format
        return SimulationResponse(
            median_outcome=results.median_outcome,
            best_case=results.best_case,
            worst_case=results.worst_case,
            percentiles=results.percentiles,
            probability_of_loss=results.probability_of_loss,
            expected_return=results.expected_return,
            expected_volatility=results.expected_volatility,
            sharpe_ratio=results.sharpe_ratio,
            max_drawdown=results.max_drawdown,
            value_at_risk_95=results.value_at_risk_95,
            simulation_paths=None,  # Omit paths to reduce response size
            rebalancing_analysis=None
        )
        
    except Exception as e:
        raise SimulationError(str(e))


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_simulation_task_status(task_id: str):
    """Get status of background simulation task."""
    try:
        # Get status from Celery
        status_info = get_celery_task_status(task_id)
        
        return TaskStatusResponse(
            task_id=task_id,
            status=status_info.get('state', 'unknown').lower(),
            progress=status_info.get('current', 0),
            message=status_info.get('status', 'Task status unknown'),
            error=status_info.get('error')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get task status: {str(e)}"
        )