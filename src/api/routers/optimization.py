"""
Portfolio optimization API router.

Endpoints for portfolio optimization operations.
"""

from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
import numpy as np
from typing import List

from api.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
    EfficientFrontierResponse,
    EfficientFrontierPoint,
)
from services.optimization_service import OptimizationService
from services.storage_adapter import DataStorageAdapter
from repositories.price_data_repository import PriceDataRepository
from domain.optimization import (
    OptimizationRequest as DomainOptRequest,
    OptimizationObjective,
)
from api.auth import get_current_user, User
from api.exceptions import BusinessLogicError, InsufficientDataError, InvalidConstraintsError


router = APIRouter(prefix="/optimization", tags=["Optimization"])


def get_optimization_service() -> OptimizationService:
    """Get optimization service with repository."""
    storage = DataStorageAdapter()
    price_repo = PriceDataRepository(storage)
    return OptimizationService(price_data_repository=price_repo)


@router.post("/max-sharpe", response_model=OptimizationResponse)
async def maximize_sharpe_ratio(request: OptimizationRequest):
    """
    Find portfolio weights that maximize Sharpe ratio.
    
    Returns optimal allocation for best risk-adjusted returns.
    """
    if len(request.symbols) < 2:
        raise BusinessLogicError("Optimization requires at least 2 symbols")
    
    try:
        # Convert to domain request
        domain_request = DomainOptRequest(
            symbols=request.symbols,
            objective=OptimizationObjective.MAX_SHARPE,
            risk_free_rate=request.risk_free_rate,
            constraints=request.constraints
        )
        
        service = get_optimization_service()
        results = service.optimize(domain_request)
        
        return OptimizationResponse(
            optimal_weights=results.optimal_weights,
            symbols=request.symbols,
            expected_return=results.expected_return,
            volatility=results.volatility,
            sharpe_ratio=results.sharpe_ratio,
            objective_value=results.sharpe_ratio,
            success=True
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/min-volatility", response_model=OptimizationResponse)
async def minimize_volatility(request: OptimizationRequest):
    """
    Find portfolio weights that minimize volatility.
    
    Returns optimal allocation for lowest risk.
    """
    if len(request.symbols) < 2:
        raise BusinessLogicError("Optimization requires at least 2 symbols")
    
    try:
        # Convert to domain request
        domain_request = DomainOptRequest(
            symbols=request.symbols,
            objective=OptimizationObjective.MIN_VOLATILITY,
            risk_free_rate=request.risk_free_rate,
            constraints=request.constraints
        )
        
        service = get_optimization_service()
        results = service.optimize(domain_request)
        
        return OptimizationResponse(
            optimal_weights=results.optimal_weights,
            symbols=request.symbols,
            expected_return=results.expected_return,
            volatility=results.volatility,
            sharpe_ratio=results.sharpe_ratio,
            objective_value=results.volatility,
            success=True
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/efficient-frontier", response_model=EfficientFrontierResponse)
async def calculate_efficient_frontier(request: OptimizationRequest):
    """
    Calculate the efficient frontier for given symbols.
    
    Returns multiple portfolio allocations along the efficient frontier,
    from minimum volatility to maximum Sharpe ratio.
    """
    if len(request.symbols) < 2:
        raise BusinessLogicError("Efficient frontier requires at least 2 symbols")
    
    try:
        service = get_optimization_service()
        frontier_points: List[EfficientFrontierPoint] = []
        
        # Calculate minimum volatility portfolio
        min_vol_request = DomainOptRequest(
            symbols=request.symbols,
            objective=OptimizationObjective.MIN_VOLATILITY,
            risk_free_rate=request.risk_free_rate,
            constraints=request.constraints
        )
        min_vol_results = service.optimize(min_vol_request)
        min_vol_point = EfficientFrontierPoint(
            return_value=min_vol_results.expected_return,
            volatility=min_vol_results.volatility,
            sharpe_ratio=min_vol_results.sharpe_ratio,
            weights=min_vol_results.optimal_weights
        )
        frontier_points.append(min_vol_point)
        
        # Calculate maximum Sharpe portfolio
        max_sharpe_request = DomainOptRequest(
            symbols=request.symbols,
            objective=OptimizationObjective.MAX_SHARPE,
            risk_free_rate=request.risk_free_rate,
            constraints=request.constraints
        )
        max_sharpe_results = service.optimize(max_sharpe_request)
        max_sharpe_point = EfficientFrontierPoint(
            return_value=max_sharpe_results.expected_return,
            volatility=max_sharpe_results.volatility,
            sharpe_ratio=max_sharpe_results.sharpe_ratio,
            weights=max_sharpe_results.optimal_weights
        )
        
        # Generate intermediate points along frontier
        # Use target return optimization for points between min vol and max sharpe
        min_return = min_vol_results.expected_return
        max_return = max_sharpe_results.expected_return
        num_points = 8
        
        for i in range(1, num_points):
            target_ret = min_return + (max_return - min_return) * (i / num_points)
            try:
                target_request = DomainOptRequest(
                    symbols=request.symbols,
                    objective=OptimizationObjective.TARGET_RETURN,
                    risk_free_rate=request.risk_free_rate,
                    target_return=target_ret,
                    constraints=request.constraints
                )
                target_results = service.optimize(target_request)
                frontier_points.append(EfficientFrontierPoint(
                    return_value=target_results.expected_return,
                    volatility=target_results.volatility,
                    sharpe_ratio=target_results.sharpe_ratio,
                    weights=target_results.optimal_weights
                ))
            except:
                # Skip if target return is unachievable
                continue
        
        frontier_points.append(max_sharpe_point)
        
        # Sort by volatility
        frontier_points.sort(key=lambda p: p.volatility)
        
        return EfficientFrontierResponse(
            frontier_points=frontier_points,
            symbols=request.symbols,
            min_volatility_point=min_vol_point,
            max_sharpe_point=max_sharpe_point
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frontier calculation failed: {str(e)}")
