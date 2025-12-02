"""
Order form component for recording trades
"""

import streamlit as st
from datetime import datetime
from src.components import SymbolSearchComponent


class OrderFormComponent:
    """Component for creating buy/sell orders"""
    
    def __init__(self, storage, av_client, instruments):
        self.storage = storage
        self.av_client = av_client
        self.instruments = instruments
    
    def render(self):
        """Render the order form"""
        st.subheader("Record Trade")
        
        # Show success message if one exists from previous submission
        if 'order_success' in st.session_state:
            st.success(st.session_state.order_success)
            del st.session_state.order_success
        
        # Symbol search section
        search = SymbolSearchComponent(self.av_client)
        search.render()
        
        # Get symbol from search or allow manual entry
        selected_symbol = st.session_state.get('selected_symbol', '')
        
        with st.form("order_form", clear_on_submit=True, border=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Always show text input, optionally with autocomplete from existing
                if self.instruments and not selected_symbol:
                    # Show dropdown if no search result and we have instruments
                    symbol = st.selectbox(
                        "Instrument",
                        options=[i['symbol'] for i in self.instruments],
                        # format_func=lambda x: f"{x} - {next((i['name'][:30] for i in self.instruments if i['symbol'] == x), x)}"
                    )
                else:
                    # Show text input (for search results or manual entry)
                    symbol = st.text_input(
                        "Symbol*",
                        value=selected_symbol,
                        placeholder="e.g., AAPL, QQQ"
                    )
                    if symbol:
                        symbol = symbol.upper()
            
            with col2:
                order_type = st.selectbox(
                    "Order Type",
                    options=["Buy", "Sell"]
                )
            
            col3, col4 = st.columns(2)
            
            with col3:
                volume = st.number_input(
                    "Volume (shares)",
                    min_value=1,
                    value=1,
                    step=1,
                    help="Number of shares to buy or sell"
                )
            
            with col4:
                order_date = st.date_input(
                    "Trade Date",
                    value=datetime.now(),
                    help="Date the trade was executed"
                )
            
            notes = st.text_area(
                "Notes (optional)",
                placeholder="e.g., Price per share, broker, trade reason..."
            )
            
            submitted = st.form_submit_button(f"Record {order_type} Order", type="primary")
            
            if submitted:
                if not symbol:
                    st.error("Please enter a symbol")
                elif volume <= 0:
                    st.error("Volume must be greater than 0")
                else:
                    self._handle_order(symbol, order_type, volume, order_date, notes)
    
    def _handle_order(self, symbol, order_type, volume, order_date, notes):
        """Handle creating an order"""
        # Prevent double submission with a unique key
        submission_key = f"processing_order_{symbol}_{order_type}_{volume}_{order_date}"
        
        # Check if we're already processing this exact order
        if submission_key in st.session_state:
            return  # Skip duplicate submission
        
        # Mark as processing
        st.session_state[submission_key] = True
        
        try:
            with st.spinner(f"Recording {order_type} order..."):
                # Check if instrument exists, if not, add it
                existing = self.storage.get_instrument(symbol)
                
                if not existing:
                    # Fetch instrument data from yfinance (more reliable than Alpha Vantage)
                    try:
                        import yfinance as yf
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        
                        name = info.get('longName') or info.get('shortName') or symbol
                        
                        # Determine instrument type
                        quote_type = info.get('quoteType', 'EQUITY')
                        if quote_type == 'ETF':
                            instrument_type = 'ETF'
                        elif 'INDEX' in quote_type:
                            instrument_type = 'Index'
                        else:
                            instrument_type = 'Stock'
                        
                        sector = info.get('sector', None)
                    except Exception as e:
                        # Fallback if yfinance fails
                        st.warning(f"Could not fetch data for {symbol}: {str(e)}. Adding with basic info.")
                        name = symbol
                        instrument_type = 'Stock'
                        sector = None
                    
                    # Add the instrument
                    add_result = self.storage.add_instrument(
                        symbol=symbol,
                        name=name,
                        instrument_type=instrument_type,
                        sector=sector,
                        notes=f"Auto-added from {order_type} order"
                    )
                    
                    if not add_result['success']:
                        st.error(f"Failed to add instrument: {add_result['message']}")
                        return
                
                # Convert date to datetime
                order_datetime = datetime.combine(order_date, datetime.min.time())
                st.write(f"DEBUG: order_date input: {order_date}, order_datetime: {order_datetime}")
                
                # Create the order
                result = self.storage.create_order(
                    symbol=symbol,
                    order_type=order_type,
                    volume=volume,
                    order_date=order_datetime,
                    notes=notes if notes else None
                )
                
                if result['success']:
                    # Store success message in session state to show after rerun
                    if not existing:
                        st.session_state.order_success = f"✓ Added {symbol} and recorded {order_type} of {volume} units"
                    else:
                        st.session_state.order_success = f"✓ {order_type} {volume} units of {symbol}"
                    
                    # Clear search state and submission key
                    for key in ['selected_symbol', 'selected_name', 'selected_type', 'selected_sector']:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    # Clear the processing flag after successful submission
                    submission_key = f"processing_order_{symbol}_{order_type}_{volume}_{order_date}"
                    if submission_key in st.session_state:
                        del st.session_state[submission_key]
                    
                    st.rerun()
                else:
                    st.error(result['message'])
        except Exception as e:
            st.error(f"Error recording order: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
