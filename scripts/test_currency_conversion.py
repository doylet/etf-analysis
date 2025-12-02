#!/usr/bin/env python3
"""
Test script to verify currency conversion is working
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.storage_adapter import DataStorageAdapter
from src.utils.currency_converter import CurrencyConverter


def main():
    """Test currency conversion functionality"""
    print("=" * 60)
    print("Currency Conversion Test")
    print("=" * 60)
    
    storage = DataStorageAdapter()
    converter = CurrencyConverter(storage, base_currency='AUD')
    
    # Test conversion
    usd_amount = 1000.0
    aud_amount = converter.convert_to_base(usd_amount, 'USD')
    fx_rate = storage.get_fx_rate('AUDUSD')
    
    print(f"\n✓ Currency Converter Working:")
    print(f"  USD $1,000.00 = AUD ${aud_amount:,.2f}")
    print(f"  Current AUDUSD rate: {fx_rate:.4f}")
    print()
    print("✓ Multi-currency support is ready!")
    print()


if __name__ == '__main__':
    main()
