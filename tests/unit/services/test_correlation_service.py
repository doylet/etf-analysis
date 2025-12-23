"""
Unit tests for CorrelationService.

These tests demonstrate testing business logic without any UI framework dependencies.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.services.correlation_service import CorrelationService, CorrelationAnalysis


@pytest.fixture
def correlation_service():
    """Create a CorrelationService instance."""
    return CorrelationService()


@pytest.fixture
def sample_returns_data():
    """Create sample returns data for testing."""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    # Create correlated returns for testing
    np.random.seed(42)
    spy_returns = np.random.normal(0.001, 0.02, 100)
    
    # QQQ is highly correlated with SPY
    qqq_returns = spy_returns * 0.8 + np.random.normal(0, 0.01, 100)
    
    # AAPL is moderately correlated
    aapl_returns = spy_returns * 0.5 + np.random.normal(0, 0.015, 100)
    
    # GLD is less correlated (gold)
    gld_returns = np.random.normal(0, 0.015, 100)
    
    return pd.DataFrame({
        'SPY': spy_returns,
        'QQQ': qqq_returns,
        'AAPL': aapl_returns,
        'GLD': gld_returns
    }, index=dates)


class TestCorrelationAnalysis:
    """Test the main correlation analysis calculation."""
    
    def test_calculate_correlation_analysis_basic(self, correlation_service, sample_returns_data):
        """Test basic correlation analysis calculation."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 4, 9)
        
        result = correlation_service.calculate_correlation_analysis(
            returns_df=sample_returns_data,
            selected_holdings=['AAPL'],
            selected_additional=['SPY', 'QQQ'],
            start_date=start_date,
            end_date=end_date
        )
        
        assert isinstance(result, CorrelationAnalysis)
        assert not result.correlation_matrix.empty
        assert not result.pairs_df.empty
        assert result.num_days == 100
        assert result.start_date == start_date
        assert result.end_date == end_date
        assert -1 <= result.avg_correlation <= 1
        assert -1 <= result.max_correlation <= 1
        assert -1 <= result.min_correlation <= 1
    
    def test_correlation_matrix_shape(self, correlation_service, sample_returns_data):
        """Test that correlation matrix has correct shape."""
        result = correlation_service.calculate_correlation_analysis(
            returns_df=sample_returns_data,
            selected_holdings=['AAPL', 'SPY'],
            selected_additional=['QQQ', 'GLD'],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 4, 9)
        )
        
        # Correlation matrix should be 4x4 (all symbols)
        assert result.correlation_matrix.shape == (4, 4)
        
        # Diagonal should be 1.0 (perfect self-correlation)
        for i in range(len(result.correlation_matrix)):
            assert result.correlation_matrix.iloc[i, i] == pytest.approx(1.0)
    
    def test_benchmark_comparison_created(self, correlation_service, sample_returns_data):
        """Test that benchmark comparison pivot is created when both holdings and benchmarks exist."""
        result = correlation_service.calculate_correlation_analysis(
            returns_df=sample_returns_data,
            selected_holdings=['AAPL'],
            selected_additional=['SPY', 'QQQ'],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 4, 9)
        )
        
        assert result.benchmark_pivot is not None
        assert 'AAPL' in result.benchmark_pivot.index
        assert 'SPY' in result.benchmark_pivot.columns
        assert 'QQQ' in result.benchmark_pivot.columns
    
    def test_no_benchmark_comparison_without_holdings(self, correlation_service, sample_returns_data):
        """Test that benchmark comparison is None when no holdings selected."""
        result = correlation_service.calculate_correlation_analysis(
            returns_df=sample_returns_data,
            selected_holdings=[],
            selected_additional=['SPY', 'QQQ'],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 4, 9)
        )
        
        assert result.benchmark_pivot is None
    
    def test_empty_dataframe_raises_error(self, correlation_service):
        """Test that empty dataframe raises ValueError."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Returns dataframe cannot be empty"):
            correlation_service.calculate_correlation_analysis(
                returns_df=empty_df,
                selected_holdings=['AAPL'],
                selected_additional=['SPY'],
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 4, 9)
            )
    
    def test_insufficient_data_raises_error(self, correlation_service):
        """Test that insufficient data points raise ValueError."""
        # Only 1 data point
        single_row_df = pd.DataFrame({
            'AAPL': [0.01],
            'SPY': [0.02]
        })
        
        with pytest.raises(ValueError, match="Need at least 2 data points"):
            correlation_service.calculate_correlation_analysis(
                returns_df=single_row_df,
                selected_holdings=['AAPL'],
                selected_additional=['SPY'],
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 1)
            )


class TestCorrelationPairs:
    """Test correlation pairs extraction."""
    
    def test_calculate_correlation_pairs(self, correlation_service, sample_returns_data):
        """Test that correlation pairs are extracted correctly."""
        corr_matrix = sample_returns_data.corr()
        pairs_df = correlation_service._calculate_correlation_pairs(corr_matrix)
        
        # Should have 6 pairs from 4 symbols: (4 * 3) / 2
        assert len(pairs_df) == 6
        assert 'Pair' in pairs_df.columns
        assert 'Correlation' in pairs_df.columns
        
        # Should be sorted by correlation (descending)
        assert pairs_df['Correlation'].is_monotonic_decreasing
    
    def test_pairs_format(self, correlation_service, sample_returns_data):
        """Test that pair names are formatted correctly."""
        corr_matrix = sample_returns_data.corr()
        pairs_df = correlation_service._calculate_correlation_pairs(corr_matrix)
        
        # Check format of pair names
        for pair_name in pairs_df['Pair']:
            assert ' - ' in pair_name
            parts = pair_name.split(' - ')
            assert len(parts) == 2
    
    def test_empty_matrix_returns_empty_dataframe(self, correlation_service):
        """Test that empty correlation matrix returns empty pairs dataframe."""
        empty_matrix = pd.DataFrame()
        pairs_df = correlation_service._calculate_correlation_pairs(empty_matrix)
        
        assert pairs_df.empty
        assert list(pairs_df.columns) == ['Pair', 'Correlation']


class TestBenchmarkComparison:
    """Test benchmark comparison calculations."""
    
    def test_benchmark_comparison_basic(self, correlation_service, sample_returns_data):
        """Test basic benchmark comparison calculation."""
        corr_matrix = sample_returns_data.corr()
        
        pivot = correlation_service._calculate_benchmark_comparison(
            correlation_matrix=corr_matrix,
            holdings=['AAPL'],
            benchmarks=['SPY', 'QQQ'],
            available_columns=corr_matrix.columns
        )
        
        assert pivot is not None
        assert pivot.shape == (1, 2)  # 1 holding x 2 benchmarks
        assert 'AAPL' in pivot.index
        assert 'SPY' in pivot.columns
        assert 'QQQ' in pivot.columns
    
    def test_multiple_holdings_and_benchmarks(self, correlation_service, sample_returns_data):
        """Test comparison with multiple holdings and benchmarks."""
        corr_matrix = sample_returns_data.corr()
        
        pivot = correlation_service._calculate_benchmark_comparison(
            correlation_matrix=corr_matrix,
            holdings=['AAPL', 'GLD'],
            benchmarks=['SPY', 'QQQ'],
            available_columns=corr_matrix.columns
        )
        
        assert pivot is not None
        assert pivot.shape == (2, 2)  # 2 holdings x 2 benchmarks
    
    def test_missing_symbols_skipped(self, correlation_service, sample_returns_data):
        """Test that missing symbols are gracefully skipped."""
        corr_matrix = sample_returns_data.corr()
        
        pivot = correlation_service._calculate_benchmark_comparison(
            correlation_matrix=corr_matrix,
            holdings=['AAPL', 'MISSING'],
            benchmarks=['SPY', 'ALSO_MISSING'],
            available_columns=corr_matrix.columns
        )
        
        # Should only have AAPL x SPY
        assert pivot is not None
        assert pivot.shape == (1, 1)
    
    def test_no_valid_pairs_returns_none(self, correlation_service, sample_returns_data):
        """Test that no valid pairs returns None."""
        corr_matrix = sample_returns_data.corr()
        
        pivot = correlation_service._calculate_benchmark_comparison(
            correlation_matrix=corr_matrix,
            holdings=['MISSING1'],
            benchmarks=['MISSING2'],
            available_columns=corr_matrix.columns
        )
        
        assert pivot is None


class TestPortfolioAggregateCorrelation:
    """Test portfolio aggregate correlation calculation."""
    
    def test_portfolio_aggregate_correlation_basic(self, correlation_service, sample_returns_data):
        """Test basic portfolio aggregate correlation."""
        result = correlation_service.calculate_portfolio_aggregate_correlation(
            returns_df=sample_returns_data,
            holdings=['AAPL', 'GLD'],
            weights=[0.6, 0.4],
            benchmarks=['SPY', 'QQQ']
        )
        
        assert len(result) == 2
        assert 'Benchmark' in result.columns
        assert 'Correlation' in result.columns
        assert set(result['Benchmark']) == {'SPY', 'QQQ'}
    
    def test_weights_must_match_holdings(self, correlation_service, sample_returns_data):
        """Test that weights must match holdings length."""
        with pytest.raises(ValueError, match="Holdings and weights must have the same length"):
            correlation_service.calculate_portfolio_aggregate_correlation(
                returns_df=sample_returns_data,
                holdings=['AAPL', 'GLD'],
                weights=[0.5],  # Only 1 weight for 2 holdings
                benchmarks=['SPY']
            )
    
    def test_empty_holdings_raises_error(self, correlation_service, sample_returns_data):
        """Test that empty holdings raises error."""
        with pytest.raises(ValueError, match="Must provide at least one holding"):
            correlation_service.calculate_portfolio_aggregate_correlation(
                returns_df=sample_returns_data,
                holdings=[],
                weights=[],
                benchmarks=['SPY']
            )
    
    def test_missing_holdings_raises_error(self, correlation_service, sample_returns_data):
        """Test that missing holdings raise error."""
        with pytest.raises(ValueError, match="Holdings not found in returns data"):
            correlation_service.calculate_portfolio_aggregate_correlation(
                returns_df=sample_returns_data,
                holdings=['AAPL', 'MISSING'],
                weights=[0.5, 0.5],
                benchmarks=['SPY']
            )
    
    def test_missing_benchmarks_raises_error(self, correlation_service, sample_returns_data):
        """Test that missing benchmarks raise error."""
        with pytest.raises(ValueError, match="Benchmarks not found in returns data"):
            correlation_service.calculate_portfolio_aggregate_correlation(
                returns_df=sample_returns_data,
                holdings=['AAPL'],
                weights=[1.0],
                benchmarks=['MISSING']
            )
    
    def test_single_holding_100_percent(self, correlation_service, sample_returns_data):
        """Test portfolio with single 100% holding."""
        result = correlation_service.calculate_portfolio_aggregate_correlation(
            returns_df=sample_returns_data,
            holdings=['AAPL'],
            weights=[1.0],
            benchmarks=['SPY']
        )
        
        # Should have perfect correlation with itself
        # Portfolio returns should equal AAPL returns
        assert len(result) == 1
        assert result.iloc[0]['Benchmark'] == 'SPY'
