"""
Manual test script for holdings breakdown widget calculations.

Run with: conda run -n etf-analysis python tests/widgets/test_holdings_manual.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from src.widgets.holdings_breakdown_widget import HoldingsBreakdownWidget


def test_calculate_allocation_percentages():
    """Test allocation percentage calculation"""
    print("\n=== Testing _calculate_allocation_percentages ===")
    
    # Create sample values
    values = pd.Series([5000, 3000, 2000])
    total_value = 10000
    
    # Calculate allocations
    result = HoldingsBreakdownWidget._calculate_allocation_percentages(values, total_value)
    
    # Assertions
    assert len(result) == 3, "Should have 3 results"
    assert result.iloc[0] == 50.0, "First allocation should be 50%"
    assert result.iloc[1] == 30.0, "Second allocation should be 30%"
    assert result.iloc[2] == 20.0, "Third allocation should be 20%"
    assert abs(result.sum() - 100.0) < 0.1, "Total should be ~100%"
    
    print(f"✓ Allocations: {result.values} (sum = {result.sum():.2f}%)")


def test_calculate_allocation_percentages_uneven():
    """Test allocation with uneven values"""
    print("\n=== Testing uneven allocations ===")
    
    values = pd.Series([7500, 1500, 1000])
    total_value = 10000
    
    result = HoldingsBreakdownWidget._calculate_allocation_percentages(values, total_value)
    
    assert result.iloc[0] == 75.0, "First should be 75%"
    assert result.iloc[1] == 15.0, "Second should be 15%"
    assert result.iloc[2] == 10.0, "Third should be 10%"
    
    print(f"✓ Uneven allocations: {result.values}")


def test_calculate_allocation_percentages_small_values():
    """Test allocation with very small values"""
    print("\n=== Testing small value allocations ===")
    
    values = pd.Series([0.01, 0.02, 0.03])
    total_value = 0.06
    
    result = HoldingsBreakdownWidget._calculate_allocation_percentages(values, total_value)
    
    # Should still sum to ~100%
    assert abs(result.sum() - 100.0) < 0.1, "Small values should still sum to ~100%"
    
    print(f"✓ Small value allocations: {result.values} (sum = {result.sum():.2f}%)")


def test_calculate_grouped_breakdown_by_sector():
    """Test grouped breakdown by sector"""
    print("\n=== Testing _calculate_grouped_breakdown (by Sector) ===")
    
    # Create sample holdings data
    df = pd.DataFrame({
        'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'XOM', 'CVX'],
        'Sector': ['Tech', 'Tech', 'Tech', 'Energy', 'Energy'],
        'Type': ['Stock', 'Stock', 'Stock', 'Stock', 'Stock'],
        'Value': [5000, 3000, 2000, 1500, 500]
    })
    total_value = 12000
    
    # Calculate grouped breakdown
    result = HoldingsBreakdownWidget._calculate_grouped_breakdown(df, 'Sector', total_value)
    
    # Assertions
    assert len(result) == 2, "Should have 2 sectors"
    assert 'Sector' in result.columns, "Should have Sector column"
    assert 'Value' in result.columns, "Should have Value column"
    assert 'Allocation %' in result.columns, "Should have Allocation % column"
    
    # Tech sector should be first (largest value)
    assert result.iloc[0]['Sector'] == 'Tech', "Tech should be first (largest)"
    assert result.iloc[0]['Value'] == 10000, "Tech value should be 10000"
    assert abs(result.iloc[0]['Allocation %'] - 83.33) < 0.01, "Tech allocation should be ~83.33%"
    
    # Energy sector should be second
    assert result.iloc[1]['Sector'] == 'Energy', "Energy should be second"
    assert result.iloc[1]['Value'] == 2000, "Energy value should be 2000"
    assert abs(result.iloc[1]['Allocation %'] - 16.67) < 0.01, "Energy allocation should be ~16.67%"
    
    print(f"✓ Grouped by Sector:")
    print(f"  - {result.iloc[0]['Sector']}: ${result.iloc[0]['Value']} ({result.iloc[0]['Allocation %']}%)")
    print(f"  - {result.iloc[1]['Sector']}: ${result.iloc[1]['Value']} ({result.iloc[1]['Allocation %']}%)")


def test_calculate_grouped_breakdown_by_type():
    """Test grouped breakdown by type"""
    print("\n=== Testing grouped breakdown (by Type) ===")
    
    # Create sample holdings with different types
    df = pd.DataFrame({
        'Symbol': ['AAPL', 'SPY', 'AGG', 'GOOGL'],
        'Sector': ['Tech', 'Index', 'Bond', 'Tech'],
        'Type': ['Stock', 'ETF', 'ETF', 'Stock'],
        'Value': [5000, 3000, 2000, 4000]
    })
    total_value = 14000
    
    # Calculate grouped breakdown
    result = HoldingsBreakdownWidget._calculate_grouped_breakdown(df, 'Type', total_value)
    
    # Assertions
    assert len(result) == 2, "Should have 2 types"
    
    # Stock should be first (largest value: 5000 + 4000 = 9000)
    assert result.iloc[0]['Type'] == 'Stock', "Stock should be first"
    assert result.iloc[0]['Value'] == 9000, "Stock value should be 9000"
    assert abs(result.iloc[0]['Allocation %'] - 64.29) < 0.01, "Stock allocation should be ~64.29%"
    
    # ETF should be second (3000 + 2000 = 5000)
    assert result.iloc[1]['Type'] == 'ETF', "ETF should be second"
    assert result.iloc[1]['Value'] == 5000, "ETF value should be 5000"
    assert abs(result.iloc[1]['Allocation %'] - 35.71) < 0.01, "ETF allocation should be ~35.71%"
    
    print(f"✓ Grouped by Type:")
    print(f"  - {result.iloc[0]['Type']}: ${result.iloc[0]['Value']} ({result.iloc[0]['Allocation %']}%)")
    print(f"  - {result.iloc[1]['Type']}: ${result.iloc[1]['Value']} ({result.iloc[1]['Allocation %']}%)")


def test_calculate_grouped_breakdown_single_group():
    """Test grouped breakdown with single group"""
    print("\n=== Testing single group ===")
    
    df = pd.DataFrame({
        'Symbol': ['AAPL', 'MSFT'],
        'Sector': ['Tech', 'Tech'],
        'Type': ['Stock', 'Stock'],
        'Value': [5000, 3000]
    })
    total_value = 8000
    
    result = HoldingsBreakdownWidget._calculate_grouped_breakdown(df, 'Sector', total_value)
    
    assert len(result) == 1, "Should have 1 group"
    assert result.iloc[0]['Sector'] == 'Tech', "Should be Tech"
    assert result.iloc[0]['Value'] == 8000, "Value should be 8000"
    assert result.iloc[0]['Allocation %'] == 100.0, "Allocation should be 100%"
    
    print(f"✓ Single group: {result.iloc[0]['Sector']} = 100%")


def main():
    """Run all tests"""
    print("=" * 60)
    print("HOLDINGS BREAKDOWN WIDGET LOGIC LAYER TESTS")
    print("=" * 60)
    
    try:
        test_calculate_allocation_percentages()
        test_calculate_allocation_percentages_uneven()
        test_calculate_allocation_percentages_small_values()
        test_calculate_grouped_breakdown_by_sector()
        test_calculate_grouped_breakdown_by_type()
        test_calculate_grouped_breakdown_single_group()
        
        print("\n" + "=" * 60)
        print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("=" * 60)
        print("\nThe refactored holdings breakdown widget's pure logic")
        print("functions are working correctly and can be tested without Streamlit!")
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
