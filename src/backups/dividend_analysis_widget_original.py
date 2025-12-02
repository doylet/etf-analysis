"""
Dividend analysis widget - shows dividend history and cash flows
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from .base_widget import BaseWidget


class DividendAnalysisWidget(BaseWidget):
    """Widget showing dividend history and cash flow tracking"""
    
    def get_name(self) -> str:
        return "Dividend Analysis"
    
    def get_description(self) -> str:
        return "Track dividend history and actual dividend cash flows received"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render dividend analysis"""
        with st.container(border=True):
            if not instruments:
                st.info("No instruments in portfolio")
                return
            
            # Get holdings with quantities > 0
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            symbols = [h['symbol'] for h in holdings] if holdings else [i['symbol'] for i in instruments]
            
            if not symbols:
                st.info("No holdings to track dividends for")
                return
            
            # Tab selection
            tab1, tab2, tab3 = st.tabs(["Dividend History", "Cash Flow Tracker", "Summary"])
            
            with tab1:
                self._render_dividend_history(symbols)
            
            with tab2:
                self._render_cash_flow_tracker(holdings)
            
            with tab3:
                self._render_dividend_summary(symbols)
    
    def _render_dividend_history(self, symbols: List[str]):
        """Render historical dividend data"""
        st.subheader("Dividend History")
        
        # Fetch button
        col1, col2 = st.columns([3, 1])
        with col1:
            fetch_symbol = st.selectbox(
                "Fetch dividend data for:",
                options=symbols,
                key=f"{self.widget_id}_fetch_symbol"
            )
        
        with col2:
            st.space("small")  # Spacing
            if st.button("Fetch Dividends", key=f"{self.widget_id}_fetch_btn"):
                result = self.storage.fetch_and_store_dividends(fetch_symbol)
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
        
        
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            selected_symbol = st.selectbox(
                "Filter by symbol:",
                options=['All'] + symbols,
                key=f"{self.widget_id}_hist_filter"
            )
        
        with col2:
            period = st.selectbox(
                "Period:",
                options=['All Time', '1 Year', '2 Years', '5 Years'],
                key=f"{self.widget_id}_hist_period"
            )
        
        # Get dividend data
        end_date = datetime.now()
        start_date = None
        
        if period == '1 Year':
            start_date = end_date - timedelta(days=365)
        elif period == '2 Years':
            start_date = end_date - timedelta(days=730)
        elif period == '5 Years':
            start_date = end_date - timedelta(days=1825)
        
        symbol_filter = None if selected_symbol == 'All' else selected_symbol
        dividends = self.storage.get_dividends(symbol_filter, start_date, end_date)
        
        if dividends:
            df = pd.DataFrame(dividends)
            df['ex_date'] = pd.to_datetime(df['ex_date']).dt.date
            display_df = df[['symbol', 'ex_date', 'amount', 'dividend_type']]
            display_df.columns = ['Symbol', 'Ex-Date', 'Amount ($)', 'Type']
            
            st.dataframe(display_df, hide_index=True, width='stretch')
            
            # Summary stats
            total_dividends = df['amount'].sum()
            avg_dividend = df['amount'].mean()
            st.caption(f"Total: ${total_dividends:.2f} | Average: ${avg_dividend:.2f} | Count: {len(df)}")
        else:
            st.info("No dividend data. Use 'Fetch Dividends' button above to fetch from yfinance.")
    
    def _render_cash_flow_tracker(self, holdings: List[Dict]):
        """Render dividend cash flow recording and display"""
        st.subheader("Dividend Cash Flow Tracker")
        
        # Auto-calculate button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**Auto-Calculate Dividends:**")
            st.caption("Automatically calculate dividends received based on your holdings at each ex-dividend date")
        with col2:
            if st.button("Auto-Calculate All", key=f"{self.widget_id}_auto_calc", type="primary"):
                with st.spinner("Calculating dividends from holdings..."):
                    result = self.storage.auto_populate_dividend_cash_flows()
                    if result['success']:
                        st.success(f"{result['message']}")
                        st.rerun()
                    else:
                        st.error(result['message'])
        
        
        
        st.write("**Manual Entry (Optional):**")
        st.caption("Use this only if you need to override or add custom dividend entries")
        
        # Form to record dividend cash flow
        with st.form(key=f"{self.widget_id}_cash_flow_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                cf_symbol = st.selectbox(
                    "Symbol:",
                    options=[h['symbol'] for h in holdings],
                    key=f"{self.widget_id}_cf_symbol"
                )
                cf_date = st.date_input(
                    "Payment Date:",
                    value=datetime.now(),
                    key=f"{self.widget_id}_cf_date"
                )
            
            with col2:
                cf_shares = st.number_input(
                    "Shares Held:",
                    min_value=0.0,
                    step=1.0,
                    key=f"{self.widget_id}_cf_shares"
                )
                cf_per_share = st.number_input(
                    "Dividend per Share:",
                    min_value=0.0,
                    step=0.01,
                    format="%.4f",
                    key=f"{self.widget_id}_cf_per_share"
                )
            
            cf_notes = st.text_input(
                "Notes (optional):",
                key=f"{self.widget_id}_cf_notes"
            )
            
            total_preview = cf_shares * cf_per_share
            st.info(f"Total Amount: ${total_preview:.2f}")
            
            submitted = st.form_submit_button("Record Dividend", type="primary")
            
            if submitted and cf_shares > 0 and cf_per_share > 0:
                result = self.storage.record_dividend_cash_flow(
                    cf_symbol,
                    datetime.combine(cf_date, datetime.min.time()),
                    cf_shares,
                    cf_per_share,
                    cf_notes
                )
                
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
        
        
        
        # Display recorded cash flows
        st.write("**Dividend Cash Flows:**")
        
        cash_flows = self.storage.get_dividend_cash_flows()
        
        if cash_flows:
            df = pd.DataFrame(cash_flows)
            df['payment_date'] = pd.to_datetime(df['payment_date']).dt.date
            display_df = df[['symbol', 'payment_date', 'shares_held', 'dividend_per_share', 'total_amount', 'notes']]
            display_df.columns = ['Symbol', 'Payment Date', 'Shares', '$ Per Share', 'Total ($)', 'Notes']
            
            st.dataframe(display_df, hide_index=True, width='stretch')
            
            total_received = df['total_amount'].sum()
            st.metric("Total Dividends Received", f"${total_received:,.2f}")
        else:
            st.info("No dividend cash flows recorded yet.")
    
    def _render_dividend_summary(self, symbols: List[str]):
        """Render dividend summary statistics"""
        st.subheader("Dividend Summary")
        
        # Calculate totals
        total_all_time = self.storage.calculate_total_dividends_received()
        total_1y = self.storage.calculate_total_dividends_received(
            start_date=datetime.now() - timedelta(days=365)
        )
        total_ytd = self.storage.calculate_total_dividends_received(
            start_date=datetime(datetime.now().year, 1, 1)
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total (All Time)", f"${total_all_time:,.2f}")
        
        with col2:
            st.metric("Last 12 Months", f"${total_1y:,.2f}")
        
        with col3:
            st.metric("Year to Date", f"${total_ytd:,.2f}")
        
        
        
        # Per-symbol breakdown
        st.write("**By Symbol:**")
        
        symbol_data = []
        for symbol in symbols:
            total = self.storage.calculate_total_dividends_received(symbol=symbol)
            if total > 0:
                symbol_data.append({
                    'Symbol': symbol,
                    'Total Received': f"${total:,.2f}"
                })
        
        if symbol_data:
            df = pd.DataFrame(symbol_data)
            st.dataframe(df, hide_index=True, width='stretch')
        else:
            st.info("No dividend cash flows recorded yet.")
