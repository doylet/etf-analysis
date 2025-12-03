"""
API schemas for portfolio management endpoints.

Request/response models for portfolio data and holdings.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class InstrumentTypeEnum(str, Enum):
    """Instrument types."""
    ETF = "ETF"
    STOCK = "STOCK"
    BOND = "BOND"
    COMMODITY = "COMMODITY"
    CRYPTO = "CRYPTO"
    CASH = "CASH"
    OTHER = "OTHER"


class HoldingResponse(BaseModel):
    """Response schema for a single portfolio holding."""
    
    symbol: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Instrument name")
    type: InstrumentTypeEnum = Field(..., description="Instrument type")
    quantity: float = Field(..., description="Number of shares/units held")
    average_cost: float = Field(..., description="Average purchase cost per share")
    current_price: float = Field(..., description="Current market price")
    current_value: float = Field(..., description="Current market value (quantity * price)")
    cost_basis: float = Field(..., description="Total cost basis (quantity * avg_cost)")
    unrealized_gain_loss: float = Field(..., description="Unrealized profit/loss")
    unrealized_gain_loss_pct: float = Field(..., description="Unrealized profit/loss percentage")
    weight_pct: float = Field(..., description="Percentage of total portfolio value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "VTI",
                "name": "Vanguard Total Stock Market ETF",
                "type": "ETF",
                "quantity": 150,
                "average_cost": 205.50,
                "current_price": 220.75,
                "current_value": 33112.50,
                "cost_basis": 30825.00,
                "unrealized_gain_loss": 2287.50,
                "unrealized_gain_loss_pct": 7.42,
                "weight_pct": 62.5
            }
        }


class PortfolioSummaryResponse(BaseModel):
    """Response schema for portfolio summary."""
    
    total_value: float = Field(..., description="Total portfolio market value")
    total_cost_basis: float = Field(..., description="Total cost basis")
    total_unrealized_gain_loss: float = Field(..., description="Total unrealized profit/loss")
    total_unrealized_gain_loss_pct: float = Field(..., description="Total unrealized profit/loss percentage")
    holdings: List[HoldingResponse] = Field(..., description="List of portfolio holdings")
    num_holdings: int = Field(..., description="Number of holdings")
    last_updated: datetime = Field(..., description="Last price update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_value": 53000.00,
                "total_cost_basis": 50000.00,
                "total_unrealized_gain_loss": 3000.00,
                "total_unrealized_gain_loss_pct": 6.0,
                "num_holdings": 3,
                "last_updated": "2023-12-04T16:00:00Z",
                "holdings": []
            }
        }


class InstrumentResponse(BaseModel):
    """Response schema for instrument details."""
    
    symbol: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Instrument name")
    type: InstrumentTypeEnum = Field(..., description="Instrument type")
    sector: Optional[str] = Field(None, description="Sector/category")
    currency: str = Field("USD", description="Trading currency")
    quantity: float = Field(0, description="Currently held quantity")
    current_value: float = Field(0, description="Current market value")
    average_cost: float = Field(0, description="Average purchase cost")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "type": "STOCK",
                "sector": "Technology",
                "currency": "USD",
                "quantity": 50,
                "current_value": 8750.00,
                "average_cost": 165.00
            }
        }


class InstrumentListResponse(BaseModel):
    """Response schema for paginated instrument list."""
    
    instruments: List[InstrumentResponse] = Field(..., description="List of instruments")
    total: int = Field(..., description="Total number of instruments")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(50, description="Items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "instruments": [],
                "total": 15,
                "page": 1,
                "page_size": 50
            }
        }


class InstrumentCreateRequest(BaseModel):
    """Request schema for creating new instrument."""
    
    symbol: str = Field(..., min_length=1, max_length=10, description="Ticker symbol")
    name: str = Field(..., min_length=1, description="Instrument name")
    type: InstrumentTypeEnum = Field(..., description="Instrument type")
    sector: Optional[str] = Field(None, description="Sector/category")
    currency: str = Field("USD", description="Trading currency")
    
    @field_validator('symbol')
    @classmethod
    def symbol_uppercase(cls, v: str) -> str:
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "type": "STOCK",
                "sector": "Technology",
                "currency": "USD"
            }
        }


class InstrumentUpdateRequest(BaseModel):
    """Request schema for updating instrument."""
    
    name: Optional[str] = Field(None, min_length=1, description="Instrument name")
    sector: Optional[str] = Field(None, description="Sector/category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Name",
                "sector": "Updated Sector"
            }
        }
