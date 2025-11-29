"""
Alpha Vantage API integration for symbol search and discovery
"""

import requests
import os
from typing import List, Dict, Optional


class AlphaVantageClient:
    """Client for Alpha Vantage API"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHAVANTAGE_API_KEY')
        if not self.api_key:
            print("Warning: No Alpha Vantage API key found. Symbol search will be disabled.")
    
    def search_symbols(self, keywords: str) -> List[Dict]:
        """
        Search for symbols using Alpha Vantage SYMBOL_SEARCH endpoint
        
        Args:
            keywords: Search keywords (company name, symbol, etc.)
            
        Returns:
            List of matching symbols with details
        """
        if not self.api_key:
            return []
        
        try:
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': keywords,
                'apikey': self.api_key
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                print(f"Alpha Vantage Error: {data['Error Message']}")
                return []
            
            if 'Note' in data:
                print(f"Alpha Vantage Rate Limit: {data['Note']}")
                return []
            
            # Parse results
            matches = data.get('bestMatches', [])
            
            results = []
            for match in matches:
                results.append({
                    'symbol': match.get('1. symbol', ''),
                    'name': match.get('2. name', ''),
                    'type': match.get('3. type', ''),
                    'region': match.get('4. region', ''),
                    'currency': match.get('8. currency', ''),
                    'match_score': float(match.get('9. matchScore', 0))
                })
            
            return results
        
        except requests.exceptions.RequestException as e:
            print(f"Error searching Alpha Vantage: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Alpha Vantage API is configured"""
        return self.api_key is not None
