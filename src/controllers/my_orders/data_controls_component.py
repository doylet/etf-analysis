"""
Data controls component for fetching price data
"""

import streamlit as st


class DataControlsComponent:
    """Component for updating historical price data"""
    
    def __init__(self, storage, instruments):
        self.storage = storage
        self.instruments = instruments
    
    def render(self):
        """Render the data fetch controls"""
        st.markdown("Update Historical Data")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_symbols = st.multiselect(
                "Select instruments to update",
                options=['All'] + [i['symbol'] for i in self.instruments],
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
            st.space("small")  # Spacing
            if st.button("Fetch Data", type="primary", width='stretch'):
                self._handle_fetch(selected_symbols, period)
    
    def _handle_fetch(self, selected_symbols, period):
        """Handle fetching data for selected symbols"""
        if 'All' in selected_symbols:
            symbols_to_fetch = [i['symbol'] for i in self.instruments]
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
