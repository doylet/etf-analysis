"""
Portfolio management API router.

Endpoints for viewing portfolio summary and holdings.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List

from ..schemas.portfolio import (
    PortfolioSummaryResponse,
    HoldingResponse,
    InstrumentTypeEnum,
)
from ...services.storage_adapter import DataStorageAdapter
from ...repositories.instrument_repository import InstrumentRepository
from ...repositories.order_repository import OrderRepository
from ...repositories.price_data_repository import PriceDataRepository


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
        
        # Get latest prices
        symbols = list(holdings_dict.keys())
        prices = repos['price'].get_latest_prices(symbols)
        
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
            
            # Get orders to calculate average cost
            orders = repos['order'].find_by_symbol(symbol)
            buy_orders = [o for o in orders if o.order_type.value == 'BUY']
            
            total_spent = sum(o.volume * o.price for o in buy_orders)
            total_shares = sum(o.volume for o in buy_orders)
            average_cost = total_spent / total_shares if total_shares > 0 else 0
            
            current_price = prices.get(symbol, 0.0)
            current_value = quantity * current_price
            cost_basis = quantity * average_cost
            unrealized_gl = current_value - cost_basis
            unrealized_gl_pct = (unrealized_gl / cost_basis * 100) if cost_basis > 0 else 0
            
            total_value += current_value
            total_cost_basis += cost_basis
            
            holdings.append(HoldingResponse(
                symbol=symbol,
                name=instrument.name,
                type=InstrumentTypeEnum[instrument.type.value],
                quantity=quantity,
                average_cost=average_cost,
                current_price=current_price,
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
