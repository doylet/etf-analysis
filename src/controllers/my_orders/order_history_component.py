"""
Order history component for displaying and managing orders
"""

import streamlit as st
import pandas as pd


class OrderHistoryComponent:
    """Component for displaying order history"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def render(self, symbol=None):
        """Render order history table"""
        st.subheader("Order History")
        
        orders = self.storage.get_orders(symbol)
        
        if not orders:
            st.info("No orders recorded yet.")
            return
        
        # Build DataFrame
        rows = []
        for order in orders:
            rows.append({
                'Select': False,
                'Date': pd.to_datetime(order['order_date']).strftime('%Y-%m-%d'),
                'Symbol': order['symbol'],
                'Type': order['order_type'],
                'Volume': order['volume'],
                'Notes': order.get('notes', ''),
                'id': order['id']  # Hidden column for deletion
            })
        
        df = pd.DataFrame(rows)
        
        # Display editable dataframe
        edited_df = st.data_editor(
            df,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select rows to delete",
                    default=False,
                ),
                "Date": st.column_config.TextColumn("Date", disabled=True),
                "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
                "Type": st.column_config.TextColumn("Type", disabled=True),
                "Volume": st.column_config.NumberColumn(
                    "Volume",
                    disabled=True,
                    format="%.2f"
                ),
                "Notes": st.column_config.TextColumn("Notes", disabled=True),
                "id": None,  # Hide the id column
            },
            hide_index=True,
            width="content",
            key="order_history_table"
        )
        
        # Bulk delete button
        selected_rows = edited_df[edited_df['Select'] == True]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if not selected_rows.empty:
                st.caption(f"{len(selected_rows)} order(s) selected")
        with col2:
            if st.button("Delete Selected", type="primary", key="delete_orders_btn", disabled=selected_rows.empty):
                self._handle_bulk_delete(selected_rows['id'].tolist())
    
    def _handle_bulk_delete(self, order_ids):
        """Handle deleting multiple orders"""
        success_count = 0
        for order_id in order_ids:
            result = self.storage.delete_order(order_id)
            if result['success']:
                success_count += 1
        
        if success_count > 0:
            st.success(f"Deleted {success_count} order(s)")
            st.rerun()
        else:
            st.error("Failed to delete selected orders")
