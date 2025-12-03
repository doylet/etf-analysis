"""
News Analysis Domain Models

Models for surprise event detection and news correlation analysis.
"""

from typing import List, Dict, Optional
from enum import Enum
from pydantic import Field, HttpUrl
from datetime import datetime
from src.domain import DomainModel


class EventType(str, Enum):
    """Types of surprise events."""
    VOLATILITY_SPIKE = "volatility_spike"
    UNUSUAL_RETURN = "unusual_return"
    CORRELATION_BREAK = "correlation_break"
    PORTFOLIO_SHOCK = "portfolio_shock"


class SurpriseEvent(DomainModel):
    """
    Detected surprise event in market or portfolio.
    
    Represents statistically significant deviations from expected behavior.
    """
    
    date: datetime = Field(
        ...,
        description="Date when event occurred"
    )
    
    symbol: Optional[str] = Field(
        None,
        description="Instrument symbol (None for portfolio-level events)"
    )
    
    event_type: EventType = Field(
        ...,
        description="Type of surprise event"
    )
    
    magnitude: float = Field(
        ...,
        ge=0,
        description="Event magnitude (absolute value)"
    )
    
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Human-readable event description"
    )
    
    z_score: float = Field(
        ...,
        description="Statistical significance (standard deviations from baseline)"
    )
    
    affected_value: float = Field(
        ...,
        description="Dollar impact or percentage change"
    )


class NewsArticle(DomainModel):
    """
    News article related to surprise event.
    """
    
    title: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Article title"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Article description or excerpt"
    )
    
    url: str = Field(
        ...,
        description="URL to full article"
    )
    
    source: str = Field(
        ...,
        description="News source name"
    )
    
    published_at: datetime = Field(
        ...,
        description="Article publication date"
    )
    
    relevance_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Relevance score (0-1, higher = more relevant)"
    )


class EventNewsCorrelation(DomainModel):
    """
    Correlation analysis between surprise event and news coverage.
    
    Uses AI-style heuristics to determine if news explains the event.
    """
    
    event: SurpriseEvent = Field(
        ...,
        description="The surprise event being analyzed"
    )
    
    articles: List[NewsArticle] = Field(
        ...,
        description="Related news articles"
    )
    
    ai_analysis: str = Field(
        ...,
        min_length=50,
        description="AI-generated analysis of correlation"
    )
    
    correlation_strength: float = Field(
        ...,
        ge=0,
        le=1,
        description="Correlation strength (0-1, higher = stronger)"
    )
    
    key_themes: List[str] = Field(
        ...,
        description="Key themes identified in news coverage"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When analysis was performed"
    )
