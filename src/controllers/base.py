"""
Base controller class with dependency injection
"""

from abc import ABC, abstractmethod


class BaseController(ABC):
    """Abstract base controller class for dependency injection and state management"""
    
    def __init__(self, storage, **kwargs):
        """
        Initialize controller with dependencies
        
        Args:
            storage: DataStorageAdapter instance
            **kwargs: Additional dependencies (av_client, etc.)
        """
        self.storage = storage
        
        # Inject optional dependencies
        self.av_client = kwargs.get('av_client')
        
        # Initialize state management
        self._state = {}
        
        # Call subclass initialization
        self._init_dependencies(**kwargs)
    
    def _init_dependencies(self, **kwargs):
        """
        Hook for subclasses to initialize additional dependencies
        Override this method to handle custom dependencies
        """
        pass
    
    def _set_state(self, key, value):
        """
        Set a state value
        
        Args:
            key: State key
            value: State value
        """
        self._state[key] = value
    
    def _get_state(self, key, default=None):
        """
        Get a state value
        
        Args:
            key: State key
            default: Default value if key doesn't exist
            
        Returns:
            State value or default
        """
        return self._state.get(key, default)
    
    def _load_instruments(self, active_only=True):
        """
        Load instruments from storage and cache in state
        
        Args:
            active_only: Only return active instruments
            
        Returns:
            List of instruments
        """
        instruments = self.storage.get_all_instruments(active_only=active_only)
        self._set_state('instruments', instruments)
        return instruments
    
    def _load_latest_prices(self, symbols):
        """
        Load latest prices from storage and cache in state
        
        Args:
            symbols: List of symbols to load prices for
            
        Returns:
            Dictionary of latest prices by symbol
        """
        latest_prices = self.storage.get_latest_prices(symbols)
        self._set_state('latest_prices', latest_prices)
        return latest_prices
    
    @property
    def instruments(self):
        """Get cached instruments"""
        return self._get_state('instruments', [])
    
    @property
    def latest_prices(self):
        """Get cached latest prices"""
        return self._get_state('latest_prices', {})
    
    @abstractmethod
    def render(self):
        """Render the page - must be implemented by subclasses"""
        pass
