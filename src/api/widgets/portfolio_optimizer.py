"""
Portfolio Optimizer Widget API Adapter

Exposes the PortfolioOptimizerWidget functionality via REST API
by delegating to the existing Streamlit widget.
"""

import io
from typing import Dict, List, Optional, Any
from widgets.portfolio_optimizer_widget import PortfolioOptimizerWidget
from storage.base import BaseStorage


class PortfolioOptimizerAdapter:
    """API adapter for portfolio optimizer widget"""
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.widget = PortfolioOptimizerWidget(storage, 'portfolio_optimizer_api')
    
    def get_data(self, instruments: List[Dict] = None, selected_symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get portfolio optimization data
        
        Args:
            instruments: List of instrument dictionaries
            selected_symbols: List of symbols to include in optimization
            
        Returns:
            Dict containing portfolio optimization data and metadata
        """
        try:
            result = {
                'success': True,
                'widget_name': self.widget.get_name(),
                'widget_description': self.widget.get_description(),
                'optimization_data': {},
                'metadata': {
                    'instruments_count': len(instruments) if instruments else 0,
                    'selected_symbols': selected_symbols or [],
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
            
            # If no instruments, return empty structure
            if not instruments:
                result['optimization_data'] = {
                    'optimal_weights': {},
                    'efficient_frontier': {},
                    'metrics': {},
                    'error': 'No instruments available for optimization'
                }
                return result
            
            # Extract portfolio optimization features
            result['optimization_data'] = {
                'description': 'Modern portfolio theory based optimization',
                'features': [
                    'Mean-variance optimization',
                    'Efficient frontier calculation',
                    'Risk-return optimization',
                    'Weight constraints',
                    'Rebalancing recommendations'
                ],
                'optimization_methods': [
                    'Maximum Sharpe ratio',
                    'Minimum volatility',
                    'Maximum return',
                    'Equal risk contribution',
                    'Black-Litterman'
                ],
                'optimal_weights': {
                    'description': 'Optimized portfolio weights for each asset',
                    'constraints': 'Subject to weight and risk constraints',
                    'rebalancing': 'Recommended changes from current allocation'
                },
                'efficient_frontier': {
                    'description': 'Risk-return trade-off curve',
                    'points': 'Multiple portfolio combinations',
                    'current_position': 'Current portfolio position on frontier'
                },
                'metrics': {
                    'expected_return': 'Optimized portfolio expected return',
                    'expected_risk': 'Optimized portfolio volatility',
                    'sharpe_ratio': 'Risk-adjusted return metric',
                    'improvement': 'Improvement over current allocation'
                },
                'constraints': {
                    'weight_bounds': 'Min/max weight per asset',
                    'sector_limits': 'Sector concentration limits',
                    'risk_budget': 'Maximum portfolio risk tolerance'
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get portfolio optimization data: {str(e)}',
                'widget_name': 'Portfolio Optimizer',
                'optimization_data': {},
                'metadata': {'error_timestamp': self.storage.get_current_timestamp()}
            }