"""
Dividend repository - manages dividend data and calculations.

Wraps DataStorageAdapter to provide domain-focused API for dividend operations.
"""

from typing import List, Dict
from datetime import datetime
import pandas as pd

from services.storage_adapter import DataStorageAdapter


class DividendRepository:
    """Repository for managing dividend data."""
    
    def __init__(self, storage: DataStorageAdapter):
        """
        Initialize repository with storage adapter.
        
        Args:
            storage: DataStorageAdapter instance for data access
        """
        self.storage = storage
    
    def get_dividends(
        self,
        symbol: str,
        start: datetime,
        end: datetime
    ) -> List[Dict]:
        """
        Get dividend records for symbol in date range.
        
        Args:
            symbol: Ticker symbol
            start: Start date
            end: End date
            
        Returns:
            List of dividend dictionaries with ex_date and amount
        """
        dividends = self.storage.get_dividends(symbol, start, end)
        
        if not dividends:
            return []
        
        # Ensure consistent format
        result = []
        for div in dividends:
            result.append({
                'ex_date': div.get('ex_date'),
                'amount': float(div.get('amount', 0.0)),
                'symbol': symbol
            })
        
        return result
    
    def get_cash_flows(self, symbol: str) -> pd.DataFrame:
        """
        Get all dividend cash flows for symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            DataFrame with ex_date and amount columns
        """
        dividends = self.storage.get_dividends(symbol)
        
        if not dividends:
            return pd.DataFrame(columns=['ex_date', 'amount'])
        
        df = pd.DataFrame(dividends)
        
        # Ensure required columns exist
        if 'ex_date' not in df.columns:
            df['ex_date'] = pd.NaT
        if 'amount' not in df.columns:
            df['amount'] = 0.0
        
        return df[['ex_date', 'amount']].sort_values('ex_date')
    
    def calculate_yield(
        self,
        symbol: str,
        lookback_days: int = 365
    ) -> float:
        """
        Calculate trailing dividend yield.
        
        Args:
            symbol: Ticker symbol
            lookback_days: Days to look back (default 365 for TTM)
            
        Returns:
            Dividend yield as decimal (e.g., 0.025 for 2.5%)
        """
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - 1)
        
        # Get dividends in period
        dividends = self.get_dividends(symbol, start_date, end_date)
        total_dividends = sum(div['amount'] for div in dividends)
        
        # Get current price
        price_df = self.storage.get_price_data(
            symbol,
            start_date=end_date.replace(day=max(1, end_date.day - 7)),
            end_date=end_date
        )
        
        if price_df.empty or 'close' not in price_df.columns:
            return 0.0
        
        current_price = float(price_df['close'].iloc[-1])
        
        if current_price <= 0:
            return 0.0
        
        return total_dividends / current_price
    
    def get_all_dividends_for_portfolio(
        self,
        symbols: List[str],
        start: datetime,
        end: datetime
    ) -> pd.DataFrame:
        """
        Get all dividends for multiple symbols.
        
        Args:
            symbols: List of ticker symbols
            start: Start date
            end: End date
            
        Returns:
            DataFrame with symbol, ex_date, amount columns
        """
        all_divs = []
        
        for symbol in symbols:
            divs = self.get_dividends(symbol, start, end)
            for div in divs:
                all_divs.append({
                    'symbol': symbol,
                    'ex_date': div['ex_date'],
                    'amount': div['amount']
                })
        
        if not all_divs:
            return pd.DataFrame(columns=['symbol', 'ex_date', 'amount'])
        
        df = pd.DataFrame(all_divs)
        return df.sort_values('ex_date')
