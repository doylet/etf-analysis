"""
Currency conversion utilities for multi-currency portfolio support
"""

from typing import Dict, List
from datetime import datetime
import pandas as pd


class CurrencyConverter:
    """Convert values between currencies using stored FX rates"""
    
    def __init__(self, storage_adapter, base_currency: str = 'AUD'):
        """
        Initialize currency converter
        
        Args:
            storage_adapter: Storage adapter instance for accessing FX rates
            base_currency: Base currency for portfolio (default: AUD)
        """
        self.storage = storage_adapter
        self.base_currency = base_currency
        self._fx_cache = {}
    
    def convert_to_base(self, amount: float, from_currency: str, date: datetime = None) -> float:
        """
        Convert amount to base currency
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., 'USD', 'AUD')
            date: Date for exchange rate (defaults to latest)
            
        Returns:
            Converted amount in base currency
        """
        if from_currency == self.base_currency:
            return amount
        
        # Get appropriate currency pair and invert if needed
        currency_pair, invert = self._get_currency_pair(from_currency, self.base_currency)
        
        # Get FX rate
        rate = self._get_rate(currency_pair, date)
        
        if invert:
            # If we have AUDUSD but need USD->AUD, divide instead of multiply
            return amount / rate if rate != 0 else amount
        else:
            return amount * rate
    
    def convert_series(self, amounts: pd.Series, currencies: pd.Series, 
                      dates: pd.Series = None) -> pd.Series:
        """
        Convert a series of amounts to base currency
        
        Args:
            amounts: Series of amounts to convert
            currencies: Series of currency codes
            dates: Series of dates (optional)
            
        Returns:
            Series of converted amounts
        """
        if dates is None:
            dates = pd.Series([None] * len(amounts), index=amounts.index)
        
        return pd.Series([
            self.convert_to_base(amt, curr, date)
            for amt, curr, date in zip(amounts, currencies, dates)
        ], index=amounts.index)
    
    def _get_currency_pair(self, from_currency: str, to_currency: str) -> tuple:
        """
        Get standard currency pair and whether to invert
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Tuple of (currency_pair, invert_rate)
        """
        # Standard pairs we support
        if from_currency == 'USD' and to_currency == 'AUD':
            return ('AUDUSD', True)  # Invert because AUDUSD is AUD per USD
        elif from_currency == 'AUD' and to_currency == 'USD':
            return ('AUDUSD', False)
        else:
            # Default: assume pair exists as-is
            return (f'{to_currency}{from_currency}', False)
    
    def _get_rate(self, currency_pair: str, date: datetime = None) -> float:
        """
        Get FX rate from cache or storage
        
        Args:
            currency_pair: Currency pair code
            date: Date for rate (optional)
            
        Returns:
            Exchange rate
        """
        cache_key = f"{currency_pair}_{date}" if date else f"{currency_pair}_latest"
        
        if cache_key not in self._fx_cache:
            self._fx_cache[cache_key] = self.storage.get_fx_rate(currency_pair, date)
        
        return self._fx_cache[cache_key]
    
    def clear_cache(self):
        """Clear FX rate cache"""
        self._fx_cache = {}
