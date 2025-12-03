"""
Monte Carlo simulation API router.

Endpoints for running portfolio simulations.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
import pandas as pd
from datetime import datetime
import uuid

from ..schemas.simulation import SimulationRequest, SimulationResponse, TaskStatusResponse
from ...services.monte_carlo_service import MonteCarloService
from ...services.storage_adapter import DataStorageAdapter
from ...repositories.price_data_repository import PriceDataRepository
from ...domain.simulation import SimulationParameters


router = APIRouter(prefix="/simulation", tags=["Simulation"])

# In-memory task storage (replace with Redis/Celery in production)
_task_store: Dict[str, Dict] = {}


def get_simulation_service() -> MonteCarloService:
    """Get Monte Carlo service with repository."""
    storage = DataStorageAdapter()
    price_repo = PriceDataRepository(storage)
    return MonteCarloService(price_data_repository=price_repo)


async def run_simulation_task(task_id: str, params: SimulationParameters):
    """Background task for running simulation."""
    try:
        _task_store[task_id]["status"] = "running"
        _task_store[task_id]["started_at"] = datetime.utcnow()
        
        service = get_simulation_service()
        results = service.run_simulation(params)
        
        # Convert results to response format
        response = SimulationResponse(
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
        
        _task_store[task_id]["status"] = "completed"
        _task_store[task_id]["completed_at"] = datetime.utcnow()
        _task_store[task_id]["result"] = response
        
    except Exception as e:
        _task_store[task_id]["status"] = "failed"
        _task_store[task_id]["error"] = str(e)
        _task_store[task_id]["completed_at"] = datetime.utcnow()


@router.post("/monte-carlo", response_model=SimulationResponse | TaskStatusResponse)
async def run_monte_carlo_simulation(
    request: SimulationRequest,
    background_tasks: BackgroundTasks
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
        raise HTTPException(
            status_code=400,
            detail="Portfolio weights must sum to 1.0"
        )
    
    # Validate symbols and weights match
    if len(request.symbols) != len(request.weights):
        raise HTTPException(
            status_code=400,
            detail="Number of symbols must match number of weights"
        )
    
    # For large simulations, use background task
    if request.num_simulations > 1000:
        task_id = str(uuid.uuid4())
        _task_store[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0.0,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }
        
        background_tasks.add_task(run_simulation_task, task_id, params)
        
        return TaskStatusResponse(
            task_id=task_id,
            status="pending",
            progress=0.0,
            created_at=_task_store[task_id]["created_at"],
            started_at=None,
            completed_at=None,
            result=None,
            error=None
        )
    
    # For small simulations, run synchronously
    try:
        service = get_simulation_service()
        results = service.run_simulation(params)
        
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
            simulation_paths=None,
            rebalancing_analysis=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get status of background simulation task."""
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = _task_store[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task.get("progress", 0.0),
        created_at=task["created_at"],
        started_at=task.get("started_at"),
        completed_at=task.get("completed_at"),
        result=task.get("result"),
        error=task.get("error")
    )
