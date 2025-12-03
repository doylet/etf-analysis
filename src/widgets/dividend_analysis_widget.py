"""
Dividend analysis widget - shows dividend history and cash flows.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Data fetching and validation (_fetch_*, _prepare_* methods)
- Logic Layer: Pure calculations (_calculate_* static methods)
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .layered_base_widget import LayeredBaseWidget


@dataclass
class DividendSummary:
    """Summary of dividend statistics."""
    total_all_time: float
    total_1y: float
    total_ytd: float
    symbol_breakdown: List[Dict[str, str]]


class DividendAnalysisWidget(LayeredBaseWidget):
    """Widget showing dividend history and cash flow tracking"""
    
    def get_name(self) -> str:
        return "Dividend Analysis"
    
    def get_description(self) -> str:
        return "Track dividend history and actual dividend cash flows received"
    
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
            
            # Get ALL instruments for dividend fetching (not just holdings)
            all_instruments = self.storage.get_all_instruments(active_only=False)
            all_symbols = [i['symbol'] for i in all_instruments]
            
            # Prepare data for holdings-specific features
            holdings, holding_symbols = self._prepare_holdings_and_symbols(instruments)
            
            # Tab selection
            tab1, tab2, tab3 = st.tabs(["Dividend History", "Cash Flow Tracker", "Summary"])
            
            with tab1:
                # Allow fetching dividends for ANY instrument
                self._render_dividend_history(all_symbols, holding_symbols)
            
            with tab2:
                if not holding_symbols:
                    st.info("No holdings to track cash flows for. Add positions to use this feature.")
                else:
                    self._render_cash_flow_tracker(holdings)
            
            with tab3:
                if not holding_symbols:
                    st.info("No holdings to summarize. Add positions to use this feature.")
                else:
                    self._render_dividend_summary(holding_symbols)
    
    def _render_dividend_history(self, all_symbols: List[str], holding_symbols: List[str]):
        """Render historical dividend data.
        
        Parameters:
            all_symbols: All available symbols (for fetching)
            holding_symbols: Symbols in current holdings (for filtering)
        """
        st.subheader("Dividend History")
        
        # Fetch button - allow fetching for ANY instrument
        col1, col2 = st.columns([3, 1])
        with col1:
            fetch_symbol = st.selectbox(
                "Fetch dividend data for:",
                options=all_symbols,
                key=self._get_session_key("fetch_symbol"),
                help="Fetch dividends for any instrument (not just holdings)"
            )
        
        with col2:
            st.space("small")
            if st.button("Fetch Dividends", key=self._get_session_key("fetch_btn")):
                result = self.storage.fetch_and_store_dividends(fetch_symbol)
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
        
        st.space("small")
        
        # Filter options - use holding_symbols if available, otherwise all_symbols
        filter_symbols = holding_symbols if holding_symbols else all_symbols
        selected_symbol, start_date = self._render_history_filters(filter_symbols)
        
        # Get dividend data
        symbol_filter = None if selected_symbol == 'All' else selected_symbol
        dividends = self.storage.get_dividends(symbol_filter, start_date, datetime.now())
        
        if dividends:
            self._render_dividend_history_table(dividends)
        else:
            st.info("No dividend data. Use 'Fetch Dividends' button above to fetch from yfinance.")
    
    def _render_history_filters(self, symbols: List[str]) -> Tuple[str, Optional[datetime]]:
        """Render filter controls for dividend history.
        
        Parameters:
            symbols: Available symbols for filtering
            
        Returns:
            Tuple[str, Optional[datetime]]: Selected symbol and start date
        """
        col1, col2 = st.columns(2)
        
        with col1:
            selected_symbol = st.selectbox(
                "Filter by symbol:",
                options=['All'] + symbols,
                key=self._get_session_key("hist_filter")
            )
        
        with col2:
            period = st.selectbox(
                "Period:",
                options=['All Time', '1 Year', '2 Years', '5 Years'],
                key=self._get_session_key("hist_period")
            )
        
        # Calculate start date
        start_date = self._calculate_period_start_date(period)
        return selected_symbol, start_date
    
    def _render_dividend_history_table(self, dividends: List[Dict]):
        """Display dividend history as table with statistics.
        
        Parameters:
            dividends: List of dividend dictionaries
        """
        df = pd.DataFrame(dividends)
        df['ex_date'] = pd.to_datetime(df['ex_date']).dt.date
        display_df = df[['symbol', 'ex_date', 'amount', 'dividend_type']]
        display_df.columns = ['Symbol', 'Ex-Date', 'Amount ($)', 'Type']
        
        st.dataframe(display_df, hide_index=True, width='stretch')
        
        # Summary stats
        total_dividends = df['amount'].sum()
        avg_dividend = df['amount'].mean()
        st.caption(f"Total: ${total_dividends:.2f} | Average: ${avg_dividend:.2f} | Count: {len(df)}")
    
    def _render_cash_flow_tracker(self, holdings: List[Dict]):
        """Render dividend cash flow recording and display.
        
        Parameters:
            holdings: List of holding dictionaries
        """
        st.subheader("Dividend Cash Flow Tracker")
        
        # Auto-calculate button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**Auto-Calculate Dividends:**")
            st.caption("Automatically calculate dividends received based on your holdings at each ex-dividend date")
        with col2:
            if st.button("Auto-Calculate All", key=self._get_session_key("auto_calc"), type="primary"):
                with st.spinner("Calculating dividends from holdings..."):
                    result = self.storage.auto_populate_dividend_cash_flows()
                    if result['success']:
                        st.success(f"{result['message']}")
                        st.rerun()
                    else:
                        st.error(result['message'])
        
        st.space("small")
        
        # Manual entry form
        self._render_manual_entry_form(holdings)
        
        st.space("small")
        
        # Display recorded cash flows
        self._render_cash_flows_table()
    
    def _render_manual_entry_form(self, holdings: List[Dict]):
        """Render manual dividend entry form.
        
        Parameters:
            holdings: List of holding dictionaries
        """
        st.write("**Manual Entry (Optional):**")
        st.caption("Use this only if you need to override or add custom dividend entries")
        
        with st.form(key=self._get_session_key("cash_flow_form")):
            col1, col2 = st.columns(2)
            
            with col1:
                cf_symbol = st.selectbox(
                    "Symbol:",
                    options=[h['symbol'] for h in holdings],
                    key=self._get_session_key("cf_symbol")
                )
                cf_date = st.date_input(
                    "Payment Date:",
                    value=datetime.now(),
                    key=self._get_session_key("cf_date")
                )
            
            with col2:
                cf_shares = st.number_input(
                    "Shares Held:",
                    min_value=0.0,
                    step=1.0,
                    key=self._get_session_key("cf_shares")
                )
                cf_per_share = st.number_input(
                    "Dividend per Share:",
                    min_value=0.0,
                    step=0.01,
                    format="%.4f",
                    key=self._get_session_key("cf_per_share")
                )
            
            cf_notes = st.text_input(
                "Notes (optional):",
                key=self._get_session_key("cf_notes")
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
    
    def _render_cash_flows_table(self):
        """Display recorded dividend cash flows."""
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
        """Render dividend summary statistics.
        
        Parameters:
            symbols: List of symbols to summarize
        """
        st.subheader("Dividend Summary")
        
        # Fetch summary data
        summary = self._fetch_dividend_summary(symbols)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total (All Time)", f"${summary.total_all_time:,.2f}")
        
        with col2:
            st.metric("Last 12 Months", f"${summary.total_1y:,.2f}")
        
        with col3:
            st.metric("Year to Date", f"${summary.total_ytd:,.2f}")
        
        st.space("small")
        
        # Per-symbol breakdown
        st.write("**By Symbol:**")
        
        if summary.symbol_breakdown:
            df = pd.DataFrame(summary.symbol_breakdown)
            st.dataframe(df, hide_index=True, width='stretch')
        else:
            st.info("No dividend cash flows recorded yet.")
    
    # ========================================================================
    # DATA LAYER - Data fetching and validation methods
    # ========================================================================
    
    def _prepare_holdings_and_symbols(self, instruments: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Prepare holdings and symbols lists from instruments.
        
        Parameters:
            instruments: List of instrument dictionaries
            
        Returns:
            Tuple[List[Dict], List[str]]: Holdings list and symbols list
        """
        holdings = [i for i in instruments if i.get('quantity', 0) > 0]
        symbols = [h['symbol'] for h in holdings] if holdings else [i['symbol'] for i in instruments]
        return holdings, symbols
    
    def _fetch_dividend_summary(self, symbols: List[str]) -> DividendSummary:
        """Fetch dividend summary data from storage.
        
        Parameters:
            symbols: List of symbols to summarize
            
        Returns:
            DividendSummary: Aggregated summary data
        """
        # Calculate totals
        total_all_time = self.storage.calculate_total_dividends_received()
        total_1y = self.storage.calculate_total_dividends_received(
            start_date=datetime.now() - timedelta(days=365)
        )
        total_ytd = self.storage.calculate_total_dividends_received(
            start_date=datetime(datetime.now().year, 1, 1)
        )
        
        # Per-symbol breakdown
        symbol_data = []
        for symbol in symbols:
            total = self.storage.calculate_total_dividends_received(symbol=symbol)
            if total > 0:
                symbol_data.append({
                    'Symbol': symbol,
                    'Total Received': f"${total:,.2f}"
                })
        
        return DividendSummary(
            total_all_time=total_all_time,
            total_1y=total_1y,
            total_ytd=total_ytd,
            symbol_breakdown=symbol_data
        )
    
    # ========================================================================
    # LOGIC LAYER - Pure calculation methods
    # ========================================================================
    
    @staticmethod
    def _calculate_period_start_date(period: str) -> Optional[datetime]:
        """Calculate start date based on period selection.
        
        Parameters:
            period: Period string ('1 Year', '2 Years', etc.)
            
        Returns:
            Optional[datetime]: Start date or None for 'All Time'
        """
        if period == 'All Time':
            return None
        elif period == '1 Year':
            return datetime.now() - timedelta(days=365)
        elif period == '2 Years':
            return datetime.now() - timedelta(days=730)
        elif period == '5 Years':
            return datetime.now() - timedelta(days=1825)
        return None
