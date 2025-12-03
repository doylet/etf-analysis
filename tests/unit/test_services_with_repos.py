"""
Unit tests for services with mocked repositories.

Tests T043: Verify dependency injection pattern works with mocked repositories.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from src.services.monte_carlo_service import MonteCarloService
from src.services.optimization_service import OptimizationService
from src.services.rebalancing_service import RebalancingService
from src.domain.simulation import SimulationParameters
from src.domain.optimization import OptimizationRequest, OptimizationObjective


@pytest.fixture
def mock_price_repo():
    """Create mock PriceDataRepository."""
    repo = Mock()
    
    # Mock get_returns to return sample returns data
    def mock_get_returns(symbol, start, end):
        # Generate 252 days of random returns
        dates = pd.date_range(start=start, periods=252, freq='D')
        returns = pd.Series(
            np.random.normal(0.0008, 0.02, 252),
            index=dates,
            name=symbol
        )
        return returns
    
    repo.get_returns = Mock(side_effect=mock_get_returns)
    return repo


@pytest.fixture
def sample_returns_df():
    """Create sample returns DataFrame for direct data passing."""
    dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
    data = {
        'VTI': np.random.normal(0.0008, 0.02, 252),
        'BND': np.random.normal(0.0003, 0.01, 252),
        'VEA': np.random.normal(0.0006, 0.025, 252)
    }
    return pd.DataFrame(data, index=dates)


# T043: Service Unit Tests with Mocked Repositories

class TestMonteCarloServiceWithMocks:
    """Test MonteCarloService with mocked repository."""
    
    def test_service_with_repository(self, mock_price_repo):
        """Test service works with injected repository."""
        service = MonteCarloService(price_data_repository=mock_price_repo)
        
        params = SimulationParameters(
            symbols=['VTI', 'BND'],
            weights=[0.6, 0.4],
            initial_investment=10000,
            years=10,
            num_simulations=100
        )
        
        # Should fetch returns from repository
        results = service.run_simulation(params)
        
        assert results is not None
        assert results.median_outcome > 0
        assert len(results.percentiles) > 0
        assert mock_price_repo.get_returns.called
        assert mock_price_repo.get_returns.call_count == 2  # Called for each symbol
    
    def test_service_without_repository(self, sample_returns_df):
        """Test service works with direct data passing (backward compatibility)."""
        service = MonteCarloService()  # No repository
        
        params = SimulationParameters(
            symbols=['VTI', 'BND'],
            weights=[0.6, 0.4],
            initial_investment=10000,
            years=10,
            num_simulations=100
        )
        
        # Pass returns directly
        results = service.run_simulation(params, returns_df=sample_returns_df)
        
        assert results is not None
        assert results.median_outcome > 0
        assert len(results.percentiles) > 0
    
    def test_service_raises_without_data_or_repo(self):
        """Test service raises error when neither data nor repository provided."""
        service = MonteCarloService()  # No repository
        
        params = SimulationParameters(
            symbols=['VTI', 'BND'],
            weights=[0.6, 0.4],
            initial_investment=10000,
            years=10,
            num_simulations=100
        )
        
        with pytest.raises(ValueError, match="Either returns_df or price_data_repository"):
            service.run_simulation(params)  # No returns_df either


class TestOptimizationServiceWithMocks:
    """Test OptimizationService with mocked repository."""
    
    def test_service_with_repository(self, mock_price_repo):
        """Test optimization service with injected repository."""
        service = OptimizationService(price_data_repository=mock_price_repo)
        
        request = OptimizationRequest(
            symbols=['VTI', 'BND', 'VEA'],
            objective=OptimizationObjective.MAX_SHARPE,
            risk_free_rate=0.04
        )
        
        # Should fetch returns from repository
        results = service.optimize(request)
        
        assert results is not None
        assert len(results.optimal_weights) == 3
        assert abs(sum(results.optimal_weights) - 1.0) < 0.01  # Weights sum to 1
        assert results.sharpe_ratio > 0
        assert mock_price_repo.get_returns.called
        assert mock_price_repo.get_returns.call_count == 3  # Called for each symbol
    
    def test_service_without_repository(self, sample_returns_df):
        """Test optimization with direct data passing."""
        service = OptimizationService()  # No repository
        
        request = OptimizationRequest(
            symbols=['VTI', 'BND', 'VEA'],
            objective=OptimizationObjective.MAX_SHARPE,
            risk_free_rate=0.04
        )
        
        # Pass returns directly
        results = service.optimize(request, returns_df=sample_returns_df)
        
        assert results is not None
        assert len(results.optimal_weights) == 3
        assert abs(sum(results.optimal_weights) - 1.0) < 0.01
    
    def test_min_volatility_optimization(self, sample_returns_df):
        """Test minimum volatility optimization."""
        service = OptimizationService()
        
        request = OptimizationRequest(
            symbols=['VTI', 'BND', 'VEA'],
            objective=OptimizationObjective.MIN_VOLATILITY,
            risk_free_rate=0.04
        )
        
        results = service.optimize(request, returns_df=sample_returns_df)
        
        assert results is not None
        assert results.volatility > 0
        assert len(results.optimal_weights) == 3
    
    def test_service_raises_without_data_or_repo(self):
        """Test service raises error when neither data nor repository provided."""
        service = OptimizationService()
        
        request = OptimizationRequest(
            symbols=['VTI', 'BND'],
            objective=OptimizationObjective.MAX_SHARPE,
            risk_free_rate=0.04
        )
        
        with pytest.raises(ValueError, match="Either returns_df or price_data_repository"):
            service.optimize(request)


class TestRebalancingServiceWithMocks:
    """Test RebalancingService with mocked repository."""
    
    def test_service_with_repository(self, mock_price_repo):
        """Test rebalancing service with injected repository."""
        service = RebalancingService(price_data_repository=mock_price_repo)
        
        symbols = ['VTI', 'BND']
        target_weights = np.array([0.6, 0.4])
        
        # Should fetch returns from repository
        results = service.analyze_timing(
            symbols=symbols,
            target_weights=target_weights,
            years=5,
            drift_threshold=0.10,
            transaction_cost_pct=0.001,
            mu=0.08,
            sigma=0.15
        )
        
        assert results is not None
        assert results.trigger_threshold == 0.10
        assert isinstance(results.rebalance_dates, list)
        assert mock_price_repo.get_returns.called
    
    def test_service_without_repository(self, sample_returns_df):
        """Test rebalancing with direct data passing."""
        service = RebalancingService()  # No repository
        
        symbols = ['VTI', 'BND']
        target_weights = np.array([0.6, 0.4])
        
        # Pass returns directly
        results = service.analyze_timing(
            symbols=symbols,
            target_weights=target_weights,
            returns_df=sample_returns_df,
            years=5,
            drift_threshold=0.10,
            transaction_cost_pct=0.001,
            mu=0.08,
            sigma=0.15
        )
        
        assert results is not None
        assert results.trigger_threshold == 0.10
        assert isinstance(results.rebalance_dates, list)
    
    def test_service_raises_without_data_or_repo(self):
        """Test service raises error when neither data nor repository provided."""
        service = RebalancingService()
        
        with pytest.raises(ValueError, match="Either returns_df or price_data_repository"):
            service.analyze_timing(
                symbols=['VTI', 'BND'],
                target_weights=np.array([0.6, 0.4])
            )


class TestDependencyInjectionPattern:
    """Test the dependency injection pattern itself."""
    
    def test_services_accept_none_repository(self):
        """Test services can be instantiated without repository."""
        mc_service = MonteCarloService()
        opt_service = OptimizationService()
        reb_service = RebalancingService()
        
        assert mc_service.price_data_repository is None
        assert opt_service.price_data_repository is None
        assert reb_service.price_data_repository is None
    
    def test_services_accept_repository(self, mock_price_repo):
        """Test services can be instantiated with repository."""
        mc_service = MonteCarloService(price_data_repository=mock_price_repo)
        opt_service = OptimizationService(price_data_repository=mock_price_repo)
        reb_service = RebalancingService(price_data_repository=mock_price_repo)
        
        assert mc_service.price_data_repository is mock_price_repo
        assert opt_service.price_data_repository is mock_price_repo
        assert reb_service.price_data_repository is mock_price_repo
    
    def test_repository_methods_not_called_when_data_provided(self, mock_price_repo, sample_returns_df):
        """Test repository not used when data is directly provided."""
        service = MonteCarloService(price_data_repository=mock_price_repo)
        
        params = SimulationParameters(
            symbols=['VTI', 'BND'],
            weights=[0.6, 0.4],
            initial_investment=10000,
            years=10,
            num_simulations=100
        )
        
        # Pass returns directly - repository should not be called
        service.run_simulation(params, returns_df=sample_returns_df)
        
        # Repository should not have been called
        assert not mock_price_repo.get_returns.called


class TestMockVerification:
    """Verify mock behavior matches expected repository interface."""
    
    def test_mock_returns_correct_type(self, mock_price_repo):
        """Test mock repository returns correct data types."""
        start = datetime(2023, 1, 1)
        end = datetime(2023, 12, 31)
        
        returns = mock_price_repo.get_returns('VTI', start, end)
        
        assert isinstance(returns, pd.Series)
        assert len(returns) > 0
        assert returns.name == 'VTI'
    
    def test_mock_can_be_called_multiple_times(self, mock_price_repo):
        """Test mock repository can handle multiple calls."""
        start = datetime(2023, 1, 1)
        end = datetime(2023, 12, 31)
        
        returns1 = mock_price_repo.get_returns('VTI', start, end)
        returns2 = mock_price_repo.get_returns('BND', start, end)
        returns3 = mock_price_repo.get_returns('VEA', start, end)
        
        assert mock_price_repo.get_returns.call_count == 3
        assert returns1.name == 'VTI'
        assert returns2.name == 'BND'
        assert returns3.name == 'VEA'
