#!/usr/bin/env python3
"""
Database migration: Add currency column to instruments table
"""

import sqlite3
import os

DB_PATH = 'data/etf_analysis.db'

def migrate():
    """Add currency column to instruments table"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(instruments)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'currency' in columns:
            print("✓ Currency column already exists")
            return True
        
        # Add currency column
        print("Adding currency column to instruments table...")
        cursor.execute("""
            ALTER TABLE instruments 
            ADD COLUMN currency VARCHAR(3) DEFAULT 'USD'
        """)
        
        # Update currencies based on symbol suffix
        print("Setting currency for Australian securities (.AX)...")
        cursor.execute("""
            UPDATE instruments 
            SET currency = 'AUD' 
            WHERE symbol LIKE '%.AX'
        """)
        aud_count = cursor.rowcount
        
        print("Setting currency for US securities...")
        cursor.execute("""
            UPDATE instruments 
            SET currency = 'USD' 
            WHERE symbol NOT LIKE '%.AX' AND (currency IS NULL OR currency = 'USD')
        """)
        usd_count = cursor.rowcount
        
        conn.commit()
        
        print(f"\n✓ Migration successful!")
        print(f"  - AUD securities: {aud_count}")
        print(f"  - USD securities: {usd_count}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add Currency Support")
    print("=" * 60)
    print()
    
    success = migrate()
    
    if success:
        print("\n✓ Ready to run setup_currency_support.py")
    else:
        print("\n❌ Migration failed. Please check the error above.")
