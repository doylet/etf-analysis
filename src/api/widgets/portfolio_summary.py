"""Portfolio Summary Widget API Adapter."""

from typing import Dict, Any
from datetime import datetime
import logging

from api.widgets.base import BaseWidgetAdapter
from api.widgets.exceptions import WidgetDataError, WidgetValidationError
from api.schemas.widgets import PortfolioSummaryData
from widgets.portfolio_summary_widget import PortfolioSummaryWidget

logger = logging.getLogger(__name__)


class PortfolioSummaryAdapter(BaseWidgetAdapter):
    """Adapter to expose portfolio summary widget through API."""
    
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
        """
        try:
            # Get instruments data from storage
            instruments = self.storage.get_all_instruments()
            
            if not instruments:
                raise WidgetDataError("No instruments found in portfolio")
                
            # Get holdings with quantities > 0 (same as widget logic)
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                # Return zero values for empty portfolio
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
            
            # Calculate metrics using the widget's calculation method
            metrics = widget_instance._calculate_all_metrics(holdings)
            
            if not metrics:
                raise WidgetDataError("Unable to calculate portfolio metrics - no price data available")
            
            # Calculate basic portfolio summary data
            total_positions = len(holdings)
            allocated_cash = sum(h.get('cash_allocation', 0.0) for h in holdings)
            
            # Calculate day change (simplified - would need historical prices for accuracy)
            day_change = 0.0  # Placeholder - would need yesterday's prices
            day_change_percent = 0.0  # Placeholder
            
            # Create portfolio summary response data
            return {
                "total_value": float(metrics.total_value),
                "total_return": float(metrics.total_return_with_divs * metrics.total_value if metrics.total_value > 0 else 0),
                "total_return_percent": float(metrics.total_return_with_divs * 100),
                "day_change": day_change,
                "day_change_percent": day_change_percent,
                "positions": total_positions,
                "allocated_cash": allocated_cash,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error extracting portfolio summary data: {e}", exc_info=True)
            raise WidgetDataError(f"Failed to extract portfolio summary: {str(e)}")
            
    def _create_widget_instance(self, validated_params: Dict[str, Any]):
        """Create portfolio summary widget instance."""
        widget_id = f"portfolio_summary_{hash(str(validated_params))}"
        widget = self.widget_class(self.storage, widget_id)
        
        # Set portfolio ID if provided
        if validated_params.get('portfolio_id'):
            widget.portfolio_id = validated_params['portfolio_id']
            
        return widget