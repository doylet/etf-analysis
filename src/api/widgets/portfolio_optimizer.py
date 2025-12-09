"""Portfolio Optimizer Widget API Adapter."""

from typing import Dict, Any, List
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.portfolio_optimizer_widget import PortfolioOptimizerWidget

logger = logging.getLogger(__name__)


class PortfolioOptimizerAdapter(BaseWidgetAdapter):
    """Adapter to expose portfolio optimizer widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, PortfolioOptimizerWidget)
        
    def get_widget_name(self) -> str:
        return "portfolio_optimizer"
        
    def get_widget_description(self) -> str:
        return "Optimize portfolio allocation for risk/return"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Validate mode
        mode = kwargs.get('mode', 'Max Sharpe')
        valid_modes = ['Efficient Frontier', 'Max Sharpe', 'Min Volatility', 'Max Return', 'Target Return']
        if mode not in valid_modes:
            raise WidgetValidationError(f"mode must be one of {valid_modes}")
        validated['mode'] = mode
        
        # Validate time_period
        time_period = kwargs.get('time_period', '1Y')
        valid_periods = ['1M', '3M', '6M', '1Y', '2Y', '5Y']
        if time_period not in valid_periods:
            raise WidgetValidationError(f"time_period must be one of {valid_periods}")
        validated['time_period'] = time_period
        
        # Validate target_return
        target_return = kwargs.get('target_return')
        if target_return is not None:
            try:
                target_return = float(target_return)
                if target_return < -100 or target_return > 1000:
                    raise WidgetValidationError("target_return must be between -100 and 1000")
                validated['target_return'] = target_return
            except (TypeError, ValueError):
                raise WidgetValidationError("target_return must be a number")
        else:
            validated['target_return'] = None
        
        # Validate include_dividends
        include_dividends = kwargs.get('include_dividends', True)
        if not isinstance(include_dividends, bool):
            raise WidgetValidationError("include_dividends must be a boolean")
        validated['include_dividends'] = include_dividends
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        import numpy as np
        
        if validated_params is None:
            validated_params = {}
        
        mode = validated_params.get('mode', 'Max Sharpe')
        time_period = validated_params.get('time_period', '1Y')
        target_return = validated_params.get('target_return')
        include_dividends = validated_params.get('include_dividends', True)
        
        # Map time_period to days
        period_map = {'1M': 30, '3M': 90, '6M': 180, '1Y': 365, '2Y': 730, '5Y': 1825}
        days = period_map.get(time_period, 365)
        
        try:
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available"}
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings"}
            
            symbols = [h['symbol'] for h in holdings]
            
            # Fetch returns data
            returns_df = widget_instance._fetch_returns_data(symbols, days, include_dividends=include_dividends)
            
            if returns_df is None or returns_df.empty:
                return {"message": "No price data available for optimization"}
            
            # Calculate current portfolio metrics
            current_metrics = widget_instance._calculate_current_portfolio_metrics(
                symbols, returns_df
            )
            
            if current_metrics is None:
                return {"message": "Cannot calculate current portfolio metrics"}
            
            # Optimize for maximum Sharpe ratio
            optimized = widget_instance._optimize_for_max_sharpe(returns_df)
            
            if optimized is None:
                return {
                    "expected_return": float(current_metrics.expected_return * 100),
                    "expected_risk": float(current_metrics.volatility * 100),
                    "sharpe_ratio": float(current_metrics.sharpe_ratio),
                    "message": "Current portfolio metrics only"
                }
            
            # Calculate improvements
            return_improvement = (optimized.expected_return - current_metrics.expected_return) * 100
            risk_reduction = (current_metrics.volatility - optimized.volatility) * 100
            sharpe_improvement = optimized.sharpe_ratio - current_metrics.sharpe_ratio
            
            return {
                "expected_return": float(optimized.expected_return * 100),
                "expected_risk": float(optimized.volatility * 100),
                "sharpe_ratio": float(optimized.sharpe_ratio),
                "improvement_metrics": {
                    "return_improvement": float(return_improvement),
                    "risk_reduction": float(risk_reduction),
                    "sharpe_improvement": float(sharpe_improvement)
                },
                "current_return": float(current_metrics.expected_return * 100),
                "current_risk": float(current_metrics.volatility * 100),
                "current_sharpe": float(current_metrics.sharpe_ratio),
                "holdings_analyzed": len(symbols)
            }
        except Exception as e:
            logger.error(f"Portfolio optimizer extraction failed: {e}")
            return {"error": str(e)}
    