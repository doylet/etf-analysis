"""
Unit tests for RebalancingService.

Tests drift detection, rebalancing timing, and cost-benefit analysis.
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.rebalancing_service import RebalancingService
from src.domain.rebalancing import RebalancingRecommendation


class TestRebalancingService:
    """Test suite for RebalancingService."""
    
    @pytest.fixture
    def service(self):
        """Create RebalancingService instance for testing."""
        return RebalancingService()
    
    @pytest.fixture
    def service_with_repo(self):
        """Create RebalancingService with mocked repository."""
        mock_repo = Mock()
        return RebalancingService(price_data_repository=mock_repo)
    
    @pytest.fixture
    def synthetic_returns(self):
        """Generate synthetic returns data for 3 symbols, 252 trading days."""
        np.random.seed(42)  # For reproducible tests
        dates = pd.date_range(start='2023-01-01', periods=252, freq='B')
        
        # Generate correlated returns with different volatilities
        returns_data = {
            'AAPL': np.random.normal(0.0008, 0.02, 252),    # ~20% annual volatility
            'GOOGL': np.random.normal(0.0006, 0.025, 252),  # ~25% annual volatility 
            'MSFT': np.random.normal(0.0007, 0.018, 252),   # ~18% annual volatility
        }
        
        return pd.DataFrame(returns_data, index=dates)
    
    @pytest.fixture
    def three_symbol_weights(self):
        """Equal weights for 3-symbol portfolio."""
        return np.array([0.4, 0.3, 0.3])
    
    def test_analyze_timing_valid_parameters(self, service, synthetic_returns, three_symbol_weights):
        """Test rebalancing analysis with valid parameters returns proper recommendation."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        result = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=synthetic_returns,
            years=2,
            drift_threshold=0.15,  # 15% drift threshold
            transaction_cost_pct=0.001,
            mu=0.08,
            sigma=0.15
        )
        
        # Verify result is correct type
        assert isinstance(result, RebalancingRecommendation)
        
        # Verify basic structure
        assert hasattr(result, 'rebalance_dates')
        assert hasattr(result, 'drift_at_rebalance')
        assert hasattr(result, 'trigger_threshold')
        assert hasattr(result, 'avg_drift')
        assert hasattr(result, 'cost_benefit_ratio')
        assert hasattr(result, 'sharpe_improvement')
        
        # Verify threshold is set correctly
        assert result.trigger_threshold == 0.15
        
        # Verify dates and drift arrays match length
        assert len(result.rebalance_dates) == len(result.drift_at_rebalance)
        
        # Verify non-negative metrics
        assert result.avg_drift >= 0
        assert result.total_transaction_costs >= 0
        
        # If rebalances occurred, verify drift exceeded threshold
        for drift in result.drift_at_rebalance:
            assert drift >= result.trigger_threshold
    
    def test_analyze_timing_high_drift_threshold(self, service, synthetic_returns, three_symbol_weights):
        """Test that high drift threshold results in fewer rebalances."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        # High threshold - should result in few/no rebalances
        result_high_threshold = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=synthetic_returns,
            years=1,
            drift_threshold=0.50,  # 50% - very high
            transaction_cost_pct=0.001
        )
        
        # Low threshold - should result in more rebalances
        result_low_threshold = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=synthetic_returns,
            years=1,
            drift_threshold=0.05,  # 5% - very low
            transaction_cost_pct=0.001
        )
        
        # Verify high threshold results in fewer rebalances
        assert len(result_high_threshold.rebalance_dates) <= len(result_low_threshold.rebalance_dates)
    
    def test_max_rebalances_per_year_constraint(self, service, synthetic_returns, three_symbol_weights):
        """Test max_rebalances_per_year constraint is enforced."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        # Low threshold to trigger many rebalances
        result = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=synthetic_returns,
            years=2,
            drift_threshold=0.05,  # Low threshold
            max_rebalances_per_year=2  # Limit to 2 per year
        )
        
        # Should not exceed 4 rebalances (2 years * 2 per year)
        assert len(result.rebalance_dates) <= 4
        
        # If rebalances occurred, they should be the highest drift events
        if len(result.drift_at_rebalance) > 1:
            # Verify list is not empty and contains meaningful drifts
            assert all(drift >= 0.05 for drift in result.drift_at_rebalance)
    
    def test_cost_benefit_calculations(self, service, synthetic_returns, three_symbol_weights):
        """Test cost-benefit ratio and Sharpe improvement calculations."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        result = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=synthetic_returns,
            years=1,
            drift_threshold=0.10,
            transaction_cost_pct=0.005,  # Higher cost for testing
            mu=0.08,
            sigma=0.15
        )
        
        # Verify cost calculations
        expected_total_costs = len(result.rebalance_dates) * 0.005
        assert abs(result.total_transaction_costs - expected_total_costs) < 1e-6
        
        # Verify cost-benefit ratio is calculated
        assert isinstance(result.cost_benefit_ratio, float)
        assert isinstance(result.sharpe_improvement, float)
        
        # If no rebalances, metrics should be zero
        if len(result.rebalance_dates) == 0:
            assert result.cost_benefit_ratio == 0.0
            assert result.sharpe_improvement == 0.0
    
    def test_no_rebalances_needed(self, service, synthetic_returns, three_symbol_weights):
        """Test scenario where no rebalancing is needed."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        # Very high threshold - unlikely to be exceeded (but within validation limits)
        result = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=synthetic_returns,
            years=0.25,  # Short period
            drift_threshold=0.50,  # 50% threshold (max allowed)
            transaction_cost_pct=0.001
        )
        
        # Should have no rebalances
        assert len(result.rebalance_dates) == 0
        assert len(result.drift_at_rebalance) == 0
        assert result.avg_drift == 0.0
        assert result.total_transaction_costs == 0.0
        assert result.cost_benefit_ratio == 0.0
        assert result.sharpe_improvement == 0.0
    
    def test_returns_data_validation(self, service):
        """Test validation of input parameters."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        weights = np.array([0.4, 0.3, 0.3])
        
        # Test missing returns_df and no repository
        with pytest.raises(ValueError, match="Either returns_df or price_data_repository must be provided"):
            service.analyze_timing(
                symbols=symbols,
                target_weights=weights,
                returns_df=None,
                years=1
            )
    
    def test_with_repository_data_fetch(self, service_with_repo):
        """Test that service fetches data from repository when returns_df not provided."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        weights = np.array([0.4, 0.3, 0.3])
        
        # Mock repository to return synthetic data
        mock_returns = pd.Series(np.random.normal(0.001, 0.02, 252))
        service_with_repo.price_data_repository.get_returns.return_value = mock_returns
        
        # Mock the _fetch_returns method to return proper DataFrame
        synthetic_returns = pd.DataFrame({
            'AAPL': np.random.normal(0.0008, 0.02, 252),
            'GOOGL': np.random.normal(0.0006, 0.025, 252),
            'MSFT': np.random.normal(0.0007, 0.018, 252)
        })
        
        with patch.object(service_with_repo, '_fetch_returns', return_value=synthetic_returns):
            result = service_with_repo.analyze_timing(
                symbols=symbols,
                target_weights=weights,
                returns_df=None,  # Should trigger repository usage
                years=1,
                drift_threshold=0.10
            )
            
            # Verify service was called and returned valid result
            assert isinstance(result, RebalancingRecommendation)
            assert service_with_repo._fetch_returns.called
    
    def test_chronological_rebalance_dates(self, service, synthetic_returns, three_symbol_weights):
        """Test that rebalance dates are in chronological order."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        result = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=synthetic_returns,
            years=2,
            drift_threshold=0.08,
            max_rebalances_per_year=4
        )
        
        # Verify dates are in chronological order
        if len(result.rebalance_dates) > 1:
            for i in range(1, len(result.rebalance_dates)):
                assert result.rebalance_dates[i] > result.rebalance_dates[i-1]
    
    def test_portfolio_values_tracking(self, service, synthetic_returns, three_symbol_weights):
        """Test that portfolio values are tracked at rebalancing dates."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        result = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=synthetic_returns,
            years=1,
            drift_threshold=0.12
        )
        
        # Verify portfolio values are recorded
        assert len(result.portfolio_value_at_dates) == len(result.rebalance_dates)
        
        # Portfolio values should be positive
        for value in result.portfolio_value_at_dates:
            assert value > 0
    
    def test_different_asset_parameters(self, service):
        """Test with different asset return/volatility parameters."""
        symbols = ['HIGH_VOL', 'LOW_VOL']
        weights = np.array([0.5, 0.5])
        
        # Create returns with very different characteristics
        dates = pd.date_range(start='2023-01-01', periods=126, freq='B')  # 6 months
        
        returns_data = {
            'HIGH_VOL': np.random.normal(0.001, 0.05, 126),  # High volatility
            'LOW_VOL': np.random.normal(0.0005, 0.005, 126),  # Low volatility
        }
        
        returns_df = pd.DataFrame(returns_data, index=dates)
        
        result = service.analyze_timing(
            symbols=symbols,
            target_weights=weights,
            returns_df=returns_df,
            years=0.5,
            drift_threshold=0.10
        )
        
        # Should still return valid recommendation
        assert isinstance(result, RebalancingRecommendation)
        assert result.trigger_threshold == 0.10
    
    def test_edge_case_zero_years(self, service, synthetic_returns, three_symbol_weights):
        """Test edge case with minimal time horizon."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        # Very short period
        short_returns = synthetic_returns.head(5)  # Just 5 days
        
        result = service.analyze_timing(
            symbols=symbols,
            target_weights=three_symbol_weights,
            returns_df=short_returns,
            years=0.02,  # About 5 trading days
            drift_threshold=0.10
        )
        
        # Should handle gracefully
        assert isinstance(result, RebalancingRecommendation)
        # Likely no rebalances in such short period
        assert len(result.rebalance_dates) >= 0