"""Performance Widget API Adapter."""

from typing import Dict, Any
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.performance_widget import PerformanceWidget

logger = logging.getLogger(__name__)


class PerformanceAdapter(BaseWidgetAdapter):
    """Adapter to expose performance widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, PerformanceWidget)
        
    def get_widget_name(self) -> str:
        return "performance"
        
    def get_widget_description(self) -> str:
        return "Analyze portfolio performance metrics and statistics"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Time period mapping
        period_map = {
            '1W': 7, '1M': 30, '3M': 90, '6M': 180, 
            '1Y': 365, '2Y': 730, '5Y': 1825
        }
        time_period = kwargs.get('time_period', '1Y')
        validated['period_days'] = period_map.get(time_period, 365)
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        import pandas as pd
        import numpy as np
        from src.utils.performance_metrics import calculate_returns, calculate_sharpe_ratio
        from src.api.routers.portfolio import get_portfolio_summary
        
        try:
            # Get parameters from validated_params or use defaults
            period_days = validated_params.get('period_days', 365) if validated_params else 365
            
            # Use centralized portfolio calculation service (single source of truth)
            from src.services.portfolio_service import calculate_portfolio_metrics
            
            total_value, total_cost_basis, portfolio_return, holdings_with_details = calculate_portfolio_metrics()
            
            if not holdings_with_details:
                return {"message": "No holdings found"}
            
            # Create mock portfolio data for compatibility with existing code
            class MockHolding:
                def __init__(self, symbol, quantity):
                    self.symbol = symbol
                    self.quantity = quantity
            
            portfolio_data = type('obj', (object,), {
                'holdings': [MockHolding(symbol, details['quantity']) for symbol, details in holdings_with_details.items()],
                'total_unrealized_gain_loss_pct': portfolio_return
            })()
            
            if not portfolio_data.holdings:
                return {"message": "No holdings found"}
            
            symbols = [h.symbol for h in portfolio_data.holdings]
            
            # Fetch performance data using widget's method for volatility/sharpe
            performance_metrics = widget_instance._fetch_performance_data(symbols, period_days)
            
            if not performance_metrics:
                return {"message": "No price data available for selected period"}
            
            # Use the total return from portfolio endpoint (reuse existing calculation)
            total_return = portfolio_data.total_unrealized_gain_loss_pct
            
            # Calculate annualized return
            years = period_days / 365.0
            if years > 0 and total_return > -100:
                annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100
            else:
                annualized_return = total_return
            
            # Calculate volatility and Sharpe ratio from time series
            portfolio_values = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            for holding in portfolio_data.holdings:
                price_df = self.storage.get_price_data(holding.symbol, start_date, end_date)
                if price_df is not None and not price_df.empty:
                    # Use the holding's current value to get position size
                    position_values = price_df['close'] * holding.quantity
                    portfolio_values.append(position_values)
            
            # Calculate volatility from time series if available
            if portfolio_values:
                total_portfolio_value = pd.concat(portfolio_values, axis=1).sum(axis=1)
                portfolio_returns_series = calculate_returns(total_portfolio_value)
                volatility = portfolio_returns_series.std() * np.sqrt(252) * 100
                sharpe = calculate_sharpe_ratio(portfolio_returns_series)
            else:
                volatility = 0.0
                sharpe = 0.0
            
            return {
                "total_return": float(total_return),
                "annualized_return": float(annualized_return),
                "volatility": float(volatility),
                "sharpe_ratio": float(sharpe),
                "holdings_analyzed": len(performance_metrics),
                "period_days": period_days
            }
        except Exception as e:
            logger.error(f"Performance extraction failed: {e}")
            return {"error": str(e)}
    
