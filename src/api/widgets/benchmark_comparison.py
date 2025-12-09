"""Benchmark Comparison Widget API Adapter."""

from typing import Dict, Any
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.benchmark_comparison_widget import BenchmarkComparisonWidget

logger = logging.getLogger(__name__)


class BenchmarkComparisonAdapter(BaseWidgetAdapter):
    """Adapter to expose benchmark comparison widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, BenchmarkComparisonWidget)
        
    def get_widget_name(self) -> str:
        return "benchmark_comparison"
        
    def get_widget_description(self) -> str:
        return "Compare portfolio performance against market benchmarks"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters for benchmark comparison."""
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Time period mapping
        period_map = {
            '1W': 7, '1M': 30, '3M': 90, '6M': 180, 
            '1Y': 365, '2Y': 730, '5Y': 1825
        }
        time_period = kwargs.get('time_period', '1Y')
        validated['days'] = period_map.get(time_period, 365)
        
        # Benchmark selection
        valid_benchmarks = ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'EFA', 'AGG', 'GLD']
        benchmark = kwargs.get('benchmark', 'SPY')
        validated['benchmark_symbol'] = benchmark if benchmark in valid_benchmarks else 'SPY'
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract benchmark comparison calculation data from widget."""
        from datetime import datetime, timedelta
        from src.utils.performance_metrics import calculate_returns
        
        try:
            # Get parameters from validated_params or use defaults
            days = validated_params.get('days', 365) if validated_params else 365
            benchmark_symbol = validated_params.get('benchmark_symbol', 'SPY') if validated_params else 'SPY'
            
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available for benchmark comparison"}
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings for benchmark comparison"}
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Calculate portfolio returns
            portfolio_values = widget_instance._fetch_portfolio_values(holdings, start_date, end_date)
            if portfolio_values.empty:
                return {"message": "No price data available for selected period"}
            
            portfolio_returns = calculate_returns(portfolio_values)
            
            # Get benchmark data
            benchmark_df = self.storage.get_price_data(benchmark_symbol, start_date, end_date)
            if benchmark_df is None or benchmark_df.empty:
                return {
                    "message": "Benchmark data not available",
                    "benchmarks": widget_instance.BENCHMARKS
                }
            
            benchmark_returns = calculate_returns(benchmark_df['close'])
            
            # Calculate metrics using widget's method
            metrics = widget_instance._calculate_benchmark_metrics(
                portfolio_returns, benchmark_returns,
                portfolio_values, benchmark_df['close']
            )
            
            return {
                "portfolio_return": float(metrics.portfolio_total_return),
                "benchmark_return": float(metrics.benchmark_total_return),
                "alpha": float(metrics.alpha),
                "beta": float(metrics.beta),
                "sharpe_ratio": float(metrics.portfolio_sharpe),
                "benchmark_sharpe": float(metrics.benchmark_sharpe),
                "information_ratio": float(metrics.info_ratio),
                "portfolio_volatility": float(metrics.portfolio_vol),
                "benchmark_volatility": float(metrics.benchmark_vol),
                "benchmark_symbol": benchmark_symbol,
                "period_days": days
            }
        except Exception as e:
            logger.error(f"Benchmark comparison extraction failed: {e}")
            return {"error": str(e)}
