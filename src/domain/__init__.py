"""
Domain Package Initialization

Provides base classes and utilities for domain models using Pydantic.
All domain models should inherit from these base classes for consistent serialization.
"""

from pydantic import BaseModel, ConfigDict
from typing import Any, Dict
import json


class DomainModel(BaseModel):
    """
    Base class for all domain models.
    
    Provides:
    - JSON serialization/deserialization
    - Validation via Pydantic
    - Immutability (frozen models)
    - Type safety
    """
    
    model_config = ConfigDict(
        # Allow arbitrary types (for numpy arrays, pandas DataFrames, etc.)
        arbitrary_types_allowed=True,
        # Validate on assignment
        validate_assignment=True,
        # Use enums values instead of enum objects
        use_enum_values=True,
        # Extra fields forbidden (strict validation)
        extra='forbid'
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.
        
        Returns:
            Dictionary representation with all fields
        """
        return self.model_dump()
    
    def to_json(self) -> str:
        """
        Convert model to JSON string.
        
        Returns:
            JSON string representation
        """
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainModel':
        """
        Create model instance from dictionary.
        
        Args:
            data: Dictionary with model fields
            
        Returns:
            Model instance
            
        Raises:
            ValidationError: If data doesn't match model schema
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DomainModel':
        """
        Create model instance from JSON string.
        
        Args:
            json_str: JSON string with model fields
            
        Returns:
            Model instance
            
        Raises:
            ValidationError: If JSON doesn't match model schema
        """
        return cls.model_validate_json(json_str)


from .simulation import SimulationParameters, SimulationResults
from .optimization import OptimizationRequest, OptimizationResults, OptimizationObjective
from .rebalancing import RebalancingRecommendation
from .news import SurpriseEvent, NewsArticle, EventNewsCorrelation, EventType
from .portfolio import (
    PortfolioSummary,
    InstrumentDomainModel,
    OrderRecord,
    PriceHistory,
    InstrumentType,
    OrderType
)

__all__ = [
    'DomainModel',
    'SimulationParameters',
    'SimulationResults',
    'OptimizationRequest',
    'OptimizationResults',
    'OptimizationObjective',
    'RebalancingRecommendation',
    'SurpriseEvent',
    'NewsArticle',
    'EventNewsCorrelation',
    'EventType',
    'PortfolioSummary',
    'InstrumentDomainModel',
    'OrderRecord',
    'PriceHistory',
    'InstrumentType',
    'OrderType',
]
