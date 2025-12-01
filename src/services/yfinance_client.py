"""
Yahoo Finance API client for fetching stock/ETF data
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional


class YFinanceClient:
    """Client for Yahoo Finance data fetching"""
    
    @staticmethod
    def get_ticker_info(symbol: str) -> Optional[Dict]:
        """
        Get basic ticker information
        
        Args:
            symbol: Stock/ETF symbol
            
        Returns:
            Dictionary with ticker info or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol.upper(),
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'currency': info.get('currency'),
                'exchange': info.get('exchange')
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_price_history(symbol: str, period: str = '1y') -> pd.DataFrame:
        """
        Get historical price data
        
        Args:
            symbol: Stock/ETF symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            return df
        except Exception as e:
            print(f"Error fetching price history for {symbol}: {e}")
            return pd.DataFrame()
