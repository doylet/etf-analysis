"""Portfolio Summary Widget API Adapter."""

from typing import Dict, Any
from datetime import datetime
import logging

from api.widgets.base import BaseWidgetAdapter
from api.widgets.exceptions import WidgetDataError, WidgetValidationError
from api.schemas.widgets import PortfolioSummaryData
from api.services.widget_cache import widget_cache
from api.services.performance_monitor import monitor_widget_performance
from widgets.portfolio_summary_widget import PortfolioSummaryWidget

logger = logging.getLogger(__name__)


class PortfolioSummaryAdapter(BaseWidgetAdapter):
    """Adapter to expose portfolio summary widget through API."""
    
    # Portfolio summary cache TTL (5 minutes - frequent updates expected)
    CACHE_TTL_MINUTES = 5
    
    def __init__(self, storage):
        super().__init__(storage, PortfolioSummaryWidget)
        
    def get_widget_name(self) -> str:
        return "portfolio_summary"
        
    def get_widget_description(self) -> str:
        return "Portfolio performance metrics including total value, returns, and position count"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters for portfolio summary."""
        validated = {}
        
        # Portfolio ID is optional - if not provided, use default portfolio
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
            
        return validated
        
    def extract_calculation_data(self, widget_instance) -> Dict[str, Any]:
        """Extract portfolio summary calculation data from widget.
        
        This method properly delegates to the existing widget's calculation logic
        without duplicating any business logic (proper adapter pattern).
        
        Raises:
            WidgetDataError: When insufficient data is available for calculation
        """
        try:
            # Get instruments data from storage (same as widget does)
            instruments = self.storage.get_all_instruments()
            
            if not instruments:
                logger.warning("No instruments found in database")
                raise WidgetDataError(
                    "No instruments found in portfolio. Please add some positions first.",
                    error_code="NO_INSTRUMENTS"
                )
                
            # Get holdings with quantities > 0 (same logic as widget)
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                logger.info("Portfolio exists but all positions have zero quantity")
                # Return zero values for empty portfolio with valid structure
                return {
                    "total_value": 0.0,
                    "total_return": 0.0,
                    "total_return_percent": 0.0,
                    "day_change": 0.0,
                    "day_change_percent": 0.0,
                    "positions": 0,
                    "allocated_cash": 0.0,
                    "last_updated": datetime.utcnow()
                }
            
            # **DELEGATE TO EXISTING WIDGET** - This is the key change!
            # Use the existing widget's calculation method instead of rewriting logic
            try:
                metrics = widget_instance._calculate_all_metrics(holdings)
            except Exception as calc_error:
                logger.error(f"Widget calculation failed: {calc_error}")
                raise WidgetDataError(
                    f"Portfolio calculation failed: {str(calc_error)}",
                    error_code="CALCULATION_ERROR"
                )
            
            if not metrics:
                raise WidgetDataError(
                    "Widget calculation returned empty results - check data quality",
                    error_code="EMPTY_METRICS"
                )
            
            # Convert the existing widget's PortfolioMetrics to API response format
            # This is pure data transformation, not business logic duplication
            total_return_amount = (
                metrics.total_return_with_divs * metrics.total_value 
                if metrics.total_value > 0 else 0
            )
            
            # Create API response using existing widget's calculated data
            result = {
                "total_value": float(metrics.total_value),
                "total_return": float(total_return_amount),
                "total_return_percent": float(metrics.total_return_with_divs * 100),
                "day_change": 0.0,  # TODO: Add day change calculation to existing widget
                "day_change_percent": 0.0,  # TODO: Add day change calculation to existing widget
                "positions": len(holdings),
                "allocated_cash": 0.0,  # TODO: Extract from widget if available
                "last_updated": datetime.utcnow()
            }
            
            # Validate result structure
            self._validate_summary_result(result)
            
            return result
            
        except WidgetDataError:
            # Re-raise widget data errors as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting portfolio summary data: {e}", exc_info=True)
            raise WidgetDataError(
                f"Failed to extract portfolio summary: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )
    
    def _validate_summary_result(self, result: Dict[str, Any]):
        """Validate portfolio summary result structure and values."""
        required_fields = [
            "total_value", "total_return", "total_return_percent",
            "day_change", "day_change_percent", "positions",
            "allocated_cash", "last_updated"
        ]
        
        for field in required_fields:
            if field not in result:
                raise WidgetDataError(
                    f"Missing required field in result: {field}",
                    error_code="INVALID_RESULT_STRUCTURE"
                )
        
        # Validate numeric values
        numeric_fields = [
            "total_value", "total_return", "total_return_percent",
            "day_change", "day_change_percent", "allocated_cash"
        ]
        
        for field in numeric_fields:
            value = result[field]
            if not isinstance(value, (int, float)) or not isinstance(value, bool):
                try:
                    result[field] = float(value)
                except (ValueError, TypeError):
                    raise WidgetDataError(
                        f"Invalid numeric value for {field}: {value}",
                        error_code="INVALID_NUMERIC_VALUE"
                    )
        
        # Validate positions count
            if not isinstance(result["positions"], int) or result["positions"] < 0:
                raise WidgetDataError(
                    f"Invalid positions count: {result['positions']}",
                    error_code="INVALID_POSITIONS_COUNT"
                )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute portfolio summary with caching and performance monitoring."""
        # Validate parameters
        validated_params = self.validate_input_parameters(**kwargs)
        
        # Check cache first
        cache_key = f"portfolio_summary_{str(validated_params)}"
        cached_result = widget_cache.get(self.get_widget_name(), validated_params)
        
        if cached_result:
            logger.debug(f"Cache hit for portfolio summary: {cache_key}")
            # Add cache metadata
            cached_result["metadata"] = cached_result.get("metadata", {})
            cached_result["metadata"]["cache_hit"] = True
            cached_result["metadata"]["cached_at"] = cached_result.get("cached_at")
            return cached_result
        
        # Execute calculation with performance monitoring
        with monitor_widget_performance(self.get_widget_name(), validated_params):
            try:
                # Create widget instance and execute calculation
                widget_instance = self._create_widget_instance(validated_params)
                calculation_data = self.extract_calculation_data(widget_instance)
                
                # Prepare response
                result = {
                    "widget_name": self.get_widget_name(),
                    "success": True,
                    "data": calculation_data,
                    "metadata": {
                        "execution_time": datetime.now().isoformat(),
                        "parameters": validated_params,
                        "widget_description": self.get_widget_description(),
                        "cache_hit": False
                    },
                    "error": None
                }
                
                # Cache the successful result
                widget_cache.set(
                    self.get_widget_name(), 
                    validated_params, 
                    result,
                    ttl_minutes=self.CACHE_TTL_MINUTES
                )
                
                logger.debug(f"Portfolio summary calculated and cached: {cache_key}")
                return result
                
            except Exception as e:
                logger.error(f"Portfolio summary calculation failed: {e}")
                # Don't cache errors, return them directly
                return {
                    "widget_name": self.get_widget_name(),
                    "success": False,
                    "data": None,
                    "metadata": {
                        "execution_time": datetime.now().isoformat(),
                        "parameters": validated_params,
                        "widget_description": self.get_widget_description(),
                        "cache_hit": False
                    },
                    "error": {
                        "code": getattr(e, 'code', 'CALCULATION_ERROR'),
                        "message": str(e),
                        "details": getattr(e, 'details', {})
                    }
                }
    
    def _create_widget_instance(self, validated_params: Dict[str, Any]):
        """Create portfolio summary widget instance."""
        widget_id = f"portfolio_summary_{hash(str(validated_params))}"
        widget = self.widget_class(self.storage, widget_id)
        
        # Set portfolio ID if provided
        if validated_params.get('portfolio_id'):
            widget.portfolio_id = validated_params['portfolio_id']
            
        return widget