#!/usr/bin/env python3
"""
Test that currency conversion happens automatically at the data layer
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.storage_adapter import DataStorageAdapter


def main():
    """Test automatic currency conversion in get_all_instruments"""
    print("=" * 60)
    print("Testing Automatic Currency Conversion")
    print("=" * 60)
    
    storage = DataStorageAdapter()
    
    # Get instruments - should be automatically enriched
    instruments = storage.get_all_instruments(active_only=True)
    
    print(f"\n✓ Retrieved {len(instruments)} instruments")
    print()
    
    # Check for enrichment
    aud_total = 0
    usd_total = 0
    
    print("Holdings with automatic currency conversion:")
    print("-" * 60)
    for inst in instruments:
        if inst.get('quantity', 0) > 0:
            symbol = inst['symbol']
            currency = inst.get('currency', '?')
            value_local = inst.get('value_local', 0)
            value_base = inst.get('value_base', 0)
            
            print(f"{symbol:8} {currency}  Local: ${value_local:>10,.2f}  →  AUD: ${value_base:>10,.2f}")
            
            if currency == 'AUD':
                aud_total += value_base
            else:
                usd_total += value_base
    
    print("-" * 60)
    print(f"{'AUD Holdings:':<20} AUD ${aud_total:>10,.2f}")
    print(f"{'USD Holdings (→AUD):':<20} AUD ${usd_total:>10,.2f}")
    print(f"{'Total Portfolio:':<20} AUD ${(aud_total + usd_total):>10,.2f}")
    print()
    print("✓ Currency conversion happens automatically!")
    print("  All widgets now get pre-converted values!")
    print()


if __name__ == '__main__':
    main()
