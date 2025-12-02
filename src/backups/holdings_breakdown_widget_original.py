"""
Holdings breakdown widget - shows allocation by sector, type, or individual holdings
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from .base_widget import BaseWidget


class HoldingsBreakdownWidget(BaseWidget):
    """Widget showing portfolio allocation breakdown"""
    
    def get_name(self) -> str:
        return "Holdings Breakdown"
    
    def get_description(self) -> str:
        return "Breakdown of portfolio allocation by sector, type, or individual positions"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render holdings breakdown"""
        with st.container(border=True):
            if not instruments:
                st.info("No instruments in portfolio")
                return
            
            # Get latest prices
            symbols = [i['symbol'] for i in instruments]
            latest_prices = self.storage.get_latest_prices(symbols)
            
            # Calculate holdings value
            holdings_data = []
            for inst in instruments:
                symbol = inst['symbol']
                quantity = inst.get('quantity', 0)
                
                if quantity > 0 and symbol in latest_prices:
                    price = latest_prices[symbol]['close']
                    value = quantity * price
                    holdings_data.append({
                        'Symbol': symbol,
                        'Name': inst['name'],
                        'Sector': inst['sector'],
                        'Type': inst['type'],
                        'Quantity': quantity,
                        'Price': price,
                        'Value': value
                    })
            
            if not holdings_data:
                st.info("No active holdings with price data")
                return
            
            df = pd.DataFrame(holdings_data)
            total_value = df['Value'].sum()
            df['Allocation %'] = (df['Value'] / total_value * 100).round(2)
            
            # Portfolio summary
            st.markdown(f"**Total Portfolio Value:** ${total_value:,.2f}")
            st.divider()
            
            # Breakdown selector
            breakdown_by = st.selectbox(
                "Breakdown by:",
                options=['Individual', 'Sector', 'Type'],
                key=f"{self.widget_id}_breakdown"
            )
            
            if breakdown_by == 'Individual':
                display_df = df[['Symbol', 'Name', 'Quantity', 'Price', 'Value', 'Allocation %']]
                display_df = display_df.sort_values('Value', ascending=False)
                st.dataframe(display_df, hide_index=True, width='stretch')
            
            elif breakdown_by == 'Sector':
                sector_df = df.groupby('Sector').agg({
                    'Value': 'sum'
                }).reset_index()
                sector_df['Allocation %'] = (sector_df['Value'] / total_value * 100).round(2)
                sector_df = sector_df.sort_values('Value', ascending=False)
                st.dataframe(sector_df, hide_index=True, width='stretch')
            
            elif breakdown_by == 'Type':
                type_df = df.groupby('Type').agg({
                    'Value': 'sum'
                }).reset_index()
                type_df['Allocation %'] = (type_df['Value'] / total_value * 100).round(2)
                type_df = type_df.sort_values('Value', ascending=False)
                st.dataframe(type_df, hide_index=True, width='stretch')
