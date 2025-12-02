"""
Performance widget - shows returns and performance metrics.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Data fetching and validation (_fetch_* methods)
- Logic Layer: Pure calculations (_calculate_* static methods)
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .layered_base_widget import LayeredBaseWidget


@dataclass
class PerformanceMetrics:
    """Results from performance calculations."""
    symbol: str
    start_price: float
    end_price: float
    change: float
    change_pct: float


class PerformanceWidget(LayeredBaseWidget):
    """Widget showing performance metrics for holdings"""
    
    def get_name(self) -> str:
        return "Performance Metrics"
    
    def get_description(self) -> str:
        return "Price performance and returns for selected holdings"
    
    def get_scope(self) -> str:
        return "multiple"  # Can work with one or more symbols
    
    # ========================================================================
    # UI LAYER - Streamlit rendering methods
    # ========================================================================
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Main render orchestration - UI only.
        
        Parameters:
            instruments: List of instrument dictionaries
            selected_symbols: Optional list of symbols to analyze
        """
        with st.container(border=True):
            if not instruments:
                st.info("No instruments available")
                return
            
            # Determine symbols to analyze
            symbols = self._prepare_symbols(instruments, selected_symbols)
            
            if not symbols:
                st.info("No holdings to analyze. Select symbols or add positions.")
                return
            
            # Render controls and get user selections
            period_days = self._render_period_selector()
            
            # Fetch and calculate performance
            performance_metrics = self._fetch_performance_data(symbols, period_days)
            
            if not performance_metrics:
                st.warning("No price data available for selected period")
                return
            
            # Display results
            self._render_performance_table(performance_metrics)
    
    def _render_period_selector(self) -> int:
        """Render time period selector and return days.
        
        Returns:
            int: Number of days for the selected period
        """
        period = st.selectbox(
            "Time period:",
            options=['1 Week', '1 Month', '3 Months', '6 Months', '1 Year'],
            key=self._get_session_key("period")
        )
        
        period_map = {
            '1 Week': 7,
            '1 Month': 30,
            '3 Months': 90,
            '6 Months': 180,
            '1 Year': 365
        }
        return period_map[period]
    
    def _render_performance_table(self, metrics: List[PerformanceMetrics]):
        """Render performance metrics as a table.
        
        Parameters:
            metrics: List of PerformanceMetrics objects to display
        """
        performance_data = []
        for metric in metrics:
            performance_data.append({
                'Symbol': metric.symbol,
                'Start Price': f"${metric.start_price:.2f}",
                'Current Price': f"${metric.end_price:.2f}",
                'Change': f"${metric.change:.2f}",
                'Change %': f"{metric.change_pct:.2f}%"
            })
        
        perf_df = pd.DataFrame(performance_data)
        st.dataframe(perf_df, hide_index=True, width='stretch')
    
    # ========================================================================
    # DATA LAYER - Data fetching and validation methods
    # ========================================================================
    
    def _prepare_symbols(self, instruments: List[Dict], 
                        selected_symbols: Optional[List[str]]) -> List[str]:
        """Prepare list of symbols to analyze.
        
        Parameters:
            instruments: List of instrument dictionaries
            selected_symbols: Optional pre-selected symbols
            
        Returns:
            List[str]: Symbols to analyze
        """
        if selected_symbols:
            return selected_symbols
        
        return [i['symbol'] for i in instruments if i.get('quantity', 0) > 0]
    
    def _fetch_performance_data(self, symbols: List[str], 
                               days: int) -> List[PerformanceMetrics]:
        """Fetch price data and calculate performance for all symbols.
        
        Parameters:
            symbols: List of symbols to analyze
            days: Number of days to look back
            
        Returns:
            List[PerformanceMetrics]: Performance metrics for each symbol
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        metrics = []
        for symbol in symbols:
            df = self.storage.get_price_data(symbol, start_date, end_date)
            
            if df is not None and not df.empty:
                start_price = df.iloc[0]['close']
                end_price = df.iloc[-1]['close']
                
                metric = self._calculate_performance(symbol, start_price, end_price)
                metrics.append(metric)
        
        return metrics
    
    # ========================================================================
    # LOGIC LAYER - Pure calculation methods
    # ========================================================================
    
    @staticmethod
    def _calculate_performance(symbol: str, start_price: float, 
                              end_price: float) -> PerformanceMetrics:
        """Calculate performance metrics from start and end prices.
        
        Parameters:
            symbol: Stock symbol
            start_price: Starting price
            end_price: Ending price
            
        Returns:
            PerformanceMetrics: Calculated performance metrics
        """
        change = end_price - start_price
        change_pct = (change / start_price * 100) if start_price > 0 else 0
        
        return PerformanceMetrics(
            symbol=symbol,
            start_price=start_price,
            end_price=end_price,
            change=change,
            change_pct=change_pct
        )
