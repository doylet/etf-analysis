"""
Correlation matrix widget - analyze correlations between holdings and benchmarks.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Data fetching and validation (_fetch_*, _prepare_* methods)  
- Logic Layer: Pure calculations (_calculate_*, _analyze_* static methods)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .layered_base_widget import LayeredBaseWidget
from .ui_helpers import (
    render_bulk_selection_buttons,
    render_removable_list,
    render_add_item_input,
    render_holdings_selection_grid
)
from src.utils.performance_metrics import calculate_returns
from src.utils.symbol_validation import validate_symbol, format_symbol


@dataclass
class CorrelationAnalysis:
    """Results from correlation analysis calculations."""
    correlation_matrix: pd.DataFrame
    pairs_df: pd.DataFrame
    benchmark_pivot: Optional[pd.DataFrame]
    avg_correlation: float
    max_correlation: float
    min_correlation: float
    num_days: int
    start_date: datetime
    end_date: datetime


class CorrelationMatrixWidget(LayeredBaseWidget):
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
    
    PERIOD_DAYS_MAP = {
        '1 Month': 30,
        '3 Months': 90,
        '6 Months': 180,
        '1 Year': 365,
        '2 Years': 730
    }
    
    def get_name(self) -> str:
        return "Correlation Matrix"
    
    def get_description(self) -> str:
        return "Analyze correlations between portfolio holdings, benchmarks, and other instruments"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    # =========================================================================
    # MAIN RENDER - UI ORCHESTRATION ONLY
    # =========================================================================
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """
        Render correlation matrix widget.
        
        Orchestrates three layers:
        1. UI: Get user selections
        2. Data: Fetch and prepare data
        3. Logic: Calculate correlations
        4. UI: Display results
        """
        with st.container(border=True):
            # Validate basic inputs
            if not instruments:
                st.info("No instruments in portfolio")
                return
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                st.info("No active positions. Add orders to see correlation analysis.")
                return
            
            # UI LAYER: Get user selections
            period_days, start_date, end_date = self._render_period_selector()
            # st.space("medium")
            
            selected_holdings = self._render_holdings_selection(holdings)
            include_portfolio = self._render_portfolio_aggregate_option()
            # st.space("medium")
            
            selected_additional = self._render_benchmark_selection()
            # st.space("medium")
            
            self._render_custom_symbols()
            
            # Combine selections
            all_symbols = selected_holdings + selected_additional
            if len(all_symbols) < 1:
                st.warning("Please select at least 1 instrument to create a correlation matrix.")
                return
            
            # Show selection summary
            if selected_additional:
                st.caption(f"Additional instruments selected: {', '.join(selected_additional)}")
            
            # DATA LAYER: Fetch and prepare data
            returns_result = self._fetch_returns_data(
                all_symbols, selected_holdings, start_date, end_date, 
                include_portfolio, holdings
            )
            
            if returns_result['status'] == 'error':
                self._handle_data_error(returns_result['message'])
                return
            
            if returns_result.get('missing_data'):
                self._render_fetch_missing_data_button(returns_result['missing_data'])
            
            returns_df = returns_result['returns_df']
            
            # Validate sufficient data
            if len(returns_df.columns) < 2:
                st.warning("Need at least 2 instruments/portfolio with overlapping data to show correlations.")
                return
            
            # LOGIC LAYER: Calculate correlation analysis
            analysis = self._calculate_correlation_analysis(
                returns_df, selected_holdings, selected_additional, start_date, end_date
            )
            
            # UI LAYER: Display results
            self._render_analysis_results(analysis)
    
    # =========================================================================
    # UI LAYER - CONTROLS AND INPUTS
    # =========================================================================
    
    def _render_period_selector(self) -> Tuple[int, datetime, datetime]:
        """
        Render time period selection control.
        
        Returns:
            Tuple of (days, start_date, end_date)
        """
        period = st.selectbox(
            "Time Period:",
            options=list(self.PERIOD_DAYS_MAP.keys()),
            index=2,  # Default to 6 months
            key=self._get_session_key("period")
        )
        
        days = self.PERIOD_DAYS_MAP[period]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return days, start_date, end_date
    
    def _render_holdings_selection(self, holdings: List[Dict]) -> List[str]:
        """
        Render portfolio holdings selection UI.
        
        Parameters:
            holdings: List of portfolio holdings dictionaries
            
        Returns:
            List of selected holding symbols
        """
        # Initialize session state
        key = self._get_session_key("selected_holdings")
        if key not in st.session_state:
            st.session_state[key] = [h['symbol'] for h in holdings]
        
        selected_count = len(st.session_state[key])
        total_count = len(holdings)
        
        with st.expander(f"Portfolio Holdings ({selected_count}/{total_count} selected)", expanded=True):
            # Bulk selection buttons
            render_bulk_selection_buttons(
                select_all_key=self._get_session_key("select_all_holdings"),
                deselect_all_key=self._get_session_key("deselect_all_holdings"),
                on_select_all=lambda: st.session_state.update({key: [h['symbol'] for h in holdings]}),
                on_deselect_all=lambda: st.session_state.update({key: []})
            )
            
            # Checkbox grid using helper
            selected_holdings = render_holdings_selection_grid(
                holdings=holdings,
                session_key=key,
                checkbox_key_prefix=self._get_session_key("holding"),
                num_columns=6
            )
        
        return selected_holdings
    
    def _render_portfolio_aggregate_option(self) -> bool:
        """
        Render portfolio aggregate checkbox.
        
        Returns:
            True if portfolio should be included
        """
        with st.expander("Portfolio Aggregate", expanded=True):
            return st.checkbox(
                "Include Portfolio (aggregate of selected holdings)",
                value=True,
                key=self._get_session_key("include_portfolio"),
                help="Adds a 'PORTFOLIO' series representing combined performance weighted by position sizes"
            )
    
    def _render_benchmark_selection(self) -> List[str]:
        """
        Render benchmark instruments selection UI.
        
        Returns:
            List of selected benchmark symbols (including custom)
        """
        key = self._get_session_key("selected_additional")
        self._init_session_state(key, ['SPY'])
        current_additional = st.session_state[key]
        
        # Calculate benchmark count (excluding custom symbols)
        benchmark_selected = [s for s in current_additional if s in self.AVAILABLE_INSTRUMENTS]
        selected_count = len(benchmark_selected)
        total_count = len(self.AVAILABLE_INSTRUMENTS)
        
        with st.expander(f"Benchmark Instruments ({selected_count}/{total_count} selected)", expanded=False):
            # Bulk selection buttons
            def select_all():
                custom_symbols = [s for s in current_additional if s not in self.AVAILABLE_INSTRUMENTS]
                st.session_state[key] = list(self.AVAILABLE_INSTRUMENTS.keys()) + custom_symbols
            
            def deselect_all():
                custom_symbols = [s for s in current_additional if s not in self.AVAILABLE_INSTRUMENTS]
                st.session_state[key] = custom_symbols
            
            render_bulk_selection_buttons(
                select_all_key=self._get_session_key("select_all_benchmarks"),
                deselect_all_key=self._get_session_key("deselect_all_benchmarks"),
                on_select_all=select_all,
                on_deselect_all=deselect_all
            )
            
            # Checkbox grid
            num_cols = 4
            cols = st.columns(num_cols)
            selected_additional = []
            
            for idx, (symbol, name) in enumerate(self.AVAILABLE_INSTRUMENTS.items()):
                col_idx = idx % num_cols
                with cols[col_idx]:
                    is_selected = st.checkbox(
                        f"{symbol} - {name}",
                        value=symbol in current_additional,
                        key=self._get_session_key(f"additional_{symbol}")
                    )
                    if is_selected:
                        selected_additional.append(symbol)
            
            # Add custom symbols
            custom_symbols = [s for s in current_additional if s not in self.AVAILABLE_INSTRUMENTS]
            selected_additional.extend(custom_symbols)
            
            st.session_state[key] = selected_additional
        
        return selected_additional
    
    def _render_custom_symbols(self):
        """Render custom symbol input UI with add/remove functionality."""
        key = self._get_session_key("selected_additional")
        current_additional = st.session_state.get(key, [])
        custom_symbols = [s for s in current_additional if s not in self.AVAILABLE_INSTRUMENTS]
        
        with st.expander(f"Custom Symbols ({len(custom_symbols)})", expanded=True):
            # Display existing custom symbols with remove buttons
            def remove_symbol(symbol):
                current_additional.remove(symbol)
                st.session_state[key] = current_additional
            
            render_removable_list(
                items=custom_symbols,
                key_prefix=self._get_session_key("custom"),
                on_remove=remove_symbol,
                empty_message="No custom symbols added yet",
                title="Current custom symbols:"
            )
            
            # Add new symbol input
            st.markdown("**Add custom symbol:**")
            render_add_item_input(
                label="Enter symbol:",
                button_label="Add",
                input_key=self._get_session_key("custom_symbol"),
                button_key=self._get_session_key("add_custom"),
                on_add=lambda _: self._handle_add_custom_symbol(),
                placeholder="e.g., AAPL, MSFT, VEU.AX"
            )
    
    def _handle_add_custom_symbol(self):
        """Handle custom symbol addition with validation."""
        symbol_input = format_symbol(st.session_state.get(self._get_session_key("custom_symbol"), ""))
        
        # Validate
        validation_result = validate_symbol(symbol_input, st.session_state.get(self._get_session_key("selected_additional"), []))
        
        if not validation_result['valid']:
            if validation_result['error_type'] == 'warning':
                st.warning(validation_result['message'])
            else:
                st.error(validation_result['message'])
            return
        
        # Add symbol
        key = self._get_session_key("selected_additional")
        current_list = st.session_state.get(key, [])
        current_list.append(symbol_input)
        st.session_state[key] = current_list
        st.success(f"Added {symbol_input}")
        st.rerun()
    
    def _render_fetch_missing_data_button(self, missing_symbols: List[str]):
        """Render button to fetch missing price data."""
        st.warning(f"Missing sufficient data for: {', '.join(missing_symbols)}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption("Click to fetch missing price data")
        with col2:
            if st.button("Fetch Data", key=self._get_session_key("fetch_missing")):
                with st.spinner("Fetching data..."):
                    for symbol in missing_symbols:
                        self.storage.fetch_and_store_prices(symbol)
                st.success("Data fetched. Refresh to see updated correlation matrix.")
                st.rerun()
    
    # =========================================================================
    # UI LAYER - RESULTS DISPLAY
    # =========================================================================
    
    def _render_analysis_results(self, analysis: CorrelationAnalysis):
        """
        Render correlation analysis results.
        
        Parameters:
            analysis: CorrelationAnalysis dataclass with results
        """
        # Header
        st.subheader("Correlation Matrix")
        st.caption(
            f"Based on {analysis.num_days} days of returns data "
            f"from {analysis.start_date.date()} to {analysis.end_date.date()}"
        )
        
        # Heatmap
        self._render_correlation_heatmap(analysis.correlation_matrix)
        
        # Statistics
        self._render_correlation_statistics(analysis)
        
        # Key pairs
        self._render_key_pairs(analysis.pairs_df)
        
        # Portfolio vs benchmarks
        if analysis.benchmark_pivot is not None:
            self._render_portfolio_benchmark_comparison(analysis.benchmark_pivot)
    
    def _render_correlation_heatmap(self, correlation_matrix: pd.DataFrame):
        """Render correlation matrix as Plotly heatmap."""
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
    
    def _render_correlation_statistics(self, analysis: CorrelationAnalysis):
        """Render correlation statistics metrics."""
        st.markdown("**Correlation Statistics**")
        
        col1, col2, col3, col4 = st.columns(4, vertical_alignment="center", gap="medium", border=True, )
        
        with col1:
            if analysis.avg_correlation > 0.7:
                st.warning("High average correlation - portfolio may lack diversification")
            elif analysis.avg_correlation > 0.5:
                st.info("Moderate correlation - reasonable diversification")
            else:
                st.success("Low average correlation - well-diversified portfolio")
        
        with col2:
            st.metric("Highest Correlation", f"{analysis.max_correlation:.2f}")
        with col3:
            st.metric("Average Correlation", f"{analysis.avg_correlation:.2f}")
        with col4:
            st.metric("Lowest Correlation", f"{analysis.min_correlation:.2f}")
    
    def _render_key_pairs(self, pairs_df: pd.DataFrame):
        """Render most and least correlated pairs."""
        st.markdown("**Key Relationships**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Most Correlated Pairs:**")
            st.dataframe(pairs_df.head(5), hide_index=True, width='stretch')
        
        with col2:
            st.markdown("**Least Correlated Pairs:**")
            st.dataframe(pairs_df.tail(5), hide_index=True, width='stretch')
    
    def _render_portfolio_benchmark_comparison(self, pivot_df: pd.DataFrame):
        """Render portfolio vs benchmarks comparison table."""
        st.markdown("**Portfolio vs Benchmarks**")
        formatted_pivot = pivot_df.style.format("{:.2f}")
        st.dataframe(formatted_pivot, width='stretch')
    
    # =========================================================================
    # DATA LAYER - FETCH AND PREPARE
    # =========================================================================
    
    def _fetch_returns_data(
        self, 
        all_symbols: List[str],
        selected_holdings: List[str],
        start_date: datetime,
        end_date: datetime,
        include_portfolio: bool,
        holdings: List[Dict]
    ) -> Dict:
        """
        Fetch and prepare returns data for all symbols.
        
        Parameters:
            all_symbols: All symbols to fetch (holdings + benchmarks + custom)
            selected_holdings: Selected holding symbols
            start_date: Start date for data fetch
            end_date: End date for data fetch
            include_portfolio: Whether to calculate portfolio aggregate
            holdings: Full holdings list with quantities
            
        Returns:
            Dict with status, returns_df, and optional missing_data list
        """
        returns_data = {}
        missing_data = []
        
        with st.spinner("Calculating correlations..."):
            # Fetch individual symbol returns
            for symbol in all_symbols:
                # Ensure instrument exists in database
                self._ensure_instrument_exists(symbol)
                
                # Get price data
                price_df = self.storage.get_price_data(symbol, start_date, end_date)
                
                if price_df is None or price_df.empty or len(price_df) < 10:
                    missing_data.append(symbol)
                    continue
                
                # Calculate returns
                returns = calculate_returns(price_df['close'])
                returns_data[symbol] = returns
            
            # Calculate portfolio returns if requested
            if include_portfolio and selected_holdings:
                portfolio_returns = self._calculate_portfolio_returns(
                    selected_holdings, holdings, start_date, end_date
                )
                if portfolio_returns is not None and len(portfolio_returns) >= 10:
                    returns_data['PORTFOLIO'] = portfolio_returns
        
        # Create DataFrame and clean
        if len(returns_data) < 1:
            return {'status': 'error', 'message': 'Need at least 1 instrument with valid data'}
        
        returns_df = pd.DataFrame(returns_data).dropna()
        
        if returns_df.empty or len(returns_df) < 10:
            return {'status': 'error', 'message': 'Insufficient overlapping data to calculate correlations'}
        
        return {
            'status': 'success',
            'returns_df': returns_df,
            'missing_data': missing_data if missing_data else None
        }
    
    def _ensure_instrument_exists(self, symbol: str):
        """Ensure instrument exists in database, create if missing."""
        instrument = self.storage.get_instrument(symbol)
        if not instrument:
            name = self.AVAILABLE_INSTRUMENTS.get(symbol, symbol)
            self.storage.add_instrument(
                symbol=symbol,
                instrument_type='ETF',
                name=name,
                is_active=False
            )
    
    def _calculate_portfolio_returns(
        self,
        selected_holdings: List[str],
        holdings: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.Series]:
        """
        Calculate portfolio aggregate returns.
        
        Parameters:
            selected_holdings: Selected holding symbols
            holdings: Full holdings list with quantities
            start_date: Start date
            end_date: End date
            
        Returns:
            Portfolio returns series or None if insufficient data
        """
        holdings_list = [h for h in holdings if h['symbol'] in selected_holdings]
        if not holdings_list:
            return None
        
        portfolio_values = self._calculate_portfolio_values(holdings_list, start_date, end_date)
        if portfolio_values.empty or len(portfolio_values) < 10:
            return None
        
        return calculate_returns(portfolio_values)
    
    def _calculate_portfolio_values(
        self, 
        holdings: List[Dict], 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.Series:
        """
        Calculate portfolio value time series.
        
        Parameters:
            holdings: Holdings with symbols and quantities
            start_date: Start date
            end_date: End date
            
        Returns:
            Portfolio value series (sum of all positions)
        """
        portfolio_df = None
        
        for holding in holdings:
            symbol = holding['symbol']
            quantity = holding.get('quantity', 0)
            
            if quantity <= 0:
                continue
            
            price_df = self.storage.get_price_data(symbol, start_date, end_date)
            if price_df is None or price_df.empty:
                continue
            
            position_values = price_df['close'] * quantity
            
            if portfolio_df is None:
                portfolio_df = pd.DataFrame(position_values, columns=[symbol])
            else:
                portfolio_df[symbol] = position_values
        
        if portfolio_df is None or portfolio_df.empty:
            return pd.Series()
        
        return portfolio_df.sum(axis=1)
    
    # =========================================================================
    # LOGIC LAYER - PURE CALCULATIONS
    # =========================================================================
    
    @staticmethod
    def _calculate_correlation_analysis(
        returns_df: pd.DataFrame,
        selected_holdings: List[str],
        selected_additional: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> CorrelationAnalysis:
        """
        Calculate complete correlation analysis.
        
        Parameters:
            returns_df: DataFrame of returns for all symbols
            selected_holdings: Holdings symbols
            selected_additional: Benchmark symbols
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            CorrelationAnalysis dataclass with all results
        """
        # Calculate correlation matrix
        correlation_matrix = returns_df.corr()
        
        # Calculate correlation statistics
        corr_values = []
        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                corr_values.append(correlation_matrix.iloc[i, j])
        
        avg_corr = float(np.mean(corr_values)) if corr_values else 0.0
        max_corr = float(np.max(corr_values)) if corr_values else 0.0
        min_corr = float(np.min(corr_values)) if corr_values else 0.0
        
        # Calculate pairs
        pairs_df = CorrelationMatrixWidget._calculate_correlation_pairs(correlation_matrix)
        
        # Calculate benchmark comparison if applicable
        benchmark_pivot = None
        if selected_holdings and selected_additional:
            benchmark_pivot = CorrelationMatrixWidget._calculate_benchmark_comparison(
                correlation_matrix, selected_holdings, selected_additional, returns_df.columns
            )
        
        return CorrelationAnalysis(
            correlation_matrix=correlation_matrix,
            pairs_df=pairs_df,
            benchmark_pivot=benchmark_pivot,
            avg_correlation=avg_corr,
            max_correlation=max_corr,
            min_correlation=min_corr,
            num_days=len(returns_df),
            start_date=start_date,
            end_date=end_date
        )
    
    @staticmethod
    def _calculate_correlation_pairs(correlation_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and sort correlation pairs.
        
        Parameters:
            correlation_matrix: Correlation matrix DataFrame
            
        Returns:
            DataFrame with Pair and Correlation columns, sorted by correlation
        """
        pairs = []
        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                pairs.append({
                    'Pair': f"{correlation_matrix.index[i]} - {correlation_matrix.columns[j]}",
                    'Correlation': correlation_matrix.iloc[i, j]
                })
        
        return pd.DataFrame(pairs).sort_values('Correlation', ascending=False)
    
    @staticmethod
    def _calculate_benchmark_comparison(
        correlation_matrix: pd.DataFrame,
        holdings: List[str],
        benchmarks: List[str],
        available_columns: pd.Index
    ) -> Optional[pd.DataFrame]:
        """
        Calculate portfolio holdings vs benchmarks correlation table.
        
        Parameters:
            correlation_matrix: Correlation matrix
            holdings: Holding symbols
            benchmarks: Benchmark symbols
            available_columns: Available columns in correlation matrix
            
        Returns:
            Pivoted DataFrame or None if no data
        """
        benchmark_corr = []
        
        for holding in holdings:
            if holding not in available_columns:
                continue
            for benchmark in benchmarks:
                if benchmark not in available_columns:
                    continue
                benchmark_corr.append({
                    'Holding': holding,
                    'Benchmark': benchmark,
                    'Correlation': correlation_matrix.loc[holding, benchmark]
                })
        
        if not benchmark_corr:
            return None
        
        benchmark_df = pd.DataFrame(benchmark_corr)
        return benchmark_df.pivot(index='Holding', columns='Benchmark', values='Correlation')
