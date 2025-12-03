"""
Bulk fetch dividends for all instruments in the database.
Run with: python3 fetch_all_dividends.py
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.storage_adapter import DataStorageAdapter

def main():
    storage = DataStorageAdapter()
    
    # Get all instruments
    instruments = storage.get_all_instruments(active_only=False)
    
    print(f"\nFetching dividends for {len(instruments)} instruments...")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    no_div_count = 0
    
    for i, inst in enumerate(instruments, 1):
        symbol = inst['symbol']
        print(f"\n[{i}/{len(instruments)}] {symbol:8s} - {inst['name'][:40]}")
        
        try:
            result = storage.fetch_and_store_dividends(symbol, period='max')
            
            if result['success']:
                records = result.get('records_added', 0)
                if records > 0:
                    print(f"  ✓ Added {records} dividend records")
                    success_count += 1
                else:
                    print(f"  ○ No dividends found")
                    no_div_count += 1
            else:
                print(f"  ✗ {result['message']}")
                fail_count += 1
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"\nSummary:")
    print(f"  Success (with dividends): {success_count}")
    print(f"  No dividends found:       {no_div_count}")
    print(f"  Failed:                   {fail_count}")
    print(f"  Total:                    {len(instruments)}")

if __name__ == "__main__":
    main()
