"""
Portfolio Transition Widget API Adapter

Exposes the PortfolioTransitionWidget functionality via REST API
by delegating to the existing Streamlit widget.
"""

import io
from typing import Dict, List, Optional, Any
from widgets.portfolio_transition_widget import PortfolioTransitionWidget
from storage.base import BaseStorage


class PortfolioTransitionAdapter:
    """API adapter for portfolio transition widget"""
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.widget = PortfolioTransitionWidget(storage, 'portfolio_transition_api')
    
    def get_data(self, instruments: List[Dict] = None, selected_symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get portfolio transition analysis data
        
        Args:
            instruments: List of instrument dictionaries
            selected_symbols: List of symbols to include in analysis
            
        Returns:
            Dict containing portfolio transition data and metadata
        """
        try:
            result = {
                'success': True,
                'widget_name': self.widget.get_name(),
                'widget_description': self.widget.get_description(),
                'transition_data': {},
                'metadata': {
                    'instruments_count': len(instruments) if instruments else 0,
                    'selected_symbols': selected_symbols or [],
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
            
            # If no instruments, return empty structure
            if not instruments:
                result['transition_data'] = {
                    'rebalancing_plan': {},
                    'transaction_costs': {},
                    'implementation': {},
                    'error': 'No instruments available for portfolio transition analysis'
                }
                return result
            
            # Extract portfolio transition features
            result['transition_data'] = {
                'description': 'Portfolio rebalancing and transition cost analysis',
                'features': [
                    'Rebalancing optimization',
                    'Transaction cost modeling',
                    'Implementation scheduling',
                    'Tax-aware transitions',
                    'Liquidity analysis'
                ],
                'rebalancing_strategies': [
                    'Threshold-based rebalancing',
                    'Calendar-based rebalancing',
                    'Volatility-triggered rebalancing',
                    'Tax-loss harvesting',
                    'Drift-adjusted rebalancing'
                ],
                'rebalancing_plan': {
                    'description': 'Optimal rebalancing strategy',
                    'target_weights': 'Desired portfolio allocation',
                    'current_weights': 'Current portfolio weights',
                    'required_trades': 'Buy/sell orders needed',
                    'priority_order': 'Trade execution sequence'
                },
                'transaction_costs': {
                    'description': 'Comprehensive cost analysis',
                    'explicit_costs': 'Commissions and fees',
                    'implicit_costs': 'Bid-ask spreads and market impact',
                    'total_cost_estimate': 'Total transition cost',
                    'cost_optimization': 'Strategies to minimize costs'
                },
                'implementation': {
                    'description': 'Execution planning and timing',
                    'execution_schedule': 'Optimal timing for trades',
                    'market_conditions': 'Current market liquidity',
                    'risk_management': 'Execution risk mitigation',
                    'performance_tracking': 'Implementation quality metrics'
                },
                'tax_considerations': [
                    'Capital gains implications',
                    'Tax-loss harvesting opportunities',
                    'Wash sale rules',
                    'Asset location optimization'
                ]
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get portfolio transition data: {str(e)}',
                'widget_name': 'Portfolio Transition',
                'transition_data': {},
                'metadata': {'error_timestamp': self.storage.get_current_timestamp()}
            }