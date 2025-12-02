"""
Holdings breakdown widget - shows allocation by sector, type, or individual holdings.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Data fetching and validation (_fetch_*, _prepare_* methods)
- Logic Layer: Pure calculations (_calculate_* static methods)
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass

from .layered_base_widget import LayeredBaseWidget


@dataclass
class HoldingsData:
    """Processed holdings data with valuations."""
    df: pd.DataFrame
    total_value: float
    base_currency: str


class HoldingsBreakdownWidget(LayeredBaseWidget):
    """Widget showing portfolio allocation breakdown"""
    
    def get_name(self) -> str:
        return "Holdings Breakdown"
    
    def get_description(self) -> str:
        return "Breakdown of portfolio allocation by sector, type, or individual positions"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    # ========================================================================
    # UI LAYER - Streamlit rendering methods
    # ========================================================================
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Main render orchestration - UI only.
        
        Parameters:
            instruments: List of instrument dictionaries
            selected_symbols: Optional list of selected symbols
        """
        with st.container(border=True):
            if not instruments:
                st.info("No instruments in portfolio")
                return
            
            # Fetch and prepare holdings data
            holdings_data = self._fetch_holdings_data(instruments)
            
            if holdings_data.df.empty:
                st.info("No active holdings with price data")
                return
            
            # Display portfolio summary
            st.markdown(f"**Total Portfolio Value:** {holdings_data.base_currency} ${holdings_data.total_value:,.2f}")
            
            # Breakdown selector
            breakdown_by = st.selectbox(
                "Breakdown by:",
                options=['Individual', 'Sector', 'Type'],
                key=self._get_session_key("breakdown")
            )
            
            # Render appropriate breakdown
            self._render_breakdown(breakdown_by, holdings_data)
    
    def _render_breakdown(self, breakdown_by: str, holdings_data: HoldingsData):
        """Render the selected breakdown view.
        
        Parameters:
            breakdown_by: Type of breakdown ('Individual', 'Sector', or 'Type')
            holdings_data: Processed holdings data
        """
        if breakdown_by == 'Individual':
            # Check if we have currency data
            has_currency = holdings_data.df['Currency'].notna().any() and (holdings_data.df['Currency'] != '').any()
            
            if has_currency:
                # Multi-currency view
                display_df = holdings_data.df[['Symbol', 'Name', 'Currency', 'Quantity', 'Price', 'Value', 'Value (AUD)', 'Allocation %']]
                display_df = display_df.sort_values('Value (AUD)', ascending=False)
                st.dataframe(display_df, hide_index=True, width='stretch', column_config={
                    "Value": st.column_config.NumberColumn("Value (Local)", format="%.2f"),
                    "Value (AUD)": st.column_config.NumberColumn("Value (AUD)", format="%.2f"),
                    "Price": st.column_config.NumberColumn("Price", format="%.2f"),
                    "Allocation %": st.column_config.NumberColumn("Allocation %", format="%.2f%%"),
                })
            else:
                # Simple view (backward compatible)
                display_df = holdings_data.df[['Symbol', 'Name', 'Quantity', 'Price', 'Value', 'Allocation %']]
                display_df = display_df.sort_values('Value', ascending=False)
                st.dataframe(display_df, hide_index=True, width='stretch', column_config={
                    "Value": st.column_config.NumberColumn("Value", format="%.2f"),
                    "Price": st.column_config.NumberColumn("Price", format="%.2f"),
                    "Allocation %": st.column_config.NumberColumn("Allocation %", format="%.2f%%"),
                })
        
        elif breakdown_by == 'Sector':
            sector_df = self._calculate_grouped_breakdown(
                holdings_data.df, 'Sector', holdings_data.total_value
            )
            st.dataframe(sector_df, hide_index=True, width='stretch')
        
        elif breakdown_by == 'Type':
            type_df = self._calculate_grouped_breakdown(
                holdings_data.df, 'Type', holdings_data.total_value
            )
            st.dataframe(type_df, hide_index=True, width='stretch')
    
    # ========================================================================
    # DATA LAYER - Data fetching and validation methods
    # ========================================================================
    
    def _fetch_holdings_data(self, instruments: List[Dict]) -> HoldingsData:
        """Fetch holdings data with latest prices and calculate values.
        
        Parameters:
            instruments: List of instrument dictionaries (pre-enriched with currency conversion)
            
        Returns:
            HoldingsData: Processed holdings with valuations
        """
        # Check if instruments are pre-enriched with currency data
        has_currency_data = any(inst.get('value_base') is not None for inst in instruments)
        base_currency = instruments[0].get('base_currency', 'AUD') if instruments else 'AUD'
        
        # Build holdings data
        holdings_data = []
        for inst in instruments:
            quantity = inst.get('quantity', 0)
            
            if quantity > 0 and inst.get('price', 0) > 0:
                # Use pre-calculated values if available
                if has_currency_data:
                    holdings_data.append({
                        'Symbol': inst['symbol'],
                        'Name': inst['name'],
                        'Currency': inst.get('currency', 'USD'),
                        'Sector': inst['sector'],
                        'Type': inst['type'],
                        'Quantity': quantity,
                        'Price': inst['price'],
                        'Value': inst['value_local'],
                        'Value (AUD)': inst['value_base']
                    })
                else:
                    # Fallback to simple calculation
                    holdings_data.append({
                        'Symbol': inst['symbol'],
                        'Name': inst['name'],
                        'Currency': '',
                        'Sector': inst['sector'],
                        'Type': inst['type'],
                        'Quantity': quantity,
                        'Price': inst.get('price', 0),
                        'Value': inst.get('value_local', 0),
                        'Value (AUD)': inst.get('value_local', 0)
                    })
        
        if not holdings_data:
            return HoldingsData(df=pd.DataFrame(), total_value=0, base_currency=base_currency)
        
        df = pd.DataFrame(holdings_data)
        total_value = df['Value (AUD)'].sum()
        df['Allocation %'] = self._calculate_allocation_percentages(df['Value (AUD)'], total_value)
        
        return HoldingsData(df=df, total_value=total_value, base_currency=base_currency)
    
    # ========================================================================
    # LOGIC LAYER - Pure calculation methods
    # ========================================================================
    
    @staticmethod
    def _calculate_allocation_percentages(values: pd.Series, total_value: float) -> pd.Series:
        """Calculate allocation percentages.
        
        Parameters:
            values: Series of position values
            total_value: Total portfolio value
            
        Returns:
            pd.Series: Allocation percentages
        """
        return (values / total_value * 100).round(2)
    
    @staticmethod
    def _calculate_grouped_breakdown(df: pd.DataFrame, group_by: str, 
                                     total_value: float) -> pd.DataFrame:
        """Calculate grouped breakdown by sector or type.
        
        Parameters:
            df: Holdings dataframe
            group_by: Column to group by ('Sector' or 'Type')
            total_value: Total portfolio value
            
        Returns:
            pd.DataFrame: Grouped breakdown with allocations
        """
        grouped_df = df.groupby(group_by).agg({'Value (AUD)': 'sum'}).reset_index()
        grouped_df.rename(columns={'Value (AUD)': 'Value'}, inplace=True)
        grouped_df['Allocation %'] = (grouped_df['Value'] / total_value * 100).round(2)
        grouped_df = grouped_df.sort_values('Value', ascending=False)
        return grouped_df
