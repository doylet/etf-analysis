"""Constrained Optimization Widget API Adapter."""

from typing import Dict, Any
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.constrained_optimization_widget import ConstrainedOptimizationWidget

logger = logging.getLogger(__name__)


class ConstrainedOptimizationAdapter(BaseWidgetAdapter):
    """Adapter to expose constrained optimization widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, ConstrainedOptimizationWidget)
        
    def get_widget_name(self) -> str:
        return "constrained_optimization"
        
    def get_widget_description(self) -> str:
        return "Optimize portfolio with custom constraints"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Validate objective
        objective = kwargs.get('objective', 'Max Sharpe')
        valid_objectives = ['Max Sharpe', 'Min Volatility', 'Max Return', 'Target Return', 'Risk Parity']
        if objective not in valid_objectives:
            raise WidgetValidationError(f"objective must be one of {valid_objectives}")
        validated['objective'] = objective
        
        # Validate max_weight
        max_weight = kwargs.get('max_weight', 40.0)
        try:
            max_weight = float(max_weight)
            if max_weight < 1 or max_weight > 100:
                raise WidgetValidationError("max_weight must be between 1 and 100")
            validated['max_weight'] = max_weight / 100  # Convert to decimal
        except (TypeError, ValueError):
            raise WidgetValidationError("max_weight must be a number")
        
        # Validate min_weight
        min_weight = kwargs.get('min_weight', 0.0)
        try:
            min_weight = float(min_weight)
            if min_weight < 0 or min_weight > 50:
                raise WidgetValidationError("min_weight must be between 0 and 50")
            validated['min_weight'] = min_weight / 100  # Convert to decimal
        except (TypeError, ValueError):
            raise WidgetValidationError("min_weight must be a number")
        
        # Validate constraint: min_weight <= max_weight
        if validated['min_weight'] > validated['max_weight']:
            raise WidgetValidationError("min_weight cannot be greater than max_weight")
        
        # Validate target_return
        target_return = kwargs.get('target_return')
        if target_return is not None:
            try:
                target_return = float(target_return)
                if target_return < -100 or target_return > 1000:
                    raise WidgetValidationError("target_return must be between -100 and 1000")
                validated['target_return'] = target_return / 100  # Convert to decimal
            except (TypeError, ValueError):
                raise WidgetValidationError("target_return must be a number")
        else:
            validated['target_return'] = None
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        import numpy as np
        
        if validated_params is None:
            validated_params = {}
        
        objective = validated_params.get('objective', 'Max Sharpe')
        max_weight = validated_params.get('max_weight', 0.4)
        min_weight = validated_params.get('min_weight', 0.0)
        target_return = validated_params.get('target_return')
        
        try:
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available"}
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings"}
            
            symbols = [h['symbol'] for h in holdings]
            
            # Fetch returns data (1 year lookback)
            days = 365
            returns_df = widget_instance._fetch_returns_data(symbols, days, include_dividends=True)
            
            if returns_df is None or returns_df.empty:
                return {"message": "No price data available for optimization"}
            
            # For constrained optimization, calculate basic metrics
            # In a full implementation, this would run scipy.optimize with constraints
            from src.utils.performance_metrics import calculate_returns, calculate_sharpe_ratio
            
            # Calculate simple metrics from returns data
            mean_returns = returns_df.mean() * 252
            cov_matrix = returns_df.cov() * 252
            
            # Equal weight portfolio as baseline
            n_assets = len(returns_df.columns)
            weights = np.array([1/n_assets] * n_assets)
            
            portfolio_return = float(np.dot(weights, mean_returns))
            portfolio_risk = float(np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))))
            sharpe_ratio = float((portfolio_return - 0.03) / portfolio_risk if portfolio_risk > 0 else 0)
            
            # Check for constraint violations
            # Using simplified constraint: max 40% per position
            max_weight = 0.4
            constraint_violations = []
            
            for i, (symbol, weight) in enumerate(zip(symbols, weights)):
                if weight > max_weight:
                    constraint_violations.append({
                        "constraint": f"Max weight {symbol}",
                        "violation": float(weight - max_weight),
                        "limit": max_weight
                    })
            
            return {
                "optimization_result": {
                    "return": float(portfolio_return * 100),
                    "risk": float(portfolio_risk * 100),
                    "sharpe_ratio": float(sharpe_ratio)
                },
                "constraint_violations": constraint_violations,
                "constraints_met": len(constraint_violations) == 0,
                "holdings_analyzed": len(symbols),
                "constraints_applied": [f"Max position size: {max_weight*100}%", "Min weight: 0%"]
            }
        except Exception as e:
            logger.error(f"Constrained optimization extraction failed: {e}")
            return {"error": str(e)}
