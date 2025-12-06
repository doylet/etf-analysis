#!/usr/bin/env python3
"""
Simple script to delete an instrument from the database
Usage: python delete_instrument.py <SYMBOL>
"""

import sys
from src.services.storage_adapter import DataStorageAdapter

def delete_instrument(symbol: str):
    """Delete an instrument by symbol"""
    storage = DataStorageAdapter()
    
    # Check if it exists first
    instrument = storage.get_instrument(symbol)
    if not instrument:
        print(f"❌ Instrument '{symbol}' not found in database")
        return False
    
    print(f"Found instrument: {instrument['name']} ({symbol})")
    print(f"Type: {instrument['type']}, Sector: {instrument.get('sector', 'N/A')}")
    
    # Confirm deletion
    confirm = input(f"\nAre you sure you want to delete '{symbol}'? (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("Deletion cancelled")
        return False
    
    # Delete it
    result = storage.remove_instrument(symbol)
    
    if result['success']:
        print(f"✅ {result['message']}")
        return True
    else:
        print(f"❌ {result['message']}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_instrument.py <SYMBOL>")
        print("Example: python delete_instrument.py DIP")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    success = delete_instrument(symbol)
    sys.exit(0 if success else 1)
