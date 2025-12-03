"""
Rebalancing analysis service - analyzes optimal portfolio rebalancing timing.

Extracted from src/widgets/monte_carlo_widget.py to be framework-agnostic.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

from ..domain.rebalancing import RebalancingRecommendation


class RebalancingService:
    """Service for analyzing portfolio rebalancing timing and impact."""
    
    def __init__(self, price_data_repository=None):
        """
        Initialize service with optional repository.
        
        Args:
            price_data_repository: Optional PriceDataRepository for fetching data
        """
        self.price_data_repository = price_data_repository
    
    def analyze_timing(
        self,
        symbols: list[str],
        target_weights: np.ndarray,
        returns_df: Optional[pd.DataFrame] = None,
        years: int = 10,
        drift_threshold: float = 0.10,
        transaction_cost_pct: float = 0.001,
        mu: float = 0.08,
        sigma: float = 0.15,
        max_rebalances_per_year: Optional[int] = None
    ) -> RebalancingRecommendation:
        """
        Analyze optimal rebalancing timing based on drift from target weights.
        
        Args:
            symbols: List of instrument symbols
            target_weights: Target portfolio weights (must sum to 1)
            returns_df: Historical returns DataFrame (optional if repository provided)
            years: Simulation horizon
            drift_threshold: Drift threshold to trigger rebalancing (e.g., 0.10 for 10%)
            transaction_cost_pct: Transaction cost per rebalance (% of portfolio)
            mu: Expected portfolio return (annualized)
            sigma: Expected portfolio volatility (annualized)
            max_rebalances_per_year: Maximum rebalances per year (optional constraint)
            
        Returns:
            RebalancingRecommendation with timing and impact analysis
        """
        # Fetch returns if not provided and repository available
        if returns_df is None:
            if self.price_data_repository is None:
                raise ValueError("Either returns_df or price_data_repository must be provided")
            returns_df = self._fetch_returns(symbols)
        
        # Simulate asset paths to predict weight drift
        n_assets = len(symbols)
        dt = 1 / 252
        num_steps = int(years * 252)
        
        # Get individual asset parameters
        asset_returns = returns_df.mean() * 252
        asset_vols = returns_df.std() * np.sqrt(252)
        correlation_matrix = returns_df.corr().values
        
        # Simulate one median scenario for analysis
        np.random.seed(42)
        asset_paths = np.zeros((n_assets, num_steps + 1))
        asset_paths[:, 0] = 1.0  # Start with normalized prices
        
        # Generate correlated random returns
        L = np.linalg.cholesky(correlation_matrix)
        
        for t in range(1, num_steps + 1):
            Z = np.random.standard_normal(n_assets)
            correlated_Z = L @ Z
            
            for i in range(n_assets):
                asset_paths[i, t] = asset_paths[i, t-1] * np.exp(
                    (asset_returns.iloc[i] - 0.5 * asset_vols.iloc[i]**2) * dt + 
                    asset_vols.iloc[i] * np.sqrt(dt) * correlated_Z[i]
                )
        
        # Track weight evolution and rebalancing points
        current_weights = target_weights.copy()
        rebalance_dates = []
        drift_at_rebalance = []
        portfolio_value_at_dates = []
        
        start_date = datetime.now()
        
        for t in range(1, num_steps + 1):
            # Calculate current weights based on asset performance
            portfolio_values = asset_paths[:, t] * current_weights
            total_value = portfolio_values.sum()
            current_weights = portfolio_values / total_value
            
            # Calculate maximum drift from target
            weight_drifts = np.abs(current_weights - target_weights)
            max_drift = weight_drifts.max()
            
            # Check if rebalancing is needed
            if max_drift > drift_threshold:
                days_elapsed = t
                rebalance_date = start_date + timedelta(days=days_elapsed)
                rebalance_dates.append(rebalance_date)
                drift_at_rebalance.append(max_drift)
                portfolio_value_at_dates.append(total_value)
                
                # Rebalance back to target weights
                current_weights = target_weights.copy()
        
        # Apply max rebalances constraint if specified
        if max_rebalances_per_year is not None and len(rebalance_dates) > 0:
            max_allowed = int(max_rebalances_per_year * years)
            if len(rebalance_dates) > max_allowed:
                # Keep only the most important rebalances (highest drift)
                rebalance_info = list(zip(rebalance_dates, drift_at_rebalance, portfolio_value_at_dates))
                # Sort by drift (descending) and take top max_allowed
                rebalance_info_sorted = sorted(rebalance_info, key=lambda x: x[1], reverse=True)[:max_allowed]
                # Sort back by date to maintain chronological order
                rebalance_info_sorted = sorted(rebalance_info_sorted, key=lambda x: x[0])
                
                # Extract filtered lists
                rebalance_dates = [info[0] for info in rebalance_info_sorted]
                drift_at_rebalance = [info[1] for info in rebalance_info_sorted]
                portfolio_value_at_dates = [info[2] for info in rebalance_info_sorted]
        
        # Calculate metrics
        avg_drift = float(np.mean(drift_at_rebalance)) if drift_at_rebalance else 0.0
        max_drift = float(np.max(drift_at_rebalance)) if drift_at_rebalance else 0.0
        num_rebalances = len(rebalance_dates)
        
        # Estimate cost-benefit
        total_transaction_costs = num_rebalances * transaction_cost_pct
        
        if num_rebalances > 0:
            # Benefit: reducing variance from drift (heuristic)
            variance_reduction = avg_drift * 0.5
            sharpe_benefit = variance_reduction * (mu / sigma) if sigma > 0 else 0
            
            # Cost: transaction costs
            cost_drag_on_sharpe = total_transaction_costs / years  # Annualized cost impact
            
            sharpe_improvement = sharpe_benefit - cost_drag_on_sharpe
            cost_benefit_ratio = sharpe_benefit / cost_drag_on_sharpe if cost_drag_on_sharpe > 0 else 0
        else:
            sharpe_improvement = 0.0
            cost_benefit_ratio = 0.0
        
        return RebalancingRecommendation(
            rebalance_dates=rebalance_dates,
            drift_at_rebalance=drift_at_rebalance,
            trigger_threshold=drift_threshold,
            avg_drift=avg_drift,
            max_drift=max_drift,
            cost_benefit_ratio=cost_benefit_ratio,
            sharpe_improvement=sharpe_improvement,
            total_transaction_costs=total_transaction_costs,
            instruments_to_rebalance=[],  # Will be populated by higher-level logic if needed
            portfolio_value_at_dates=portfolio_value_at_dates
        )
    
    def _fetch_returns(self, symbols: list) -> pd.DataFrame:
        """
        Fetch historical returns using repository.
        
        Args:
            symbols: List of symbols
            
        Returns:
            DataFrame with returns for each symbol
        """
        end = datetime.now()
        start = end - timedelta(days=365 * 5)  # 5 years of history
        
        returns_dict = {}
        for symbol in symbols:
            returns = self.price_data_repository.get_returns(symbol, start, end)
            returns_dict[symbol] = returns
        
        return pd.DataFrame(returns_dict)
