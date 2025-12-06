#!/usr/bin/env python3
"""
Add sample portfolio data for testing the frontend.
"""

import sqlite3
import os
from datetime import datetime

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Connect to database
db_path = 'data/etf_analysis.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing data
cursor.execute('SELECT COUNT(*) FROM instruments')
instrument_count = cursor.fetchone()[0]

print(f'Current instruments in database: {instrument_count}')

if instrument_count == 0:
    print('Adding sample data...')
    
    # Add sample instruments
    instruments = [
        ('VTI', 'Vanguard Total Stock Market ETF', 'ETF', 'Broad Market'),
        ('BND', 'Vanguard Total Bond Market ETF', 'ETF', 'Bonds'),
        ('AAPL', 'Apple Inc.', 'STOCK', 'Technology')
    ]
    
    cursor.executemany(
        'INSERT INTO instruments (symbol, name, type, sector) VALUES (?, ?, ?, ?)',
        instruments
    )
    
    # Add sample orders (buy transactions)
    orders = [
        ('VTI', 'BUY', 100, 200.0, '2023-01-15'),
        ('VTI', 'BUY', 50, 210.0, '2023-06-15'),
        ('BND', 'BUY', 200, 80.0, '2023-02-01'),
        ('AAPL', 'BUY', 25, 150.0, '2023-03-01'),
        ('AAPL', 'BUY', 25, 160.0, '2023-07-01')
    ]
    
    cursor.executemany(
        'INSERT INTO orders (symbol, order_type, volume, price, date) VALUES (?, ?, ?, ?, ?)',
        orders
    )
    
    # Add current prices
    prices = [
        ('VTI', 220.0, '2024-12-04'),
        ('BND', 85.0, '2024-12-04'),
        ('AAPL', 175.0, '2024-12-04')
    ]
    
    cursor.executemany(
        'INSERT INTO price_data (symbol, price, date) VALUES (?, ?, ?)',
        prices
    )
    
    conn.commit()
    print('✓ Sample data added successfully!')
    
    # Show what was added
    cursor.execute('SELECT symbol, name, type FROM instruments')
    instruments = cursor.fetchall()
    print(f'\nAdded {len(instruments)} instruments:')
    for symbol, name, type_ in instruments:
        print(f'  {symbol}: {name} ({type_})')
    
    cursor.execute('SELECT symbol, order_type, volume, price FROM orders')
    orders = cursor.fetchall()
    print(f'\nAdded {len(orders)} orders:')
    for symbol, order_type, volume, price in orders:
        print(f'  {symbol}: {order_type} {volume} @ ${price}')
    
    print('\n✓ Ready to test frontend!')
    
else:
    print('✓ Database already has sample data')

conn.close()