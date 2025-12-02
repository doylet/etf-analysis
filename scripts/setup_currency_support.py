#!/usr/bin/env python3
"""
Setup script for multi-currency support

This script:
1. Fetches AUDUSD FX rates
2. Detects currency for each instrument based on symbol suffix
3. Updates instrument currency fields
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.storage_adapter import DataStorageAdapter


def detect_currency(symbol: str) -> str:
    """
    Detect currency based on symbol suffix
    
    Australian securities typically end with .AX
    US securities have no suffix
    """
    if symbol.endswith('.AX'):
        return 'AUD'
    else:
        return 'USD'


def main():
    print("=" * 60)
    print("Multi-Currency Support Setup")
    print("=" * 60)
    
    storage = DataStorageAdapter()
    
    # Step 1: Fetch FX rates
    print("\n1. Fetching AUDUSD FX rates...")
    result = storage.fetch_and_store_fx_rates('AUDUSD', period='5y', force_refresh=False)
    
    if result['success']:
        print(f"   ✓ {result['message']}")
        if result.get('cached'):
            print("   ℹ Using cached data")
    else:
        print(f"   ✗ Failed: {result['message']}")
        return
    
    # Step 2: Update instrument currencies
    print("\n2. Detecting and updating instrument currencies...")
    instruments = storage.get_all_instruments(active_only=True)
    
    updated_count = 0
    for inst in instruments:
        symbol = inst['symbol']
        current_currency = inst.get('currency', 'USD')
        detected_currency = detect_currency(symbol)
        
        if current_currency != detected_currency:
            print(f"   {symbol}: {current_currency} -> {detected_currency}")
            # Note: You'll need to add update_instrument method to storage adapter
            # For now, this will need manual SQL update or add the method
            updated_count += 1
        else:
            print(f"   {symbol}: {current_currency} (no change)")
    
    print(f"\n✓ Setup complete!")
    print(f"  - FX rates: {result.get('records_added', 0)} records")
    print(f"  - Instruments checked: {len(instruments)}")
    print(f"  - Currencies detected: {updated_count} updates needed")
    
    if updated_count > 0:
        print("\n⚠ Note: Currency updates require manual SQL update or adding update_instrument method")
        print("   Run this SQL to update:")
        print("   UPDATE instruments SET currency = 'AUD' WHERE symbol LIKE '%.AX';")
        print("   UPDATE instruments SET currency = 'USD' WHERE symbol NOT LIKE '%.AX';")


if __name__ == '__main__':
    main()
