"""
Dashboard page controller
"""

import streamlit as st
import pandas as pd
import json
from .base import BaseController
from src.widgets import (
    PortfolioSummaryWidget,
    HoldingsBreakdownWidget,
    PerformanceWidget,
    BenchmarkComparisonWidget,
    DividendAnalysisWidget,
    CorrelationMatrixWidget,
    PortfolioOptimizerWidget,
    MonteCarloWidget
)


class DashboardPage(BaseController):
    """Controller for main Dashboard page"""
    
    # Registry of available widgets
    AVAILABLE_WIDGETS = {
        'portfolio_summary': PortfolioSummaryWidget,
        'benchmark_comparison': BenchmarkComparisonWidget,
        'portfolio_optimizer': PortfolioOptimizerWidget,
        'monte_carlo': MonteCarloWidget,
        'holdings_breakdown': HoldingsBreakdownWidget,
        'performance': PerformanceWidget,
        'dividend_analysis': DividendAnalysisWidget,
        'correlation_matrix': CorrelationMatrixWidget
    }
    
    def __init__(self, storage):
        super().__init__(storage)
        
        # Load widget configuration from database
        if 'dashboard_widgets' not in st.session_state:
            saved_widgets = self.storage.get_setting('dashboard_widgets')
            
            if saved_widgets:
                try:
                    st.session_state.dashboard_widgets = json.loads(saved_widgets)
                except:
                    # Fallback to defaults if JSON parsing fails
                    st.session_state.dashboard_widgets = [
                        'portfolio_summary',
                        'benchmark_comparison',
                        'holdings_breakdown'
                    ]
            else:
                # Default widgets on first load
                st.session_state.dashboard_widgets = [
                    'portfolio_summary',
                    'benchmark_comparison',
                    'holdings_breakdown'
                ]
                # Save defaults to database
                self._save_widget_state()
    
    def render(self):
        st.title("ETF Analysis Dashboard")
        
        instruments = self._load_instruments(active_only=True)
        
        if not instruments:
            st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
            return
        
        # Widget management controls
        self._render_widget_controls()
        
        # Render active widgets
        self._render_active_widgets(instruments)
    
    def _render_widget_controls(self):
        """Render widget management controls"""
        with st.expander("Manage Dashboard Widgets", expanded=False):
            st.write("**Active Widgets:**")
            
            if st.session_state.dashboard_widgets:
                for widget_key in st.session_state.dashboard_widgets:
                    widget_class = self.AVAILABLE_WIDGETS.get(widget_key)
                    if widget_class:
                        temp_widget = widget_class(self.storage, widget_key)
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"• {temp_widget.get_name()}")
                        with col2:
                            if st.button("Remove", key=f"remove_{widget_key}"):
                                st.session_state.dashboard_widgets.remove(widget_key)
                                self._save_widget_state()
                                st.rerun()
            else:
                st.info("No widgets active. Add some below.")
            
            st.write("**Available Widgets:**")
            
            # Show available widgets to add
            for widget_key, widget_class in self.AVAILABLE_WIDGETS.items():
                if widget_key not in st.session_state.dashboard_widgets:
                    temp_widget = widget_class(self.storage, widget_key)
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"• {temp_widget.get_name()} - _{temp_widget.get_description()}_")
                    with col2:
                        if st.button("Add", key=f"add_{widget_key}"):
                            st.session_state.dashboard_widgets.append(widget_key)
                            self._save_widget_state()
                            st.rerun()
    
    def _save_widget_state(self):
        """Save current widget configuration to database"""
        widgets_json = json.dumps(st.session_state.dashboard_widgets)
        self.storage.set_setting(
            'dashboard_widgets',
            widgets_json,
            'Active dashboard widgets configuration'
        )
    
    def _render_active_widgets(self, instruments):
        """Render all active widgets"""
        if not st.session_state.dashboard_widgets:
            st.info("No widgets active. Use 'Manage Dashboard Widgets' above to add some.")
            return
        
        for widget_key in st.session_state.dashboard_widgets:
            widget_class = self.AVAILABLE_WIDGETS.get(widget_key)
            if widget_class:
                widget = widget_class(self.storage, widget_key)
                
                # Render widget in a container
                with st.container():
                    st.subheader(widget.get_name())
                    widget.render(instruments=instruments)
