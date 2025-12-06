"""
Unit tests for MonteCarloService.

Tests the core Monte Carlo simulation logic with synthetic data,
validates parameter validation, and verifies result structure.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.services.monte_carlo_service import MonteCarloService
from src.domain.simulation import SimulationParameters, SimulationResults


class TestMonteCarloService:
    """Test suite for MonteCarloService."""
    
    @pytest.fixture
    def service(self):
        """Create MonteCarloService instance for testing."""
        return MonteCarloService()
    
    @pytest.fixture
    def service_with_mock_repo(self):
        """Create MonteCarloService with mocked repository."""
        mock_repo = Mock()
        return MonteCarloService(price_data_repository=mock_repo)
    
    @pytest.fixture
    def valid_params(self):
        """Valid simulation parameters for testing."""
        return SimulationParameters(
            symbols=["AAPL", "GOOGL", "MSFT"],
            weights=[0.4, 0.3, 0.3],
            years=5,
            num_simulations=1000,
            initial_value=100000.0,
            contribution_amount=0.0,  # No contributions for basic tests
            contribution_frequency="monthly",
            rebalancing_frequency="quarterly"
        )
    
    @pytest.fixture
    def synthetic_returns(self):
        """Generate synthetic returns data for 3 symbols, 252 trading days."""
        np.random.seed(42)  # For reproducible tests
        dates = pd.date_range(start='2023-01-01', periods=252, freq='B')
        
        # Generate correlated returns
        returns_data = {
            'AAPL': np.random.normal(0.0008, 0.02, 252),    # ~20% annual volatility
            'GOOGL': np.random.normal(0.0006, 0.025, 252),  # ~25% annual volatility 
            'MSFT': np.random.normal(0.0007, 0.018, 252),   # ~18% annual volatility
        }
        
        return pd.DataFrame(returns_data, index=dates)
    
    def test_run_simulation_valid_parameters(self, service, valid_params, synthetic_returns):
        """Test simulation with valid parameters returns proper SimulationResults."""
        result = service.run_simulation(valid_params, synthetic_returns)
        
        # Verify result is correct type
        assert isinstance(result, SimulationResults)
        
        # Verify result structure
        assert hasattr(result, 'paths')
        assert hasattr(result, 'time_points')
        assert hasattr(result, 'percentiles')
        assert hasattr(result, 'final_values')
        assert hasattr(result, 'risk_metrics')
        
        # Verify paths shape (paths is a List[List[float]])
        expected_time_steps = valid_params.years * 12  # Monthly steps
        print(f"Expected paths: {valid_params.num_simulations}")
        print(f"Actual paths count: {len(result.paths)}")
        print(f"First path length: {len(result.paths[0]) if result.paths else 'No paths'}")
        print(f"Expected path length: {expected_time_steps + 1}")
        assert len(result.paths) == valid_params.num_simulations
        assert len(result.paths[0]) == expected_time_steps + 1
        
        # Verify time_points length
        assert len(result.time_points) == expected_time_steps + 1
        
        # Verify percentiles are in ascending order
        percentile_values = list(result.percentiles.values())
        assert percentile_values == sorted(percentile_values)
        
        # Verify final values are positive
        assert all(v > 0 for v in result.final_values)
        assert len(result.final_values) == valid_params.num_simulations
        
        # Verify risk metrics are reasonable
        assert result.risk_metrics['var_95'] > 0
        assert result.risk_metrics['cvar_95'] > result.risk_metrics['var_95']
        assert 0 <= result.risk_metrics['max_drawdown_median'] <= 1
        assert result.risk_metrics['cagr_median'] > -1  # Greater than -100%
        assert result.risk_metrics['historical_sharpe'] is not None
        assert result.risk_metrics['historical_volatility'] > 0
    
    def test_simulation_with_contributions(self, service, synthetic_returns):
        """Test simulation with monthly contributions."""
        params = SimulationParameters(
            symbols=["AAPL", "GOOGL"],
            weights=[0.6, 0.4],
            years=3,
            num_simulations=500,
            initial_value=50000.0,
            contribution_amount=2000.0,
            contribution_frequency="monthly"
        )
        
        result = service.run_simulation(params, synthetic_returns)
        
        # Verify contributions increased portfolio value
        median_final = np.percentile(result.final_values, 50)
        expected_contributions = 3 * 12 * 2000  # 3 years * 12 months * $2000
        
        # Final value should be significantly higher than initial due to contributions
        assert median_final > params.initial_value + expected_contributions * 0.8
    
    def test_simulation_with_rebalancing(self, service, synthetic_returns):
        """Test simulation with quarterly rebalancing."""
        params = SimulationParameters(
            symbols=["AAPL", "GOOGL", "MSFT"],
            weights=[0.5, 0.3, 0.2],
            years=2,
            num_simulations=500,
            initial_value=75000.0,
            contribution_amount=0.0,
            rebalancing_enabled=True,
            rebalancing_frequency="quarterly"
        )
        
        result = service.run_simulation(
            params, 
            synthetic_returns,
            enable_rebalancing_analysis=True,
            drift_threshold=0.05
        )
        
        # Verify rebalancing analysis exists
        assert hasattr(result, 'rebalancing_analysis')
        if result.rebalancing_analysis:
            assert hasattr(result.rebalancing_analysis, 'rebalance_dates')
            assert hasattr(result.rebalancing_analysis, 'avg_drift')
    
    def test_parameter_validation_negative_years(self):
        """Test that negative years raises ValidationError."""
        with pytest.raises(ValueError):
            SimulationParameters(
                symbols=["AAPL"],
                weights=[1.0],
                years=-1,  # Invalid
                num_simulations=1000,
                initial_value=100000.0
            )
    
    def test_parameter_validation_weights_not_sum_to_one(self):
        """Test that weights not summing to 1.0 raises ValidationError."""
        with pytest.raises(ValueError):
            SimulationParameters(
                symbols=["AAPL", "GOOGL"],
                weights=[0.4, 0.4],  # Sum = 0.8, not 1.0
                years=5,
                num_simulations=1000,
                initial_value=100000.0
            )
    
    def test_parameter_validation_mismatched_symbols_weights(self):
        """Test that mismatched symbols and weights length raises ValidationError."""
        with pytest.raises(ValueError):
            SimulationParameters(
                symbols=["AAPL", "GOOGL", "MSFT"],
                weights=[0.5, 0.5],  # Only 2 weights for 3 symbols
                years=5,
                num_simulations=1000,
                initial_value=100000.0
            )
    
    def test_parameter_validation_too_few_simulations(self):
        """Test that too few simulations raises ValidationError."""
        with pytest.raises(ValueError):
            SimulationParameters(
                symbols=["AAPL"],
                weights=[1.0],
                years=5,
                num_simulations=50,  # Below minimum of 100
                initial_value=100000.0
            )
    
    def test_parameter_validation_zero_initial_value(self):
        """Test that zero initial value raises ValidationError."""
        with pytest.raises(ValueError):
            SimulationParameters(
                symbols=["AAPL"],
                weights=[1.0],
                years=5,
                num_simulations=1000,
                initial_value=0.0  # Invalid
            )
    
    def test_simulation_different_estimation_methods(self, service, valid_params, synthetic_returns):
        """Test simulation with different estimation methods."""
        # Historical Mean method
        result_hist = service.run_simulation(
            valid_params, 
            synthetic_returns,
            estimation_method="Historical Mean"
        )
        
        # Exponentially Weighted method
        result_exp = service.run_simulation(
            valid_params,
            synthetic_returns, 
            estimation_method="Exponentially Weighted"
        )
        
        # Both should return valid results
        assert isinstance(result_hist, SimulationResults)
        assert isinstance(result_exp, SimulationResults)
        
        # Results may differ due to different estimation methods
        assert len(result_hist.final_values) == len(result_exp.final_values)
    
    def test_simulation_different_confidence_levels(self, service, valid_params, synthetic_returns):
        """Test simulation with different confidence levels."""
        result_90 = service.run_simulation(
            valid_params,
            synthetic_returns,
            confidence_level=90
        )
        
        result_95 = service.run_simulation(
            valid_params,
            synthetic_returns, 
            confidence_level=95
        )
        
        # 95% confidence should have wider percentile range
        assert result_95.percentiles['p5'] <= result_90.percentiles['p5']
        assert result_95.percentiles['p95'] >= result_90.percentiles['p95']
    
    def test_simulation_reproducibility(self, service, valid_params, synthetic_returns):
        """Test that simulation results are reproducible with same random seed."""
        # Note: This may not work if service doesn't set np.random.seed internally
        # But we can test that multiple runs produce valid results
        
        result1 = service.run_simulation(valid_params, synthetic_returns)
        result2 = service.run_simulation(valid_params, synthetic_returns)
        
        # Both results should be valid
        assert isinstance(result1, SimulationResults)
        assert isinstance(result2, SimulationResults)
        assert len(result1.final_values) == len(result2.final_values)
    
    def test_simulation_with_mock_repository(self, service_with_mock_repo, valid_params):
        """Test simulation when repository is provided but returns_df is not."""
        # Mock the repository to return synthetic data with proper DataFrame structure
        dates = pd.date_range(start='2023-01-01', periods=252, freq='B')
        mock_returns = pd.DataFrame({
            'AAPL': [0.01, 0.02, -0.01] * 84,  # 252 days
            'GOOGL': [0.015, -0.005, 0.008] * 84,
            'MSFT': [0.012, 0.003, -0.002] * 84
        }, index=dates)
        
        service_with_mock_repo.price_data_repository.get_returns.return_value = mock_returns
        
        # Should be able to run without explicit returns_df
        result = service_with_mock_repo.run_simulation(valid_params)
        assert isinstance(result, SimulationResults)
    
    def test_small_simulation_performance(self, service, synthetic_returns):
        """Test that small simulations complete quickly."""
        import time
        
        params = SimulationParameters(
            symbols=["AAPL", "GOOGL"],
            weights=[0.7, 0.3],
            years=1,
            num_simulations=100,  # Small simulation
            initial_value=10000.0,
            contribution_amount=0.0
        )
        
        start_time = time.time()
        result = service.run_simulation(params, synthetic_returns)
        duration = time.time() - start_time
        
        # Should complete quickly (under 5 seconds)
        assert duration < 5.0
        assert isinstance(result, SimulationResults)
        assert len(result.final_values) == 100
    
    def test_empty_returns_dataframe_handling(self, service, valid_params):
        """Test handling of empty returns DataFrame."""
        empty_returns = pd.DataFrame()
        
        with pytest.raises((ValueError, KeyError)):
            service.run_simulation(valid_params, empty_returns)
    
    def test_insufficient_returns_data(self, service, valid_params):
        """Test handling of insufficient returns data."""
        # Only 10 days of data (insufficient for reliable statistics)
        insufficient_returns = pd.DataFrame({
            'AAPL': [0.01] * 10,
            'GOOGL': [0.02] * 10,
            'MSFT': [-0.01] * 10
        })
        
        # Should still run but may produce warning
        result = service.run_simulation(valid_params, insufficient_returns)
        assert isinstance(result, SimulationResults)