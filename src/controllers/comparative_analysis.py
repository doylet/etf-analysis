"""
Comparative Analysis page controller
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


class ComparativeAnalysisPage:
    """Controller for Comparative Analysis page"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def render(self):
        st.title("Comparative Analysis")
        
        instruments = self.storage.get_all_instruments(active_only=True)
        
        if not instruments:
            st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
            return
        
        if len(instruments) < 2:
            st.warning("Add at least 2 instruments to compare.")
            return
        
        symbols = [i['symbol'] for i in instruments]
        selected_symbols, period = self._render_controls(symbols)
        
        if len(selected_symbols) >= 2:
            self._render_comparison(selected_symbols, period)
        else:
            st.info("Select at least 2 instruments to compare.")
    
    def _render_controls(self, symbols):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_symbols = st.multiselect(
                "Select Instruments to Compare (max 5)",
                options=symbols,
                default=symbols[:min(3, len(symbols))],
                max_selections=5
            )
        
        with col2:
            period = st.selectbox(
                "Period",
                options=['1M', '3M', '6M', '1Y', 'All'],
                index=3
            )
        
        return selected_symbols, period
    
    def _render_comparison(self, symbols, period):
        start_date = self._calculate_start_date(period)
        all_data = self._fetch_data(symbols, start_date)
        
        if not all_data:
            st.warning("No price data available for selected instruments. Fetch data from the Dashboard first.")
            return
        
        self._render_normalized_chart(all_data)
        self._render_metrics_table(all_data)
    
    def _calculate_start_date(self, period):
        end_date = datetime.now()
        period_days = {'1M': 30, '3M': 90, '6M': 180, '1Y': 365}
        
        if period in period_days:
            return end_date - timedelta(days=period_days[period])
        return None
    
    def _fetch_data(self, symbols, start_date):
        all_data = {}
        for symbol in symbols:
            df = self.storage.get_price_data(symbol, start_date=start_date)
            if not df.empty:
                all_data[symbol] = df
        return all_data
    
    def _render_normalized_chart(self, all_data):
        st.subheader("Normalized Performance Comparison")
        
        fig = go.Figure()
        
        for symbol, df in all_data.items():
            normalized = ((df['close'] / df['close'].iloc[0]) - 1) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=normalized,
                mode='lines',
                name=symbol,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Return (%)",
            hovermode='x unified',
            height=500,
            yaxis=dict(ticksuffix="%")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_metrics_table(self, all_data):
        st.subheader("Performance Metrics")
        
        metrics_data = []
        for symbol, df in all_data.items():
            first_price = df['close'].iloc[0]
            last_price = df['close'].iloc[-1]
            pct_change = ((last_price / first_price) - 1) * 100
            
            metrics_data.append({
                'Symbol': symbol,
                'Start Price': f"${first_price:.2f}",
                'End Price': f"${last_price:.2f}",
                'Return': f"{pct_change:+.2f}%",
                'High': f"${df['high'].max():.2f}",
                'Low': f"${df['low'].min():.2f}",
                'Avg Volume': f"{df['volume'].mean():,.0f}"
            })
        
        st.dataframe(
            pd.DataFrame(metrics_data),
            use_container_width=True,
            hide_index=True
        )
