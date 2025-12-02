"""
Benchmark comparison widget - compares portfolio against market benchmarks
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from .base_widget import BaseWidget
from src.utils.performance_metrics import (
    calculate_returns,
    calculate_beta,
    calculate_alpha,
    calculate_information_ratio,
    calculate_sharpe_ratio
)


class BenchmarkComparisonWidget(BaseWidget):
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
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render benchmark comparison"""
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
            st.write("**Select instruments to include in comparison:**")
            
            # Create columns for instrument selection
            num_cols = 3
            cols = st.columns(num_cols)
            
            # Initialize selected instruments in session state
            if f"{self.widget_id}_selected_instruments" not in st.session_state:
                st.session_state[f"{self.widget_id}_selected_instruments"] = [h['symbol'] for h in holdings]
            
            selected_instruments = []
            for idx, holding in enumerate(holdings):
                col_idx = idx % num_cols
                with cols[col_idx]:
                    is_selected = st.checkbox(
                        f"{holding['symbol']} ({holding.get('name', '')})",
                        value=holding['symbol'] in st.session_state[f"{self.widget_id}_selected_instruments"],
                        key=f"{self.widget_id}_instrument_{holding['symbol']}"
                    )
                    if is_selected:
                        selected_instruments.append(holding['symbol'])
            
            # Update session state
            st.session_state[f"{self.widget_id}_selected_instruments"] = selected_instruments
            
            if not selected_instruments:
                st.info("Please select at least one instrument to compare.")
                return
            
            # Filter holdings to selected instruments
            selected_holdings = [h for h in holdings if h['symbol'] in selected_instruments]
        
            
            
            
            # Select benchmark
            benchmark_symbol = st.selectbox(
                "Select Benchmark:",
                options=list(self.BENCHMARKS.keys()),
                format_func=lambda x: f"{x} - {self.BENCHMARKS[x]}",
                key=f"{self.widget_id}_benchmark"
            )
            
            # Time period
            period = st.selectbox(
                "Time Period:",
                options=['1 Month', '3 Months', '6 Months', '1 Year'],
                key=f"{self.widget_id}_period"
            )
            
            period_days = {
                '1 Month': 30,
                '3 Months': 90,
                '6 Months': 180,
                '1 Year': 365
            }
            days = period_days[period]
            
            # Calculate portfolio returns
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            portfolio_values = self._calculate_portfolio_values(selected_holdings, start_date, end_date)
            
            if portfolio_values.empty:
                st.warning("No price data available for selected period")
                return
            
            portfolio_returns = calculate_returns(portfolio_values)
            
            # Get benchmark data
            benchmark_df = self.storage.get_price_data(benchmark_symbol, start_date, end_date)
            
            if benchmark_df is None or benchmark_df.empty:
                st.warning(f"No benchmark data available for {benchmark_symbol}")
                
                # Offer to fetch benchmark data
                if st.button(f"Fetch {benchmark_symbol} data", key=f"{self.widget_id}_fetch_benchmark"):
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
                return
            
            benchmark_returns = calculate_returns(benchmark_df['close'])
            
            # Calculate metrics
            beta = calculate_beta(portfolio_returns, benchmark_returns)
            alpha = calculate_alpha(portfolio_returns, benchmark_returns)
            info_ratio = calculate_information_ratio(portfolio_returns, benchmark_returns)
            
            portfolio_sharpe = calculate_sharpe_ratio(portfolio_returns)
            benchmark_sharpe = calculate_sharpe_ratio(benchmark_returns)
            
            # Calculate cumulative returns
            portfolio_cumret = (1 + portfolio_returns).cumprod() - 1
            benchmark_cumret = (1 + benchmark_returns).cumprod() - 1
            
            # Display metrics
            st.markdown("**Benchmark Comparison Metrics**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Beta", f"{beta:.2f}", help="Sensitivity to benchmark movements")
            
            with col2:
                st.metric("Alpha (Annual)", f"{alpha*100:.2f}%", help="Excess return vs benchmark")
            
            with col3:
                st.metric("Information Ratio", f"{info_ratio:.2f}", help="Excess return per unit tracking error")
            
            
            
            # Comparison metrics
            st.markdown("**Performance Comparison**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Portfolio**")
                portfolio_total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100
                st.metric("Total Return", f"{portfolio_total_return:.1f}%")
                st.metric("Sharpe Ratio", f"{portfolio_sharpe:.2f}")
                portfolio_vol = portfolio_returns.std() * np.sqrt(252) * 100
                st.metric("Volatility (Annual)", f"{portfolio_vol:.1f}%")
            
            with col2:
                st.markdown(f"**{self.BENCHMARKS[benchmark_symbol]}**")
                benchmark_total_return = (benchmark_df['close'].iloc[-1] / benchmark_df['close'].iloc[0] - 1) * 100
                st.metric("Total Return", f"{benchmark_total_return:.1f}%")
                st.metric("Sharpe Ratio", f"{benchmark_sharpe:.2f}")
                benchmark_vol = benchmark_returns.std() * np.sqrt(252) * 100
                st.metric("Volatility (Annual)", f"{benchmark_vol:.1f}%")
            
            
            
            # Performance chart
            st.markdown("**Cumulative Returns**")
            
            comparison_df = pd.DataFrame({
                'Portfolio': portfolio_cumret * 100,
                'Benchmark': benchmark_cumret * 100
            })
            
            st.line_chart(comparison_df)
    
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
