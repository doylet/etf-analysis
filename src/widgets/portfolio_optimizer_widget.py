"""
Portfolio optimizer widget - construct hypothetical portfolios and find efficient frontier.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Data fetching and validation (_fetch_*, _prepare_* methods)
- Logic Layer: Pure calculations (_calculate_* static methods)
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import plotly.graph_objects as go
from scipy.optimize import minimize

from .layered_base_widget import LayeredBaseWidget
from src.utils.performance_metrics import calculate_returns, calculate_sharpe_ratio


@dataclass
class PortfolioMetrics:
    """Metrics for a portfolio allocation."""
    weights: np.ndarray
    expected_return: float
    volatility: float
    sharpe_ratio: float


@dataclass
class EfficientFrontier:
    """Efficient frontier data."""
    portfolios: List[PortfolioMetrics]
    min_vol_portfolio: PortfolioMetrics
    max_sharpe_portfolio: PortfolioMetrics


class PortfolioOptimizerWidget(LayeredBaseWidget):
    """Widget for portfolio optimization and efficient frontier analysis"""
    
    def get_name(self) -> str:
        return "Portfolio Optimizer"
    
    def get_description(self) -> str:
        return "Construct hypothetical portfolios, optimize allocations, and visualize the efficient frontier"
    
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
                st.info("No instruments available")
                return
            
            # Get all instruments (including those not in portfolio)
            # Use active_only=False to include ALL instruments for selection
            all_instruments = self.storage.get_all_instruments(active_only=False)
            
            if not all_instruments:
                st.info("No instruments available for optimization")
                return
            
            # Select instruments and time period
            selected_symbols, days = self._render_instrument_and_period_selectors(all_instruments)
            
            if len(selected_symbols) < 2:
                st.info("Please select at least 2 instruments to optimize")
                return
            
            # Toggle for total returns vs price returns
            include_dividends = st.toggle(
                "Include dividends in returns",
                value=True,
                help="Calculate total returns (price + dividends) instead of price-only returns",
                key=self._get_session_key("include_dividends")
            )
            
            # Choose optimization mode
            mode = st.radio(
                "Optimization Mode:",
                options=["Custom Weights", "Efficient Frontier", "Target Return", 
                        "Max Diversification", "Min Drawdown", "Mean-CVaR", "Max Income-Growth"],
                horizontal=False,
                key=self._get_session_key("mode")
            )
            
            # Fetch returns data
            returns_df = self._fetch_returns_data(selected_symbols, days, include_dividends)
            
            if returns_df is None or returns_df.empty:
                st.warning("Insufficient price data for selected instruments")
                return
            
            # Render based on mode
            if mode == "Custom Weights":
                self._render_custom_weights_mode(selected_symbols, returns_df, include_dividends)
            elif mode == "Efficient Frontier":
                self._render_efficient_frontier_mode(selected_symbols, returns_df, include_dividends)
            elif mode == "Target Return":
                self._render_target_return_mode(selected_symbols, returns_df, include_dividends)
            elif mode == "Max Diversification":
                self._render_max_diversification_mode(selected_symbols, returns_df, include_dividends)
            elif mode == "Min Drawdown":
                self._render_min_drawdown_mode(selected_symbols, returns_df, include_dividends)
            elif mode == "Mean-CVaR":
                self._render_mean_cvar_mode(selected_symbols, returns_df, include_dividends)
            elif mode == "Max Income-Growth":
                self._render_max_income_growth_mode(selected_symbols, returns_df, include_dividends)
    
    def _render_instrument_and_period_selectors(self, instruments: List[Dict]) -> Tuple[List[str], int]:
        """Render instrument and period selectors.
        
        Parameters:
            instruments: List of all available instruments
            
        Returns:
            Tuple[List[str], int]: (selected_symbols, period_days)
        """
        st.write("**Select instruments for portfolio:**")
        
        # Create symbol options - separate portfolio holdings from other instruments
        portfolio_holdings = sorted([i['symbol'] for i in instruments if i.get('quantity', 0) > 0])
        other_instruments = sorted([i['symbol'] for i in instruments if i.get('quantity', 0) == 0])
        
        # All options with portfolio holdings first
        symbol_options = portfolio_holdings + other_instruments
        
        # Default to portfolio holdings, or first 5 if no holdings
        default_symbols = portfolio_holdings if portfolio_holdings else symbol_options[:5]
        if len(default_symbols) > 5:
            default_symbols = default_symbols[:5]
        
        # Multi-select for instruments
        selected_symbols = st.multiselect(
            "Instruments:",
            options=symbol_options,
            default=default_symbols,
            key=self._get_session_key("instruments")
        )
        
        # Time period
        period = st.selectbox(
            "Historical Period:",
            options=['3 Months', '6 Months', '1 Year', '2 Years', '3 Years'],
            index=2,
            key=self._get_session_key("period")
        )
        
        period_days = {
            '3 Months': 90,
            '6 Months': 180,
            '1 Year': 365,
            '2 Years': 730,
            '3 Years': 1095
        }
        
        return selected_symbols, period_days[period]
    
    def _render_custom_weights_mode(self, symbols: List[str], returns_df: pd.DataFrame, include_dividends: bool = False):
        """Render custom weights input and portfolio metrics.
        
        Parameters:
            symbols: List of instrument symbols
            returns_df: DataFrame of returns for each instrument
            include_dividends: Whether dividends are included in returns
        """
        # Use only symbols that have data in returns_df
        available_symbols = [s for s in symbols if s in returns_df.columns]
        
        if len(available_symbols) == 0:
            st.warning("No data available for selected instruments")
            return
        
        # Get current portfolio weights
        # Use active_only=True since we only care about current holdings
        all_instruments = self.storage.get_all_instruments(active_only=True)
        instrument_dict = {i['symbol']: i for i in all_instruments}
        
        # Calculate total portfolio value for selected symbols
        total_value = 0.0
        symbol_values = {}
        
        for symbol in available_symbols:
            inst = instrument_dict.get(symbol, {})
            quantity = inst.get('quantity', 0)
            if quantity > 0:
                latest_prices = self.storage.get_latest_prices([symbol])
                price = latest_prices.get(symbol, {}).get('close', 0)
                symbol_values[symbol] = quantity * price
                total_value += symbol_values[symbol]
        
        # Calculate current weights as percentages
        current_weights = {}
        if total_value > 0:
            for symbol in available_symbols:
                pct = (symbol_values.get(symbol, 0) / total_value * 100)
                current_weights[symbol] = round(pct)  # Round to nearest percent
            
            # Adjust to ensure sum is exactly 100%
            weight_sum = sum(current_weights.values())
            if weight_sum != 100 and weight_sum > 0:
                # Add/subtract difference from largest position
                largest_symbol = max(current_weights, key=current_weights.get)
                current_weights[largest_symbol] += (100 - weight_sum)
        else:
            # No portfolio positions - use equal weights
            equal_weight = 100.0 / len(available_symbols)
            for symbol in available_symbols:
                current_weights[symbol] = round(equal_weight)
            
            # Adjust rounding
            weight_sum = sum(current_weights.values())
            if weight_sum != 100:
                current_weights[available_symbols[0]] += (100 - weight_sum)
        
        st.markdown("**Set Portfolio Weights:**")
        st.caption("Weights must sum to 100%. Currently showing your actual portfolio allocation.")
        
        # Auto-optimization buttons
        st.markdown("**Quick Optimization:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Apply Max Sharpe", help="Optimize for maximum risk-adjusted returns", width="stretch"):
                frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=50)
                if frontier:
                    # Store optimal weights in session state
                    for idx, symbol in enumerate(returns_df.columns):
                        weight_pct = round(frontier.max_sharpe_portfolio.weights[idx] * 100)
                        st.session_state[self._get_session_key(f"weight_{symbol}")] = float(weight_pct)
                    st.rerun()
        
        with col2:
            if st.button("Apply Min Volatility", help="Optimize for minimum risk", width="stretch"):
                frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=50)
                if frontier:
                    for idx, symbol in enumerate(returns_df.columns):
                        weight_pct = round(frontier.min_vol_portfolio.weights[idx] * 100)
                        st.session_state[self._get_session_key(f"weight_{symbol}")] = float(weight_pct)
                    st.rerun()
        
        with col3:
            if st.button("Equal Weights", help="Distribute evenly across all instruments", width="stretch"):
                equal_weight = 100.0 / len(available_symbols)
                for symbol in available_symbols:
                    st.session_state[self._get_session_key(f"weight_{symbol}")] = round(equal_weight)
                st.rerun()
        
        # Create weight inputs
        weights = {}
        cols = st.columns(min(3, len(available_symbols)))
        
        for idx, symbol in enumerate(available_symbols):
            col = cols[idx % len(cols)]
            with col:
                # Check if weight is in session state (from optimization button)
                session_key = self._get_session_key(f"weight_{symbol}")
                if session_key in st.session_state:
                    default_weight = st.session_state[session_key]
                else:
                    default_weight = current_weights.get(symbol, 100.0 / len(available_symbols))
                
                weights[symbol] = st.number_input(
                    f"{symbol} %",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(default_weight),
                    step=1.0,
                    key=session_key
                )
        
        # Validate weights
        total_weight = sum(weights.values())
        
        if abs(total_weight - 100.0) > 0.01:
            st.error(f"Weights sum to {total_weight:.1f}%. Must equal 100%")
            return
        
        # Convert to array (must match order of returns_df columns)
        weight_array = np.array([weights[s] / 100.0 for s in returns_df.columns])
        
        # Calculate metrics
        metrics = self._calculate_portfolio_metrics(weight_array, returns_df)
        
        # Display metrics
        self._render_portfolio_metrics(available_symbols, metrics, include_dividends=include_dividends)
        
        # Calculate and show efficient frontier
        with st.spinner("Calculating efficient frontier..."):
            frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=100)
        if frontier:
            self._render_efficient_frontier_chart(frontier, returns_df, available_symbols)
    
    def _render_efficient_frontier_mode(self, symbols: List[str], returns_df: pd.DataFrame, include_dividends: bool = False):
        """Render efficient frontier visualization and optimal portfolios.
        
        Parameters:
            symbols: List of instrument symbols
            returns_df: DataFrame of returns for each instrument
            include_dividends: Whether dividends are included in returns
        """
        # Use only symbols that have data in returns_df
        available_symbols = list(returns_df.columns)
        
        st.markdown("**Efficient Frontier Analysis**")
        
        with st.spinner("Calculating efficient frontier..."):
            frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=100)
        
        if frontier is None:
            st.error("Failed to calculate efficient frontier")
            return
        
        # Display optimal portfolios
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Minimum Volatility Portfolio**")
            self._render_portfolio_metrics(available_symbols, frontier.min_vol_portfolio, show_weights=True, include_dividends=include_dividends)
        
        with col2:
            st.markdown("**Maximum Sharpe Ratio Portfolio**")
            self._render_portfolio_metrics(available_symbols, frontier.max_sharpe_portfolio, show_weights=True, include_dividends=include_dividends)
        

        # Plot efficient frontier
        self._render_efficient_frontier_chart(frontier, returns_df, available_symbols)
        
        # Render recommendations for Max Sharpe portfolio
        self._render_instrument_recommendations(
            available_symbols,
            frontier.max_sharpe_portfolio,
            returns_df,
            "Max Sharpe"
        )
    
    def _render_target_return_mode(self, symbols: List[str], returns_df: pd.DataFrame, include_dividends: bool = False):
        """Render target return optimization.
        
        Parameters:
            symbols: List of instrument symbols
            returns_df: DataFrame of returns for each instrument
            include_dividends: Whether dividends are included in returns
        """
        # Use only symbols that have data in returns_df
        available_symbols = list(returns_df.columns)
        
        st.markdown("**Target Return Optimization**")
        
        # Get target return
        target_return = st.slider(
            "Target Annual Return (%):",
            min_value=0.0,
            max_value=50.0,
            value=15.0,
            step=0.5,
            key=self._get_session_key("target_return")
        )
        
        # Optimize
        with st.spinner("Optimizing portfolio..."):
            metrics = self._optimize_for_target_return(returns_df, target_return / 100.0)
        
        if metrics is None:
            st.error(f"Cannot achieve {target_return}% return with selected instruments")
            return
        
        # Display results
        self._render_portfolio_metrics(available_symbols, metrics, show_weights=True)
        
        # Calculate and show efficient frontier
        with st.spinner("Calculating efficient frontier..."):
            frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=100)
        if frontier:
            self._render_efficient_frontier_chart(frontier, returns_df, available_symbols)
        
        # Render recommendations
        self._render_instrument_recommendations(
            available_symbols,
            metrics,
            returns_df,
            "Target Return"
        )
    
    def _render_max_diversification_mode(self, symbols: List[str], returns_df: pd.DataFrame, include_dividends: bool = False):
        """Render maximum diversification optimization.
        
        Parameters:
            symbols: List of instrument symbols
            returns_df: DataFrame of returns for each instrument
            include_dividends: Whether dividends are included in returns
        """
        available_symbols = list(returns_df.columns)
        
        st.markdown("**Maximum Diversification Portfolio**")
        st.caption("Minimizes portfolio volatility / weighted average volatility (lower = better diversification)")
        
        with st.spinner("Optimizing for maximum diversification..."):
            metrics = self._optimize_for_max_diversification(returns_df)
        
        if metrics is None:
            st.error("Failed to optimize for maximum diversification")
            return
        
        self._render_portfolio_metrics(available_symbols, metrics, show_weights=True, include_dividends=include_dividends)
        
        # Calculate and show efficient frontier
        with st.spinner("Calculating efficient frontier..."):
            frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=100)
        if frontier:
            self._render_efficient_frontier_chart(frontier, returns_df, available_symbols)
        
        # Render recommendations
        self._render_instrument_recommendations(
            available_symbols,
            metrics,
            returns_df,
            "Max Diversification"
        )
    
    def _render_min_drawdown_mode(self, symbols: List[str], returns_df: pd.DataFrame, include_dividends: bool = False):
        """Render minimum drawdown optimization.
        
        Parameters:
            symbols: List of instrument symbols
            returns_df: DataFrame of returns for each instrument
            include_dividends: Whether dividends are included in returns
        """
        available_symbols = list(returns_df.columns)
        
        st.markdown("**Minimum Drawdown Portfolio**")
        st.caption("Minimizes the maximum peak-to-trough decline in portfolio value")
        
        with st.spinner("Optimizing for minimum drawdown..."):
            metrics = self._optimize_for_min_drawdown(returns_df)
        
        if metrics is None:
            st.error("Failed to optimize for minimum drawdown")
            return
        
        self._render_portfolio_metrics(available_symbols, metrics, show_weights=True, include_dividends=include_dividends)
        
        # Calculate and show efficient frontier
        with st.spinner("Calculating efficient frontier..."):
            frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=100)
        if frontier:
            self._render_efficient_frontier_chart(frontier, returns_df, available_symbols)
        
        # Render recommendations
        self._render_instrument_recommendations(
            available_symbols,
            metrics,
            returns_df,
            "Min Drawdown"
        )
    
    def _render_mean_cvar_mode(self, symbols: List[str], returns_df: pd.DataFrame, include_dividends: bool = False):
        """Render Mean-CVaR optimization.
        
        Parameters:
            symbols: List of instrument symbols
            returns_df: DataFrame of returns for each instrument
            include_dividends: Whether dividends are included in returns
        """
        available_symbols = list(returns_df.columns)
        
        st.markdown("**Mean-CVaR Portfolio**")
        st.caption("Optimizes based on Conditional Value at Risk (expected shortfall in worst 5% of cases)")
        
        # CVaR confidence level selector
        alpha = st.slider("CVaR Confidence Level (α)", min_value=0.01, max_value=0.10, value=0.05, step=0.01,
                         help="Percentage of worst scenarios to consider (e.g., 0.05 = worst 5%)")
        
        with st.spinner("Optimizing based on CVaR..."):
            metrics = self._optimize_for_mean_cvar(returns_df, alpha)
        
        if metrics is None:
            st.error("Failed to optimize for Mean-CVaR")
            return
        
        self._render_portfolio_metrics(available_symbols, metrics, show_weights=True, include_dividends=include_dividends)
        
        # Calculate and show efficient frontier
        with st.spinner("Calculating efficient frontier..."):
            frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=100)
        if frontier:
            self._render_efficient_frontier_chart(frontier, returns_df, available_symbols)
        
        # Render recommendations
        self._render_instrument_recommendations(
            available_symbols,
            metrics,
            returns_df,
            "Mean-CVaR"
        )
    
    def _render_max_income_growth_mode(self, symbols: List[str], returns_df: pd.DataFrame, include_dividends: bool = False):
        """Render Max Income-Growth optimization.
        
        Parameters:
            symbols: List of instrument symbols
            returns_df: DataFrame of returns for each instrument
            include_dividends: Whether dividends are included in returns
        """
        available_symbols = list(returns_df.columns)
        
        st.markdown("**Max Income-Growth Portfolio**")
        st.caption("Optimizes for the best balance between dividend yield (cash flow) and capital appreciation (growth)")
        
        # Weight slider for yield vs growth preference
        yield_weight = st.slider(
            "Income vs Growth Balance", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.5, 
            step=0.1,
            help="0.0 = Pure growth (no yield consideration), 1.0 = Pure income (no growth consideration), 0.5 = Equal balance",
            format="%.1f"
        )
        
        # Show interpretation
        if yield_weight < 0.3:
            st.info("Focus: Capital Appreciation (Growth)")
        elif yield_weight > 0.7:
            st.info("Focus: Dividend Income (Yield)")
        else:
            st.info("Focus: Balanced Income-Growth")
        
        with st.spinner("Optimizing for income-growth balance..."):
            metrics = self._optimize_for_income_growth(returns_df, available_symbols, yield_weight)
        
        if metrics is None:
            st.error("Failed to optimize for income-growth balance")
            return
        
        self._render_portfolio_metrics(available_symbols, metrics, show_weights=True, include_dividends=include_dividends)
        
        # Show portfolio dividend yield if available
        if hasattr(metrics, 'dividend_yield'):
            # Format dividend yield, showing 0.00% for very small values
            if abs(metrics.dividend_yield) < 0.0001:  # Less than 0.01%
                yield_display = "0.00%"
            else:
                yield_display = f"{metrics.dividend_yield * 100:.2f}%"
            st.metric("Portfolio Dividend Yield", yield_display)
        
        # Calculate and show efficient frontier
        with st.spinner("Calculating efficient frontier..."):
            frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=100)
        if frontier:
            self._render_efficient_frontier_chart(frontier, returns_df, available_symbols)
        
        # Render recommendations
        self._render_instrument_recommendations(
            available_symbols,
            metrics,
            returns_df,
            "Max Income-Growth"
        )
    
    def _render_portfolio_metrics(self, symbols: List[str], metrics: PortfolioMetrics, 
                                  show_weights: bool = False, include_dividends: bool = False):
        """Display portfolio metrics.
        
        Parameters:
            symbols: List of instrument symbols
            metrics: Portfolio metrics
            show_weights: Whether to show weight breakdown
            include_dividends: Whether dividends are included in returns
        """
        # Calculate dividend yield if dividends are included
        if include_dividends:
            # Get weighted average dividend yield
            dividend_yields = []
            for symbol, weight in zip(symbols, metrics.weights):
                dividends = self.storage.get_dividends(symbol)
                if dividends and len(dividends) > 0:
                    # Get most recent price
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    price_df = self.storage.get_price_data(symbol, start_date, end_date)
                    if price_df is not None and not price_df.empty:
                        recent_price = price_df['close'].iloc[-1]
                        # Calculate annual dividend
                        one_year_ago = datetime.now() - timedelta(days=365)
                        recent_divs = [d['amount'] for d in dividends 
                                     if pd.to_datetime(d['ex_date']) >= one_year_ago]
                        annual_dividend = sum(recent_divs)
                        div_yield = (annual_dividend / recent_price) if recent_price > 0 else 0
                        dividend_yields.append(div_yield * weight)
            
            portfolio_yield = sum(dividend_yields)
            
            # Display with 4 columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Expected Annual Return", f"{metrics.expected_return * 100:.3g}%")
            
            with col2:
                st.metric("Annual Volatility", f"{metrics.volatility * 100:.3g}%")
            
            with col3:
                st.metric("Sharpe Ratio", f"{metrics.sharpe_ratio:.3g}")
            
            with col4:
                # Format dividend yield, showing 0.00% for very small values
                if abs(portfolio_yield) < 0.0001:  # Less than 0.01%
                    yield_display = "0.00%"
                else:
                    yield_display = f"{portfolio_yield * 100:.2f}%"
                st.metric("Dividend Yield", yield_display,
                         help="Weighted average dividend yield based on portfolio allocation")
        else:
            # Display with 3 columns (no dividend yield)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Expected Annual Return", f"{metrics.expected_return * 100:.3g}%")
            
            with col2:
                st.metric("Annual Volatility", f"{metrics.volatility * 100:.3g}%")
            
            with col3:
                st.metric("Sharpe Ratio", f"{metrics.sharpe_ratio:.3g}")
        
        if show_weights:
            st.markdown("**Portfolio Allocation:**")
            
            # Create DataFrame for weights
            weights_data = []
            for symbol, weight in zip(symbols, metrics.weights):
                weight_pct = weight * 100
                if weight_pct < 0.01:
                    formatted_weight = "<0.01%"
                else:
                    formatted_weight = f"{weight_pct:.2f}%"
                weights_data.append({'Symbol': symbol, 'Weight (%)': formatted_weight})
            
            weights_df = pd.DataFrame(weights_data)
            # Sort by numeric value for proper ordering
            weights_df['_sort_key'] = [w * 100 for w in metrics.weights]
            weights_df = weights_df.sort_values('_sort_key', ascending=False).drop('_sort_key', axis=1)
            
            # Display as table
            st.dataframe(
                weights_df,
                hide_index=True,
                width='stretch'
            )
    
    def _render_efficient_frontier_chart(self, frontier: EfficientFrontier, 
                                         returns_df: pd.DataFrame, symbols: List[str]):
        """Render efficient frontier chart with Plotly.
        
        Parameters:
            frontier: Efficient frontier data
            returns_df: Returns DataFrame
            symbols: List of symbols
        """
        st.markdown("**Efficient Frontier Visualization**")
        
        # Calculate current portfolio metrics
        current_portfolio_metrics = self._calculate_current_portfolio_metrics(symbols, returns_df)
        
        # Extract data for plotting
        volatilities = [p.volatility * 100 for p in frontier.portfolios]
        returns = [p.expected_return * 100 for p in frontier.portfolios]
        sharpes = [p.sharpe_ratio for p in frontier.portfolios]
        
        # Create figure with custom template
        fig = go.Figure()
        
        # Add efficient frontier
        fig.add_trace(go.Scatter(
            x=volatilities,
            y=returns,
            mode='markers',
            marker=dict(
                size=8,
                color=sharpes,
                colorscale='Turbo',
                showscale=True,
                colorbar=dict(
                    title="Sharpe Ratio",
                    tickformat=".2f"
                ),
                line=dict(width=0.5, color='white')
            ),
            text=[f"<b>Portfolio</b><br>Return: {r:.2f}%<br>Volatility: {v:.2f}%<br>Sharpe: {s:.2f}" 
                  for r, v, s in zip(returns, volatilities, sharpes)],
            hovertemplate='%{text}<extra></extra>',
            name='Portfolio',
            showlegend=False
        ))
        
        # Add current portfolio if it exists
        if current_portfolio_metrics is not None:
            fig.add_trace(go.Scatter(
                x=[current_portfolio_metrics.volatility * 100],
                y=[current_portfolio_metrics.expected_return * 100],
                mode='markers+text',
                marker=dict(size=20, color='#9467BD', symbol='star', line=dict(width=2, color='white')),
                name='Current Portfolio',
                text=['Current'],
                textposition='top right',
                textfont=dict(size=11, color='#9467BD', family='Arial Black'),
                hovertemplate=f"<b>Current Portfolio</b><br>Return: {current_portfolio_metrics.expected_return * 100:.2f}%<br>Volatility: {current_portfolio_metrics.volatility * 100:.2f}%<br>Sharpe: {current_portfolio_metrics.sharpe_ratio:.2f}<extra></extra>"
            ))
        
        # Add minimum volatility portfolio
        fig.add_trace(go.Scatter(
            x=[frontier.min_vol_portfolio.volatility * 100],
            y=[frontier.min_vol_portfolio.expected_return * 100],
            mode='markers+text',
            marker=dict(size=18, color='#00CC96', symbol='circle', line=dict(width=2, color='white')),
            name='Min Volatility',
            text=['Min Vol'],
            textposition='top center',
            textfont=dict(size=10, color='#00CC96'),
            hovertemplate=f"<b>Min Volatility Portfolio</b><br>Return: {frontier.min_vol_portfolio.expected_return * 100:.2f}%<br>Volatility: {frontier.min_vol_portfolio.volatility * 100:.2f}%<br>Sharpe: {frontier.min_vol_portfolio.sharpe_ratio:.2f}<extra></extra>"
        ))
        
        # Add maximum Sharpe portfolio
        fig.add_trace(go.Scatter(
            x=[frontier.max_sharpe_portfolio.volatility * 100],
            y=[frontier.max_sharpe_portfolio.expected_return * 100],
            mode='markers+text',
            marker=dict(size=18, color='#EF553B', symbol='circle', line=dict(width=2, color='white')),
            name='Max Sharpe',
            text=['Max Sharpe'],
            textposition='bottom center',
            textfont=dict(size=10, color='#EF553B'),
            hovertemplate=f"<b>Max Sharpe Portfolio</b><br>Return: {frontier.max_sharpe_portfolio.expected_return * 100:.2f}%<br>Volatility: {frontier.max_sharpe_portfolio.volatility * 100:.2f}%<br>Sharpe: {frontier.max_sharpe_portfolio.sharpe_ratio:.2f}<extra></extra>"
        ))
        
        # Add individual assets
        individual_returns = returns_df.mean() * 252 * 100
        individual_vols = returns_df.std() * np.sqrt(252) * 100
        
        fig.add_trace(go.Scatter(
            x=individual_vols,
            y=individual_returns,
            mode='markers+text',
            marker=dict(
                size=12, 
                color='#636EFA',
                symbol='diamond',
                line=dict(width=2, color='white')
            ),
            text=symbols,
            textposition='top center',
            textfont=dict(size=11, color='#636EFA'),
            name='Individual Assets',
            hovertemplate='<b>%{text}</b><br>Return: %{y:.2f}%<br>Volatility: %{x:.2f}%<extra></extra>'
        ))
        
        # Update layout with improved styling
        fig.update_layout(
            title=dict(
                text="Efficient Frontier",
                font=dict(size=20, color='#333'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Annual Volatility (%)",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128, 128, 128, 0.2)',
                zeroline=False
            ),
            yaxis=dict(
                title="Annual Return (%)",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128, 128, 128, 0.2)',
                zeroline=False
            ),
            hovermode='closest',
            showlegend=True,
            legend=dict(
                yanchor="bottom",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(0, 0, 0, 0.2)',
                borderwidth=1
            ),
            height=650,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def _render_instrument_recommendations(
        self,
        current_symbols: List[str],
        optimal_metrics: PortfolioMetrics,
        returns_df: pd.DataFrame,
        optimization_mode: str
    ):
        """Render instrument recommendations section.
        
        Parameters:
            current_symbols: Current portfolio symbols
            optimal_metrics: Optimal portfolio metrics
            returns_df: Historical returns data
            optimization_mode: Type of optimization
        """
        st.subheader("Alternative Instrument Recommendations")
        
        # Create cache key based on current portfolio and optimization settings
        cache_key = f"recommendations_{'-'.join(sorted(current_symbols))}_{optimization_mode}"
        
        # Check if we have cached recommendations
        if cache_key in st.session_state:
            recommendations = st.session_state[cache_key]
            st.caption(f"✓ Showing cached recommendations")
        else:
            with st.spinner("Analyzing alternative instruments..."):
                # Get all instruments and filter to candidates
                # CRITICAL: Pass active_only=False to get ALL instruments from database
                all_instruments = self.storage.get_all_instruments(active_only=False)
                
                # Filter to candidates: exclude current portfolio only
                # Include ALL instruments regardless of is_active flag
                candidate_symbols = [
                    i['symbol'] for i in all_instruments 
                    if i['symbol'] not in current_symbols
                ]
                
                total_available = len(candidate_symbols)
                
                # Sample up to 100 candidates randomly for better diversity
                if len(candidate_symbols) > 100:
                    import random
                    random.seed(42)  # For reproducibility
                    candidate_symbols = random.sample(candidate_symbols, 100)
                
                st.caption(f"Analyzing {len(candidate_symbols)} candidate instruments (of {total_available} total available)...")
                
                if not candidate_symbols:
                    st.info("No alternative instruments available for recommendation.")
                    return
                
                # Calculate recommendations
                recommendations = self._calculate_instrument_recommendations(
                    current_symbols,
                    candidate_symbols,
                    returns_df,
                    optimal_metrics,
                    optimization_mode
                )
                
                # Cache the results
                st.session_state[cache_key] = recommendations
            
            if not recommendations:
                st.info("No recommendations found that would improve the current optimization.")
                return
            
            # Display top 5 recommendations
            top_recommendations = recommendations[:5]
            
            st.markdown(f"**Top {len(top_recommendations)} instruments to add to your portfolio:**")
            st.caption("💡 Suggested weights show how much to allocate when ADDING to your current portfolio (not replacing it)")
            
            for idx, rec in enumerate(top_recommendations, 1):
                # Expand first 2 by default
                improvement_metric = rec.get('improvement_label', 'Sharpe')
                with st.expander(
                    f"**{idx}. {rec['symbol']}** - {rec['name']} ({rec['type']}) "
                    f"[+{rec['improvement']:.1f}% {improvement_metric} improvement]",
                    expanded=(idx <= 2)
                ):
                    # Show dividend yield for income-growth mode
                    if optimization_mode == "Max Income-Growth" and 'dividend_yield' in rec:
                        col1, col2, col3, col4 = st.columns(4)
                    else:
                        col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("New Sharpe Ratio", f"{rec['new_sharpe']:.3g}")
                        st.metric("Add to Portfolio", f"{rec['suggested_weight']*100:.1f}%",
                                 help="Suggested allocation when adding this instrument")
                    
                    with col2:
                        st.metric("New Expected Return", f"{rec['new_return']*100:.2f}%")
                        st.metric("Correlation", f"{rec['correlation']:.2f}")
                    
                    with col3:
                        st.metric("New Volatility", f"{rec['new_volatility']*100:.2f}%")
                        st.metric(f"{improvement_metric} Improvement", f"+{rec['improvement']:.1f}%")
                    
                    if optimization_mode == "Max Income-Growth" and 'dividend_yield' in rec:
                        with col4:
                            div_yield = rec['dividend_yield']
                            if abs(div_yield) < 0.0001:
                                yield_display = "0.00%"
                            else:
                                yield_display = f"{div_yield * 100:.2f}%"
                            st.metric("Dividend Yield", yield_display)
                            st.metric("New Portfolio Yield", f"{rec.get('new_portfolio_yield', 0) * 100:.2f}%")
                    
                    st.markdown("**Rationale:**")
                    st.markdown(rec['rationale'])
    
    # ========================================================================
    # DATA LAYER - Data fetching and validation methods
    # ========================================================================
    
    def _fetch_returns_data(self, symbols: List[str], days: int, 
                            include_dividends: bool = True) -> Optional[pd.DataFrame]:
        """Fetch historical returns for selected instruments.
        
        Parameters:
            symbols: List of instrument symbols
            days: Number of days of historical data
            include_dividends: Whether to include dividends in total return calculation
            
        Returns:
            pd.DataFrame: Returns for each instrument, or None if insufficient data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        returns_dict = {}
        
        for symbol in symbols:
            price_df = self.storage.get_price_data(symbol, start_date, end_date)
            
            if price_df is None or price_df.empty or len(price_df) < 30:
                st.warning(f"Insufficient data for {symbol}")
                continue
            
            # Calculate returns
            if include_dividends:
                # Get dividend data
                dividends = self.storage.get_dividends(symbol)
                
                if dividends and len(dividends) > 0:
                    # Calculate total returns (price + dividends)
                    returns = self._calculate_total_returns(price_df['close'], dividends, start_date, end_date)
                else:
                    # No dividend data, fall back to price returns
                    returns = calculate_returns(price_df['close'])
            else:
                # Price returns only
                returns = calculate_returns(price_df['close'])
            returns_dict[symbol] = returns
        
        if len(returns_dict) < 2:
            return None
        
        # Combine into DataFrame and align dates
        returns_df = pd.DataFrame(returns_dict)
        
        # Forward-fill missing values
        returns_df = returns_df.ffill()
        
        # Drop any remaining NaN
        returns_df = returns_df.dropna()
        
        return returns_df
    
    # ========================================================================
    # LOGIC LAYER - Pure calculation methods
    # ========================================================================
    
    @staticmethod
    def _calculate_portfolio_metrics(weights: np.ndarray, returns_df: pd.DataFrame) -> PortfolioMetrics:
        """Calculate portfolio metrics for given weights.
        
        Parameters:
            weights: Portfolio weights (must sum to 1)
            returns_df: DataFrame of returns
            
        Returns:
            PortfolioMetrics: Calculated metrics
        """
        # Portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Annualized metrics
        expected_return = portfolio_returns.mean() * 252
        volatility = portfolio_returns.std() * np.sqrt(252)
        
        # Sharpe ratio (assuming 3% risk-free rate)
        risk_free_rate = 0.03
        sharpe_ratio = (expected_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        return PortfolioMetrics(
            weights=weights,
            expected_return=expected_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio
        )
    
    def _calculate_efficient_frontier(self, returns_df: pd.DataFrame, 
                                      num_portfolios: int = 100) -> Optional[EfficientFrontier]:
        """Calculate efficient frontier portfolios.
        
        Parameters:
            returns_df: DataFrame of returns
            num_portfolios: Number of portfolios to generate
            
        Returns:
            EfficientFrontier: Efficient frontier data, or None if calculation fails
        """
        n_assets = len(returns_df.columns)
        
        # Generate random portfolios
        portfolios = []
        
        for _ in range(num_portfolios):
            # Random weights
            weights = np.random.random(n_assets)
            weights /= weights.sum()
            
            metrics = self._calculate_portfolio_metrics(weights, returns_df)
            portfolios.append(metrics)
        
        # Find minimum volatility portfolio
        min_vol_portfolio = self._optimize_for_min_volatility(returns_df)
        if min_vol_portfolio:
            portfolios.append(min_vol_portfolio)
        
        # Find maximum Sharpe ratio portfolio
        max_sharpe_portfolio = self._optimize_for_max_sharpe(returns_df)
        if max_sharpe_portfolio:
            portfolios.append(max_sharpe_portfolio)
        
        if not portfolios:
            return None
        
        return EfficientFrontier(
            portfolios=portfolios,
            min_vol_portfolio=min_vol_portfolio or portfolios[0],
            max_sharpe_portfolio=max_sharpe_portfolio or portfolios[0]
        )
    
    def _optimize_for_min_volatility(self, returns_df: pd.DataFrame) -> Optional[PortfolioMetrics]:
        """Optimize for minimum volatility.
        
        Parameters:
            returns_df: DataFrame of returns
            
        Returns:
            PortfolioMetrics: Optimal portfolio, or None if optimization fails
        """
        n_assets = len(returns_df.columns)
        
        def portfolio_volatility(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            return portfolio_returns.std() * np.sqrt(252)
        
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        # Bounds: 0 <= weight <= 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            return None
        
        return self._calculate_portfolio_metrics(result.x, returns_df)
    
    def _optimize_for_max_sharpe(self, returns_df: pd.DataFrame) -> Optional[PortfolioMetrics]:
        """Optimize for maximum Sharpe ratio.
        
        Parameters:
            returns_df: DataFrame of returns
            
        Returns:
            PortfolioMetrics: Optimal portfolio, or None if optimization fails
        """
        n_assets = len(returns_df.columns)
        
        def negative_sharpe(weights):
            metrics = self._calculate_portfolio_metrics(weights, returns_df)
            return -metrics.sharpe_ratio
        
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        # Bounds: 0 <= weight <= 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            negative_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            return None
        
        return self._calculate_portfolio_metrics(result.x, returns_df)
    
    def _optimize_for_target_return(self, returns_df: pd.DataFrame, 
                                    target_return: float) -> Optional[PortfolioMetrics]:
        """Optimize for target return with minimum volatility.
        
        Parameters:
            returns_df: DataFrame of returns
            target_return: Target annual return (as decimal)
            
        Returns:
            PortfolioMetrics: Optimal portfolio, or None if target is unachievable
        """
        n_assets = len(returns_df.columns)
        
        def portfolio_volatility(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            return portfolio_returns.std() * np.sqrt(252)
        
        def portfolio_return(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            return portfolio_returns.mean() * 252
        
        # Constraints: weights sum to 1, return equals target
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: portfolio_return(w) - target_return}
        ]
        
        # Bounds: 0 <= weight <= 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            return None
        
        return self._calculate_portfolio_metrics(result.x, returns_df)
    
    def _optimize_for_max_diversification(self, returns_df: pd.DataFrame) -> Optional[PortfolioMetrics]:
        """Optimize for maximum diversification ratio (portfolio vol / weighted avg vol).
        
        Parameters:
            returns_df: DataFrame of returns
            
        Returns:
            PortfolioMetrics: Optimal portfolio, or None if optimization fails
        """
        n_assets = len(returns_df.columns)
        
        # Asset volatilities
        asset_vols = returns_df.std() * np.sqrt(252)
        
        def negative_diversification_ratio(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            portfolio_vol = portfolio_returns.std() * np.sqrt(252)
            weighted_avg_vol = np.dot(weights, asset_vols)
            # Diversification ratio = portfolio_vol / weighted_avg_vol
            # Lower ratio means more diversification benefit
            diversification_ratio = portfolio_vol / weighted_avg_vol if weighted_avg_vol > 0 else 1e10
            return diversification_ratio  # Minimize (don't negate)
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            negative_diversification_ratio,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            return None
        
        return self._calculate_portfolio_metrics(result.x, returns_df)
    
    def _optimize_for_min_drawdown(self, returns_df: pd.DataFrame) -> Optional[PortfolioMetrics]:
        """Optimize to minimize historical maximum drawdown.
        
        Parameters:
            returns_df: DataFrame of returns
            
        Returns:
            PortfolioMetrics: Optimal portfolio, or None if optimization fails
        """
        n_assets = len(returns_df.columns)
        
        def max_drawdown(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            # Return the absolute value of the worst drawdown (minimize it)
            return abs(drawdown.min())
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            max_drawdown,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            return None
        
        return self._calculate_portfolio_metrics(result.x, returns_df)
    
    def _optimize_for_mean_cvar(self, returns_df: pd.DataFrame, alpha: float = 0.05) -> Optional[PortfolioMetrics]:
        """Optimize based on Conditional Value at Risk (CVaR/Expected Shortfall).
        
        Parameters:
            returns_df: DataFrame of returns
            alpha: Confidence level for CVaR (default 0.05 = 5% worst cases)
            
        Returns:
            PortfolioMetrics: Optimal portfolio, or None if optimization fails
        """
        n_assets = len(returns_df.columns)
        
        def cvar(weights):
            portfolio_returns = (returns_df * weights).sum(axis=1)
            # Calculate VaR at alpha level
            var = np.percentile(portfolio_returns, alpha * 100)
            # CVaR is the mean of returns below VaR
            cvar_value = portfolio_returns[portfolio_returns <= var].mean()
            # Return negative CVaR (minimize losses in tail)
            return -cvar_value
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            cvar,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            return None
        
        return self._calculate_portfolio_metrics(result.x, returns_df)
    
    def _optimize_for_income_growth(self, returns_df: pd.DataFrame, symbols: List[str], yield_weight: float = 0.5) -> Optional[PortfolioMetrics]:
        """Optimize for balance between dividend yield and capital growth with risk management.
        
        Parameters:
            returns_df: DataFrame of returns
            symbols: List of instrument symbols
            yield_weight: Weight given to yield vs growth (0=all growth, 1=all yield)
            
        Returns:
            PortfolioMetrics: Optimal portfolio, or None if optimization fails
        """
        n_assets = len(returns_df.columns)
        
        # Fetch dividend yields for all symbols
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        dividend_yields = {}
        
        for symbol in symbols:
            try:
                dividends = self.storage.get_dividends(symbol, start_date, end_date)
                price_df = self.storage.get_price_data(symbol, start_date, end_date)
                
                if dividends and len(dividends) > 0 and price_df is not None:
                    # Calculate trailing 12-month yield
                    total_dividends = sum(d['amount'] for d in dividends)
                    avg_price = price_df['close'].mean()
                    dividend_yields[symbol] = (total_dividends / avg_price) if avg_price > 0 else 0.0
                else:
                    dividend_yields[symbol] = 0.0
            except Exception as e:
                dividend_yields[symbol] = 0.0
        
        # Convert to array matching returns_df column order
        yields_array = np.array([dividend_yields.get(sym, 0.0) for sym in returns_df.columns])
        
        # Calculate annualized capital appreciation (price returns)
        mean_returns = returns_df.mean().values * 252
        
        # Calculate covariance matrix
        cov_matrix = returns_df.cov().values * 252
        
        def objective(weights):
            # Portfolio yield (weighted average)
            portfolio_yield = np.dot(weights, yields_array)
            # Portfolio capital appreciation
            portfolio_growth = np.dot(weights, mean_returns)
            # Portfolio volatility (risk)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Combined total return (yield + growth)
            total_return = yield_weight * portfolio_yield + (1 - yield_weight) * portfolio_growth
            
            # Risk-adjusted return: maximize (return - risk_penalty * volatility)
            # This ensures we don't just pick the highest return instrument
            risk_penalty = 2.0  # Penalize volatility
            risk_adjusted_return = total_return - risk_penalty * portfolio_vol
            
            # Negative because we minimize
            return -risk_adjusted_return
        
        # Constraints: weights sum to 1, and max 40% in any single asset for diversification
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]
        
        # Bounds: min 0%, max 40% per asset (prevents concentration)
        bounds = tuple((0, 0.40) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            return None
        
        metrics = self._calculate_portfolio_metrics(result.x, returns_df)
        # Add dividend yield to metrics
        if metrics:
            metrics.dividend_yield = float(np.dot(result.x, yields_array))
        return metrics
    
    def _calculate_total_returns(self, prices: pd.Series, dividends: List[Dict], 
                                  start_date: datetime, end_date: datetime) -> pd.Series:
        """Calculate total returns including dividends.
        
        Parameters:
            prices: Price series
            dividends: List of dividend records
            start_date: Start date for returns
            end_date: End date for returns
            
        Returns:
            pd.Series: Total returns including dividends
        """
        # Create dividend series aligned with price dates
        div_series = pd.Series(0.0, index=prices.index)
        
        for div in dividends:
            ex_date = pd.to_datetime(div['ex_date'])
            if start_date <= ex_date <= end_date and ex_date in div_series.index:
                div_series[ex_date] = div['amount']
        
        # Calculate total return: (price change + dividend) / previous price
        price_change = prices.diff()
        total_change = price_change + div_series
        total_returns = total_change / prices.shift(1)
        
        return total_returns.dropna()
    
    def _calculate_current_portfolio_metrics(self, symbols: List[str], returns_df: pd.DataFrame) -> Optional[PortfolioMetrics]:
        """Calculate metrics for the current portfolio allocation.
        
        Parameters:
            symbols: List of symbols
            returns_df: Returns DataFrame
            
        Returns:
            PortfolioMetrics for current portfolio, or None if no current holdings
        """
        # Get current holdings
        # Use active_only=True since we only need current portfolio holdings
        all_instruments = self.storage.get_all_instruments(active_only=True)
        instrument_dict = {i['symbol']: i for i in all_instruments}
        
        # Calculate current weights based on market value
        total_value = 0.0
        symbol_values = {}
        
        for symbol in symbols:
            inst = instrument_dict.get(symbol, {})
            quantity = inst.get('quantity', 0)
            if quantity > 0:
                latest_prices = self.storage.get_latest_prices([symbol])
                price = latest_prices.get(symbol, {}).get('close', 0)
                symbol_values[symbol] = quantity * price
                total_value += symbol_values[symbol]
        
        if total_value == 0:
            return None  # No current holdings
        
        # Calculate weights matching returns_df column order
        weights = np.array([symbol_values.get(s, 0) / total_value for s in returns_df.columns])
        
        if weights.sum() == 0:
            return None
        
        # Calculate metrics
        return self._calculate_portfolio_metrics(weights, returns_df)
    
    def _calculate_instrument_recommendations(
        self, 
        current_symbols: List[str],
        candidate_symbols: List[str],
        returns_df: pd.DataFrame,
        optimal_metrics: PortfolioMetrics,
        optimization_mode: str
    ) -> List[Dict]:
        """Calculate recommendations for alternative instruments.
        
        Parameters:
            current_symbols: Current portfolio symbols
            candidate_symbols: Candidate symbols to evaluate
            returns_df: Historical returns data
            optimal_metrics: Optimal portfolio metrics
            optimization_mode: Type of optimization
            
        Returns:
            List of recommendation dictionaries sorted by improvement
        """
        recommendations = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years
        
        for candidate in candidate_symbols:
            try:
                # Fetch returns for candidate
                price_df = self.storage.get_price_data(candidate, start_date, end_date)
                if price_df is None or len(price_df) < 100:
                    continue
                
                candidate_returns = calculate_returns(price_df['close'])
                
                # Create augmented returns dataframe
                augmented_returns = returns_df.copy()
                augmented_returns[candidate] = candidate_returns
                augmented_returns = augmented_returns.dropna()
                
                if len(augmented_returns) < 50:
                    continue
                
                # Re-optimize with candidate included
                if optimization_mode == "Max Sharpe":
                    new_metrics = self._optimize_for_max_sharpe(augmented_returns)
                elif optimization_mode == "Target Return":
                    target_return = optimal_metrics.expected_return
                    new_metrics = self._optimize_for_target_return(augmented_returns, target_return)
                elif optimization_mode == "Max Diversification":
                    new_metrics = self._optimize_for_max_diversification(augmented_returns)
                elif optimization_mode == "Min Drawdown":
                    new_metrics = self._optimize_for_min_drawdown(augmented_returns)
                elif optimization_mode == "Mean-CVaR":
                    new_metrics = self._optimize_for_mean_cvar(augmented_returns)
                elif optimization_mode == "Max Income-Growth":
                    augmented_symbols = list(augmented_returns.columns)
                    new_metrics = self._optimize_for_income_growth(augmented_returns, augmented_symbols)
                else:
                    new_metrics = self._optimize_for_max_sharpe(augmented_returns)
                
                if new_metrics is None:
                    continue
                
                # Calculate improvement based on optimization mode
                if optimization_mode == "Max Income-Growth":
                    # For income-growth, use combined score of yield and return improvement
                    old_combined = optimal_metrics.expected_return + getattr(optimal_metrics, 'dividend_yield', 0)
                    new_combined = new_metrics.expected_return + getattr(new_metrics, 'dividend_yield', 0)
                    improvement = ((new_combined - old_combined) / abs(old_combined) * 100) if old_combined != 0 else 0
                    improvement_label = "Total Return + Yield"
                else:
                    # For other modes, use Sharpe improvement
                    improvement = ((new_metrics.sharpe_ratio - optimal_metrics.sharpe_ratio) / 
                                         abs(optimal_metrics.sharpe_ratio) * 100)
                    improvement_label = "Sharpe"
                
                # Only recommend if there's meaningful improvement
                if improvement > 1.0:  # At least 1% improvement
                    # Get candidate weight in new optimal portfolio
                    candidate_idx = list(augmented_returns.columns).index(candidate)
                    optimal_candidate_weight = new_metrics.weights[candidate_idx]
                    
                    # Calculate REALISTIC incremental weight (5-20% of portfolio)
                    # This is what you'd actually add, not replace everything with
                    min_realistic_weight = 0.05  # 5% minimum
                    max_realistic_weight = 0.20  # 20% maximum
                    candidate_weight = np.clip(optimal_candidate_weight, min_realistic_weight, max_realistic_weight)
                    
                    # Calculate average correlation with current portfolio
                    correlations = augmented_returns[[candidate]].corrwith(
                        augmented_returns[current_symbols]
                    )
                    # Get the mean correlation value, handling NaN
                    avg_correlation = correlations.iloc[0] if len(correlations) > 0 else 0.0
                    if pd.isna(avg_correlation):
                        avg_correlation = 0.0
                    
                    # Get instrument details
                    instrument = self.storage.get_instrument(candidate)
                    
                    # Generate rationale
                    rationale = self._generate_recommendation_rationale(
                        candidate, candidate_weight, avg_correlation, 
                        new_metrics, optimal_metrics, optimization_mode
                    )
                    
                    rec_dict = {
                        'symbol': candidate,
                        'name': instrument.get('name', candidate) if instrument else candidate,
                        'type': instrument.get('type', 'Unknown') if instrument else 'Unknown',
                        'improvement': improvement,
                        'improvement_label': improvement_label,
                        'new_sharpe': new_metrics.sharpe_ratio,
                        'new_return': new_metrics.expected_return,
                        'new_volatility': new_metrics.volatility,
                        'suggested_weight': candidate_weight,
                        'correlation': avg_correlation,
                        'rationale': rationale
                    }
                    
                    # Add dividend yield info for income-growth mode
                    if optimization_mode == "Max Income-Growth":
                        # Get candidate's dividend yield
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=365)
                        dividends = self.storage.get_dividends(candidate, start_date, end_date)
                        price_df = self.storage.get_price_data(candidate, start_date, end_date)
                        
                        if dividends and price_df is not None and not price_df.empty:
                            total_divs = sum(d['amount'] for d in dividends)
                            avg_price = price_df['close'].mean()
                            candidate_yield = (total_divs / avg_price) if avg_price > 0 else 0.0
                        else:
                            candidate_yield = 0.0
                        
                        rec_dict['dividend_yield'] = candidate_yield
                        rec_dict['new_portfolio_yield'] = getattr(new_metrics, 'dividend_yield', 0)
                    
                    recommendations.append(rec_dict)
                    
            except Exception as e:
                # Skip instruments that fail
                continue
        
        # Sort by improvement (descending)
        recommendations.sort(key=lambda x: x['improvement'], reverse=True)
        
        return recommendations
    
    def _generate_recommendation_rationale(
        self,
        symbol: str,
        weight: float,
        correlation: float,
        new_metrics: PortfolioMetrics,
        old_metrics: PortfolioMetrics,
        mode: str
    ) -> str:
        """Generate human-readable rationale for recommendation.
        
        Parameters:
            symbol: Candidate symbol
            weight: Suggested weight in portfolio
            correlation: Average correlation with current holdings
            new_metrics: Metrics with candidate
            old_metrics: Metrics without candidate
            mode: Optimization mode
            
        Returns:
            Rationale string
        """
        rationale_parts = []
        
        # Handle NaN correlation
        if pd.isna(correlation):
            correlation = 0.0
        
        # Correlation-based insights
        if abs(correlation) < 0.3:
            rationale_parts.append(f"Low correlation ({correlation:.2f}) provides excellent diversification benefits")
        elif abs(correlation) < 0.6:
            rationale_parts.append(f"Moderate correlation ({correlation:.2f}) offers good diversification")
        else:
            rationale_parts.append(f"High correlation ({correlation:.2f}) but strong individual performance")
        
        # Volatility impact
        vol_change = (new_metrics.volatility - old_metrics.volatility) / old_metrics.volatility * 100
        if vol_change < -2:
            rationale_parts.append(f"reduces portfolio volatility by {abs(vol_change):.1f}%")
        elif vol_change > 2:
            rationale_parts.append(f"increases volatility by {vol_change:.1f}% but with higher returns")
        
        # Return impact
        return_change = (new_metrics.expected_return - old_metrics.expected_return) / old_metrics.expected_return * 100
        if return_change > 2:
            rationale_parts.append(f"boosts expected returns by {return_change:.1f}%")
        
        # Weight recommendation
        if weight > 0.15:
            rationale_parts.append(f"recommended as core holding ({weight*100:.1f}% allocation)")
        elif weight > 0.05:
            rationale_parts.append(f"suggested as supporting position ({weight*100:.1f}% allocation)")
        else:
            rationale_parts.append(f"adds value in small allocation ({weight*100:.1f}%)")
        
        return ". ".join(rationale_parts) + "."
