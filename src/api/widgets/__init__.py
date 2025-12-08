"""Widget API adapters package.

This package contains adapters that expose existing Streamlit widgets
through REST API endpoints, enabling NextJS frontend integration.
"""

from .portfolio_summary import PortfolioSummaryAdapter
from .holdings_breakdown import HoldingsBreakdownAdapter
from .correlation_matrix import CorrelationMatrixAdapter
from .monte_carlo import MonteCarloAdapter

__all__ = [
    'PortfolioSummaryAdapter',
    'HoldingsBreakdownAdapter', 
    'CorrelationMatrixAdapter',
    'MonteCarloAdapter'
]