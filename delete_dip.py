#!/usr/bin/env python3
"""Quick script to delete DIP instrument"""

from src.services.storage_adapter import DataStorageAdapter

storage = DataStorageAdapter()

# Check if it exists
instrument = storage.get_instrument('DIP')
if instrument:
    print(f"Found: {instrument['name']} ({instrument['symbol']})")
    result = storage.remove_instrument('DIP')
    if result['success']:
        print(f"✅ Successfully deleted DIP")
    else:
        print(f"❌ Failed: {result['message']}")
else:
    print("❌ DIP not found in database")
