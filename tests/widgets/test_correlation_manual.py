"""
Manual test script for correlation widget calculations.

Run with: conda run -n etf-analysis python tests/widgets/test_correlation_manual.py

This script manually tests the pure logic functions extracted in the refactoring.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from datetime import datetime
from src.widgets.correlation_matrix_widget import CorrelationMatrixWidget
from src.utils.symbol_validation import validate_symbol


def test_validate_custom_symbol():
    """Test custom symbol validation"""
    print("\n=== Testing validate_symbol (from symbol_validation module) ===")
    
    # Test 1: Valid symbol
    result = validate_symbol('AAPL', [])
    assert result['valid'] is True, "Valid symbol should pass"
    print("✓ Valid symbol test passed")
    
    # Test 2: Empty symbol
    result = validate_symbol('', [])
    assert result['valid'] is False, "Empty symbol should fail"
    assert result['error_type'] == 'warning'
    print("✓ Empty symbol test passed")
    
    # Test 3: Too long symbol
    result = validate_symbol('VERYLONGSYMBOL', [])
    assert result['valid'] is False, "Too long symbol should fail"
    assert result['error_type'] == 'error'
    assert '1 and 10 characters' in result['message']
    print("✓ Too long symbol test passed")
    
    # Test 4: Invalid characters
    result = validate_symbol('AAP$L', [])
    assert result['valid'] is False, "Symbol with invalid chars should fail"
    assert result['error_type'] == 'error'
    print("✓ Invalid characters test passed")
    
    # Test 5: Duplicate symbol
    result = validate_symbol('AAPL', ['AAPL', 'MSFT'])
    assert result['valid'] is False, "Duplicate symbol should fail"
    assert 'already selected' in result['message']
    print("✓ Duplicate symbol test passed")
    
    # Test 6: International symbols with dots/dashes
    result1 = validate_symbol('VEU.AX', [])
    result2 = validate_symbol('BRK-B', [])
    assert result1['valid'] is True, "Symbol with dot should pass"
    assert result2['valid'] is True, "Symbol with dash should pass"
    print("✓ International symbols test passed")
    
    print("✓✓✓ All validation tests passed!")


def test_calculate_correlation_pairs():
    """Test correlation pairs extraction"""
    print("\n=== Testing _calculate_correlation_pairs ===")
    
    # Create correlation matrix
    corr_matrix = pd.DataFrame({
        'A': [1.0, 0.8, 0.3],
        'B': [0.8, 1.0, 0.4],
        'C': [0.3, 0.4, 1.0]
    }, index=['A', 'B', 'C'])
    
    # Test
    pairs_df = CorrelationMatrixWidget._calculate_correlation_pairs(corr_matrix)
    
    # Assertions
    assert len(pairs_df) == 3, "Should have 3 unique pairs from 3 symbols"
    assert 'Pair' in pairs_df.columns, "Should have Pair column"
    assert 'Correlation' in pairs_df.columns, "Should have Correlation column"
    
    # Check sorting (descending)
    assert pairs_df.iloc[0]['Correlation'] >= pairs_df.iloc[1]['Correlation'], \
        "Pairs should be sorted by correlation"
    
    # Highest correlation should be A-B (0.8)
    assert pairs_df.iloc[0]['Correlation'] == 0.8, "Highest correlation should be 0.8"
    assert 'A - B' in pairs_df.iloc[0]['Pair'], "Highest pair should be A - B"
    
    print("✓ Correlation pairs test passed")
    print("✓✓✓ All pairs tests passed!")


def test_calculate_benchmark_comparison():
    """Test portfolio vs benchmark correlation table"""
    print("\n=== Testing _calculate_benchmark_comparison ===")
    
    # Create correlation matrix
    corr_matrix = pd.DataFrame({
        'AAPL': [1.0, 0.7, 0.85, 0.6],
        'MSFT': [0.7, 1.0, 0.75, 0.55],
        'SPY': [0.85, 0.75, 1.0, 0.8],
        'QQQ': [0.6, 0.55, 0.8, 1.0]
    }, index=['AAPL', 'MSFT', 'SPY', 'QQQ'])
    
    holdings = ['AAPL', 'MSFT']
    benchmarks = ['SPY', 'QQQ']
    available_columns = corr_matrix.columns
    
    # Test
    result = CorrelationMatrixWidget._calculate_benchmark_comparison(
        corr_matrix, holdings, benchmarks, available_columns
    )
    
    # Assertions
    assert result is not None, "Should return a result"
    assert result.shape == (2, 2), "Should be 2 holdings x 2 benchmarks"
    assert 'SPY' in result.columns, "Should have SPY column"
    assert 'QQQ' in result.columns, "Should have QQQ column"
    assert 'AAPL' in result.index, "Should have AAPL row"
    assert 'MSFT' in result.index, "Should have MSFT row"
    assert result.loc['AAPL', 'SPY'] == 0.85, "AAPL-SPY correlation should be 0.85"
    assert result.loc['MSFT', 'QQQ'] == 0.55, "MSFT-QQQ correlation should be 0.55"
    
    print("✓ Benchmark comparison test passed")
    print("✓✓✓ All benchmark tests passed!")


def test_calculate_correlation_analysis():
    """Test complete correlation analysis calculation"""
    print("\n=== Testing _calculate_correlation_analysis ===")
    
    # Create sample returns data
    returns_df = pd.DataFrame({
        'SPY': [0.01, 0.02, -0.01, 0.03, 0.01],
        'QQQ': [0.02, 0.03, -0.02, 0.04, 0.02],
        'AGG': [-0.005, 0.001, 0.003, -0.001, 0.002]
    })
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 5)
    selected_holdings = ['SPY']
    selected_additional = ['QQQ', 'AGG']
    
    # Test
    analysis = CorrelationMatrixWidget._calculate_correlation_analysis(
        returns_df, selected_holdings, selected_additional, start_date, end_date
    )
    
    # Assertions
    assert analysis is not None, "Should return an analysis object"
    assert analysis.correlation_matrix.shape == (3, 3), "Matrix should be 3x3"
    assert analysis.num_days == 5, "Should have 5 days"
    assert analysis.start_date == start_date, "Start date should match"
    assert analysis.end_date == end_date, "End date should match"
    assert -1.0 <= analysis.avg_correlation <= 1.0, "Avg correlation should be in [-1, 1]"
    assert -1.0 <= analysis.max_correlation <= 1.0, "Max correlation should be in [-1, 1]"
    assert -1.0 <= analysis.min_correlation <= 1.0, "Min correlation should be in [-1, 1]"
    assert len(analysis.pairs_df) == 3, "Should have 3 unique pairs"
    
    print("✓ Correlation analysis test passed")
    print(f"  - Avg correlation: {analysis.avg_correlation:.3f}")
    print(f"  - Max correlation: {analysis.max_correlation:.3f}")
    print(f"  - Min correlation: {analysis.min_correlation:.3f}")
    print("✓✓✓ All analysis tests passed!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("CORRELATION WIDGET LOGIC LAYER TESTS")
    print("=" * 60)
    
    try:
        test_validate_custom_symbol()
        test_calculate_correlation_pairs()
        test_calculate_benchmark_comparison()
        test_calculate_correlation_analysis()
        
        print("\n" + "=" * 60)
        print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("=" * 60)
        print("\nThe refactored correlation widget's pure logic functions")
        print("are working correctly and can be tested without Streamlit!")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
