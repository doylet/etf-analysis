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
        
        instruments = self.storage.get_all_instruments(active_only=True)
        self.instruments = instruments

        col1, col2 = st.columns([2, 1])

        if instruments:
            with col1:
                self._render_instruments_list()
                if st.button("Refresh List", type="secondary", width="content"):
                    st.rerun()

            with col2:

                self._render_add_form()

                self._render_remove_form()

    def _render_add_form(self):
        st.subheader("Add New Instrument")
        
        # Symbol search feature
        if self.av_client.is_available():
            self._render_symbol_search()
        else:
            st.info("Add ALPHAVANTAGE_API_KEY to .env for symbol search")

        with st.form("add_instrument_form"):
            symbol = st.text_input("Symbol (e.g., SPY, AAPL, BHP.AX)", key="add_symbol").upper()
            instrument_type = st.selectbox("Type", ["ETF", "Stock", "Index"], key="add_type")
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
                    st.markdown("**Search Results (click to add):**")
                    for idx, result in enumerate(results[:10]):
                        col_a, col_b, col_c, col_d = st.columns([1.5, 3, 1, 1])
                        with col_a:
                            st.code(result['symbol'])
                        with col_b:
                            st.write(f"{result['name']} ({result['type']})")
                        with col_c:
                            st.caption(result['region'])
                        with col_d:
                            if st.button("Add", key=f"add_search_{idx}", type="secondary", width="stretch"):
                                # Determine instrument type from search result
                                result_type = result['type'].upper()
                                if 'ETF' in result_type:
                                    instrument_type = 'ETF'
                                elif 'INDEX' in result_type:
                                    instrument_type = 'Index'
                                else:
                                    instrument_type = 'Stock'
                                
                                self._handle_add_instrument(
                                    symbol=result['symbol'],
                                    instrument_type=instrument_type,
                                    sector=None,
                                    notes=f"Added from search: {result['name']}"
                                )
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
    
    def _render_data_controls(self):
        st.subheader("Manage Historical Data")
        
        instruments = self.instruments

        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_symbols = st.multiselect(
                "Select instruments to update",
                options=['All'] + [i['symbol'] for i in instruments],
                default=['All'],
                key="data_update_select"
            )
        
        with col2:
            period = st.selectbox(
                "Time period",
                options=['1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'],
                index=3,
                key="data_period"
            )
        
        with col3:
            st.write("")
            if st.button("Fetch Data", type="primary", width="stretch"):
                self._handle_data_fetch(selected_symbols, instruments, period)
    
    def _handle_data_fetch(self, selected_symbols, instruments, period):
        if 'All' in selected_symbols:
            symbols_to_fetch = [i['symbol'] for i in instruments]
        else:
            symbols_to_fetch = selected_symbols
        
        if not symbols_to_fetch:
            st.warning("Please select at least one instrument")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, symbol in enumerate(symbols_to_fetch):
            status_text.text(f"Fetching {symbol}... ({idx + 1}/{len(symbols_to_fetch)})")
            
            result = self.storage.fetch_and_store_prices(symbol, period=period, force_refresh=True)
            
            if result['success']:
                if result.get('cached'):
                    st.info(f"✓ {symbol}: {result['message']}")
                else:
                    st.success(f"✓ {symbol}: Added {result.get('records_added', 0)} records")
            else:
                st.error(f"✗ {symbol}: {result['message']}")
            
            progress_bar.progress((idx + 1) / len(symbols_to_fetch))
        
        status_text.text("Data fetch complete!")
        st.rerun()
    
    def _render_instruments_list(self):
        st.subheader("Tracked Instruments")
                
        if self.instruments:
            df = pd.DataFrame(self.instruments)
            df['added_date'] = pd.to_datetime(df['added_date']).dt.strftime('%Y-%m-%d')
            df['last_updated'] = pd.to_datetime(df['last_updated']).dt.strftime('%Y-%m-%d %H:%M')
            
            edited_df = st.data_editor(
                df[['symbol', 'name', 'type', 'sector', 'added_date', 'last_updated']],
                width="stretch",
                hide_index=True,
                disabled=['symbol', 'added_date', 'last_updated'],  # Make these columns read-only
                num_rows="fixed"  # Prevent adding/deleting rows
            )
            
            self._render_data_controls()

        else:
            st.info("No instruments tracked yet. Add some above!")
    
    def _render_remove_form(self):
        st.subheader("Remove Instrument")

        instruments = self.instruments

        if instruments:
            remove_symbol = st.selectbox(
                "Select instrument to remove",
                options=[i['symbol'] for i in instruments],
                key="remove_select"
            )

            if st.button("Remove", type="secondary"):
                result = self.storage.remove_instrument(remove_symbol)
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
