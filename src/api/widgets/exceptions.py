"""Widget-specific exceptions and error handling."""

from typing import Dict, Any, Optional


class WidgetError(Exception):
    """Base exception for widget API errors."""
    
    def __init__(self, message: str, code: str = "WIDGET_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class WidgetValidationError(WidgetError):
    """Raised when widget input parameters fail validation."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class WidgetCalculationError(WidgetError):
    """Raised when widget calculation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CALCULATION_ERROR", details=details)


class WidgetDataError(WidgetError):
    """Raised when widget cannot access required data."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="DATA_ERROR", details=details)


class WidgetTimeoutError(WidgetError):
    """Raised when widget calculation exceeds time limit."""
    
    def __init__(self, message: str, timeout_seconds: float):
        super().__init__(message, code="TIMEOUT_ERROR", details={"timeout_seconds": timeout_seconds})


class WidgetConfigurationError(WidgetError):
    """Raised when widget is misconfigured."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)