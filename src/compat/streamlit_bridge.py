"""
Streamlit Service Bridge

Translates between widget dict-based parameters and domain model dataclasses.
Enables gradual migration from old widget implementation to new service layer.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime

from ..domain.simulation import SimulationParameters, SimulationResults
from ..domain.optimization import OptimizationRequest, OptimizationResults
from ..domain.rebalancing import RebalancingRecommendation
from ..domain.news import SurpriseEvent, EventNewsCorrelation
from ..services.monte_carlo_service import MonteCarloService
from ..services.optimization_service import OptimizationService
from ..services.rebalancing_service import RebalancingService
from ..services.news_analysis_service import NewsAnalysisService
from ..repositories.price_data_repository import PriceDataRepository
from ..storage.adapter import DataStorageAdapter


class StreamlitServiceBridge:
    """
    Compatibility bridge between Streamlit widgets and new service layer.
    
    Converts widget dict-based parameters to domain models, calls services,
    and converts results back to dicts for widget consumption.
    """
    
    def __init__(self, storage_adapter: Optional[DataStorageAdapter] = None):
        """
        Initialize bridge with optional storage adapter.
        
        Args:
            storage_adapter: Storage adapter for data access (optional)
        """
        self.storage_adapter = storage_adapter or DataStorageAdapter()
        self.price_repo = PriceDataRepository(self.storage_adapter)
        
        # Initialize services with repository dependency injection
        self.monte_carlo_service = MonteCarloService(price_data_repository=self.price_repo)
        self.optimization_service = OptimizationService(price_data_repository=self.price_repo)
        self.rebalancing_service = RebalancingService(price_data_repository=self.price_repo)
        self.news_service = NewsAnalysisService()
    
    def run_monte_carlo_compat(
        self,
        symbols: List[str],
        weights: np.ndarray,
        returns_df: pd.DataFrame,
        num_sims: int,
        years: int,
        initial_value: float,
        include_dividends: bool,
        confidence_level: int,
        estimation_method: str = "Historical Mean",
        enable_contributions: bool = False,
        contribution_amount: float = 0,
        contribution_frequency: str = "Annual",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation with widget-compatible interface.
        
        Converts widget parameters to SimulationParameters, calls MonteCarloService,
        and converts SimulationResults back to dict format.
        
        Args:
            symbols: List of instrument symbols
            weights: Portfolio weights (must sum to 1)
            returns_df: Historical returns DataFrame
            num_sims: Number of simulations to run
            years: Time horizon in years
            initial_value: Starting portfolio value
            include_dividends: Whether dividends are included
            confidence_level: Confidence level for percentiles
            estimation_method: Method for parameter estimation
            enable_contributions: Whether to include periodic contributions
            contribution_amount: Amount of periodic contribution
            contribution_frequency: Frequency of contributions
            **kwargs: Additional parameters
            
        Returns:
            Dict with simulation results (compatible with widget expectations)
        """
        # Convert widget parameters to domain model
        params = SimulationParameters(
            symbols=symbols,
            weights=weights.tolist() if isinstance(weights, np.ndarray) else weights,
            num_simulations=num_sims,
            years=years,
            initial_investment=initial_value,
            confidence_level=confidence_level,
            include_dividends=include_dividends,
            estimation_method=estimation_method,
            enable_contributions=enable_contributions,
            contribution_amount=contribution_amount,
            contribution_frequency=contribution_frequency
        )
        
        # Call service layer
        results = self.monte_carlo_service.run_simulation(
            params=params,
            returns_df=returns_df
        )
        
        # Convert domain model back to dict for widget
        return self._simulation_results_to_dict(results)
    
    def run_optimization_compat(
        self,
        returns_df: pd.DataFrame,
        objective: str = "max_sharpe",
        risk_free_rate: float = 0.04,
        constraints: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run portfolio optimization with widget-compatible interface.
        
        Args:
            returns_df: Historical returns DataFrame
            objective: Optimization objective ("max_sharpe" or "min_volatility")
            risk_free_rate: Risk-free rate for Sharpe calculation
            constraints: Optional constraints dict
            **kwargs: Additional parameters
            
        Returns:
            Dict with optimization results (compatible with widget expectations)
        """
        symbols = returns_df.columns.tolist()
        
        # Convert widget parameters to domain model
        request = OptimizationRequest(
            symbols=symbols,
            objective=objective,
            risk_free_rate=risk_free_rate,
            constraints=constraints or {}
        )
        
        # Call service layer
        if objective == "max_sharpe":
            results = self.optimization_service.maximize_sharpe(
                request=request,
                returns_df=returns_df
            )
        elif objective == "min_volatility":
            results = self.optimization_service.minimize_volatility(
                request=request,
                returns_df=returns_df
            )
        else:
            raise ValueError(f"Unknown objective: {objective}")
        
        # Convert domain model back to dict for widget
        return self._optimization_results_to_dict(results)
    
    def calculate_efficient_frontier_compat(
        self,
        returns_df: pd.DataFrame,
        risk_free_rate: float = 0.04,
        num_points: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate efficient frontier with widget-compatible interface.
        
        Args:
            returns_df: Historical returns DataFrame
            risk_free_rate: Risk-free rate for Sharpe calculation
            num_points: Number of frontier points to calculate
            **kwargs: Additional parameters
            
        Returns:
            Dict with efficient frontier points
        """
        symbols = returns_df.columns.tolist()
        
        request = OptimizationRequest(
            symbols=symbols,
            objective="efficient_frontier",
            risk_free_rate=risk_free_rate
        )
        
        # Call service layer
        results = self.optimization_service.calculate_efficient_frontier(
            request=request,
            returns_df=returns_df,
            num_points=num_points
        )
        
        # Convert to dict format
        return {
            "frontier_points": [
                {
                    "return": point.expected_return,
                    "volatility": point.volatility,
                    "sharpe_ratio": point.sharpe_ratio,
                    "weights": point.weights
                }
                for point in results.efficient_frontier
            ],
            "min_volatility_point": {
                "return": results.expected_return,
                "volatility": results.volatility,
                "weights": results.optimal_weights
            } if results.optimal_weights else None
        }
    
    def analyze_rebalancing_compat(
        self,
        returns_df: pd.DataFrame,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        drift_threshold: float = 0.05,
        transaction_cost: float = 0.001,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze rebalancing timing with widget-compatible interface.
        
        Args:
            returns_df: Historical returns DataFrame
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            drift_threshold: Drift threshold for rebalancing
            transaction_cost: Transaction cost percentage
            **kwargs: Additional parameters
            
        Returns:
            Dict with rebalancing recommendations
        """
        # Call service layer
        recommendation = self.rebalancing_service.analyze_timing(
            current_weights=current_weights,
            target_weights=target_weights,
            drift_threshold=drift_threshold,
            transaction_cost=transaction_cost,
            returns_df=returns_df
        )
        
        # Convert domain model back to dict for widget
        return self._rebalancing_results_to_dict(recommendation)
    
    def detect_surprise_events_compat(
        self,
        price_data: pd.DataFrame,
        threshold: float = 2.0,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Detect surprise events with widget-compatible interface.
        
        Args:
            price_data: Price history DataFrame
            threshold: Standard deviation threshold for event detection
            **kwargs: Additional parameters
            
        Returns:
            List of event dicts (compatible with widget expectations)
        """
        # Call service layer
        events = self.news_service.detect_surprise_events(
            price_data=price_data,
            threshold=threshold
        )
        
        # Convert domain models to dicts
        return [self._surprise_event_to_dict(event) for event in events]
    
    def correlate_with_news_compat(
        self,
        events: List[Dict[str, Any]],
        news_data: List[Dict],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Correlate events with news with widget-compatible interface.
        
        Args:
            events: List of surprise event dicts
            news_data: List of news article dicts
            **kwargs: Additional parameters
            
        Returns:
            List of correlation dicts
        """
        # Convert dicts to domain models
        event_models = [
            SurpriseEvent(
                date=event['date'],
                event_type=event['event_type'],
                magnitude=event['magnitude'],
                statistical_significance=event.get('statistical_significance', 0.0),
                description=event.get('description', '')
            )
            for event in events
        ]
        
        # Call service layer
        correlations = self.news_service.correlate_with_news(
            events=event_models,
            news_data=news_data
        )
        
        # Convert domain models to dicts
        return [self._news_correlation_to_dict(corr) for corr in correlations]
    
    # Helper methods for domain model <-> dict conversion
    
    def _simulation_results_to_dict(self, results: SimulationResults) -> Dict[str, Any]:
        """Convert SimulationResults domain model to dict."""
        return {
            "paths": results.paths,
            "time_points": results.time_points,
            "percentiles": results.percentiles,
            "final_values": results.final_values,
            "risk_metrics": {
                "var_95": results.var_95,
                "cvar_95": results.cvar_95,
                "max_drawdown_median": results.max_drawdown_median,
                "cagr_median": results.cagr_median,
                "cagr_5th": results.cagr_5th,
                "cagr_95th": results.cagr_95th,
                "historical_sharpe": results.historical_sharpe,
                "historical_volatility": results.historical_volatility
            },
            "median_outcome": results.median_outcome,
            "best_case": results.best_case,
            "worst_case": results.worst_case
        }
    
    def _optimization_results_to_dict(self, results: OptimizationResults) -> Dict[str, Any]:
        """Convert OptimizationResults domain model to dict."""
        return {
            "optimal_weights": results.optimal_weights,
            "expected_return": results.expected_return,
            "volatility": results.volatility,
            "sharpe_ratio": results.sharpe_ratio,
            "efficient_frontier": [
                {
                    "return": point.expected_return,
                    "volatility": point.volatility,
                    "sharpe_ratio": point.sharpe_ratio,
                    "weights": point.weights
                }
                for point in (results.efficient_frontier or [])
            ]
        }
    
    def _rebalancing_results_to_dict(self, recommendation: RebalancingRecommendation) -> Dict[str, Any]:
        """Convert RebalancingRecommendation domain model to dict."""
        return {
            "rebalance_dates": recommendation.rebalance_dates,
            "drift_at_rebalance": recommendation.drift_at_rebalance,
            "trigger_threshold": recommendation.trigger_threshold,
            "avg_drift": recommendation.avg_drift,
            "cost_benefit_ratio": recommendation.cost_benefit_ratio,
            "sharpe_improvement": recommendation.sharpe_improvement,
            "instruments_to_rebalance": recommendation.instruments_to_rebalance
        }
    
    def _surprise_event_to_dict(self, event: SurpriseEvent) -> Dict[str, Any]:
        """Convert SurpriseEvent domain model to dict."""
        return {
            "date": event.date,
            "event_type": event.event_type,
            "magnitude": event.magnitude,
            "statistical_significance": event.statistical_significance,
            "description": event.description
        }
    
    def _news_correlation_to_dict(self, correlation: EventNewsCorrelation) -> Dict[str, Any]:
        """Convert EventNewsCorrelation domain model to dict."""
        return {
            "event": self._surprise_event_to_dict(correlation.event),
            "correlated_news": correlation.correlated_news,
            "correlation_score": correlation.correlation_score,
            "time_delta_hours": correlation.time_delta_hours
        }
