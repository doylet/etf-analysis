"""
Manual test script for performance widget calculations.

Run with: conda run -n etf-analysis python tests/widgets/test_performance_manual.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.widgets.performance_widget import PerformanceWidget


def test_calculate_performance_positive_return():
    """Test performance calculation with positive return"""
    print("\n=== Testing positive return ===")
    
    result = PerformanceWidget._calculate_performance('AAPL', 150.0, 165.0)
    
    assert result.symbol == 'AAPL', "Symbol should match"
    assert result.start_price == 150.0, "Start price should match"
    assert result.end_price == 165.0, "End price should match"
    assert result.change == 15.0, "Change should be 15.0"
    assert abs(result.change_pct - 10.0) < 0.01, "Change % should be 10%"
    
    print(f"✓ AAPL: ${result.start_price} → ${result.end_price} = {result.change_pct:.2f}%")


def test_calculate_performance_negative_return():
    """Test performance calculation with negative return"""
    print("\n=== Testing negative return ===")
    
    result = PerformanceWidget._calculate_performance('SPY', 400.0, 380.0)
    
    assert result.symbol == 'SPY', "Symbol should match"
    assert result.start_price == 400.0, "Start price should match"
    assert result.end_price == 380.0, "End price should match"
    assert result.change == -20.0, "Change should be -20.0"
    assert abs(result.change_pct - (-5.0)) < 0.01, "Change % should be -5%"
    
    print(f"✓ SPY: ${result.start_price} → ${result.end_price} = {result.change_pct:.2f}%")


def test_calculate_performance_zero_change():
    """Test performance calculation with no change"""
    print("\n=== Testing zero change ===")
    
    result = PerformanceWidget._calculate_performance('QQQ', 350.0, 350.0)
    
    assert result.symbol == 'QQQ', "Symbol should match"
    assert result.change == 0.0, "Change should be 0"
    assert result.change_pct == 0.0, "Change % should be 0%"
    
    print(f"✓ QQQ: ${result.start_price} → ${result.end_price} = {result.change_pct:.2f}%")


def test_calculate_performance_large_gain():
    """Test performance calculation with large gain"""
    print("\n=== Testing large gain ===")
    
    result = PerformanceWidget._calculate_performance('TSLA', 100.0, 250.0)
    
    assert result.change == 150.0, "Change should be 150.0"
    assert abs(result.change_pct - 150.0) < 0.01, "Change % should be 150%"
    
    print(f"✓ TSLA: ${result.start_price} → ${result.end_price} = {result.change_pct:.2f}%")


def test_calculate_performance_precision():
    """Test performance calculation with decimal precision"""
    print("\n=== Testing decimal precision ===")
    
    result = PerformanceWidget._calculate_performance('MSFT', 299.99, 305.50)
    
    expected_change = 305.50 - 299.99  # 5.51
    expected_pct = (5.51 / 299.99) * 100  # ~1.84%
    
    assert abs(result.change - expected_change) < 0.01, "Change should be accurate"
    assert abs(result.change_pct - expected_pct) < 0.01, "Percentage should be accurate"
    
    print(f"✓ MSFT: ${result.start_price:.2f} → ${result.end_price:.2f} = {result.change_pct:.2f}%")


def test_calculate_performance_small_price():
    """Test performance calculation with small prices"""
    print("\n=== Testing small prices ===")
    
    result = PerformanceWidget._calculate_performance('PENNY', 0.50, 0.75)
    
    assert result.change == 0.25, "Change should be 0.25"
    assert abs(result.change_pct - 50.0) < 0.01, "Change % should be 50%"
    
    print(f"✓ PENNY: ${result.start_price:.2f} → ${result.end_price:.2f} = {result.change_pct:.2f}%")


def main():
    """Run all tests"""
    print("=" * 60)
    print("PERFORMANCE WIDGET LOGIC LAYER TESTS")
    print("=" * 60)
    
    try:
        test_calculate_performance_positive_return()
        test_calculate_performance_negative_return()
        test_calculate_performance_zero_change()
        test_calculate_performance_large_gain()
        test_calculate_performance_precision()
        test_calculate_performance_small_price()
        
        print("\n" + "=" * 60)
        print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("=" * 60)
        print("\nThe refactored performance widget's pure logic functions")
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
