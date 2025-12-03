"""
Base Repository Interfaces

Defines abstract base classes for repository pattern implementation.
All repositories should inherit from these interfaces to ensure consistent CRUD operations.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from datetime import datetime


# Generic type for domain models
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository providing common CRUD interface.
    
    Type parameter T represents the domain model type returned by this repository.
    """
    
    @abstractmethod
    def find_by_id(self, id: Any) -> Optional[T]:
        """
        Find entity by ID.
        
        Args:
            id: Entity identifier
            
        Returns:
            Domain model instance or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        Find all entities with optional pagination.
        
        Args:
            limit: Maximum number of results (None for all)
            offset: Number of results to skip
            
        Returns:
            List of domain model instances
        """
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """
        Create new entity.
        
        Args:
            entity: Domain model instance to create
            
        Returns:
            Created domain model with generated ID
        """
        pass
    
    @abstractmethod
    def update(self, id: Any, updates: Dict[str, Any]) -> Optional[T]:
        """
        Update existing entity.
        
        Args:
            id: Entity identifier
            updates: Dictionary of field names and new values
            
        Returns:
            Updated domain model or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """
        Delete entity by ID.
        
        Args:
            id: Entity identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass


class ReadOnlyRepository(ABC, Generic[T]):
    """
    Abstract base repository for read-only access (e.g., external data sources).
    """
    
    @abstractmethod
    def find_by_id(self, id: Any) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Find all entities with pagination."""
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 100) -> List[T]:
        """
        Search entities by query string.
        
        Args:
            query: Search query (implementation-specific)
            limit: Maximum results
            
        Returns:
            List of matching domain models
        """
        pass


class TimeSeriesRepository(ABC, Generic[T]):
    """
    Abstract base repository for time-series data (prices, returns, etc.).
    """
    
    @abstractmethod
    def get_range(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[T]:
        """
        Get time series data for symbol in date range.
        
        Args:
            symbol: Instrument symbol
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            List of time-series data points
        """
        pass
    
    @abstractmethod
    def get_latest(self, symbol: str, limit: int = 1) -> List[T]:
        """
        Get most recent data points for symbol.
        
        Args:
            symbol: Instrument symbol
            limit: Number of recent points
            
        Returns:
            List of most recent data points (newest first)
        """
        pass
    
    @abstractmethod
    def store(self, symbol: str, data: List[T]) -> bool:
        """
        Store time series data for symbol.
        
        Args:
            symbol: Instrument symbol
            data: List of data points to store
            
        Returns:
            True if successful
        """
        pass
