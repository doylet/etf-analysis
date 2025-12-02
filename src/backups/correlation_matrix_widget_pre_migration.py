"""
Correlation matrix widget - analyze correlations between holdings and benchmarks
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List
from datetime import datetime, timedelta
from .base_widget import BaseWidget
from src.utils.performance_metrics import calculate_returns


class CorrelationMatrixWidget(BaseWidget):
    """Widget for creating correlation matrix between portfolio holdings and benchmarks"""
    
    # Available benchmarks/instruments to add
    AVAILABLE_INSTRUMENTS = {
        'SPY': 'S&P 500',
        'QQQ': 'Nasdaq 100',
        'DIA': 'Dow Jones',
        'IWM': 'Russell 2000',
        'VTI': 'Total US Market',
        'EFA': 'EAFE (International)',
        'EEM': 'Emerging Markets',
        'AGG': 'US Bonds',
        'TLT': 'Long-Term Treasury',
        'GLD': 'Gold',
        'VNQ': 'Real Estate',
        'BND': 'Total Bond Market',
    }
    
    def get_name(self) -> str:
        return "Correlation Matrix"
    
    def get_description(self) -> str:
        return "Analyze correlations between portfolio holdings, benchmarks, and other instruments"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render correlation matrix"""
        with st.container(border=True):
            if not instruments:
                st.info("No instruments in portfolio")
                return
            
            # Get holdings with quantities > 0
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                st.info("No active positions. Add orders to see correlation analysis.")
                return
            
            # Time period selection
            period = st.selectbox(
                "Time Period:",
                options=['1 Month', '3 Months', '6 Months', '1 Year', '2 Years'],
                index=2,  # Default to 6 months
                key=f"{self.widget_id}_period"
            )
            
            period_days = {
                '1 Month': 30,
                '3 Months': 90,
                '6 Months': 180,
                '1 Year': 365,
                '2 Years': 730
            }
            days = period_days[period]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            st.space("medium")
            
            # Portfolio holdings selection
            selected_holdings = self._render_holdings_selection(holdings)
            
            # Portfolio aggregate in expander
            with st.expander("Portfolio Aggregate", expanded=True):
                include_portfolio = st.checkbox(
                    "Include Portfolio (aggregate of selected holdings)",
                    value=True,
                    key=f"{self.widget_id}_include_portfolio",
                    help="Adds a 'PORTFOLIO' series to the correlation matrix representing the combined performance of all selected holdings weighted by their position sizes"
                )
            
            st.space("medium")
            
            # Additional instruments/benchmarks selection
            selected_additional = self._render_benchmark_selection()
            
            st.space("medium")
            
            # Custom symbol input
            self._render_custom_symbols()
            
            # Show currently selected additional instruments
            if selected_additional:
                st.caption(f"Additional instruments selected: {', '.join(selected_additional)}")
            
            # Combine all selected symbols
            all_symbols = selected_holdings + selected_additional
            
            if len(all_symbols) < 1:
                st.warning("Please select at least 1 instrument to create a correlation matrix.")
                return
            
            # Fetch returns data for all symbols
            returns_data = {}
            missing_data = []
            portfolio_holdings_data = {}
            
            with st.spinner("Calculating correlations..."):
                for symbol in all_symbols:
                    # Check if instrument exists, if not add it as inactive
                    instrument = self.storage.get_instrument(symbol)
                    if not instrument:
                        name = self.AVAILABLE_INSTRUMENTS.get(symbol, symbol)
                        self.storage.add_instrument(
                            symbol=symbol,
                            instrument_type='ETF',
                            name=name,
                            is_active=False
                        )
                    
                    # Get price data
                    price_df = self.storage.get_price_data(symbol, start_date, end_date)
                    
                    if price_df is None or price_df.empty or len(price_df) < 10:
                        missing_data.append(symbol)
                        continue
                    
                    # Calculate returns
                    returns = calculate_returns(price_df['close'])
                    returns_data[symbol] = returns
                    
                    # Track holdings for portfolio calculation
                    if symbol in selected_holdings:
                        portfolio_holdings_data[symbol] = price_df['close']
            
            if missing_data:
                st.warning(f"Missing sufficient data for: {', '.join(missing_data)}")
                
                # Offer to fetch missing data
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption("Click to fetch missing price data")
                with col2:
                    if st.button("Fetch Data", key=f"{self.widget_id}_fetch_missing"):
                        with st.spinner("Fetching data..."):
                            for symbol in missing_data:
                                self.storage.fetch_and_store_prices(symbol)
                        st.success("Data fetched. Refresh to see updated correlation matrix.")
                        st.rerun()
            
            if len(returns_data) < 1:
                st.error("Need at least 1 instrument with valid data to create correlation matrix.")
                return
            
            # Calculate portfolio returns if requested
            if include_portfolio and portfolio_holdings_data:
                # Get holdings for selected symbols
                holdings_list = [h for h in holdings if h['symbol'] in selected_holdings]
                
                if holdings_list:
                    portfolio_values = self._calculate_portfolio_values(holdings_list, start_date, end_date)
                    
                    if not portfolio_values.empty and len(portfolio_values) >= 10:
                        portfolio_returns = calculate_returns(portfolio_values)
                        returns_data['PORTFOLIO'] = portfolio_returns
            
            # Create returns dataframe
            returns_df = pd.DataFrame(returns_data)
            
            # Remove any rows with NaN values
            returns_df = returns_df.dropna()
            
            if returns_df.empty or len(returns_df) < 10:
                st.error("Insufficient overlapping data to calculate correlations.")
                return
            
            if len(returns_df.columns) < 2:
                st.warning("Need at least 2 instruments/portfolio with overlapping data to show correlations.")
                return
            
            # Calculate correlation matrix
            correlation_matrix = returns_df.corr()
            
            # Display correlation matrix as heatmap
            st.subheader("Correlation Matrix")
            st.caption(f"Based on {len(returns_df)} days of returns data from {start_date.date()} to {end_date.date()}")
            
            # Create heatmap using plotly
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                colorscale='RdBu',
                zmid=0,
                zmin=-1,
                zmax=1,
                text=correlation_matrix.values,
                texttemplate='%{text:.2f}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation"),
                hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                xaxis_title="",
                yaxis_title="",
                height=max(400, len(correlation_matrix) * 40),
                width=None,
                margin=dict(l=100, r=50, t=50, b=100),
                xaxis=dict(side='bottom'),
                yaxis=dict(autorange='reversed')
            )
            
            st.plotly_chart(fig, width='stretch')
            
            # Display statistics
            st.markdown("**Correlation Statistics**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Get correlations excluding diagonal
            corr_values = []
            for i in range(len(correlation_matrix)):
                for j in range(i+1, len(correlation_matrix)):
                    corr_values.append(correlation_matrix.iloc[i, j])
            
            if corr_values:
                with col1:
                    # Diversification insight
                    st.markdown("**Diversification Insights**")
            
                    avg_corr = np.mean(corr_values)
                    if avg_corr > 0.7:
                        st.warning("High average correlation - portfolio may lack diversification")
                    elif avg_corr > 0.5:
                        st.info("ℹModerate correlation - reasonable diversification")
                    else:
                        st.success("Low average correlation - well-diversified portfolio")
                with col2:
                    st.metric("Average Correlation", f"{np.mean(corr_values):.2f}")
                with col3:
                    st.metric("Highest Correlation", f"{np.max(corr_values):.2f}")
                with col4:
                    st.metric("Lowest Correlation", f"{np.min(corr_values):.2f}")
            
            # Show most/least correlated pairs
            
            st.markdown("**Key Relationships**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Most Correlated Pairs:**")
                pairs = []
                for i in range(len(correlation_matrix)):
                    for j in range(i+1, len(correlation_matrix)):
                        pairs.append({
                            'Pair': f"{correlation_matrix.index[i]} - {correlation_matrix.columns[j]}",
                            'Correlation': correlation_matrix.iloc[i, j]
                        })
                pairs_df = pd.DataFrame(pairs).sort_values('Correlation', ascending=False)
                st.dataframe(pairs_df.head(5), hide_index=True, width='stretch')
            
            with col2:
                st.markdown("**Least Correlated Pairs:**")
                st.dataframe(pairs_df.tail(5), hide_index=True, width='stretch')

            # Portfolio holdings correlation with benchmarks
            if selected_holdings and selected_additional:
                
                st.markdown("**Portfolio vs Benchmarks**")
                
                benchmark_corr = []
                for holding in selected_holdings:
                    if holding in returns_df.columns:
                        for benchmark in selected_additional:
                            if benchmark in returns_df.columns:
                                benchmark_corr.append({
                                    'Holding': holding,
                                    'Benchmark': benchmark,
                                    'Correlation': correlation_matrix.loc[holding, benchmark]
                                })
                
                if benchmark_corr:
                    benchmark_df = pd.DataFrame(benchmark_corr)
                    
                    # Pivot for better display
                    pivot_df = benchmark_df.pivot(index='Holding', columns='Benchmark', values='Correlation')
                    
                    formatted_pivot = pivot_df.style.format("{:.2f}")
                    
                    st.dataframe(formatted_pivot, width='stretch')
    
    def _render_holdings_selection(self, holdings: List[Dict]) -> List[str]:
        """Render portfolio holdings selection UI and return selected symbols.
        
        Parameters:
            holdings: List of portfolio holdings dictionaries with 'symbol' keys
            
        Returns:
            List[str]: Selected holding symbols
            
        Session State:
            Accesses/modifies: {widget_id}_selected_holdings
        """
        # Initialize selected holdings in session state
        if f"{self.widget_id}_selected_holdings" not in st.session_state:
            st.session_state[f"{self.widget_id}_selected_holdings"] = [h['symbol'] for h in holdings]
        
        # Calculate selection count for title
        selected_count = len(st.session_state[f"{self.widget_id}_selected_holdings"])
        total_count = len(holdings)
        
        with st.expander(f"Portfolio Holdings ({selected_count}/{total_count} selected)", expanded=True):
            # Bulk selection buttons
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("Select All", key=f"{self.widget_id}_select_all_holdings"):
                    st.session_state[f"{self.widget_id}_selected_holdings"] = [h['symbol'] for h in holdings]
                    st.rerun()
            with col2:
                if st.button("Deselect All", key=f"{self.widget_id}_deselect_all_holdings"):
                    st.session_state[f"{self.widget_id}_selected_holdings"] = []
                    st.rerun()
            
            num_cols = 4
            cols = st.columns(num_cols)
            
            selected_holdings = []
            for idx, holding in enumerate(holdings):
                col_idx = idx % num_cols
                with cols[col_idx]:
                    is_selected = st.checkbox(
                        f"{holding['symbol']}",
                        value=holding['symbol'] in st.session_state[f"{self.widget_id}_selected_holdings"],
                        key=f"{self.widget_id}_holding_{holding['symbol']}"
                    )
                    if is_selected:
                        selected_holdings.append(holding['symbol'])
            
            st.session_state[f"{self.widget_id}_selected_holdings"] = selected_holdings
        return selected_holdings
    
    def _render_benchmark_selection(self) -> List[str]:
        """Render benchmark instruments selection UI and return selected symbols.
        
        Returns:
            List[str]: Selected benchmark symbols (including custom symbols)
            
        Session State:
            Accesses/modifies: {widget_id}_selected_additional
        """
        # Initialize selected additional instruments
        if f"{self.widget_id}_selected_additional" not in st.session_state:
            st.session_state[f"{self.widget_id}_selected_additional"] = ['SPY']
        
        # Get the current list from session state
        current_additional = st.session_state[f"{self.widget_id}_selected_additional"]
        
        # Calculate how many benchmarks are selected (excluding custom symbols)
        benchmark_selected = [s for s in current_additional if s in self.AVAILABLE_INSTRUMENTS]
        selected_count = len(benchmark_selected)
        total_count = len(self.AVAILABLE_INSTRUMENTS)
        
        with st.expander(f"Benchmark Instruments ({selected_count}/{total_count} selected)", expanded=False):
            # Bulk selection buttons
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("Select All", key=f"{self.widget_id}_select_all_benchmarks"):
                    # Get custom symbols first
                    custom_symbols = [s for s in current_additional if s not in self.AVAILABLE_INSTRUMENTS]
                    # Add all benchmarks
                    all_selected = list(self.AVAILABLE_INSTRUMENTS.keys()) + custom_symbols
                    st.session_state[f"{self.widget_id}_selected_additional"] = all_selected
                    st.rerun()
            with col2:
                if st.button("Deselect All", key=f"{self.widget_id}_deselect_all_benchmarks"):
                    # Keep only custom symbols
                    custom_symbols = [s for s in current_additional if s not in self.AVAILABLE_INSTRUMENTS]
                    st.session_state[f"{self.widget_id}_selected_additional"] = custom_symbols
                    st.rerun()
            
            # Show available instruments
            num_cols = 4
            cols = st.columns(num_cols)
            selected_additional = []
            
            for idx, (symbol, name) in enumerate(self.AVAILABLE_INSTRUMENTS.items()):
                col_idx = idx % num_cols
                with cols[col_idx]:
                    is_selected = st.checkbox(
                        f"{symbol} - {name}",
                        value=symbol in current_additional,
                        key=f"{self.widget_id}_additional_{symbol}"
                    )
                    if is_selected:
                        selected_additional.append(symbol)

            # Add any custom symbols that were added
            custom_symbols = [s for s in current_additional if s not in self.AVAILABLE_INSTRUMENTS]
            for custom in custom_symbols:
                selected_additional.append(custom)
            
            # Update session state
            st.session_state[f"{self.widget_id}_selected_additional"] = selected_additional
        return selected_additional
    
    def _render_custom_symbols(self):
        """Render custom symbol input UI with remove functionality.
        
        Session State:
            Accesses: {widget_id}_custom_symbol, {widget_id}_selected_additional
            Modifies: {widget_id}_selected_additional
            
        Side Effects:
            Calls st.rerun() when a symbol is successfully added or removed
        """
        # Get custom symbols from session state
        if f"{self.widget_id}_selected_additional" in st.session_state:
            current_additional = st.session_state[f"{self.widget_id}_selected_additional"]
            custom_symbols = [s for s in current_additional if s not in self.AVAILABLE_INSTRUMENTS]
        else:
            custom_symbols = []
        
        custom_count = len(custom_symbols)
        
        with st.expander(f"Custom Symbols ({custom_count})", expanded=True):
            # Display existing custom symbols with remove buttons
            if custom_symbols:
                st.caption("Current custom symbols:")
                for symbol in custom_symbols:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.text(symbol)
                    with col2:
                        if st.button("×", key=f"{self.widget_id}_remove_{symbol}", help=f"Remove {symbol}"):
                            # Remove symbol from session state
                            current_list = st.session_state[f"{self.widget_id}_selected_additional"]
                            current_list.remove(symbol)
                            st.session_state[f"{self.widget_id}_selected_additional"] = current_list
                            st.rerun()
            else:
                st.caption("No custom symbols added yet")
            
            st.markdown("**Add custom symbol:**")
            col1, col2 = st.columns([3, 1])
            with col1:
                custom_symbol = st.text_input(
                    "Enter symbol:",
                    key=f"{self.widget_id}_custom_symbol",
                    placeholder="e.g., AAPL, MSFT, VEU.AX"
                )
            with col2:
                st.markdown("&nbsp;")  # Spacer for alignment
                if st.button("Add", key=f"{self.widget_id}_add_custom"):
                    # Get the symbol from the text input via session state
                    symbol_to_add = st.session_state.get(f"{self.widget_id}_custom_symbol", "").upper().strip()
                    
                    # Validation: non-empty
                    if not symbol_to_add:
                        st.warning("Please enter a symbol")
                        return
                    
                    # Validation: length 1-10 characters
                    if len(symbol_to_add) < 1 or len(symbol_to_add) > 10:
                        st.error("Symbol must be between 1 and 10 characters")
                        return
                    
                    # Validation: alphanumeric + dots/dashes only
                    import re
                    if not re.match(r'^[A-Z0-9.\-]+$', symbol_to_add):
                        st.error("Symbol must contain only uppercase letters, numbers, dots, and dashes")
                        return
                    
                    # Check if already exists
                    current_list = st.session_state[f"{self.widget_id}_selected_additional"]
                    if symbol_to_add in current_list:
                        st.warning(f"{symbol_to_add} is already selected")
                        return
                    
                    # Add symbol
                    current_list.append(symbol_to_add)
                    st.session_state[f"{self.widget_id}_selected_additional"] = current_list
                    st.success(f"Added {symbol_to_add}")
                    st.rerun()
    
    def _calculate_portfolio_values(self, holdings: List[Dict], 
                                    start_date: datetime, end_date: datetime) -> pd.Series:
        """Calculate portfolio value over time"""
        portfolio_df = None
        
        for holding in holdings:
            symbol = holding['symbol']
            quantity = holding.get('quantity', 0)
            
            if quantity <= 0:
                continue
            
            price_df = self.storage.get_price_data(symbol, start_date, end_date)
            
            if price_df is None or price_df.empty:
                continue
            
            # Calculate position value
            position_values = price_df['close'] * quantity
            
            if portfolio_df is None:
                portfolio_df = pd.DataFrame(position_values, columns=[symbol])
            else:
                portfolio_df[symbol] = position_values
        
        if portfolio_df is None or portfolio_df.empty:
            return pd.Series()
        
        # Sum across all positions
        return portfolio_df.sum(axis=1)
