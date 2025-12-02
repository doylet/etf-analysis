"""
Instrument form component for adding new instruments to track
"""

import streamlit as st


class AddInstrumentFormComponent:
    """Component for adding new instruments to the portfolio"""
    
    def __init__(self, storage, av_client):
        self.storage = storage
        self.av_client = av_client
    
    def render(self):
        """Render the add instrument form"""
        
        # Get values from session state (populated by search component)
        symbol = st.session_state.get('selected_symbol', '')
        name = st.session_state.get('selected_name', '')
        instrument_type = st.session_state.get('selected_type', 'ETF')
        sector = st.session_state.get('selected_sector', '')
        
        with st.form("add_instrument_form", clear_on_submit=True, border=False):
            st.subheader("Add Instrument")
            
            col1, col2 = st.columns(2)
            
            with col1:
                form_symbol = st.text_input(
                    "Symbol*",
                    value=symbol,
                    placeholder="e.g., AAPL"
                )
            
            with col2:
                form_name = st.text_input(
                    "Name",
                    value=name,
                    placeholder="e.g., Apple Inc."
                )
            
            col3, col4 = st.columns(2)
            
            with col3:
                form_type = st.selectbox(
                    "Type",
                    options=['Stock', 'ETF', 'Index', 'Crypto', 'Other'],
                    index=['Stock', 'ETF', 'Index', 'Crypto', 'Other'].index(instrument_type) if instrument_type in ['Stock', 'ETF', 'Index', 'Crypto', 'Other'] else 1
                )
            
            with col4:
                form_sector = st.text_input(
                    "Sector",
                    value=sector,
                    placeholder="e.g., Technology"
                )
            
            notes = st.text_area(
                "Notes (optional)",
                placeholder="Any additional information about this instrument..."
            )
            
            submitted = st.form_submit_button("Add Instrument", type="primary")
            
            if submitted and form_symbol:
                self._handle_add(
                    form_symbol.upper(),
                    form_name,
                    form_type,
                    form_sector,
                    notes if notes else None
                )
    
    def _handle_add(self, symbol, name, instrument_type, sector, notes):
        """Handle adding an instrument"""
        
        # First check if instrument already exists
        existing = self.storage.get_instrument(symbol)
        if existing:
            st.error(f"Instrument {symbol} already exists in your portfolio.")
            return
        
        with st.spinner("Adding instrument..."):
            # Fetch additional data from Alpha Vantage if needed
            if not name:
                overview = self.av_client.get_company_overview(symbol)
                if overview:
                    name = overview.get('Name', symbol)
                    if not sector:
                        sector = overview.get('Sector', '')
            
            result = self.storage.add_instrument(
                symbol=symbol,
                name=name if name else symbol,
                instrument_type=instrument_type,
                sector=sector if sector else None,
                notes=notes
            )
            
            if result['success']:
                st.success(f"✓ Added {symbol} to your portfolio")
                # Clear search state
                if 'selected_symbol' in st.session_state:
                    del st.session_state.selected_symbol
                if 'selected_name' in st.session_state:
                    del st.session_state.selected_name
                if 'selected_type' in st.session_state:
                    del st.session_state.selected_type
                if 'selected_sector' in st.session_state:
                    del st.session_state.selected_sector
                st.rerun()
            else:
                st.error(result['message'])
