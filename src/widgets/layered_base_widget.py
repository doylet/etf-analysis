"""
Layered base widget class providing separation of concerns architecture.

This base class enforces a three-layer architecture:
1. UI Layer: Streamlit rendering and user interactions
2. Data Layer: Data fetching, validation, and preparation
3. Logic Layer: Pure business logic and calculations

Widgets inheriting from this class should follow the layer separation rules:
- UI methods: Only call st.* functions, no calculations or storage access
- Data methods: Only call self.storage, return validated data structures
- Logic methods: Pure functions, no st.* or self.storage calls
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
from datetime import datetime


class LayeredBaseWidget(ABC):
    """
    Base class for widgets following layered architecture pattern.
    
    Architecture:
    - UI Layer (_render_* methods): Streamlit components only
    - Data Layer (_fetch_*, _prepare_* methods): Storage access only
    - Logic Layer (_calculate_*, _analyze_* methods): Pure functions only
    
    Attributes:
        storage: Database storage adapter instance
        widget_id: Unique identifier for this widget instance
    """
    
    def __init__(self, storage, widget_id: str):
        """
        Initialize widget with storage adapter and unique ID.
        
        Parameters:
            storage: Database storage adapter instance
            widget_id: Unique identifier for session state keys
        """
        self.storage = storage
        self.widget_id = widget_id
    
    @abstractmethod
    def get_name(self) -> str:
        """Return widget display name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return widget description"""
        pass
    
    @abstractmethod
    def get_scope(self) -> str:
        """Return widget scope: 'portfolio', 'single', or 'multiple'"""
        pass
    
    @abstractmethod
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """
        Main render method - orchestrates UI, data, and logic layers.
        
        This method should:
        1. Call UI layer methods to get user inputs
        2. Call data layer methods to fetch required data
        3. Call logic layer methods to perform calculations
        4. Call UI layer methods to display results
        
        Parameters:
            instruments: List of instrument dictionaries from portfolio
            selected_symbols: List of pre-selected symbol strings
        """
        pass
    
    def render_config(self) -> Dict:
        """Render widget configuration options (optional)"""
        return {}
    
    # =========================================================================
    # Session State Helpers
    # =========================================================================
    
    def _get_session_key(self, purpose: str) -> str:
        """
        Generate standardized session state key.
        
        Parameters:
            purpose: Purpose identifier (e.g., 'period', 'selected_holdings')
            
        Returns:
            Formatted session state key: f"{widget_id}_{purpose}"
        """
        return f"{self.widget_id}_{purpose}"
    
    def _init_session_state(self, key: str, default_value: Any) -> Any:
        """
        Initialize session state key if not present.
        
        Parameters:
            key: Session state key
            default_value: Default value if key doesn't exist
            
        Returns:
            Current value from session state
        """
        if key not in st.session_state:
            st.session_state[key] = default_value
        return st.session_state[key]
    
    # =========================================================================
    # Error Handling Helpers
    # =========================================================================
    
    def _handle_data_error(self, error_message: str, details: Optional[str] = None) -> None:
        """
        Display user-friendly data error message.
        
        Parameters:
            error_message: Main error message to display
            details: Optional detailed error information
        """
        st.error(error_message)
        if details:
            with st.expander("Error Details"):
                st.code(details)
    
    def _handle_validation_error(self, validation_message: str, items: Optional[List[str]] = None) -> None:
        """
        Display validation error with affected items.
        
        Parameters:
            validation_message: Validation error message
            items: Optional list of items that failed validation
        """
        st.warning(validation_message)
        if items:
            st.caption(f"Affected items: {', '.join(items)}")
    
    # =========================================================================
    # Loading State Helpers
    # =========================================================================
    
    def _with_loading(self, message: str, func, *args, **kwargs) -> Any:
        """
        Execute function with loading spinner.
        
        Parameters:
            message: Loading message to display
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func execution
        """
        with st.spinner(message):
            return func(*args, **kwargs)
    
    # =========================================================================
    # Data Validation Helpers
    # =========================================================================
    
    @staticmethod
    def _validate_data_completeness(data: Dict[str, Any], required_keys: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that data dictionary contains all required keys.
        
        Parameters:
            data: Data dictionary to validate
            required_keys: List of required key names
            
        Returns:
            Tuple of (is_valid, missing_keys)
        """
        missing_keys = [key for key in required_keys if key not in data or data[key] is None]
        return len(missing_keys) == 0, missing_keys
    
    @staticmethod
    def _validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, str]:
        """
        Validate date range is logical.
        
        Parameters:
            start_date: Start date of range
            end_date: End date of range
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if start_date >= end_date:
            return False, f"Start date ({start_date.date()}) must be before end date ({end_date.date()})"
        if (end_date - start_date).days < 1:
            return False, "Date range must be at least 1 day"
        return True, ""
    
    # =========================================================================
    # Layer Separation Documentation
    # =========================================================================
    
    """
    LAYER SEPARATION RULES:
    
    UI Layer Methods (prefix: _render_):
    - MUST only call st.* functions
    - MUST NOT call self.storage
    - MUST NOT perform calculations
    - MAY call data layer methods to get data
    - MAY call logic layer methods for calculations
    - MAY read/write session state
    - Returns: User selections or None (side effects via st.*)
    
    Data Layer Methods (prefix: _fetch_, _prepare_, _validate_):
    - MUST only call self.storage for data access
    - MUST NOT call st.* functions
    - MUST NOT perform business logic calculations
    - SHOULD validate data quality and completeness
    - SHOULD return typed data structures (dicts, dataclasses, DataFrames)
    - Returns: Data structures or error dicts {'status': 'error', 'message': ...}
    
    Logic Layer Methods (prefix: _calculate_, _analyze_, _compute_):
    - MUST be pure functions (no side effects)
    - MUST NOT call st.* functions
    - MUST NOT call self.storage
    - SHOULD be @staticmethod when possible
    - MUST be unit testable without mocking
    - Takes: Data structures as parameters
    - Returns: Calculation results as data structures
    
    Example Flow:
    
    def render(self, instruments, selected_symbols):
        # UI Layer: Get user input
        period = self._render_period_selector()
        
        # Data Layer: Fetch data
        data_result = self._fetch_price_data(selected_symbols, period)
        if data_result['status'] == 'error':
            st.error(data_result['message'])
            return
        
        # Logic Layer: Calculate
        results = self._calculate_metrics(data_result['data'])
        
        # UI Layer: Display results
        self._render_results(results)
    """
