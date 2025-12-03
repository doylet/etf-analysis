"""
Portfolio optimization service - implements various optimization strategies.

Extracted from src/widgets/portfolio_optimizer_widget.py to be framework-agnostic.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional

from ..domain.optimization import (
    OptimizationRequest,
    OptimizationResults,
    OptimizationObjective
)


class OptimizationService:
    """Service for portfolio optimization using various objectives."""
    
    @staticmethod
    def optimize(
        request: OptimizationRequest,
        returns_df: pd.DataFrame
    ) -> OptimizationResults:
        """
        Optimize portfolio based on requested objective.
        
        Args:
            request: Optimization parameters (symbols, objective, constraints, etc.)
            returns_df: Historical returns DataFrame with symbol columns
            
        Returns:
            OptimizationResults with optimal weights and metrics
            
        Raises:
            ValueError: If optimization fails or inputs are invalid
        """
        # Validate inputs
        if len(request.symbols) < 2:
            raise ValueError("Optimization requires at least 2 symbols")
        
        # Filter returns to requested symbols
        returns_subset = returns_df[request.symbols]
        
        # Route to appropriate optimization method
        if request.objective == OptimizationObjective.MAX_SHARPE:
            return OptimizationService._maximize_sharpe(returns_subset, request)
        elif request.objective == OptimizationObjective.MIN_VOLATILITY:
            return OptimizationService._minimize_volatility(returns_subset, request)
        elif request.objective == OptimizationObjective.MAX_RETURN:
            return OptimizationService._maximize_return(returns_subset, request)
        elif request.objective == OptimizationObjective.EFFICIENT_FRONTIER:
            return OptimizationService._calculate_efficient_frontier(returns_subset, request)
        else:
            raise ValueError(f"Unsupported objective: {request.objective}")
    
    @staticmethod
    def _maximize_sharpe(
        returns_df: pd.DataFrame,
        request: OptimizationRequest
    ) -> OptimizationResults:
        """Maximize Sharpe ratio."""
        n_assets = len(returns_df.columns)
        
        def negative_sharpe(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            mean_return = portfolio_returns.mean() * 252
            volatility = portfolio_returns.std() * np.sqrt(252)
            
            if volatility == 0:
                return 0
            
            sharpe = (mean_return - request.risk_free_rate) / volatility
            return -sharpe
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        
        # Add custom constraints from request
        if request.constraints:
            min_weight = request.constraints.get('min_weight', 0.0)
            max_weight = request.constraints.get('max_weight', 1.0)
        else:
            min_weight, max_weight = 0.0, 1.0
        
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            negative_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            raise ValueError(f"Optimization failed: {result.message}")
        
        # Calculate metrics
        optimal_weights = result.x
        portfolio_returns = (returns_df * optimal_weights).sum(axis=1)
        expected_return = portfolio_returns.mean() * 252
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (expected_return - request.risk_free_rate) / volatility if volatility > 0 else 0
        
        return OptimizationResults(
            optimal_weights=optimal_weights.tolist(),
            expected_return=float(expected_return),
            volatility=float(volatility),
            sharpe_ratio=float(sharpe_ratio)
        )
    
    @staticmethod
    def _minimize_volatility(
        returns_df: pd.DataFrame,
        request: OptimizationRequest
    ) -> OptimizationResults:
        """Minimize portfolio volatility."""
        n_assets = len(returns_df.columns)
        
        def portfolio_volatility(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            return portfolio_returns.std() * np.sqrt(252)
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        
        # Bounds
        if request.constraints:
            min_weight = request.constraints.get('min_weight', 0.0)
            max_weight = request.constraints.get('max_weight', 1.0)
        else:
            min_weight, max_weight = 0.0, 1.0
        
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            raise ValueError(f"Optimization failed: {result.message}")
        
        # Calculate metrics
        optimal_weights = result.x
        portfolio_returns = (returns_df * optimal_weights).sum(axis=1)
        expected_return = portfolio_returns.mean() * 252
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (expected_return - request.risk_free_rate) / volatility if volatility > 0 else 0
        
        return OptimizationResults(
            optimal_weights=optimal_weights.tolist(),
            expected_return=float(expected_return),
            volatility=float(volatility),
            sharpe_ratio=float(sharpe_ratio)
        )
    
    @staticmethod
    def _maximize_return(
        returns_df: pd.DataFrame,
        request: OptimizationRequest
    ) -> OptimizationResults:
        """Maximize expected return (subject to constraints)."""
        n_assets = len(returns_df.columns)
        
        def negative_return(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            return -portfolio_returns.mean() * 252
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        
        # Bounds
        if request.constraints:
            min_weight = request.constraints.get('min_weight', 0.0)
            max_weight = request.constraints.get('max_weight', 1.0)
            max_volatility = request.constraints.get('max_volatility')
            
            if max_volatility:
                def volatility_constraint(weights):
                    portfolio_returns = (returns_df * weights).sum(axis=1)
                    vol = portfolio_returns.std() * np.sqrt(252)
                    return max_volatility - vol
                
                constraints.append({'type': 'ineq', 'fun': volatility_constraint})
        else:
            min_weight, max_weight = 0.0, 1.0
        
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            negative_return,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            raise ValueError(f"Optimization failed: {result.message}")
        
        # Calculate metrics
        optimal_weights = result.x
        portfolio_returns = (returns_df * optimal_weights).sum(axis=1)
        expected_return = portfolio_returns.mean() * 252
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (expected_return - request.risk_free_rate) / volatility if volatility > 0 else 0
        
        return OptimizationResults(
            optimal_weights=optimal_weights.tolist(),
            expected_return=float(expected_return),
            volatility=float(volatility),
            sharpe_ratio=float(sharpe_ratio)
        )
    
    @staticmethod
    def _calculate_efficient_frontier(
        returns_df: pd.DataFrame,
        request: OptimizationRequest
    ) -> OptimizationResults:
        """Calculate efficient frontier with multiple portfolios."""
        num_points = request.num_points if request.num_points else 50
        
        # Find min volatility and max Sharpe portfolios
        min_vol_result = OptimizationService._minimize_volatility(returns_df, request)
        max_sharpe_result = OptimizationService._maximize_sharpe(returns_df, request)
        
        # Generate portfolios along the efficient frontier
        frontier_portfolios = []
        
        # Target returns from min vol to max return
        min_return = min_vol_result.expected_return
        max_return = max_sharpe_result.expected_return
        
        for target_return in np.linspace(min_return, max_return, num_points):
            try:
                # Create modified request with target return constraint
                modified_constraints = request.constraints.copy() if request.constraints else {}
                modified_constraints['target_return'] = target_return
                
                modified_request = OptimizationRequest(
                    symbols=request.symbols,
                    objective=OptimizationObjective.MIN_VOLATILITY,
                    constraints=modified_constraints,
                    risk_free_rate=request.risk_free_rate
                )
                
                result = OptimizationService._optimize_for_target_return(
                    returns_df, modified_request, target_return
                )
                
                frontier_portfolios.append({
                    'weights': result.optimal_weights,
                    'return': result.expected_return,
                    'volatility': result.volatility,
                    'sharpe': result.sharpe_ratio
                })
            except:
                continue
        
        return OptimizationResults(
            optimal_weights=max_sharpe_result.optimal_weights,
            expected_return=max_sharpe_result.expected_return,
            volatility=max_sharpe_result.volatility,
            sharpe_ratio=max_sharpe_result.sharpe_ratio,
            efficient_frontier=frontier_portfolios
        )
    
    @staticmethod
    def _optimize_for_target_return(
        returns_df: pd.DataFrame,
        request: OptimizationRequest,
        target_return: float
    ) -> OptimizationResults:
        """Optimize for target return with minimum volatility."""
        n_assets = len(returns_df.columns)
        
        def portfolio_volatility(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            return portfolio_returns.std() * np.sqrt(252)
        
        def portfolio_return(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            return portfolio_returns.mean() * 252
        
        # Constraints: weights sum to 1, return equals target
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: portfolio_return(w) - target_return}
        ]
        
        # Bounds
        if request.constraints:
            min_weight = request.constraints.get('min_weight', 0.0)
            max_weight = request.constraints.get('max_weight', 1.0)
        else:
            min_weight, max_weight = 0.0, 1.0
        
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            raise ValueError(f"Target return {target_return} may be unachievable")
        
        # Calculate metrics
        optimal_weights = result.x
        portfolio_returns = (returns_df * optimal_weights).sum(axis=1)
        expected_return = portfolio_returns.mean() * 252
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (expected_return - request.risk_free_rate) / volatility if volatility > 0 else 0
        
        return OptimizationResults(
            optimal_weights=optimal_weights.tolist(),
            expected_return=float(expected_return),
            volatility=float(volatility),
            sharpe_ratio=float(sharpe_ratio)
        )
