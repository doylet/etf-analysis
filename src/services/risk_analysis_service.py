"""
Risk analysis service - calculates portfolio risk metrics.

Extracted from src/utils/performance_metrics.py to be service-oriented.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional

from utils.performance_metrics import (
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_beta,
    calculate_alpha
)


class RiskAnalysisService:
    """Service for calculating portfolio risk and performance metrics."""
    
    @staticmethod
    def calculate_risk_metrics(
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
        risk_free_rate: float = 0.04
    ) -> Dict[str, float]:
        """
        Calculate comprehensive risk metrics for a portfolio.
        
        Args:
            returns: Portfolio returns series
            benchmark_returns: Benchmark returns series (optional, for beta/alpha)
            risk_free_rate: Annual risk-free rate (default 4%)
            
        Returns:
            Dictionary with risk metrics:
            - sharpe_ratio: Sharpe ratio (annualized)
            - sortino_ratio: Sortino ratio (annualized)
            - max_drawdown: Maximum drawdown (as decimal)
            - volatility: Annualized volatility
            - var_95: Value at Risk (5th percentile)
            - cvar_95: Conditional Value at Risk (expected shortfall)
            - beta: Beta relative to benchmark (if benchmark provided)
            - alpha: Alpha relative to benchmark (if benchmark provided)
        """
        metrics = {}
        
        # Basic risk metrics
        metrics['sharpe_ratio'] = calculate_sharpe_ratio(returns, risk_free_rate)
        metrics['sortino_ratio'] = calculate_sortino_ratio(returns, risk_free_rate)
        metrics['volatility'] = returns.std() * np.sqrt(252)
        
        # Drawdown
        # Need prices to calculate drawdown, so reconstruct from returns
        prices = (1 + returns).cumprod()
        metrics['max_drawdown'] = calculate_max_drawdown(prices)
        
        # Value at Risk (VaR) and Conditional VaR (CVaR)
        var_95 = np.percentile(returns, 5)
        metrics['var_95'] = var_95
        
        worst_5_percent = returns[returns <= var_95]
        metrics['cvar_95'] = np.mean(worst_5_percent) if len(worst_5_percent) > 0 else var_95
        
        # Benchmark-relative metrics (if benchmark provided)
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            metrics['beta'] = calculate_beta(returns, benchmark_returns)
            metrics['alpha'] = calculate_alpha(returns, benchmark_returns, risk_free_rate)
        else:
            metrics['beta'] = None
            metrics['alpha'] = None
        
        return metrics
    
    @staticmethod
    def calculate_sharpe(
        returns: pd.Series,
        risk_free_rate: float = 0.04
    ) -> float:
        """Calculate Sharpe ratio."""
        return calculate_sharpe_ratio(returns, risk_free_rate)
    
    @staticmethod
    def calculate_sortino(
        returns: pd.Series,
        risk_free_rate: float = 0.04
    ) -> float:
        """Calculate Sortino ratio."""
        return calculate_sortino_ratio(returns, risk_free_rate)
    
    @staticmethod
    def calculate_var(
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """Calculate Value at Risk (VaR)."""
        percentile = (1 - confidence_level) * 100
        return np.percentile(returns, percentile)
    
    @staticmethod
    def calculate_cvar(
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """Calculate Conditional Value at Risk (CVaR / Expected Shortfall)."""
        var = RiskAnalysisService.calculate_var(returns, confidence_level)
        worst_returns = returns[returns <= var]
        return np.mean(worst_returns) if len(worst_returns) > 0 else var
    
    @staticmethod
    def calculate_drawdown(
        prices: pd.Series
    ) -> float:
        """Calculate maximum drawdown."""
        return calculate_max_drawdown(prices)
    
    @staticmethod
    def calculate_portfolio_beta(
        returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """Calculate beta relative to benchmark."""
        return calculate_beta(returns, benchmark_returns)
