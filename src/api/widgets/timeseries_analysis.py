"""Timeseries Analysis Widget API Adapter."""

from typing import Dict, Any
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.timeseries_analysis_widget import TimeSeriesAnalysisWidget

logger = logging.getLogger(__name__)


class TimeseriesAnalysisAdapter(BaseWidgetAdapter):
    """Adapter to expose timeseries analysis widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, TimeSeriesAnalysisWidget)
        
    def get_widget_name(self) -> str:
        return "timeseries_analysis"
        
    def get_widget_description(self) -> str:
        return "Analyze portfolio value over time with trends"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Validate time_period
        time_period = kwargs.get('time_period', '1Y')
        valid_periods = ['1W', '1M', '3M', '6M', '1Y', '2Y', '5Y', 'All']
        if time_period not in valid_periods:
            raise WidgetValidationError(f"time_period must be one of {valid_periods}")
        validated['time_period'] = time_period
        
        # Validate analysis_type
        analysis_type = kwargs.get('analysis_type', 'Portfolio Overview')
        valid_types = ['Portfolio Overview', 'Stationarity', 'Seasonality', 'Trend Analysis', 'Volatility']
        if analysis_type not in valid_types:
            raise WidgetValidationError(f"analysis_type must be one of {valid_types}")
        validated['analysis_type'] = analysis_type
        
        # Validate symbol filter
        symbol = kwargs.get('symbol')
        if symbol is not None:
            if isinstance(symbol, str):
                validated['symbol'] = symbol.strip().upper()
            elif isinstance(symbol, list):
                validated['symbol'] = [s.strip().upper() for s in symbol if isinstance(s, str)]
            else:
                raise WidgetValidationError("symbol must be a string or list of strings")
        else:
            validated['symbol'] = None
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        import pandas as pd
        import numpy as np
        from src.utils.performance_metrics import calculate_returns
        
        if validated_params is None:
            validated_params = {}
        
        time_period = validated_params.get('time_period', '1Y')
        analysis_type = validated_params.get('analysis_type', 'Portfolio Overview')
        symbol_filter = validated_params.get('symbol')
        
        # Map time_period to lookback_days
        period_map = {'1W': 7, '1M': 30, '3M': 90, '6M': 180, '1Y': 365, '2Y': 730, '5Y': 1825, 'All': 3650}
        lookback_days = period_map.get(time_period, 365)
        
        try:
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available"}
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings"}
            
            # Apply symbol filter if specified
            if symbol_filter:
                if isinstance(symbol_filter, str):
                    holdings = [h for h in holdings if h['symbol'] == symbol_filter]
                else:
                    holdings = [h for h in holdings if h['symbol'] in symbol_filter]
            
            # Calculate portfolio returns
            portfolio_returns, holding_details = widget_instance._calculate_portfolio_returns(
                holdings, lookback_days
            )
            
            if portfolio_returns is None or portfolio_returns.empty:
                return {"message": "No price data available for timeseries analysis"}
            
            # Calculate statistics
            total_return = ((1 + portfolio_returns).prod() - 1) * 100
            volatility = portfolio_returns.std() * np.sqrt(252) * 100
            
            from src.utils.performance_metrics import calculate_sharpe_ratio
            sharpe = calculate_sharpe_ratio(portfolio_returns)
            
            # Calculate max drawdown
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # Prepare price data for frontend (last 100 points)
            price_data = []
            if len(cumulative) > 0:
                step = max(1, len(cumulative) // 100)
                for i in range(0, len(cumulative), step):
                    price_data.append({
                        "date": cumulative.index[i].isoformat(),
                        "value": float(cumulative.iloc[i])
                    })
            
            return {
                "statistics": {
                    "total_return": float(total_return),
                    "volatility": float(volatility),
                    "sharpe_ratio": float(sharpe),
                    "max_drawdown": float(max_drawdown)
                },
                "price_data": price_data,
                "holdings_analyzed": len(holdings),
                "period_days": lookback_days
            }
        except Exception as e:
            logger.error(f"Timeseries analysis extraction failed: {e}")
            return {"error": str(e)}
