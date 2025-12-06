#!/usr/bin/env python3
"""
Add sample orders to show cost basis calculations
"""

from src.services.storage_adapter import DataStorageAdapter

# Create sample orders for the holdings we have
storage = DataStorageAdapter()

orders = [
    # VEU.AX orders
    {'symbol': 'VEU.AX', 'order_type': 'BUY', 'volume': 100, 'price': 105.0, 'date': '2023-01-15'},
    {'symbol': 'VEU.AX', 'order_type': 'BUY', 'volume': 100, 'price': 108.0, 'date': '2023-06-15'},
    
    # JEPQ orders
    {'symbol': 'JEPQ', 'order_type': 'BUY', 'volume': 300, 'price': 56.0, 'date': '2023-02-01'},
    {'symbol': 'JEPQ', 'order_type': 'BUY', 'volume': 300, 'price': 58.0, 'date': '2023-08-01'},
    
    # QQQ orders  
    {'symbol': 'QQQ', 'order_type': 'BUY', 'volume': 20, 'price': 600.0, 'date': '2023-03-01'},
    {'symbol': 'QQQ', 'order_type': 'BUY', 'volume': 10, 'price': 610.0, 'date': '2023-09-01'},
    
    # SVOL orders
    {'symbol': 'SVOL', 'order_type': 'BUY', 'volume': 400, 'price': 16.5, 'date': '2023-04-01'},
    {'symbol': 'SVOL', 'order_type': 'BUY', 'volume': 260, 'price': 17.0, 'date': '2023-10-01'},
]

print("Adding sample orders...")
for order in orders:
    try:
        result = storage.create_order(
            symbol=order['symbol'],
            order_type=order['order_type'],
            volume=order['volume'],
            price=order['price'],
            order_date=order['date']
        )
        print(f"✓ {order['symbol']}: {order['order_type']} {order['volume']} @ ${order['price']}")
    except Exception as e:
        print(f"✗ Failed to add {order['symbol']} order: {e}")

print("\nSample orders added! Cost basis should now show in dashboard.")