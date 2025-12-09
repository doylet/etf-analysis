"""Portfolio Transition Widget API Adapter."""

from typing import Dict, Any
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.portfolio_transition_widget import PortfolioTransitionWidget

logger = logging.getLogger(__name__)


class PortfolioTransitionAdapter(BaseWidgetAdapter):
    """Adapter to expose portfolio transition widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, PortfolioTransitionWidget)
        
    def get_widget_name(self) -> str:
        return "portfolio_transition"
        
    def get_widget_description(self) -> str:
        return "Analyze portfolio transitions and rebalancing"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Validate transition_method
        transition_method = kwargs.get('transition_method', 'Gradual')
        valid_methods = ['Immediate', 'Gradual', 'Tax Optimized', 'Cost Minimized']
        if transition_method not in valid_methods:
            raise WidgetValidationError(f"transition_method must be one of {valid_methods}")
        validated['transition_method'] = transition_method
        
        # Validate optimization_priority
        optimization_priority = kwargs.get('optimization_priority', 'Balance')
        valid_priorities = ['Cost', 'Speed', 'Tax Efficiency', 'Balance']
        if optimization_priority not in valid_priorities:
            raise WidgetValidationError(f"optimization_priority must be one of {valid_priorities}")
        validated['optimization_priority'] = optimization_priority
        
        # Validate target_weights
        target_weights = kwargs.get('target_weights')
        if target_weights is not None:
            if not isinstance(target_weights, dict):
                raise WidgetValidationError("target_weights must be a dictionary")
            # Validate that all values are numeric and sum close to 100
            try:
                total = sum(float(v) for v in target_weights.values())
                if abs(total - 100) > 1:
                    raise WidgetValidationError("target_weights must sum to approximately 100%")
                validated['target_weights'] = {k: float(v) for k, v in target_weights.items()}
            except (TypeError, ValueError):
                raise WidgetValidationError("target_weights values must be numeric")
        else:
            validated['target_weights'] = None
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        if validated_params is None:
            validated_params = {}
        
        transition_method = validated_params.get('transition_method', 'Gradual')
        optimization_priority = validated_params.get('optimization_priority', 'Balance')
        target_weights = validated_params.get('target_weights')
        
        try:
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available"}
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings"}
            
            # Calculate current portfolio value and weights
            total_value = sum(
                h.get('quantity', 0) * h.get('last_price', 0)
                for h in holdings
            )
            
            # Generate sample required trades (in real implementation, this would
            # compare current portfolio to optimized/target portfolio)
            required_trades = []
            for holding in holdings[:3]:  # Sample first 3
                symbol = holding['symbol']
                current_qty = holding.get('quantity', 0)
                # Simulate rebalancing - would use actual target weights
                target_qty = int(current_qty * 1.1)  # 10% increase as example
                
                if target_qty != current_qty:
                    action = 'buy' if target_qty > current_qty else 'sell'
                    shares = abs(target_qty - current_qty)
                    price = holding.get('last_price', 0)
                    
                    required_trades.append({
                        "symbol": symbol,
                        "action": action,
                        "shares": int(shares),
                        "value": float(shares * price)
                    })
            
            # Calculate transition cost (simple estimate: 0.1% of total value)
            transition_cost = total_value * 0.001
            
            return {
                "required_trades": required_trades,
                "transition_cost": float(transition_cost),
                "expected_impact": {
                    "risk_change": 0.5,  # 0.5% risk reduction estimate
                    "return_impact": 0.2  # 0.2% return improvement estimate
                },
                "holdings_analyzed": len(holdings)
            }
        except Exception as e:
            logger.error(f"Portfolio transition extraction failed: {e}")
            return {"error": str(e)}
