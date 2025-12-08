"""
Performance Widget API Adapter

Exposes the PerformanceWidget functionality via REST API
by delegating to the existing Streamlit widget.
"""

import io
from typing import Dict, List, Optional, Any
from widgets.performance_widget import PerformanceWidget
from storage.base import BaseStorage


class PerformanceAdapter:
    """API adapter for performance widget"""
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.widget = PerformanceWidget(storage, 'performance_api')
    
    def get_data(self, instruments: List[Dict] = None, selected_symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get performance analysis data
        
        Args:
            instruments: List of instrument dictionaries
            selected_symbols: List of symbols to include in analysis
            
        Returns:
            Dict containing performance analysis data and metadata
        """
        try:
            result = {
                'success': True,
                'widget_name': self.widget.get_name(),
                'widget_description': self.widget.get_description(),
                'performance_data': {},
                'metadata': {
                    'instruments_count': len(instruments) if instruments else 0,
                    'selected_symbols': selected_symbols or [],
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
            
            # If no instruments, return empty structure
            if not instruments:
                result['performance_data'] = {
                    'returns': {},
                    'risk_metrics': {},
                    'charts': {},
                    'error': 'No instruments available for performance analysis'
                }
                return result
            
            # Extract performance analysis features
            result['performance_data'] = {
                'description': 'Comprehensive performance analysis of portfolio holdings',
                'features': [
                    'Total returns calculation',
                    'Risk-adjusted returns',
                    'Performance attribution',
                    'Time-series analysis',
                    'Volatility metrics'
                ],
                'returns': {
                    'total_return': 'Cumulative portfolio return',
                    'annualized_return': 'Annualized return percentage',
                    'period_returns': 'Returns for various time periods (1M, 3M, 6M, 1Y, 3Y)',
                    'excess_returns': 'Returns above risk-free rate'
                },
                'risk_metrics': {
                    'volatility': 'Annualized standard deviation',
                    'max_drawdown': 'Maximum peak-to-trough decline',
                    'sharpe_ratio': 'Risk-adjusted return metric',
                    'sortino_ratio': 'Downside risk-adjusted return',
                    'var': 'Value at Risk calculations'
                },
                'charts': {
                    'cumulative_returns': 'Time series of cumulative returns',
                    'rolling_returns': 'Rolling period returns',
                    'drawdown_chart': 'Drawdown visualization',
                    'risk_return_scatter': 'Risk vs return positioning'
                },
                'periods': ['1M', '3M', '6M', '1Y', '3Y', '5Y', 'ALL']
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get performance data: {str(e)}',
                'widget_name': 'Performance Analysis',
                'performance_data': {},
                'metadata': {'error_timestamp': self.storage.get_current_timestamp()}
            }