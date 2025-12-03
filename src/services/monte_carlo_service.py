"""
Monte Carlo simulation service - runs portfolio simulations using geometric Brownian motion.

Extracted from src/widgets/monte_carlo_widget.py to be framework-agnostic.
"""

import numpy as np
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta

from ..domain.simulation import SimulationParameters, SimulationResults
from ..domain.rebalancing import RebalancingRecommendation


class MonteCarloService:
    """Service for running Monte Carlo portfolio simulations."""
    
    def __init__(self, price_data_repository=None):
        """
        Initialize service with optional repository.
        
        Args:
            price_data_repository: Optional PriceDataRepository for fetching data
        """
        self.price_data_repository = price_data_repository
    
    def run_simulation(
        self,
        params: SimulationParameters,
        returns_df: Optional[pd.DataFrame] = None,
        confidence_level: int = 90,
        estimation_method: str = "Historical Mean",
        enable_rebalancing_analysis: bool = False,
        drift_threshold: float = 0.10,
        transaction_cost_pct: float = 0.001,
        max_rebalances_per_year: Optional[int] = None
    ) -> SimulationResults:
        """
        Run Monte Carlo simulation using geometric Brownian motion.
        
        Args:
            params: Simulation parameters (symbols, weights, years, etc.)
            returns_df: Historical returns DataFrame with symbol columns (optional if repository provided)
            confidence_level: Confidence level for percentiles (e.g., 90)
            estimation_method: "Historical Mean" or "Exponentially Weighted"
            enable_rebalancing_analysis: Whether to analyze rebalancing timing
            drift_threshold: Drift threshold for rebalancing (default 10%)
            transaction_cost_pct: Transaction cost per rebalance (default 0.1%)
            max_rebalances_per_year: Maximum rebalances per year (optional)
            
        Returns:
            SimulationResults with paths, percentiles, and risk metrics
        """
        # Fetch returns if not provided and repository available
        if returns_df is None:
            if self.price_data_repository is None:
                raise ValueError("Either returns_df or price_data_repository must be provided")
            returns_df = self._fetch_returns(params)
        
        # 1. Estimate parameters from historical data
        weights = np.array(params.weights)
        portfolio_returns = (returns_df[params.symbols] * weights).sum(axis=1)
        
        if estimation_method == "Exponentially Weighted":
            # Use exponentially weighted moving average with higher weight on recent data
            span = 60  # Roughly 3 months of trading days
            mu = portfolio_returns.ewm(span=span).mean().iloc[-1] * 252
            sigma = portfolio_returns.ewm(span=span).std().iloc[-1] * np.sqrt(252)
        else:  # Historical Mean
            mu = portfolio_returns.mean() * 252  # Annualized drift
            sigma = portfolio_returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Calculate historical Sharpe ratio
        risk_free_rate = params.risk_free_rate if hasattr(params, 'risk_free_rate') else 0.04
        historical_sharpe = (mu - risk_free_rate) / sigma if sigma > 0 else 0
        
        # 2. Simulation parameters
        dt = 1 / 252  # Daily time steps
        num_steps = int(params.years * 252)
        
        # Determine contribution frequency
        if params.contribution_frequency == "Monthly":
            contrib_interval = 21  # ~21 trading days per month
        elif params.contribution_frequency == "Quarterly":
            contrib_interval = 63  # ~63 trading days per quarter
        else:  # Annual
            contrib_interval = 252  # 252 trading days per year
        
        # 3. Generate random paths using geometric Brownian motion with contributions
        # S(t+dt) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z) + contribution
        
        np.random.seed(42)  # For reproducibility
        paths = np.zeros((params.num_simulations, num_steps + 1))
        paths[:, 0] = params.initial_value
        
        for t in range(1, num_steps + 1):
            Z = np.random.standard_normal(params.num_simulations)
            paths[:, t] = paths[:, t-1] * np.exp(
                (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
            )
            
            # Add contribution at specified intervals
            if params.enable_contributions and t % contrib_interval == 0:
                # Prorate contribution based on frequency
                if params.contribution_frequency == "Monthly":
                    periodic_contrib = params.contribution_amount / 12
                elif params.contribution_frequency == "Quarterly":
                    periodic_contrib = params.contribution_amount / 4
                else:  # Annual
                    periodic_contrib = params.contribution_amount
                
                paths[:, t] += periodic_contrib
        
        # 4. Calculate statistics
        time_points = np.linspace(0, params.years, num_steps + 1)
        
        # Calculate percentiles
        lower_pct = (100 - confidence_level) // 2
        upper_pct = 100 - lower_pct
        
        percentiles = {}
        for pct in [5, 10, lower_pct, 25, 40, 50, 60, 75, upper_pct, 90, 95]:
            percentiles[pct] = np.percentile(paths, pct, axis=0)
        
        final_values = paths[:, -1]
        
        # Calculate risk metrics
        var_95 = np.percentile(final_values, 5)  # Value at Risk (5th percentile)
        worst_5_percent = final_values[final_values <= var_95]
        cvar_95 = np.mean(worst_5_percent) if len(worst_5_percent) > 0 else var_95
        
        # Calculate max drawdown for median path
        median_path = percentiles[50]
        cumulative_max = np.maximum.accumulate(median_path)
        drawdowns = (median_path - cumulative_max) / cumulative_max
        max_drawdown_median = np.min(drawdowns) * 100  # As percentage
        
        # Calculate CAGR for different percentiles
        cagr_median = ((percentiles[50][-1] / params.initial_value) ** (1/params.years) - 1) * 100
        cagr_10th = ((percentiles[lower_pct][-1] / params.initial_value) ** (1/params.years) - 1) * 100
        cagr_90th = ((percentiles[upper_pct][-1] / params.initial_value) ** (1/params.years) - 1) * 100
        
        # 5. Rebalancing analysis (if enabled)
        rebalancing_dates = None
        if enable_rebalancing_analysis and hasattr(params, 'enable_rebalancing') and params.enable_rebalancing:
            from .rebalancing_service import RebalancingService
            rebalancing_rec = RebalancingService.analyze_timing(
                symbols=params.symbols,
                target_weights=weights,
                returns_df=returns_df[params.symbols],
                years=params.years,
                drift_threshold=drift_threshold,
                transaction_cost_pct=transaction_cost_pct,
                mu=mu,
                sigma=sigma,
                max_rebalances_per_year=max_rebalances_per_year
            )
            rebalancing_dates = rebalancing_rec.rebalance_dates if rebalancing_rec else None
        
        return SimulationResults(
            paths=paths,
            time_points=time_points,
            percentiles=percentiles,
            final_values=final_values,
            var_95=var_95,
            cvar_95=cvar_95,
            max_drawdown_median=max_drawdown_median,
            cagr_median=cagr_median,
            cagr_10th=cagr_10th,
            cagr_90th=cagr_90th,
            historical_sharpe=historical_sharpe,
            historical_volatility=sigma,
            rebalancing_dates=rebalancing_dates
        )
    
    @staticmethod
    def calculate_total_returns(
        prices: pd.Series, 
        dividends: list,
        start_date: datetime, 
        end_date: datetime
    ) -> pd.Series:
        """
        Calculate total returns including dividends.
        
        Args:
            prices: Price series
            dividends: List of dividend dicts with 'ex_date' and 'amount'
            start_date: Start date for calculation
            end_date: End date for calculation
            
        Returns:
            Series of total returns including dividend yields
        """
        # Price returns
        returns = prices.pct_change()
        
        # Add dividend yields on ex-dates
        for div in dividends:
            ex_date = pd.to_datetime(div['ex_date'])
            if start_date <= ex_date <= end_date:
                # Find closest price date
                closest_idx = prices.index.get_indexer([ex_date], method='nearest')[0]
                if closest_idx < len(returns):
                    price = prices.iloc[closest_idx]
                    div_yield = div['amount'] / price if price > 0 else 0
                    returns.iloc[closest_idx] += div_yield
        
        return returns
    
    def _fetch_returns(self, params: SimulationParameters) -> pd.DataFrame:
        """
        Fetch historical returns using repository.
        
        Args:
            params: Simulation parameters with symbols
            
        Returns:
            DataFrame with returns for each symbol
        """
        end = datetime.now()
        start = end - timedelta(days=365 * 5)  # 5 years of history
        
        returns_dict = {}
        for symbol in params.symbols:
            returns = self.price_data_repository.get_returns(symbol, start, end)
            returns_dict[symbol] = returns
        
        return pd.DataFrame(returns_dict)
