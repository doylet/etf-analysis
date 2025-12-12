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
    Uses centralized portfolio_service for calculations.
    """
    try:
        # Use centralized portfolio calculation service
        from services.portfolio_service import calculate_portfolio_metrics
        total_value, total_cost_basis, portfolio_return_pct, holdings_with_details = calculate_portfolio_metrics()
        
        if not holdings_with_details:
            return PortfolioSummaryResponse(
                total_value=0.0,
                total_cost_basis=0.0,
                total_unrealized_gain_loss=0.0,
                total_unrealized_gain_loss_pct=0.0,
                holdings=[],
                num_holdings=0,
                last_updated=datetime.utcnow()
            )
        
        # Get repository for additional holding details
        repos = get_repositories()
        storage = DataStorageAdapter()
        price_data = storage.get_latest_prices(list(holdings_with_details.keys()))
        prices = {}
        for symbol, data in price_data.items():
            if isinstance(data, dict) and 'close' in data:
                prices[symbol] = float(data['close'])
            else:
                prices[symbol] = 0.0
        
        # Build holdings response using pre-calculated values
        holdings: List[HoldingResponse] = []
        
        for symbol, details in holdings_with_details.items():
            instrument = repos['instrument'].find_by_symbol(symbol)
            if not instrument:
                continue
            
            # Handle instrument type - instrument could be dict or domain model
            if hasattr(instrument, 'instrument_type'):
                instrument_type_str = instrument.instrument_type.upper() if hasattr(instrument.instrument_type, 'upper') else str(instrument.instrument_type).upper()
            else:
                instrument_type_str = str(instrument.get('type', 'OTHER')).upper()
            
            current_price = prices.get(symbol, 0.0)
            quantity = details['quantity']
            current_value = details['current_value']
            cost_basis = details['cost_basis']
            
            average_cost_aud = cost_basis / quantity if quantity > 0 else 0
            current_price_aud = current_value / quantity if quantity > 0 else 0
            
            unrealized_gl = current_value - cost_basis
            unrealized_gl_pct = (unrealized_gl / cost_basis * 100) if cost_basis > 0 else 0
            
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
        
        return PortfolioSummaryResponse(
            total_value=total_value,
            total_cost_basis=total_cost_basis,
            total_unrealized_gain_loss=total_gl,
            total_unrealized_gain_loss_pct=portfolio_return_pct,
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
