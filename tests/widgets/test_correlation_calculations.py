"""
Unit tests for correlation matrix widget logic layer.

These tests demonstrate how the layered architecture enables unit testing
of business logic without requiring Streamlit runtime or mocking.

Run with: python -m pytest tests/widgets/test_correlation_calculations.py
Or manually in Python REPL:
    >>> import pandas as pd
    >>> from src.widgets.correlation_matrix_widget import CorrelationMatrixWidget
    >>> # Run individual test functions
"""

import pandas as pd
import numpy as np
import pytest
from src.widgets.correlation_matrix_widget import CorrelationMatrixWidget


class TestCorrelationCalculations:
    """Test pure calculation functions from CorrelationMatrixWidget."""
    
    def test_calculate_correlation_pairs(self):
        """Test extraction of correlation pairs."""
        # Arrange: Create correlation matrix
        corr_matrix = pd.DataFrame({
            'A': [1.0, 0.8, 0.3],
            'B': [0.8, 1.0, 0.4],
            'C': [0.3, 0.4, 1.0]
        }, index=['A', 'B', 'C'])
        
        # Act
        pairs_df = CorrelationMatrixWidget._calculate_correlation_pairs(corr_matrix)
        
        # Assert
        assert len(pairs_df) == 3  # 3 unique pairs from 3 symbols
        assert 'Pair' in pairs_df.columns
        assert 'Correlation' in pairs_df.columns
        # Should be sorted by correlation (descending)
        assert pairs_df.iloc[0]['Correlation'] >= pairs_df.iloc[1]['Correlation']
        # Highest correlation should be A-B (0.8)
        assert pairs_df.iloc[0]['Correlation'] == 0.8
        assert 'A - B' in pairs_df.iloc[0]['Pair']
    
    def test_calculate_benchmark_comparison(self):
        """Test portfolio vs benchmark correlation table."""
        # Arrange
        corr_matrix = pd.DataFrame({
            'AAPL': [1.0, 0.7, 0.85, 0.6],
            'MSFT': [0.7, 1.0, 0.75, 0.55],
            'SPY': [0.85, 0.75, 1.0, 0.8],
            'QQQ': [0.6, 0.55, 0.8, 1.0]
        }, index=['AAPL', 'MSFT', 'SPY', 'QQQ'])
        
        holdings = ['AAPL', 'MSFT']
        benchmarks = ['SPY', 'QQQ']
        available_columns = corr_matrix.columns
        
        # Act
        result = CorrelationMatrixWidget._calculate_benchmark_comparison(
            corr_matrix, holdings, benchmarks, available_columns
        )
        
        # Assert
        assert result is not None
        assert result.shape == (2, 2)  # 2 holdings x 2 benchmarks
        assert 'SPY' in result.columns
        assert 'QQQ' in result.columns
        assert 'AAPL' in result.index
        assert 'MSFT' in result.index
        assert result.loc['AAPL', 'SPY'] == 0.85
        assert result.loc['MSFT', 'QQQ'] == 0.55
    
    def test_validate_custom_symbol_valid(self):
        """Test custom symbol validation with valid input."""
        # Act
        result = CorrelationMatrixWidget._validate_custom_symbol('AAPL', [])
        
        # Assert
        assert result['valid'] is True
    
    def test_validate_custom_symbol_empty(self):
        """Test custom symbol validation with empty input."""
        # Act
        result = CorrelationMatrixWidget._validate_custom_symbol('', [])
        
        # Assert
        assert result['valid'] is False
        assert 'error_type' in result
        assert result['error_type'] == 'warning'
    
    def test_validate_custom_symbol_too_long(self):
        """Test custom symbol validation with too long input."""
        # Act
        result = CorrelationMatrixWidget._validate_custom_symbol('VERYLONGSYMBOL', [])
        
        # Assert
        assert result['valid'] is False
        assert 'error_type' in result
        assert result['error_type'] == 'error'
        assert '1 and 10 characters' in result['message']
    
    def test_validate_custom_symbol_invalid_chars(self):
        """Test custom symbol validation with invalid characters."""
        # Act
        result = CorrelationMatrixWidget._validate_custom_symbol('AAP$L', [])
        
        # Assert
        assert result['valid'] is False
        assert 'error_type' in result
        assert result['error_type'] == 'error'
    
    def test_validate_custom_symbol_duplicate(self):
        """Test custom symbol validation with duplicate."""
        # Act
        result = CorrelationMatrixWidget._validate_custom_symbol('AAPL', ['AAPL', 'MSFT'])
        
        # Assert
        assert result['valid'] is False
        assert 'already selected' in result['message']
    
    def test_validate_custom_symbol_with_dots_and_dashes(self):
        """Test custom symbol validation with international symbols."""
        # Act: Valid international symbols with dots/dashes
        result1 = CorrelationMatrixWidget._validate_custom_symbol('VEU.AX', [])
        result2 = CorrelationMatrixWidget._validate_custom_symbol('BRK-B', [])
        
        # Assert
        assert result1['valid'] is True
        assert result2['valid'] is True


class TestCorrelationAnalysis:
    """Test complete correlation analysis calculation."""
    
    def test_calculate_correlation_analysis_basic(self):
        """Test complete analysis with simple data."""
        # Arrange
        returns_df = pd.DataFrame({
            'SPY': [0.01, 0.02, -0.01, 0.03, 0.01],
            'QQQ': [0.02, 0.03, -0.02, 0.04, 0.02],
            'AGG': [-0.005, 0.001, 0.003, -0.001, 0.002]
        })
        
        from datetime import datetime
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 5)
        selected_holdings = ['SPY']
        selected_additional = ['QQQ', 'AGG']
        
        # Act
        analysis = CorrelationMatrixWidget._calculate_correlation_analysis(
            returns_df, selected_holdings, selected_additional, start_date, end_date
        )
        
        # Assert
        assert analysis is not None
        assert analysis.correlation_matrix.shape == (3, 3)
        assert analysis.num_days == 5
        assert analysis.start_date == start_date
        assert analysis.end_date == end_date
        assert -1.0 <= analysis.avg_correlation <= 1.0
        assert -1.0 <= analysis.max_correlation <= 1.0
        assert -1.0 <= analysis.min_correlation <= 1.0
        assert len(analysis.pairs_df) == 3  # 3 unique pairs
    
    def test_calculate_correlation_analysis_diversification(self):
        """Test diversification detection in analysis."""
        # Arrange: Create well-diversified portfolio
        returns_df = pd.DataFrame({
            'Stock': [0.01, -0.02, 0.03, -0.01, 0.02],
            'Bonds': [-0.005, 0.008, -0.002, 0.005, -0.003],
            'Gold': [0.002, -0.001, 0.001, 0.003, -0.002]
        })
        
        from datetime import datetime
        start = datetime(2023, 1, 1)
        end = datetime(2023, 1, 5)
        
        # Act
        analysis = CorrelationMatrixWidget._calculate_correlation_analysis(
            returns_df, ['Stock'], ['Bonds', 'Gold'], start, end
        )
        
        # Assert: Should detect diversification (low average correlation)
        assert analysis.avg_correlation < 0.7  # Well diversified


# Example: Running tests manually in Python REPL
"""
To test these functions without pytest, copy this into Python REPL:

>>> import pandas as pd
>>> from src.widgets.correlation_matrix_widget import CorrelationMatrixWidget

>>> # Test 1: Basic correlation matrix
>>> returns = pd.DataFrame({'A': [0.01, 0.02], 'B': [0.01, 0.02]})
>>> result = CorrelationMatrixWidget._calculate_correlation_matrix(returns)
>>> print(result)
     A    B
A  1.0  1.0
B  1.0  1.0

>>> # Test 2: Validation
>>> validation = CorrelationMatrixWidget._validate_custom_symbol('AAPL', [])
>>> print(validation)
{'valid': True}

>>> # Test 3: Invalid symbol
>>> validation = CorrelationMatrixWidget._validate_custom_symbol('AA$PL', [])
>>> print(validation)
{'valid': False, 'message': '...', 'error_type': 'error'}

This is the power of pure functions - test anywhere, anytime, no setup required!
"""
