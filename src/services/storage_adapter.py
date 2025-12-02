"""
Data storage adapter that uses BigQuery in production and SQLite locally
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd


class DataStorageAdapter:
    """Adapter for data storage - uses BigQuery in production, SQLite locally"""
    
    def __init__(self):
        self.use_bigquery = os.getenv('USE_BIGQUERY', 'false').lower() == 'true'
        self._currency_cache = {}  # Cache for instrument currencies
        
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
            instruments = self.storage.get_all_instruments(active_only)
            # Enrich with converted values if currency data exists
            return self._enrich_with_currency_conversion(instruments)
    
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
        """Get price data, optionally with currency conversion"""
        if self.use_bigquery:
            return self.storage.get_price_data(symbol, start_date, end_date)
        else:
            price_df = self.storage.get_price_data(symbol, start_date, end_date)
            
            # Apply currency conversion if instrument has currency data
            if not price_df.empty:
                currency = self._get_instrument_currency(symbol)
                if currency and currency != 'AUD':
                    price_df = self._convert_price_data_to_base(price_df, currency, start_date, end_date)
            
            return price_df
    
    def _get_instrument_currency(self, symbol: str) -> str:
        """Get instrument currency from cache or database"""
        if symbol not in self._currency_cache:
            # Query just the currency, not the full enriched data
            from src.models.database import Instrument
            from src.models import DatabaseManager
            db = DatabaseManager()
            session = db.get_session()
            try:
                inst = session.query(Instrument).filter_by(symbol=symbol.upper()).first()
                currency = getattr(inst, 'currency', 'USD') if inst else 'USD'
                self._currency_cache[symbol] = currency
            finally:
                session.close()
        
        return self._currency_cache[symbol]
    
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
    
    def fetch_and_store_fx_rates(self, currency_pair: str = 'AUDUSD', 
                                  period: str = '5y', force_refresh: bool = False) -> Dict:
        """Fetch and store FX rates"""
        if self.use_bigquery:
            return {'success': False, 'message': 'FX rates not implemented for BigQuery'}
        else:
            return self.storage.fetch_and_store_fx_rates(currency_pair, period, force_refresh)
    
    def get_fx_rate(self, currency_pair: str, date: datetime = None) -> float:
        """Get FX rate for a specific date"""
        if self.use_bigquery:
            return 1.0
        else:
            return self.storage.get_fx_rate(currency_pair, date)
    
    def get_fx_rates(self, currency_pair: str, start_date: datetime = None,
                    end_date: datetime = None) -> pd.DataFrame:
        """Get FX rates for a date range"""
        if self.use_bigquery:
            return pd.DataFrame(columns=['date', 'rate'])
        else:
            return self.storage.get_fx_rates(currency_pair, start_date, end_date)
    
    def _enrich_with_currency_conversion(self, instruments: List[Dict]) -> List[Dict]:
        """Enrich instruments with currency-converted values
        
        This adds 'value_local', 'value_base', and 'base_currency' to each instrument
        """
        # Check if any instruments have currency data
        if not any(inst.get('currency') for inst in instruments):
            return instruments
        
        # Import here to avoid circular dependency
        from src.utils.currency_converter import CurrencyConverter
        
        base_currency = 'AUD'
        converter = CurrencyConverter(self, base_currency=base_currency)
        
        # Get latest prices for all symbols
        symbols = [inst['symbol'] for inst in instruments]
        latest_prices = self.get_latest_prices(symbols)
        
        # Enrich each instrument
        enriched = []
        for inst in instruments:
            symbol = inst['symbol']
            quantity = inst.get('quantity', 0)
            currency = inst.get('currency', 'USD')
            
            # Add base currency fields
            inst['base_currency'] = base_currency
            
            if quantity > 0 and symbol in latest_prices:
                price = latest_prices[symbol]['close']
                value_local = quantity * price
                value_base = converter.convert_to_base(value_local, currency)
                
                inst['price'] = price
                inst['value_local'] = value_local
                inst['value_base'] = value_base
            else:
                inst['price'] = 0
                inst['value_local'] = 0
                inst['value_base'] = 0
            
            enriched.append(inst)
        
        return enriched
    
    def _convert_price_data_to_base(self, price_df: pd.DataFrame, currency: str, 
                                     start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """Convert price data to base currency (AUD)
        
        Args:
            price_df: DataFrame with price data (indexed by date)
            currency: Source currency (e.g., 'USD', 'AUD')
            start_date: Start date for FX rates
            end_date: End date for FX rates
            
        Returns:
            DataFrame with prices converted to AUD
        """
        if currency == 'AUD' or price_df.empty:
            return price_df
        
        if currency == 'USD':
            # Get FX rates for the date range, with some buffer
            if start_date:
                fx_start = start_date - timedelta(days=30)  # Extra buffer for forward-fill
            else:
                fx_start = price_df.index.min() - timedelta(days=30)
            
            fx_end = end_date if end_date else price_df.index.max()
            
            fx_rates_df = self.get_fx_rates('AUDUSD', fx_start, fx_end)
            
            if fx_rates_df.empty:
                # No FX data available - return unconverted with warning
                print(f"⚠️  Warning: No FX rates available for {currency}, prices not converted")
                return price_df
            
            # Create indexed FX rates and forward-fill for missing dates
            fx_rates = fx_rates_df.set_index('date')['rate']
            
            # Resample to daily and forward-fill to ensure no gaps
            fx_rates = fx_rates.resample('D').ffill()
            
            # Also backward-fill any leading NaNs
            fx_rates = fx_rates.bfill()
            
            # Align FX rates with price data dates
            aligned_fx = fx_rates.reindex(price_df.index)
            
            # Forward-fill then backward-fill any remaining NaNs
            aligned_fx = aligned_fx.ffill().bfill()
            
            # Check for any remaining NaNs and warn
            if aligned_fx.isna().any():
                nan_count = aligned_fx.isna().sum()
                print(f"⚠️  Warning: {nan_count} FX rates still missing after alignment")
                # Use global mean as absolute last resort
                aligned_fx = aligned_fx.fillna(fx_rates.mean())
            
            # Convert all price columns (open, high, low, close)
            converted_df = price_df.copy()
            for col in ['open', 'high', 'low', 'close']:
                if col in converted_df.columns:
                    # AUDUSD rate is AUD per USD, so divide to convert USD to AUD
                    converted_df[col] = converted_df[col] / aligned_fx
            
            # Clean outliers and NaNs with nearest neighbor average
            converted_df = self._clean_price_outliers(converted_df)
            
            return converted_df
        
        # Other currencies not yet supported
        print(f"⚠️  Warning: Currency {currency} not supported, prices not converted")
        return price_df
    
    def _clean_price_outliers(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """Clean outliers and NaN values using nearest neighbor averaging.
        
        Detects extreme price changes (>25% day-over-day) and replaces them
        with the average of surrounding valid values.
        """
        if price_df.empty:
            return price_df
        
        cleaned_df = price_df.copy()
        
        for col in ['open', 'high', 'low', 'close']:
            if col not in cleaned_df.columns:
                continue
            
            series = cleaned_df[col].copy()
            
            # Calculate day-over-day percent change
            pct_change = series.pct_change().abs()
            
            # Find outliers: >25% change or NaN values
            outliers = (pct_change > 0.25) | series.isna()
            
            if outliers.any():
                # Replace outliers with interpolation (linear between neighbors)
                series_clean = series.copy()
                series_clean[outliers] = None
                series_clean = series_clean.interpolate(method='linear', limit_direction='both')
                
                # If still NaN at edges, forward/backward fill
                series_clean = series_clean.ffill().bfill()
                
                cleaned_df[col] = series_clean
        
        return cleaned_df
