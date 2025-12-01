"""
Instrument list component
"""

import streamlit as st
import pandas as pd


class InstrumentListComponent:
    """Component for displaying and managing portfolio holdings"""
    
    def __init__(self, storage, instruments):
        self.storage = storage
        self.instruments = instruments
        self._fetch_latest_prices()
    
    def _fetch_latest_prices(self):
        """Fetch latest prices for all instruments"""
        symbols = [i['symbol'] for i in self.instruments]
        if symbols:
            self.latest_prices = self.storage.get_latest_prices(symbols)
        else:
            self.latest_prices = {}
    
    def render(self):
        """Render the portfolio holdings table with inline editing"""
        st.subheader("Portfolio Holdings")
        
        if not self.instruments:
            st.info("No instruments tracked yet. Add some above!")
            return
        
        # Filter to only show instruments with orders (quantity > 0 or had orders)
        holdings_instruments = [i for i in self.instruments if i.get('quantity', 0) != 0]
        
        if not holdings_instruments:
            st.info("No portfolio holdings yet. Record your first order below!")
            return
        
        # Build DataFrame
        rows = []
        for instrument in holdings_instruments:
            symbol = instrument['symbol']
            quantity = instrument.get('quantity', 0.0)
            
            # Get latest price data
            price_data = self.latest_prices.get(symbol, {})
            current_price = price_data.get('close')
            prev_close = price_data.get('prev_close')
            
            # Calculate values
            position_value = (quantity * current_price) if current_price and quantity else None
            day_change = ((current_price - prev_close) / prev_close * 100) if current_price and prev_close else None
            
            rows.append({
                'Select': False,
                'Symbol': symbol,
                'Name': instrument['name'][:40] + '...' if len(instrument['name']) > 40 else instrument['name'],
                'Type': instrument['type'],
                'Quantity': quantity,
                'Price': current_price,
                'Value': position_value,
                'Day Change %': day_change,
            })
        
        df = pd.DataFrame(rows)
        
        # Store original quantities for comparison
        if 'original_quantities' not in st.session_state:
            st.session_state.original_quantities = df[['Symbol', 'Quantity']].copy()
        
        # Display editable dataframe
        edited_df = st.data_editor(
            df,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select rows to delete",
                    default=False,
                ),
                "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
                "Name": st.column_config.TextColumn("Name", disabled=True),
                "Type": st.column_config.TextColumn("Type", disabled=True),
                "Quantity": st.column_config.NumberColumn(
                    "Quantity",
                    min_value=0.0,
                    step=0.1,
                    format="%.1f"
                ),
                "Price": st.column_config.NumberColumn(
                    "Price",
                    disabled=True,
                    format="$%.2f"
                ),
                "Value": st.column_config.NumberColumn(
                    "Value",
                    disabled=True,
                    format="$%.2f"
                ),
                "Day Change %": st.column_config.NumberColumn(
                    "Day Change %",
                    disabled=True,
                    format="%.2f%%"
                ),
            },
            hide_index=True,
            width='stretch',
            key="portfolio_table"
        )
        
        # Detect and handle quantity changes
        # DISABLED: This auto-creates orders when editing quantities which causes duplicate orders
        # self._handle_quantity_changes(edited_df)
        
        # Bulk delete button
        selected_rows = edited_df[edited_df['Select'] == True]
        if not selected_rows.empty:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"{len(selected_rows)} row(s) selected")
            with col2:
                if st.button("Delete Selected", type="primary", width='stretch'):
                    self._handle_bulk_delete(selected_rows['Symbol'].tolist())
    
    def _handle_quantity_changes(self, edited_df):
        """Detect and handle quantity changes by creating Buy/Sell orders"""
        if 'original_quantities' not in st.session_state:
            return
        
        original_df = st.session_state.original_quantities
        
        # Compare quantities row by row
        for idx in range(len(edited_df)):
            symbol = edited_df.iloc[idx]['Symbol']
            new_qty = edited_df.iloc[idx]['Quantity']
            
            # Find original quantity for this symbol
            original_row = original_df[original_df['Symbol'] == symbol]
            if not original_row.empty:
                old_qty = original_row.iloc[0]['Quantity']
                
                if old_qty != new_qty:
                    # Calculate the difference
                    diff = new_qty - old_qty
                    
                    if diff > 0:
                        # Increase = Buy order
                        order_type = 'Buy'
                        volume = diff
                    else:
                        # Decrease = Sell order
                        order_type = 'Sell'
                        volume = abs(diff)
                    
                    # Create the order
                    result = self.storage.create_order(
                        symbol=symbol,
                        order_type=order_type,
                        volume=volume,
                        notes=f'Adjusted from {old_qty} to {new_qty}'
                    )
                    
                    if result['success']:
                        st.success(f"{order_type} {volume} units of {symbol} (new position: {new_qty})")
                        # Clear cache and rerun
                        del st.session_state.original_quantities
                        st.rerun()
                    else:
                        st.error(result['message'])
                    break  # Only process one change at a time
    
    def _handle_bulk_delete(self, symbols):
        """Handle deleting multiple instruments"""
        success_count = 0
        for symbol in symbols:
            result = self.storage.remove_instrument(symbol)
            if result['success']:
                success_count += 1
        
        if success_count > 0:
            st.success(f"Deleted {success_count} instrument(s)")
            # Clear session state cache
            if 'original_quantities' in st.session_state:
                del st.session_state.original_quantities
            st.rerun()
        else:
            st.error("Failed to delete selected instruments")
    
    def _handle_delete(self, symbol):
        """Handle deleting an instrument"""
        result = self.storage.remove_instrument(symbol)
        if result['success']:
            st.success(result['message'])
            st.rerun()
        else:
            st.error(result['message'])
