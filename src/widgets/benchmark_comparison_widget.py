"""
Benchmark comparison widget - compares portfolio against market benchmarks.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Data fetching and validation (_fetch_*, _prepare_* methods)
- Logic Layer: Pure calculations (_calculate_* static methods)
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .layered_base_widget import LayeredBaseWidget
from .ui_helpers import render_holdings_selection_grid
from src.utils.performance_metrics import (
    calculate_returns,
    calculate_beta,
    calculate_alpha,
    calculate_information_ratio,
    calculate_sharpe_ratio
)


@dataclass
class BenchmarkMetrics:
    """Comparison metrics between portfolio and benchmark."""
    beta: float
    alpha: float
    info_ratio: float
    portfolio_sharpe: float
    benchmark_sharpe: float
    portfolio_total_return: float
    benchmark_total_return: float
    portfolio_vol: float
    benchmark_vol: float


class BenchmarkComparisonWidget(LayeredBaseWidget):
    """Widget comparing portfolio performance against market benchmarks"""
    
    # Common benchmark symbols
    BENCHMARKS = {
        'SPY': 'S&P 500',
        'QQQ': 'Nasdaq 100',
        'DIA': 'Dow Jones',
        'IWM': 'Russell 2000',
        'VTI': 'Total US Market',
        'EFA': 'EAFE (International)',
        'AGG': 'US Bonds',
        "GLD": 'Gold'
    }
    
    def get_name(self) -> str:
        return "Benchmark Comparison"
    
    def get_description(self) -> str:
        return "Compare portfolio performance against market benchmarks (Beta, Alpha, Information Ratio)"
    
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
            
            # Get holdings with quantities > 0
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                st.info("No active positions. Add orders to see benchmark comparison.")
                return
            
            # Select instruments to compare
            selected_holdings = self._render_instrument_selection(holdings)
            
            if not selected_holdings:
                st.info("Please select at least one instrument to compare.")
                return
            
            st.space("small")
            
            # Get benchmark and period selections
            benchmark_symbol, days = self._render_benchmark_and_period_selectors()
            
            # Calculate and display comparison
            self._render_benchmark_comparison(selected_holdings, benchmark_symbol, days)
    
    def _render_instrument_selection(self, holdings: List[Dict]) -> List[Dict]:
        """Render instrument selection checkboxes.
        
        Parameters:
            holdings: List of holding dictionaries
            
        Returns:
            List[Dict]: Selected holdings
        """
        st.write("**Select instruments to include in comparison:**")
        
        # Initialize selected instruments in session state
        session_key = self._get_session_key("selected_instruments")
        self._init_session_state(session_key, [h['symbol'] for h in holdings])
        
        # Render checkbox grid using helper
        selected_symbols = render_holdings_selection_grid(
            holdings=holdings,
            session_key=session_key,
            checkbox_key_prefix=self._get_session_key("instrument"),
            num_columns=3,
            label_formatter=lambda h: f"{h['symbol']} ({h.get('name', '')})"
        )
        
        # Filter holdings to selected instruments
        return [h for h in holdings if h['symbol'] in selected_symbols]
    
    def _render_benchmark_and_period_selectors(self) -> Tuple[str, int]:
        """Render benchmark and period selectors.
        
        Returns:
            Tuple[str, int]: (benchmark_symbol, period_days)
        """
        # Select benchmark
        benchmark_symbol = st.selectbox(
            "Select Benchmark:",
            options=list(self.BENCHMARKS.keys()),
            format_func=lambda x: f"{x} - {self.BENCHMARKS[x]}",
            key=self._get_session_key("benchmark")
        )
        
        # Time period
        period = st.selectbox(
            "Time Period:",
            options=['1 Month', '3 Months', '6 Months', '1 Year'],
            key=self._get_session_key("period")
        )
        
        period_days = {
            '1 Month': 30,
            '3 Months': 90,
            '6 Months': 180,
            '1 Year': 365
        }
        days = period_days[period]
        
        return benchmark_symbol, days
    
    def _render_benchmark_comparison(self, selected_holdings: List[Dict], 
                                     benchmark_symbol: str, days: int):
        """Render the benchmark comparison analysis.
        
        Parameters:
            selected_holdings: List of selected holding dictionaries
            benchmark_symbol: Benchmark ticker symbol
            days: Number of days for analysis period
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Calculate portfolio returns
        portfolio_values = self._fetch_portfolio_values(selected_holdings, start_date, end_date)
        
        if portfolio_values.empty:
            st.warning("No price data available for selected period")
            return
        
        portfolio_returns = calculate_returns(portfolio_values)
        
        # Get benchmark data
        benchmark_df = self._fetch_benchmark_data(benchmark_symbol, start_date, end_date)
        
        if benchmark_df is None:
            return  # Error already displayed by fetch method
        
        benchmark_returns = calculate_returns(benchmark_df['close'])
        
        # Calculate metrics
        metrics = self._calculate_benchmark_metrics(
            portfolio_returns, benchmark_returns, 
            portfolio_values, benchmark_df['close']
        )
        
        # Display results
        self._render_metrics_display(metrics, benchmark_symbol)
        self._render_performance_chart(portfolio_returns, benchmark_returns)
    
    def _render_metrics_display(self, metrics: BenchmarkMetrics, benchmark_symbol: str):
        """Display benchmark comparison metrics.
        
        Parameters:
            metrics: Calculated benchmark metrics
            benchmark_symbol: Benchmark ticker symbol
        """
        st.markdown("**Benchmark Comparison Metrics**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Beta", f"{metrics.beta:.2f}", help="Sensitivity to benchmark movements")
        
        with col2:
            st.metric("Alpha (Annual)", f"{metrics.alpha*100:.2f}", help="Excess return vs benchmark")
        
        with col3:
            st.metric("Information Ratio", f"{metrics.info_ratio:.2f}", help="Excess return per unit tracking error")
        
        st.space("small")
        
        # Comparison metrics
        st.markdown("**Performance Comparison**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Portfolio**")
            st.metric("Total Return", f"{metrics.portfolio_total_return:.1f}%")
            st.metric("Sharpe Ratio", f"{metrics.portfolio_sharpe:.2f}")
            st.metric("Volatility (Annual)", f"{metrics.portfolio_vol:.1f}%")
        
        with col2:
            st.markdown(f"**{self.BENCHMARKS[benchmark_symbol]}**")
            st.metric("Total Return", f"{metrics.benchmark_total_return:.1f}%")
            st.metric("Sharpe Ratio", f"{metrics.benchmark_sharpe:.2f}")
            st.metric("Volatility (Annual)", f"{metrics.benchmark_vol:.1f}%")
        
        st.space("small")
    
    def _render_performance_chart(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series):
        """Render cumulative returns comparison chart.
        
        Parameters:
            portfolio_returns: Portfolio returns series
            benchmark_returns: Benchmark returns series
        """
        st.markdown("**Cumulative Returns**")
        
        # Calculate cumulative returns
        portfolio_cumret = (1 + portfolio_returns).cumprod() - 1
        benchmark_cumret = (1 + benchmark_returns).cumprod() - 1
        
        comparison_df = pd.DataFrame({
            'Portfolio': portfolio_cumret * 100,
            'Benchmark': benchmark_cumret * 100
        })
        
        st.line_chart(comparison_df)
    
    # ========================================================================
    # DATA LAYER - Data fetching and validation methods
    # ========================================================================
    
    def _fetch_portfolio_values(self, holdings: List[Dict], 
                                start_date: datetime, end_date: datetime) -> pd.Series:
        """Fetch price data and calculate portfolio values over time.
        
        Parameters:
            holdings: List of holding dictionaries
            start_date: Start date for fetching data
            end_date: End date for fetching data
            
        Returns:
            pd.Series: Portfolio values over time
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
    
    def _fetch_benchmark_data(self, benchmark_symbol: str, 
                              start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch benchmark price data with offer to fetch if missing.
        
        Parameters:
            benchmark_symbol: Benchmark ticker symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            pd.DataFrame: Benchmark price data, or None if unavailable
        """
        benchmark_df = self.storage.get_price_data(benchmark_symbol, start_date, end_date)
        
        if benchmark_df is None or benchmark_df.empty:
            st.warning(f"No benchmark data available for {benchmark_symbol}")
            
            # Offer to fetch benchmark data
            if st.button(f"Fetch {benchmark_symbol} data", key=self._get_session_key("fetch_benchmark")):
                with st.spinner(f"Fetching {benchmark_symbol} data..."):
                    # Check if benchmark exists as instrument
                    benchmark_inst = self.storage.get_instrument(benchmark_symbol)
                    if not benchmark_inst:
                        # Add benchmark as inactive instrument (not in portfolio)
                        self.storage.add_instrument(
                            symbol=benchmark_symbol,
                            instrument_type='ETF',
                            name=self.BENCHMARKS[benchmark_symbol],
                            is_active=False
                        )
                    
                    # Fetch price data
                    success = self.storage.fetch_and_store_prices(benchmark_symbol)
                    
                    if success:
                        st.success(f"Successfully fetched {benchmark_symbol} data")
                        st.rerun()
                    else:
                        st.error(f"Failed to fetch {benchmark_symbol} data")
            return None
        
        return benchmark_df
    
    # ========================================================================
    # LOGIC LAYER - Pure calculation methods
    # ========================================================================
    
    @staticmethod
    def _calculate_benchmark_metrics(portfolio_returns: pd.Series, benchmark_returns: pd.Series,
                                     portfolio_values: pd.Series, benchmark_prices: pd.Series) -> BenchmarkMetrics:
        """Calculate all benchmark comparison metrics.
        
        Parameters:
            portfolio_returns: Portfolio returns series
            benchmark_returns: Benchmark returns series
            portfolio_values: Portfolio values series
            benchmark_prices: Benchmark price series
            
        Returns:
            BenchmarkMetrics: All calculated metrics
        """
        # Risk-adjusted metrics
        beta = calculate_beta(portfolio_returns, benchmark_returns)
        alpha = calculate_alpha(portfolio_returns, benchmark_returns)
        info_ratio = calculate_information_ratio(portfolio_returns, benchmark_returns)
        
        portfolio_sharpe = calculate_sharpe_ratio(portfolio_returns)
        benchmark_sharpe = calculate_sharpe_ratio(benchmark_returns)
        
        # Return metrics
        portfolio_total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100
        benchmark_total_return = (benchmark_prices.iloc[-1] / benchmark_prices.iloc[0] - 1) * 100
        
        # Volatility metrics
        portfolio_vol = portfolio_returns.std() * np.sqrt(252) * 100
        benchmark_vol = benchmark_returns.std() * np.sqrt(252) * 100
        
        return BenchmarkMetrics(
            beta=beta,
            alpha=alpha,
            info_ratio=info_ratio,
            portfolio_sharpe=portfolio_sharpe,
            benchmark_sharpe=benchmark_sharpe,
            portfolio_total_return=portfolio_total_return,
            benchmark_total_return=benchmark_total_return,
            portfolio_vol=portfolio_vol,
            benchmark_vol=benchmark_vol
        )
