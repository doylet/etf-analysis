"""
Data storage adapter that uses BigQuery in production and SQLite locally
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd


class DataStorageAdapter:
    """Adapter for data storage - uses BigQuery in production, SQLite locally"""
    
    def __init__(self):
        self.use_bigquery = os.getenv('USE_BIGQUERY', 'false').lower() == 'true'
        
        if self.use_bigquery:
            from .bigquery_client import BigQueryClient
            self.storage = BigQueryClient()
            print("✓ Using BigQuery for data storage")
        else:
            from src.models import DatabaseManager
            from .data_fetcher import DataFetcher
            db = DatabaseManager()
            self.storage = DataFetcher(db)
            print("✓ Using SQLite for data storage")
    
    def add_instrument(self, symbol: str, instrument_type: str = 'stock',
                       sector: str = None, notes: str = None) -> Dict:
        """Add an instrument"""
        if self.use_bigquery:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            try:
                info = ticker.info
                name = info.get('longName', info.get('shortName', symbol))
                if sector is None:
                    sector = info.get('sector', 'Unknown')
            except:
                name = symbol
                sector = sector or 'Unknown'
            
            success = self.storage.add_instrument(
                symbol=symbol.upper(),
                name=name,
                instrument_type=instrument_type,
                sector=sector,
                notes=notes
            )
            return {
                'success': success,
                'message': f'Added {symbol}' if success else f'Failed to add {symbol}'
            }
        else:
            return self.storage.add_instrument(symbol, instrument_type, sector, notes)
    
    def get_all_instruments(self, active_only: bool = True) -> List[Dict]:
        """Get all instruments"""
        if self.use_bigquery:
            return self.storage.get_instruments(active_only)
        else:
            return self.storage.get_all_instruments(active_only)
    
    def remove_instrument(self, symbol: str) -> Dict:
        """Remove an instrument"""
        if self.use_bigquery:
            success = self.storage.remove_instrument(symbol.upper())
            return {
                'success': success,
                'message': f'Removed {symbol}' if success else f'Failed to remove {symbol}'
            }
        else:
            return self.storage.remove_instrument(symbol)
    
    def search_instruments(self, search_term: str) -> List[Dict]:
        """Search instruments (only works with SQLite currently)"""
        if self.use_bigquery:
            # TODO: Implement BigQuery search
            return []
        else:
            return self.storage.search_instruments(search_term)
    
    def fetch_and_store_prices(self, symbol: str, period: str = '1y',
                                force_refresh: bool = False) -> Dict:
        """Fetch and store price data"""
        if self.use_bigquery:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return {'success': False, 'message': f'No data available for {symbol}'}
            
            # Prepare DataFrame for BigQuery
            df = df.reset_index()
            df['symbol'] = symbol.upper()
            df.columns = ['date', 'open_price', 'high_price', 'low_price', 
                          'close_price', 'volume', 'dividends', 'stock_splits', 'symbol']
            df = df[['symbol', 'date', 'open_price', 'high_price', 'low_price', 
                     'close_price', 'volume']]
            
            success = self.storage.insert_price_data(df)
            return {
                'success': success,
                'message': f'Fetched data for {symbol}',
                'records_added': len(df) if success else 0,
                'cached': False
            }
        else:
            return self.storage.fetch_and_store_prices(symbol, period, force_refresh)
    
    def get_price_data(self, symbol: str, start_date: datetime = None,
                       end_date: datetime = None) -> pd.DataFrame:
        """Get price data"""
        return self.storage.get_price_data(symbol, start_date, end_date)
    
    def get_latest_prices(self, symbols: List[str]) -> Dict:
        """Get latest prices"""
        return self.storage.get_latest_prices(symbols)
