"""
Portfolio calculation service.

Centralized business logic for portfolio calculations that can be reused
across API endpoints and widgets.
"""

from datetime import datetime
from typing import Dict, Tuple
import sqlite3

from services.storage_adapter import DataStorageAdapter
from repositories.instrument_repository import InstrumentRepository
from repositories.order_repository import OrderRepository


def get_repositories():
    """Get repository instances."""
    storage = DataStorageAdapter()
    return {
        'instrument': InstrumentRepository(storage),
        'order': OrderRepository(storage)
    }


def calculate_portfolio_metrics() -> Tuple[float, float, float, Dict[str, any]]:
    """
    Calculate core portfolio metrics using repository pattern.
    
    Returns:
        Tuple of (total_value, total_cost_basis, portfolio_return_pct, holdings_dict)
        
    This is the single source of truth for portfolio calculations.
    Used by:
    - /api/portfolio/summary endpoint
    - /api/widgets/performance endpoint  
    - Any other components needing portfolio metrics
    """
    repos = get_repositories()
    
    # Get current holdings
    holdings_dict = repos['order'].calculate_holdings_at_date(datetime.now())
    
    if not holdings_dict:
        return 0.0, 0.0, 0.0, {}
    
    # Get latest prices
    storage = DataStorageAdapter()
    price_data = storage.get_latest_prices(list(holdings_dict.keys()))
    prices = {}
    for symbol, data in price_data.items():
        if isinstance(data, dict) and 'close' in data:
            prices[symbol] = float(data['close'])
        else:
            prices[symbol] = 0.0
    
    # Get FX rate
    conn = sqlite3.connect('data/etf_analysis.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT rate FROM fx_rates WHERE currency_pair = 'AUDUSD' ORDER BY date DESC LIMIT 1"
    )
    fx_result = cursor.fetchone()
    audusd_rate = float(fx_result[0]) if fx_result else 0.655
    usd_to_aud = 1 / audusd_rate
    
    # Calculate total value and cost basis
    total_value = 0.0
    total_cost_basis = 0.0
    holdings_with_details = {}
    
    for symbol, quantity in holdings_dict.items():
        if quantity <= 0:
            continue
            
        instrument = repos['instrument'].find_by_symbol(symbol)
        if not instrument:
            continue
        
        instrument_currency = instrument.currency if hasattr(instrument, 'currency') else instrument.get('currency', 'USD')
        
        # Calculate cost basis from orders
        orders = repos['order'].find_by_symbol(symbol)
        buy_orders = [o for o in orders if o.order_type.upper() == 'BUY']
        
        total_spent = 0.0
        total_shares = 0.0
        
        for o in buy_orders:
            if hasattr(o, 'price') and o.price:
                total_spent += o.volume * o.price
                total_shares += o.volume
            else:
                order_date = o.order_date if hasattr(o, 'order_date') else o.date
                date_str = order_date.strftime('%Y-%m-%d')
                
                cursor.execute(
                    "SELECT close_price FROM price_data WHERE symbol = ? AND date(date) = ?",
                    (symbol, date_str)
                )
                result = cursor.fetchone()
                
                if result and result[0]:
                    close_price = float(result[0])
                    close_price_aud = close_price * usd_to_aud if instrument_currency == 'USD' else close_price
                    cost_basis_for_order = o.volume * close_price_aud
                    total_spent += cost_basis_for_order
                    total_shares += o.volume
        
        average_cost = total_spent / total_shares if total_shares > 0 else 0
        current_price = prices.get(symbol, 0.0)
        current_price_aud = current_price * usd_to_aud if instrument_currency == 'USD' else current_price
        
        current_value = quantity * current_price_aud
        cost_basis = quantity * average_cost
        
        total_value += current_value
        total_cost_basis += cost_basis
        
        # Store detailed info for return
        holdings_with_details[symbol] = {
            'quantity': quantity,
            'current_value': current_value,
            'cost_basis': cost_basis,
            'currency': instrument_currency
        }
    
    conn.close()
    
    # Calculate portfolio return
    portfolio_return = ((total_value - total_cost_basis) / total_cost_basis * 100) if total_cost_basis > 0 else 0.0
    
    return total_value, total_cost_basis, portfolio_return, holdings_with_details
