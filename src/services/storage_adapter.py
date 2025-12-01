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
                       sector: str = None, notes: str = None, name: str = None, is_active: bool = True) -> Dict:
        """Add an instrument"""
        if self.use_bigquery:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            try:
                info = ticker.info
                name = name or info.get('longName', info.get('shortName', symbol))
                if sector is None:
                    sector = info.get('sector', 'Unknown')
            except:
                name = name or symbol
                sector = sector or 'Unknown'
            
            success = self.storage.add_instrument(
                symbol=symbol.upper(),
                name=name,
                instrument_type=instrument_type,
                sector=sector,
                notes=notes,
                is_active=is_active
            )
            return {
                'success': success,
                'message': f'Added {symbol}' if success else f'Failed to add {symbol}'
            }
        else:
            return self.storage.add_instrument(symbol, name, instrument_type, sector, notes, is_active)
    
    def get_all_instruments(self, active_only: bool = True) -> List[Dict]:
        """Get all instruments"""
        if self.use_bigquery:
            return self.storage.get_instruments(active_only)
        else:
            return self.storage.get_all_instruments(active_only)
    
    def get_instrument(self, symbol: str) -> Optional[Dict]:
        """Get a single instrument by symbol"""
        if self.use_bigquery:
            # TODO: Implement BigQuery get_instrument
            instruments = self.storage.get_instruments(active_only=True)
            for inst in instruments:
                if inst.get('symbol', '').upper() == symbol.upper():
                    return inst
            return None
        else:
            return self.storage.get_instrument(symbol)
    
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
    
    def create_order(self, symbol: str, order_type: str, volume: float,
                     order_date: datetime = None, notes: str = None) -> Dict:
        """Create an order"""
        if self.use_bigquery:
            return self.storage.create_order(symbol, order_type, volume, order_date, notes)
        else:
            return self.storage.create_order(symbol, order_type, volume, order_date, notes)
    
    def get_orders(self, symbol: str = None, include_deleted: bool = False) -> List[Dict]:
        """Get orders for a symbol or all orders"""
        if self.use_bigquery:
            return self.storage.get_orders(symbol)
        else:
            return self.storage.get_orders(symbol, include_deleted)
    
    def delete_order(self, order_id: int) -> Dict:
        """Soft delete an order"""
        if self.use_bigquery:
            return {'success': False, 'message': 'Delete order not implemented for BigQuery'}
        else:
            return self.storage.delete_order(order_id)
    
    def fetch_and_store_dividends(self, symbol: str, period: str = 'max') -> Dict:
        """Fetch and store dividend data"""
        if self.use_bigquery:
            return {'success': False, 'message': 'Dividend fetching not implemented for BigQuery'}
        else:
            return self.storage.fetch_and_store_dividends(symbol, period)
    
    def get_dividends(self, symbol: str = None, start_date: datetime = None, 
                     end_date: datetime = None) -> List[Dict]:
        """Get dividend history"""
        if self.use_bigquery:
            return []
        else:
            return self.storage.get_dividends(symbol, start_date, end_date)
    
    def record_dividend_cash_flow(self, symbol: str, payment_date: datetime,
                                  shares_held: float, dividend_per_share: float,
                                  notes: str = None) -> Dict:
        """Record dividend cash flow"""
        if self.use_bigquery:
            return {'success': False, 'message': 'Dividend cash flow not implemented for BigQuery'}
        else:
            return self.storage.record_dividend_cash_flow(
                symbol, payment_date, shares_held, dividend_per_share, notes
            )
    
    def get_dividend_cash_flows(self, symbol: str = None, start_date: datetime = None,
                                end_date: datetime = None) -> List[Dict]:
        """Get dividend cash flows"""
        if self.use_bigquery:
            return []
        else:
            return self.storage.get_dividend_cash_flows(symbol, start_date, end_date)
    
    def calculate_total_dividends_received(self, symbol: str = None, 
                                          start_date: datetime = None,
                                          end_date: datetime = None) -> float:
        """Calculate total dividends received"""
        if self.use_bigquery:
            return 0.0
        else:
            return self.storage.calculate_total_dividends_received(symbol, start_date, end_date)
    
    def calculate_dividends_from_holdings(self, symbol: str) -> List[Dict]:
        """Calculate dividends based on holdings history"""
        if self.use_bigquery:
            return []
        else:
            return self.storage.calculate_dividends_from_holdings(symbol)
    
    def auto_populate_dividend_cash_flows(self, symbol: str = None) -> Dict:
        """Auto-populate dividend cash flows from holdings"""
        if self.use_bigquery:
            return {'success': False, 'message': 'Not implemented for BigQuery', 'records_created': 0}
        else:
            return self.storage.auto_populate_dividend_cash_flows(symbol)
    
    def get_setting(self, key: str, default=None):
        """Get app setting"""
        if self.use_bigquery:
            return default
        else:
            return self.storage.get_setting(key, default)
    
    def set_setting(self, key: str, value: str, description: str = None) -> Dict:
        """Set app setting"""
        if self.use_bigquery:
            return {'success': False, 'message': 'Settings not implemented for BigQuery'}
        else:
            return self.storage.set_setting(key, value, description)
    
    def get_all_settings(self) -> Dict:
        """Get all settings"""
        if self.use_bigquery:
            return {}
        else:
            return self.storage.get_all_settings()
