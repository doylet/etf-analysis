"""
Price History page controller
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta


class PriceHistoryPage:
    """Controller for Price History page"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def render(self):
        st.title("Price History")
        
        instruments = self.storage.get_all_instruments(active_only=True)
        
        if not instruments:
            st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
            return
        
        symbols = [i['symbol'] for i in instruments]
        selected_symbol, period = self._render_controls(symbols)
        
        if selected_symbol:
            self._render_price_analysis(selected_symbol, period)
    
    def _render_controls(self, symbols):
        col1, col2 = st.columns([2, 2])
        
        with col1:
            selected_symbol = st.selectbox("Select Instrument", options=symbols)
        
        with col2:
            period = st.selectbox(
                "Time Period",
                options=['1M', '3M', '6M', '1Y', '2Y', '5Y', 'All'],
                index=3
            )
        
        return selected_symbol, period
    
    def _render_price_analysis(self, symbol, period):
        start_date = self._calculate_start_date(period)
        df = self.storage.get_price_data(symbol, start_date=start_date)
        
        if df.empty:
            st.warning(f"No price data available for {symbol}. Try fetching data from the Dashboard.")
            return
        
        self._render_metrics(df)
        self._render_price_chart(symbol, df)
        self._render_volume_chart(symbol, df)
        self._render_data_table(df)
    
    def _calculate_start_date(self, period):
        end_date = datetime.now()
        period_days = {
            '1M': 30, '3M': 90, '6M': 180,
            '1Y': 365, '2Y': 730, '5Y': 1825
        }
        
        if period in period_days:
            return end_date - timedelta(days=period_days[period])
        return None
    
    def _render_metrics(self, df):
        latest_price = df['close'].iloc[-1]
        first_price = df['close'].iloc[0]
        price_change = latest_price - first_price
        pct_change = (price_change / first_price) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", f"${latest_price:.2f}")
        with col2:
            st.metric("Change", f"${price_change:.2f}", f"{pct_change:+.2f}%")
        with col3:
            st.metric("High", f"${df['high'].max():.2f}")
        with col4:
            st.metric("Low", f"${df['low'].min():.2f}")
    
    def _render_price_chart(self, symbol, df):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.update_layout(
            title=f"{symbol} Price History",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, width="stretch")
    
    def _render_volume_chart(self, symbol, df):
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title=f"{symbol} Trading Volume",
            xaxis_title="Date",
            yaxis_title="Volume",
            height=300
        )
        
        st.plotly_chart(fig, width="stretch")
    
    def _render_data_table(self, df):
        with st.expander("View Raw Data"):
            st.dataframe(
                df.reset_index().tail(50).sort_index(ascending=False),
                width="stretch"
            )
