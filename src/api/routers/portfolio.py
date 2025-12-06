"""
Portfolio management API router.

Endpoints for viewing portfolio summary and holdings.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import List

from api.schemas.portfolio import (
    PortfolioSummaryResponse,
    HoldingResponse,
    InstrumentTypeEnum,
)
from services.storage_adapter import DataStorageAdapter
from repositories.instrument_repository import InstrumentRepository
from repositories.order_repository import OrderRepository
from repositories.price_data_repository import PriceDataRepository
from api.auth import get_current_user, User


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


def get_repositories():
    """Get repository instances."""
    storage = DataStorageAdapter()
    return {
        'instrument': InstrumentRepository(storage),
        'order': OrderRepository(storage),
        'price': PriceDataRepository(storage)
    }


@router.get("/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary():
    """
    Get complete portfolio summary with holdings and performance.
    
    Returns current holdings, values, gains/losses, and allocation.
    """
    try:
        repos = get_repositories()
        
        # Get current holdings
        holdings_dict = repos['order'].calculate_holdings_at_date(datetime.now())
        
        if not holdings_dict:
            return PortfolioSummaryResponse(
                total_value=0.0,
                total_cost_basis=0.0,
                total_unrealized_gain_loss=0.0,
                total_unrealized_gain_loss_pct=0.0,
                holdings=[],
                num_holdings=0,
                last_updated=datetime.utcnow()
            )
        
        # Get latest prices - use storage directly since it has the right format
        symbols = list(holdings_dict.keys())
        storage = DataStorageAdapter()
        price_data = storage.get_latest_prices(symbols)
        prices = {}
        for symbol, data in price_data.items():
            if isinstance(data, dict) and 'close' in data:
                prices[symbol] = float(data['close'])
            else:
                prices[symbol] = 0.0
        
        # Get latest AUD/USD exchange rate for currency conversion
        import sqlite3
        conn = sqlite3.connect('data/etf_analysis.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rate FROM fx_rates WHERE currency_pair = 'AUDUSD' ORDER BY date DESC LIMIT 1"
        )
        fx_result = cursor.fetchone()
        conn.close()
        
        # AUD/USD rate (1 AUD = X USD, so USD to AUD = 1/X)
        audusd_rate = float(fx_result[0]) if fx_result else 0.655  # fallback rate
        usd_to_aud = 1 / audusd_rate  # e.g., if AUDUSD = 0.655, then 1 USD = 1.527 AUD
        
        # Calculate holdings details
        holdings: List[HoldingResponse] = []
        total_value = 0.0
        total_cost_basis = 0.0
        
        for symbol, quantity in holdings_dict.items():
            if quantity <= 0:
                continue
                
            # Get instrument details
            instrument = repos['instrument'].find_by_symbol(symbol)
            if not instrument:
                continue
            
            # Determine instrument currency early for FX conversion
            if hasattr(instrument, 'currency'):
                instrument_currency = instrument.currency
            else:
                instrument_currency = instrument.get('currency', 'USD')
            
            # Get orders to calculate average cost
            orders = repos['order'].find_by_symbol(symbol)
            buy_orders = [o for o in orders if o.order_type.upper() == 'BUY']
            
            # Calculate average cost using historical prices
            total_spent = 0.0
            total_shares = 0.0
            
            for o in buy_orders:
                if hasattr(o, 'price') and o.price:
                    # New schema with price field
                    total_spent += o.volume * o.price
                    total_shares += o.volume
                else:
                    # Old schema without price - look up close price on order date
                    order_date = o.order_date if hasattr(o, 'order_date') else o.date
                    date_str = order_date.strftime('%Y-%m-%d')
                    
                    # Direct database query for close price on order date
                    import sqlite3
                    conn = sqlite3.connect('data/etf_analysis.db')
                    cursor = conn.cursor()
                    
                    # Look for close price on exact order date (date stored as '2025-04-30 00:00:00.000000')
                    cursor.execute(
                        "SELECT close_price FROM price_data WHERE symbol = ? AND date(date) = ?",
                        (symbol, date_str)
                    )
                    result = cursor.fetchone()
                    
                    conn.close()
                    
                    if result and result[0]:
                        close_price = float(result[0])
                        
                        # Convert historical price to AUD if needed
                        close_price_aud = close_price * usd_to_aud if instrument_currency == 'USD' else close_price
                        
                        cost_basis_for_order = o.volume * close_price_aud
                        total_spent += cost_basis_for_order
                        total_shares += o.volume
                        # Debug: print(f"Order: {symbol} {o.volume} units on {date_str} @ ${close_price:.2f} {instrument_currency} (${close_price_aud:.2f} AUD) = ${cost_basis_for_order:.2f} AUD")
            
            average_cost = total_spent / total_shares if total_shares > 0 else 0
            
            # Handle instrument type - instrument could be dict or domain model
            if hasattr(instrument, 'instrument_type'):
                # It's a domain model
                instrument_type_str = instrument.instrument_type.upper() if hasattr(instrument.instrument_type, 'upper') else str(instrument.instrument_type).upper()
                instrument_currency = instrument.currency if hasattr(instrument, 'currency') else 'USD'
            else:
                # It's a dict from storage - uses 'type' not 'instrument_type'
                instrument_type_str = str(instrument.get('type', 'OTHER')).upper()
                instrument_currency = instrument.get('currency', 'USD')
            
            current_price = prices.get(symbol, 0.0)
            
            # Convert current price to AUD (base currency)
            # Note: average_cost is already calculated in AUD from historical prices
            if instrument_currency == 'USD':
                current_price_aud = current_price * usd_to_aud
            else:  # AUD or other
                current_price_aud = current_price
            
            average_cost_aud = average_cost  # Already in AUD from calculation above
            
            current_value = quantity * current_price_aud
            cost_basis = quantity * average_cost_aud
            unrealized_gl = current_value - cost_basis
            unrealized_gl_pct = (unrealized_gl / cost_basis * 100) if cost_basis > 0 else 0
            
            total_value += current_value
            total_cost_basis += cost_basis
            
            holdings.append(HoldingResponse(
                symbol=symbol,
                name=instrument.name if hasattr(instrument, 'name') else instrument.get('name', symbol),
                type=InstrumentTypeEnum[instrument_type_str] if instrument_type_str in InstrumentTypeEnum.__members__ else InstrumentTypeEnum.OTHER,
                quantity=quantity,
                average_cost=average_cost_aud,  # Already converted to AUD
                current_price=current_price_aud,  # Already converted to AUD
                current_value=current_value,
                cost_basis=cost_basis,
                unrealized_gain_loss=unrealized_gl,
                unrealized_gain_loss_pct=unrealized_gl_pct,
                weight_pct=0.0  # Will calculate after total_value is known
            ))
        
        # Calculate weights
        for holding in holdings:
            holding.weight_pct = (holding.current_value / total_value * 100) if total_value > 0 else 0
        
        # Sort by value descending
        holdings.sort(key=lambda h: h.current_value, reverse=True)
        
        total_gl = total_value - total_cost_basis
        total_gl_pct = (total_gl / total_cost_basis * 100) if total_cost_basis > 0 else 0
        
        return PortfolioSummaryResponse(
            total_value=total_value,
            total_cost_basis=total_cost_basis,
            total_unrealized_gain_loss=total_gl,
            total_unrealized_gain_loss_pct=total_gl_pct,
            holdings=holdings,
            num_holdings=len(holdings),
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio summary: {str(e)}")


@router.get("/holdings", response_model=List[HoldingResponse])
async def get_holdings():
    """
    Get list of current portfolio holdings.
    
    Returns detailed information for each position.
    """
    try:
        summary = await get_portfolio_summary()
        return summary.holdings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get holdings: {str(e)}")
