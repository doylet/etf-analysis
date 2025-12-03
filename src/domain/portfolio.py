"""
Portfolio domain models - represent portfolio holdings, orders, and performance.

These models capture the complete portfolio state including holdings, orders,
performance metrics, and price history.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import Field, field_validator

from . import DomainModel


class InstrumentType(str, Enum):
    """Type of financial instrument."""
    ETF = "etf"
    STOCK = "stock"
    BOND = "bond"
    COMMODITY = "commodity"
    CRYPTO = "crypto"
    CASH = "cash"
    OTHER = "other"


class OrderType(str, Enum):
    """Type of order transaction."""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    SPLIT = "split"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class InstrumentDomainModel(DomainModel):
    """
    Domain model for a financial instrument in the portfolio.
    
    Represents a single holding with its current value and weight in the portfolio.
    """
    symbol: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Full instrument name")
    instrument_type: InstrumentType = Field(..., description="Type of instrument")
    sector: Optional[str] = Field(None, description="Sector classification")
    currency: str = Field(default="USD", description="Currency code")
    quantity: float = Field(..., ge=0, description="Number of shares/units held")
    current_value_local: float = Field(..., ge=0, description="Current value in instrument currency")
    current_value_base: float = Field(..., ge=0, description="Current value in portfolio base currency")
    weight_pct: float = Field(..., ge=0, le=100, description="Weight in portfolio as percentage")
    
    @field_validator('symbol')
    @classmethod
    def symbol_must_be_uppercase(cls, v: str) -> str:
        """Ensure symbol is uppercase."""
        return v.upper()
    
    @field_validator('currency')
    @classmethod
    def currency_must_be_uppercase(cls, v: str) -> str:
        """Ensure currency code is uppercase."""
        return v.upper()


class OrderRecord(DomainModel):
    """
    Domain model for a portfolio transaction order.
    
    Represents a single buy, sell, or other transaction affecting portfolio holdings.
    """
    symbol: str = Field(..., description="Ticker symbol")
    order_type: OrderType = Field(..., description="Type of order")
    volume: float = Field(..., description="Number of shares (positive for buy, negative for sell)")
    order_date: datetime = Field(..., description="Date of order execution")
    price: Optional[float] = Field(None, ge=0, description="Execution price per share")
    notes: Optional[str] = Field(None, description="Additional notes or comments")
    
    @field_validator('symbol')
    @classmethod
    def symbol_must_be_uppercase(cls, v: str) -> str:
        """Ensure symbol is uppercase."""
        return v.upper()
    
    @field_validator('volume')
    @classmethod
    def validate_volume_sign(cls, v: float, info) -> float:
        """Validate volume sign matches order type."""
        # Note: info.data may not have order_type yet during validation order
        # So we'll just ensure volume is non-zero
        if v == 0:
            raise ValueError("Volume cannot be zero")
        return v


class PriceHistory(DomainModel):
    """
    Domain model for historical price data of an instrument.
    
    Contains OHLCV data and dividend information for a date range.
    """
    symbol: str = Field(..., description="Ticker symbol")
    start_date: datetime = Field(..., description="Start of price history")
    end_date: datetime = Field(..., description="End of price history")
    prices: Dict[str, List[float]] = Field(
        ..., 
        description="OHLCV data as dict with keys: date, open, high, low, close, volume"
    )
    dividends: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of dividend records with ex_date and amount"
    )
    
    @field_validator('symbol')
    @classmethod
    def symbol_must_be_uppercase(cls, v: str) -> str:
        """Ensure symbol is uppercase."""
        return v.upper()
    
    @field_validator('end_date')
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        """Ensure end_date is after start_date."""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("end_date must be after start_date")
        return v
    
    @field_validator('prices')
    @classmethod
    def validate_prices_structure(cls, v: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """Ensure prices dict has required keys and consistent lengths."""
        required_keys = {'date', 'open', 'high', 'low', 'close', 'volume'}
        if not required_keys.issubset(v.keys()):
            raise ValueError(f"prices must contain keys: {required_keys}")
        
        # Check all lists have same length
        lengths = [len(v[key]) for key in required_keys]
        if len(set(lengths)) > 1:
            raise ValueError("All price data lists must have the same length")
        
        return v


class PortfolioSummary(DomainModel):
    """
    Domain model for complete portfolio summary with performance metrics.
    
    Represents the current state of the portfolio including all holdings,
    total value, and calculated performance metrics.
    """
    total_value: float = Field(..., ge=0, description="Total portfolio value")
    base_currency: str = Field(default="USD", description="Base currency for portfolio")
    holdings: List[InstrumentDomainModel] = Field(
        default_factory=list,
        description="List of current holdings"
    )
    
    # Performance metrics
    mwr: Optional[float] = Field(None, description="Money-weighted return")
    twr: Optional[float] = Field(None, description="Time-weighted return")
    irr: Optional[float] = Field(None, description="Internal rate of return")
    sharpe: Optional[float] = Field(None, description="Sharpe ratio")
    sortino: Optional[float] = Field(None, description="Sortino ratio")
    volatility: Optional[float] = Field(None, ge=0, description="Annualized volatility")
    max_drawdown: Optional[float] = Field(None, le=0, description="Maximum drawdown (as negative %)")
    dividend_yield: Optional[float] = Field(None, ge=0, description="Dividend yield (%)")
    
    @field_validator('base_currency')
    @classmethod
    def currency_must_be_uppercase(cls, v: str) -> str:
        """Ensure currency code is uppercase."""
        return v.upper()
    
    @field_validator('holdings')
    @classmethod
    def validate_weights_sum(cls, v: List[InstrumentDomainModel]) -> List[InstrumentDomainModel]:
        """Validate that holdings weights sum to approximately 100%."""
        if v:
            total_weight = sum(holding.weight_pct for holding in v)
            # Allow small rounding errors
            if not (99.9 <= total_weight <= 100.1):
                raise ValueError(f"Holdings weights must sum to ~100%, got {total_weight:.2f}%")
        return v
    
    @field_validator('total_value')
    @classmethod
    def validate_total_value_matches_holdings(cls, v: float, info) -> float:
        """Validate total_value matches sum of holdings (with tolerance)."""
        if 'holdings' in info.data and info.data['holdings']:
            holdings_sum = sum(h.current_value_base for h in info.data['holdings'])
            # Allow 1% tolerance for rounding/currency conversion
            tolerance = max(v * 0.01, 0.01)
            if abs(v - holdings_sum) > tolerance:
                raise ValueError(
                    f"total_value ({v}) doesn't match sum of holdings ({holdings_sum})"
                )
        return v
