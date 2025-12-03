"""
Dashboard widgets package
"""

from .base_widget import BaseWidget
from .portfolio_summary_widget import PortfolioSummaryWidget
from .holdings_breakdown_widget import HoldingsBreakdownWidget
from .performance_widget import PerformanceWidget
from .benchmark_comparison_widget import BenchmarkComparisonWidget
from .dividend_analysis_widget import DividendAnalysisWidget
from .correlation_matrix_widget import CorrelationMatrixWidget
from .portfolio_optimizer_widget import PortfolioOptimizerWidget
from .monte_carlo_widget import MonteCarloWidget
from .timeseries_analysis_widget import TimeSeriesAnalysisWidget
from .constrained_optimization_widget import ConstrainedOptimizationWidget
from .portfolio_transition_widget import PortfolioTransitionWidget
from .news_event_analysis_widget import NewsEventAnalysisWidget

__all__ = [
    'BaseWidget',
    'PortfolioSummaryWidget',
    'HoldingsBreakdownWidget',
    'PerformanceWidget',
    'BenchmarkComparisonWidget',
    'DividendAnalysisWidget',
    'CorrelationMatrixWidget',
    'PortfolioOptimizerWidget',
    'MonteCarloWidget',
    'TimeSeriesAnalysisWidget',
    'ConstrainedOptimizationWidget',
    'PortfolioTransitionWidget',
    'NewsEventAnalysisWidget',
]
