"""
Price data repository - manages historical price data.

Wraps DataStorageAdapter to provide domain-focused API returning PriceHistory.
"""

from typing import List, Dict
from datetime import datetime
import pandas as pd

from ..domain.portfolio import PriceHistory
from ..services.storage_adapter import DataStorageAdapter
from ..utils.performance_metrics import calculate_returns


class PriceDataRepository:
    """Repository for managing price data."""
    
    def __init__(self, storage: DataStorageAdapter):
        """
        Initialize repository with storage adapter.
        
        Args:
            storage: DataStorageAdapter instance for data access
        """
        self.storage = storage
    
    def get_price_history(
        self,
        symbol: str,
        start: datetime,
        end: datetime
    ) -> PriceHistory:
        """
        Get price history for symbol.
        
        Args:
            symbol: Ticker symbol
            start: Start date
            end: End date
            
        Returns:
            PriceHistory domain model
            
        Raises:
            ValueError: If no data available
        """
        # Fetch price data from storage
        price_df = self.storage.get_price_data(symbol, start, end)
        
        if price_df.empty:
            raise ValueError(f"No price data available for {symbol}")
        
        # Convert DataFrame to dict format for domain model
        prices_dict = {
            'date': price_df.index.tolist(),
            'open': price_df['open'].tolist(),
            'high': price_df['high'].tolist(),
            'low': price_df['low'].tolist(),
            'close': price_df['close'].tolist(),
            'volume': price_df['volume'].tolist()
        }
        
        # Fetch dividends if available
        dividends = self.storage.get_dividends(symbol, start, end)
        dividend_list = []
        
        if dividends:
            for div in dividends:
                dividend_list.append({
                    'ex_date': div.get('ex_date'),
                    'amount': div.get('amount', 0.0)
                })
        
        return PriceHistory(
            symbol=symbol,
            start_date=start,
            end_date=end,
            prices=prices_dict,
            dividends=dividend_list
        )
    
    def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get latest closing prices for multiple symbols.
        
        Args:
            symbols: List of ticker symbols
            
        Returns:
            Dictionary mapping symbol to latest price
        """
        latest_prices = {}
        
        for symbol in symbols:
            try:
                # Get recent data (last 7 days)
                end_date = datetime.now()
                start_date = end_date.replace(day=max(1, end_date.day - 7))
                
                price_df = self.storage.get_price_data(symbol, start_date, end_date)
                
                if not price_df.empty and 'close' in price_df.columns:
                    latest_prices[symbol] = float(price_df['close'].iloc[-1])
                else:
                    latest_prices[symbol] = 0.0
            except Exception:
                latest_prices[symbol] = 0.0
        
        return latest_prices
    
    def get_returns(
        self,
        symbol: str,
        start: datetime,
        end: datetime
    ) -> pd.Series:
        """
        Calculate returns for symbol over date range.
        
        Args:
            symbol: Ticker symbol
            start: Start date
            end: End date
            
        Returns:
            Series of daily returns
            
        Raises:
            ValueError: If no data available
        """
        price_df = self.storage.get_price_data(symbol, start, end)
        
        if price_df.empty or 'close' not in price_df.columns:
            raise ValueError(f"No price data available for {symbol}")
        
        returns = calculate_returns(price_df['close'])
        return returns
    
    def store_prices(self, symbol: str, prices: pd.DataFrame) -> bool:
        """
        Store price data for symbol.
        
        Args:
            symbol: Ticker symbol
            prices: DataFrame with OHLCV columns
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If DataFrame missing required columns
        """
        required_cols = {'open', 'high', 'low', 'close', 'volume'}
        if not required_cols.issubset(set(prices.columns)):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")
        
        # Store using underlying storage adapter
        # Note: storage_adapter might not have a direct store method,
        # so this is a placeholder for future implementation
        try:
            self.storage.store_price_data(symbol, prices)
            return True
        except AttributeError:
            # If method doesn't exist, log warning and return False
            # In production, implement proper storage method
            return False
