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
        
        This method carefully extracts only the calculation results without
        triggering any Streamlit UI components (constitution compliance).
        
        Raises:
            WidgetDataError: When insufficient data is available for calculation
        """
        try:
            # Get instruments data from storage
            instruments = self.storage.get_all_instruments()
            
            if not instruments:
                logger.warning("No instruments found in database")
                raise WidgetDataError(
                    "No instruments found in portfolio. Please add some positions first.",
                    error_code="NO_INSTRUMENTS"
                )
                
            # Get holdings with quantities > 0 (same as widget logic)
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
            
            # Verify we have price data for holdings
            holdings_with_prices = [h for h in holdings if h.get('current_price') is not None]
            if not holdings_with_prices:
                logger.error("Holdings found but no current price data available")
                raise WidgetDataError(
                    "Holdings found but no current price data available. Please check data connections.",
                    error_code="NO_PRICE_DATA"
                )
            
            if len(holdings_with_prices) < len(holdings):
                logger.warning(
                    f"Price data missing for {len(holdings) - len(holdings_with_prices)} out of {len(holdings)} holdings"
                )
            
            # Calculate metrics using the widget's calculation method
            try:
                metrics = widget_instance._calculate_all_metrics(holdings_with_prices)
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
            
            # Validate calculated metrics
            if not hasattr(metrics, 'total_value') or metrics.total_value is None:
                raise WidgetDataError(
                    "Invalid calculation result: missing total_value",
                    error_code="INVALID_METRICS"
                )
            
            # Calculate basic portfolio summary data
            total_positions = len(holdings_with_prices)
            allocated_cash = sum(h.get('cash_allocation', 0.0) for h in holdings_with_prices)
            
            # Calculate day change (simplified - would need historical prices for accuracy)
            day_change = 0.0  # Placeholder - would need yesterday's prices
            day_change_percent = 0.0  # Placeholder
            
            # Calculate total return amount (convert percentage to amount)
            total_return_amount = (
                metrics.total_return_with_divs * metrics.total_value 
                if metrics.total_value > 0 else 0
            )
            
            # Create portfolio summary response data
            result = {
                "total_value": float(metrics.total_value),
                "total_return": float(total_return_amount),
                "total_return_percent": float(metrics.total_return_with_divs * 100),
                "day_change": day_change,
                "day_change_percent": day_change_percent,
                "positions": total_positions,
                "allocated_cash": allocated_cash,
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