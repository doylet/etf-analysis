"""
Symbol validation utilities for financial instruments.

Provides validation functions for ticker symbols, including format checking,
length validation, and character restrictions.
"""

import re
from typing import Dict, List


def validate_symbol(symbol: str, existing_symbols: List[str] = None) -> Dict:
    """
    Validate a financial symbol (ticker).
    
    Parameters:
        symbol: Symbol to validate (e.g., 'AAPL', 'BRK-B', 'VEU.AX')
        existing_symbols: Optional list of already selected symbols to check for duplicates
        
    Returns:
        Dict with keys:
        - 'valid': bool indicating if symbol is valid
        - 'message': str with error message if invalid
        - 'error_type': 'error' or 'warning' indicating severity
        
    Examples:
        >>> validate_symbol('AAPL')
        {'valid': True}
        
        >>> validate_symbol('AAP$L')
        {'valid': False, 'message': 'Symbol must contain only...', 'error_type': 'error'}
        
        >>> validate_symbol('AAPL', ['AAPL', 'MSFT'])
        {'valid': False, 'message': 'AAPL is already selected', 'error_type': 'warning'}
    """
    if existing_symbols is None:
        existing_symbols = []
    
    # Check non-empty
    if not symbol:
        return {
            'valid': False, 
            'message': 'Please enter a symbol', 
            'error_type': 'warning'
        }
    
    # Check length (most ticker symbols are 1-10 characters)
    if len(symbol) < 1 or len(symbol) > 10:
        return {
            'valid': False, 
            'message': 'Symbol must be between 1 and 10 characters', 
            'error_type': 'error'
        }
    
    # Check format: uppercase letters, numbers, dots (for international), dashes (for share classes)
    if not re.match(r'^[A-Z0-9.\-]+$', symbol):
        return {
            'valid': False, 
            'message': 'Symbol must contain only uppercase letters, numbers, dots, and dashes', 
            'error_type': 'error'
        }
    
    # Check duplicates
    if symbol in existing_symbols:
        return {
            'valid': False, 
            'message': f'{symbol} is already selected', 
            'error_type': 'warning'
        }
    
    return {'valid': True}


def format_symbol(symbol: str) -> str:
    """
    Format a symbol to standard format (uppercase, trimmed).
    
    Parameters:
        symbol: Raw symbol input
        
    Returns:
        Formatted symbol
        
    Examples:
        >>> format_symbol('  aapl  ')
        'AAPL'
        >>> format_symbol('brk-b')
        'BRK-B'
    """
    return symbol.upper().strip()


def is_valid_symbol_format(symbol: str) -> bool:
    """
    Quick check if symbol matches valid format (no detailed validation).
    
    Parameters:
        symbol: Symbol to check
        
    Returns:
        True if format is valid
        
    Examples:
        >>> is_valid_symbol_format('AAPL')
        True
        >>> is_valid_symbol_format('AAP$L')
        False
    """
    if not symbol or len(symbol) < 1 or len(symbol) > 10:
        return False
    return bool(re.match(r'^[A-Z0-9.\-]+$', symbol))
