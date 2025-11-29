"""
Manage Instruments page controller
"""

import streamlit as st
import pandas as pd


class ManageInstrumentsPage:
    """Controller for Manage Instruments page"""
    
    def __init__(self, storage, av_client):
        self.storage = storage
        self.av_client = av_client
    
    def render(self):
        st.title("Manage Instruments")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self._render_add_form()
        
        with col2:
            self._render_search()
        
        st.divider()
        self._render_instruments_list()
    
    def _render_add_form(self):
        st.subheader("Add New Instrument")
        
        # Symbol search feature
        if self.av_client.is_available():
            self._render_symbol_search()
        else:
            st.info("Add ALPHAVANTAGE_API_KEY to .env for symbol search")
        
        with st.form("add_instrument_form"):
            symbol = st.text_input("Symbol (e.g., SPY, AAPL, BHP.AX)", key="add_symbol").upper()
            instrument_type = st.selectbox("Type", ["etf", "stock", "index"], key="add_type")
            sector = st.text_input("Sector (optional)", key="add_sector")
            notes = st.text_area("Notes (optional)", key="add_notes")
            
            submitted = st.form_submit_button("Add Instrument")
            
            if submitted and symbol:
                self._handle_add_instrument(symbol, instrument_type, sector, notes)
    
    def _render_symbol_search(self):
        st.markdown("**Search for symbols:**")
        search_query = st.text_input("Search by company name or symbol", key="av_search")
        
        if search_query and len(search_query) >= 2:
            with st.spinner("Searching..."):
                results = self.av_client.search_symbols(search_query)
                
                if results:
                    st.markdown("**Search Results:**")
                    for result in results[:10]:
                        col_a, col_b, col_c = st.columns([2, 3, 1])
                        with col_a:
                            st.code(result['symbol'])
                        with col_b:
                            st.write(f"{result['name']} ({result['type']})")
                        with col_c:
                            st.caption(result['region'])
                    st.divider()
                else:
                    st.info("No results found")
    
    def _handle_add_instrument(self, symbol, instrument_type, sector, notes):
        with st.spinner(f"Adding {symbol}..."):
            result = self.storage.add_instrument(
                symbol=symbol,
                instrument_type=instrument_type,
                sector=sector if sector else None,
                notes=notes if notes else None
            )
            
            if result['success']:
                st.success(result['message'])
                with st.spinner(f"Fetching historical data for {symbol}..."):
                    price_result = self.storage.fetch_and_store_prices(symbol, period='1y')
                    if price_result['success']:
                        st.info(f"Loaded {price_result.get('records_added', 0)} price records")
                st.rerun()
            else:
                st.error(result['message'])
    
    def _render_search(self):
        st.subheader("Search Instruments")
        search_term = st.text_input("Search by symbol or name", key="search")
        
        if search_term:
            results = self.storage.search_instruments(search_term)
            if results:
                st.write(f"Found {len(results)} instrument(s):")
                for inst in results:
                    st.write(f"**{inst['symbol']}** - {inst['name']} ({inst['type']})")
            else:
                st.info("No instruments found")
    
    def _render_instruments_list(self):
        st.subheader("Tracked Instruments")
        
        instruments = self.storage.get_all_instruments(active_only=True)
        
        if instruments:
            df = pd.DataFrame(instruments)
            df['added_date'] = pd.to_datetime(df['added_date']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                df[['symbol', 'name', 'type', 'sector', 'added_date']],
                use_container_width=True,
                hide_index=True
            )
            
            self._render_remove_form(instruments)
        else:
            st.info("No instruments tracked yet. Add some above!")
    
    def _render_remove_form(self, instruments):
        st.subheader("Remove Instrument")
        col_remove1, col_remove2 = st.columns([3, 1])
        
        with col_remove1:
            remove_symbol = st.selectbox(
                "Select instrument to remove",
                options=[i['symbol'] for i in instruments],
                key="remove_select"
            )
        
        with col_remove2:
            st.write("")
            st.write("")
            if st.button("Remove", type="secondary"):
                result = self.storage.remove_instrument(remove_symbol)
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
