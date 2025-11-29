"""
Page controllers for the ETF Analysis Dashboard
"""

from .manage_instruments import ManageInstrumentsPage
from .dashboard import DashboardPage
from .price_history import PriceHistoryPage
from .comparative_analysis import ComparativeAnalysisPage

__all__ = [
    'ManageInstrumentsPage',
    'DashboardPage',
    'PriceHistoryPage',
    'ComparativeAnalysisPage'
]
