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

__all__ = [
    'BaseWidget',
    'PortfolioSummaryWidget',
    'HoldingsBreakdownWidget',
    'PerformanceWidget',
    'BenchmarkComparisonWidget',
    'DividendAnalysisWidget',
    'CorrelationMatrixWidget',
]
