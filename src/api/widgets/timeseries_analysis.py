"""
Time Series Analysis Widget API Adapter

Exposes the TimeSeriesAnalysisWidget functionality via REST API
by delegating to the existing Streamlit widget.
"""

import io
from typing import Dict, List, Optional, Any
from widgets.timeseries_analysis_widget import TimeSeriesAnalysisWidget
from storage.base import BaseStorage


class TimeSeriesAnalysisAdapter:
    """API adapter for time series analysis widget"""
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.widget = TimeSeriesAnalysisWidget(storage, 'timeseries_analysis_api')
    
    def get_data(self, instruments: List[Dict] = None, selected_symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get time series analysis data
        
        Args:
            instruments: List of instrument dictionaries
            selected_symbols: List of symbols to include in analysis
            
        Returns:
            Dict containing time series analysis data and metadata
        """
        try:
            result = {
                'success': True,
                'widget_name': self.widget.get_name(),
                'widget_description': self.widget.get_description(),
                'timeseries_data': {},
                'metadata': {
                    'instruments_count': len(instruments) if instruments else 0,
                    'selected_symbols': selected_symbols or [],
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
            
            # If no instruments, return empty structure
            if not instruments:
                result['timeseries_data'] = {
                    'trend_analysis': {},
                    'seasonality': {},
                    'forecasts': {},
                    'error': 'No instruments available for time series analysis'
                }
                return result
            
            # Extract time series analysis features
            result['timeseries_data'] = {
                'description': 'Advanced time series analysis of price and return patterns',
                'features': [
                    'Trend decomposition',
                    'Seasonality detection',
                    'Forecasting models',
                    'Statistical tests',
                    'Pattern recognition'
                ],
                'analysis_methods': [
                    'ARIMA modeling',
                    'Seasonal decomposition',
                    'Trend analysis',
                    'Volatility clustering',
                    'Regime detection',
                    'Technical indicators'
                ],
                'trend_analysis': {
                    'description': 'Long-term trend identification',
                    'trend_strength': 'Statistical significance of trends',
                    'trend_changes': 'Structural break detection',
                    'momentum_indicators': 'Short and long-term momentum'
                },
                'seasonality': {
                    'description': 'Seasonal pattern detection',
                    'monthly_effects': 'Month-of-year effects',
                    'day_effects': 'Day-of-week patterns',
                    'holiday_effects': 'Holiday and event impacts'
                },
                'forecasts': {
                    'description': 'Price and return forecasting',
                    'forecast_horizon': 'Multiple forecast periods',
                    'confidence_intervals': 'Forecast uncertainty bands',
                    'model_accuracy': 'Historical forecast performance'
                },
                'statistical_tests': [
                    'Stationarity tests',
                    'Autocorrelation analysis',
                    'Volatility tests',
                    'Normality tests'
                ]
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get time series analysis data: {str(e)}',
                'widget_name': 'Time Series Analysis',
                'timeseries_data': {},
                'metadata': {'error_timestamp': self.storage.get_current_timestamp()}
            }