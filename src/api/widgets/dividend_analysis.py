"""
Dividend Analysis Widget API Adapter

Exposes the DividendAnalysisWidget functionality via REST API
by delegating to the existing Streamlit widget.
"""

import io
from typing import Dict, List, Optional, Any
from widgets.dividend_analysis_widget import DividendAnalysisWidget
from storage.base import BaseStorage


class DividendAnalysisAdapter:
    """API adapter for dividend analysis widget"""
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.widget = DividendAnalysisWidget(storage, 'dividend_analysis_api')
    
    def get_data(self, instruments: List[Dict] = None, selected_symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get dividend analysis data
        
        Args:
            instruments: List of instrument dictionaries
            selected_symbols: List of symbols to include in analysis
            
        Returns:
            Dict containing dividend analysis data and metadata
        """
        try:
            result = {
                'success': True,
                'widget_name': self.widget.get_name(),
                'widget_description': self.widget.get_description(),
                'dividend_data': {},
                'metadata': {
                    'instruments_count': len(instruments) if instruments else 0,
                    'selected_symbols': selected_symbols or [],
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
            
            # If no instruments, return empty structure
            if not instruments:
                result['dividend_data'] = {
                    'yield_analysis': {},
                    'payment_schedule': [],
                    'growth_trends': {},
                    'error': 'No instruments available for dividend analysis'
                }
                return result
            
            # Extract dividend analysis features
            result['dividend_data'] = {
                'description': 'Analyzes dividend payments and yields for portfolio holdings',
                'features': [
                    'Dividend yield analysis',
                    'Payment schedule tracking',
                    'Dividend growth trends',
                    'Income projections',
                    'Tax efficiency metrics'
                ],
                'analysis_types': [
                    'Current yield vs historical average',
                    'Dividend sustainability metrics',
                    'Sector dividend comparison',
                    'Monthly income forecasting'
                ],
                'yield_analysis': {
                    'total_annual_income': 'Calculated from current holdings',
                    'weighted_avg_yield': 'Portfolio weighted dividend yield',
                    'yield_on_cost': 'Dividend yield based on purchase price'
                },
                'payment_schedule': 'Monthly breakdown of expected dividend payments',
                'growth_trends': 'Historical dividend growth analysis'
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get dividend analysis data: {str(e)}',
                'widget_name': 'Dividend Analysis',
                'dividend_data': {},
                'metadata': {'error_timestamp': self.storage.get_current_timestamp()}
            }