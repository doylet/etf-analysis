"""
Migration: Add orders table and migrate quantity data
Run this script to migrate from Instrument.quantity to Order-based tracking
"""

import sqlite3
from datetime import datetime

def migrate_sqlite(db_path='./data/etf_analysis.db'):
    """Migrate SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting migration...")
        
        # 1. Create orders table
        print("Creating orders table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument_id INTEGER NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                order_type VARCHAR(10) NOT NULL,
                volume REAL NOT NULL,
                order_date TIMESTAMP NOT NULL,
                notes VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id) REFERENCES instruments (id)
            )
        ''')
        
        # 2. Create indexes
        print("Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_instrument_id ON orders(instrument_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)')
        
        # 3. Migrate existing quantity data to orders
        print("Migrating existing quantities to orders...")
        cursor.execute('''
            SELECT id, symbol, quantity, added_date 
            FROM instruments 
            WHERE quantity > 0 AND is_active = 1
        ''')
        instruments_with_quantity = cursor.fetchall()
        
        for inst_id, symbol, quantity, added_date in instruments_with_quantity:
            # Create a Buy order for the existing quantity
            cursor.execute('''
                INSERT INTO orders (instrument_id, symbol, order_type, volume, order_date, notes)
                VALUES (?, ?, 'Buy', ?, ?, 'Migrated from initial quantity')
            ''', (inst_id, symbol, quantity, added_date))
            print(f"  Migrated {symbol}: {quantity} units")
        
        # 4. Drop quantity column from instruments
        print("Removing quantity column from instruments...")
        # SQLite doesn't support DROP COLUMN directly, need to recreate table
        cursor.execute('''
            CREATE TABLE instruments_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol VARCHAR(10) UNIQUE NOT NULL,
                name VARCHAR(200),
                instrument_type VARCHAR(20),
                sector VARCHAR(100),
                is_active BOOLEAN DEFAULT 1,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes VARCHAR(500)
            )
        ''')
        
        cursor.execute('''
            INSERT INTO instruments_new 
            SELECT id, symbol, name, instrument_type, sector, is_active, added_date, last_updated, notes
            FROM instruments
        ''')
        
        cursor.execute('DROP TABLE instruments')
        cursor.execute('ALTER TABLE instruments_new RENAME TO instruments')
        
        # Recreate index
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_instruments_symbol ON instruments(symbol)')
        
        conn.commit()
        print("✓ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else './data/etf_analysis.db'
    migrate_sqlite(db_path)
