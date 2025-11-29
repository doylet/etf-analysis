"""
Dashboard page controller
"""

import streamlit as st
import pandas as pd


class DashboardPage:
    """Controller for main Dashboard page"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def render(self):
        st.title("ETF Analysis Dashboard")
        
        instruments = self.storage.get_all_instruments(active_only=True)
        
        if not instruments:
            st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
            return
        
        symbols = [i['symbol'] for i in instruments]
        latest_prices = self.storage.get_latest_prices(symbols)
        
        self._render_overview(instruments, latest_prices)
        st.divider()
        # self._render_data_management(symbols)
        # st.divider()
        self._render_instruments_table(instruments, latest_prices)
    
    def _render_overview(self, instruments, latest_prices):
        st.subheader("Portfolio Overview")
        
        cols = st.columns(min(4, len(instruments)))
        for idx, inst in enumerate(instruments[:4]):
            with cols[idx]:
                symbol = inst['symbol']
                if symbol in latest_prices:
                    price_info = latest_prices[symbol]
                    st.metric(
                        label=symbol,
                        value=f"${price_info['close']:.2f}",
                        delta=None
                    )
                    # st.caption(inst['name'][:30])
    
    # def _render_data_management(self, symbols):
    #     st.subheader("Data Management")
    #     col_refresh1, col_refresh2 = st.columns([3, 1])
        
    #     with col_refresh1:
    #         refresh_symbol = st.selectbox(
    #             "Update price data for:",
    #             options=['All'] + symbols,
    #             key="refresh_select"
    #         )
        
    #     with col_refresh2:
    #         st.write("")
    #         st.write("")
    #         if st.button("Fetch Latest Data"):
    #             self._handle_data_refresh(refresh_symbol, symbols)
    
    def _handle_data_refresh(self, refresh_symbol, symbols):
        symbols_to_refresh = symbols if refresh_symbol == 'All' else [refresh_symbol]
        
        progress_bar = st.progress(0)
        for idx, sym in enumerate(symbols_to_refresh):
            with st.spinner(f"Fetching {sym}..."):
                result = self.storage.fetch_and_store_prices(sym, period='1mo')
                if result['success']:
                    st.success(f"{sym}: {result['message']}")
            progress_bar.progress((idx + 1) / len(symbols_to_refresh))
        
        st.rerun()
    
    def _render_instruments_table(self, instruments, latest_prices):
        st.subheader("All Tracked Instruments")
        
        display_data = []
        for inst in instruments:
            symbol = inst['symbol']
            row = {
                'Symbol': symbol,
                'Name': inst['name'],
                'Type': inst['type'],
                'Sector': inst['sector']
            }
            if symbol in latest_prices:
                row['Last Price'] = f"${latest_prices[symbol]['close']:.2f}"
                row['Last Update'] = latest_prices[symbol]['date'].strftime('%Y-%m-%d')
            else:
                row['Last Price'] = 'N/A'
                row['Last Update'] = 'N/A'
            
            display_data.append(row)
        
        st.dataframe(
            pd.DataFrame(display_data),
            width="stretch",
            hide_index=True
        )
