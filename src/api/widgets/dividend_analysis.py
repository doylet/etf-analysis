"""Dividend Analysis Widget API Adapter."""

from typing import Dict, Any
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.dividend_analysis_widget import DividendAnalysisWidget

logger = logging.getLogger(__name__)


class DividendAnalysisAdapter(BaseWidgetAdapter):
    """Adapter to expose dividend analysis widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, DividendAnalysisWidget)
        
    def get_widget_name(self) -> str:
        return "dividend_analysis"
        
    def get_widget_description(self) -> str:
        return "Analyze dividend income and yield metrics"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters for dividend analysis."""
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Validate time_period
        time_period = kwargs.get('time_period', 'All')
        valid_periods = ['All', '1Y', '2Y', '5Y']
        if time_period not in valid_periods:
            raise WidgetValidationError(f"time_period must be one of {valid_periods}")
        validated['time_period'] = time_period
        
        # Validate symbol filter
        symbol_filter = kwargs.get('symbol')
        if symbol_filter is not None:
            if isinstance(symbol_filter, str):
                validated['symbol'] = symbol_filter.strip().upper()
            elif isinstance(symbol_filter, list):
                validated['symbol'] = [s.strip().upper() for s in symbol_filter if isinstance(s, str)]
            else:
                raise WidgetValidationError("symbol must be a string or list of strings")
        else:
            validated['symbol'] = None
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract dividend analysis calculation data from widget."""
        from datetime import datetime
        
        if validated_params is None:
            validated_params = {}
        
        time_period = validated_params.get('time_period', 'All')
        symbol_filter = validated_params.get('symbol')
        
        try:
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available for dividend analysis"}
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings for dividend analysis"}
            
            # Apply symbol filter if specified
            if symbol_filter:
                if isinstance(symbol_filter, str):
                    holdings = [h for h in holdings if h['symbol'] == symbol_filter]
                else:
                    holdings = [h for h in holdings if h['symbol'] in symbol_filter]
            
            symbols = [h['symbol'] for h in holdings]
            
            # Fetch dividend summary using widget's method
            summary = widget_instance._fetch_dividend_summary(symbols)
            
            # Calculate yield based on current portfolio value
            total_value = sum(
                h.get('quantity', 0) * h.get('last_price', 0) 
                for h in holdings
            )
            
            dividend_yield = (summary.total_1y / total_value * 100) if total_value > 0 else 0
            
            # Get top dividend holdings
            top_holdings = []
            for item in summary.symbol_breakdown[:5]:
                if isinstance(item, dict):
                    top_holdings.append({
                        "symbol": item.get('symbol', ''),
                        "amount": float(item.get('amount', 0)),
                        "yield": 0.0  # Would need price data to calculate
                    })
            
            return {
                "total_dividends": float(summary.total_1y),
                "dividend_yield": float(dividend_yield),
                "ytd_dividends": float(summary.total_ytd),
                "all_time_dividends": float(summary.total_all_time),
                "top_dividend_holdings": top_holdings,
                "holdings_analyzed": len(symbols)
            }
        except Exception as e:
            logger.error(f"Dividend analysis extraction failed: {e}")
            return {"error": str(e)}
    