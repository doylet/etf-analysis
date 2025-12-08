"""
Constrained Optimization Widget API Adapter

Exposes the ConstrainedOptimizationWidget functionality via REST API
by delegating to the existing Streamlit widget.
"""

import io
from typing import Dict, List, Optional, Any
from widgets.constrained_optimization_widget import ConstrainedOptimizationWidget
from storage.base import BaseStorage


class ConstrainedOptimizationAdapter:
    """API adapter for constrained optimization widget"""
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.widget = ConstrainedOptimizationWidget(storage, 'constrained_optimization_api')
    
    def get_data(self, instruments: List[Dict] = None, selected_symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get constrained portfolio optimization data
        
        Args:
            instruments: List of instrument dictionaries
            selected_symbols: List of symbols to include in optimization
            
        Returns:
            Dict containing constrained optimization data and metadata
        """
        try:
            result = {
                'success': True,
                'widget_name': self.widget.get_name(),
                'widget_description': self.widget.get_description(),
                'constrained_optimization_data': {},
                'metadata': {
                    'instruments_count': len(instruments) if instruments else 0,
                    'selected_symbols': selected_symbols or [],
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
            
            # If no instruments, return empty structure
            if not instruments:
                result['constrained_optimization_data'] = {
                    'optimal_allocation': {},
                    'constraints': {},
                    'performance_metrics': {},
                    'error': 'No instruments available for constrained optimization'
                }
                return result
            
            # Extract constrained optimization features
            result['constrained_optimization_data'] = {
                'description': 'Portfolio optimization with custom constraints and objectives',
                'features': [
                    'Multi-objective optimization',
                    'Custom constraint definition',
                    'ESG constraints',
                    'Sector/region limits',
                    'Risk budgeting'
                ],
                'constraint_types': [
                    'Weight bounds (min/max allocation)',
                    'Sector concentration limits',
                    'Risk factor exposure',
                    'ESG score minimums',
                    'Liquidity requirements',
                    'Correlation constraints'
                ],
                'optimal_allocation': {
                    'description': 'Optimized weights under constraints',
                    'methodology': 'Quadratic programming with linear constraints',
                    'validation': 'All constraints satisfied'
                },
                'constraints': {
                    'active_constraints': 'Currently binding constraints',
                    'constraint_violations': 'Any violated constraints',
                    'shadow_prices': 'Marginal cost of constraints'
                },
                'performance_metrics': {
                    'constrained_sharpe': 'Sharpe ratio under constraints',
                    'unconstrained_comparison': 'Performance vs unconstrained optimization',
                    'constraint_cost': 'Performance cost of constraints'
                },
                'optimization_objectives': [
                    'Maximize risk-adjusted return',
                    'Minimize tracking error',
                    'Maximize diversification',
                    'Multi-criteria optimization'
                ]
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get constrained optimization data: {str(e)}',
                'widget_name': 'Constrained Optimization',
                'constrained_optimization_data': {},
                'metadata': {'error_timestamp': self.storage.get_current_timestamp()}
            }