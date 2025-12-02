"""
Performance widget - shows returns and performance metrics
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from .base_widget import BaseWidget


class PerformanceWidget(BaseWidget):
    """Widget showing performance metrics for holdings"""
    
    def get_name(self) -> str:
        return "Performance Metrics"
    
    def get_description(self) -> str:
        return "Price performance and returns for selected holdings"
    
    def get_scope(self) -> str:
        return "multiple"  # Can work with one or more symbols
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render performance metrics"""
        with st.container(border=True):
            if not instruments:
                st.info("No instruments available")
                return
            
            # Use selected symbols or all symbols
            if selected_symbols:
                symbols = selected_symbols
            else:
                symbols = [i['symbol'] for i in instruments if i.get('quantity', 0) > 0]
            
            if not symbols:
                st.info("No holdings to analyze. Select symbols or add positions.")
                return
            
            # Time period selector
            period = st.selectbox(
                "Time period:",
                options=['1 Week', '1 Month', '3 Months', '6 Months', '1 Year'],
                key=f"{self.widget_id}_period"
            )
            
            period_map = {
                '1 Week': 7,
                '1 Month': 30,
                '3 Months': 90,
                '6 Months': 180,
                '1 Year': 365
            }
            days = period_map[period]
            
            # Calculate performance for each symbol
            performance_data = []
            for symbol in symbols:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                df = self.storage.get_price_data(symbol, start_date, end_date)
                
                if df is not None and not df.empty:
                    start_price = df.iloc[0]['close']
                    end_price = df.iloc[-1]['close']
                    change = end_price - start_price
                    change_pct = (change / start_price * 100) if start_price > 0 else 0
                    
                    performance_data.append({
                        'Symbol': symbol,
                        'Start Price': f"${start_price:.2f}",
                        'Current Price': f"${end_price:.2f}",
                        'Change': f"${change:.2f}",
                        'Change %': f"{change_pct:.2f}%"
                    })
            
            if performance_data:
                perf_df = pd.DataFrame(performance_data)
                st.dataframe(perf_df, hide_index=True, width='stretch')
            else:
                st.warning(f"No price data available for selected period")
