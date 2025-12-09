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
        
        try:
            # Get parameters from validated_params or use defaults
            period_days = validated_params.get('period_days', 365) if validated_params else 365
            
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available"}
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings"}
            
            # Get symbols and calculate performance
            symbols = [h['symbol'] for h in holdings]
            
            # Fetch performance data using widget's method
            performance_metrics = widget_instance._fetch_performance_data(symbols, period_days)
            
            if not performance_metrics:
                return {"message": "No price data available for selected period"}
            
            # Calculate aggregate portfolio metrics from individual holdings
            total_change_pct = sum(m.change_pct for m in performance_metrics) / len(performance_metrics)
            
            # Calculate portfolio-level metrics
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Calculate weighted portfolio returns
            portfolio_returns = []
            portfolio_values = []
            
            for holding in holdings:
                symbol = holding['symbol']
                quantity = holding.get('quantity', 0)
                
                if quantity <= 0:
                    continue
                
                price_df = self.storage.get_price_data(symbol, start_date, end_date)
                if price_df is not None and not price_df.empty:
                    # Calculate position values
                    position_values = price_df['close'] * quantity
                    portfolio_values.append(position_values)
            
            if portfolio_values:
                # Sum all position values to get total portfolio value
                total_portfolio_value = pd.concat(portfolio_values, axis=1).sum(axis=1)
                portfolio_returns_series = calculate_returns(total_portfolio_value)
                
                total_return = (total_portfolio_value.iloc[-1] / total_portfolio_value.iloc[0] - 1) * 100
                annualized_return = ((1 + total_return / 100) ** (252 / len(total_portfolio_value)) - 1) * 100
                volatility = portfolio_returns_series.std() * np.sqrt(252) * 100
                sharpe = calculate_sharpe_ratio(portfolio_returns_series)
            else:
                total_return = total_change_pct
                annualized_return = total_change_pct
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
    
