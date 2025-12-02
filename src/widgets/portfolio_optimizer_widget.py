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
            all_instruments = self.storage.get_all_instruments()
            
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
            
            st.divider()
            
            # Choose optimization mode
            mode = st.radio(
                "Optimization Mode:",
                options=["Custom Weights", "Efficient Frontier", "Target Return", 
                        "Max Diversification", "Min Drawdown", "Mean-CVaR"],
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
        all_instruments = self.storage.get_all_instruments()
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
            if st.button("Apply Max Sharpe", help="Optimize for maximum risk-adjusted returns", use_container_width=True):
                frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=50)
                if frontier:
                    # Store optimal weights in session state
                    for idx, symbol in enumerate(returns_df.columns):
                        weight_pct = round(frontier.max_sharpe_portfolio.weights[idx] * 100)
                        st.session_state[self._get_session_key(f"weight_{symbol}")] = float(weight_pct)
                    st.rerun()
        
        with col2:
            if st.button("Apply Min Volatility", help="Optimize for minimum risk", use_container_width=True):
                frontier = self._calculate_efficient_frontier(returns_df, num_portfolios=50)
                if frontier:
                    for idx, symbol in enumerate(returns_df.columns):
                        weight_pct = round(frontier.min_vol_portfolio.weights[idx] * 100)
                        st.session_state[self._get_session_key(f"weight_{symbol}")] = float(weight_pct)
                    st.rerun()
        
        with col3:
            if st.button("Equal Weights", help="Distribute evenly across all instruments", use_container_width=True):
                equal_weight = 100.0 / len(available_symbols)
                for symbol in available_symbols:
                    st.session_state[self._get_session_key(f"weight_{symbol}")] = round(equal_weight)
                st.rerun()
        
        st.divider()
        
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
        
        st.divider()
        
        # Plot efficient frontier
        self._render_efficient_frontier_chart(frontier, returns_df, available_symbols)
    
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
                st.metric("Dividend Yield", f"{portfolio_yield * 100:.3g}%",
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
            weights_df = pd.DataFrame({
                'Symbol': symbols,
                'Weight (%)': [f"{w * 100:.3g}" for w in metrics.weights]
            }).sort_values('Weight (%)', ascending=False, key=lambda x: x.str.replace('%', '').astype(float))
            
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
                    tickformat=".3g"
                ),
                line=dict(width=0.5, color='white')
            ),
            text=[f"<b>Portfolio</b><br>Return: {r:.3g}%<br>Volatility: {v:.3g}%<br>Sharpe: {s:.3g}" 
                  for r, v, s in zip(returns, volatilities, sharpes)],
            hovertemplate='%{text}<extra></extra>',
            name='Portfolio',
            showlegend=False
        ))
        
        # Add minimum volatility portfolio
        fig.add_trace(go.Scatter(
            x=[frontier.min_vol_portfolio.volatility * 100],
            y=[frontier.min_vol_portfolio.expected_return * 100],
            mode='markers+text',
            marker=dict(size=18, color='#00CC96', symbol='star', line=dict(width=2, color='white')),
            name='Min Volatility',
            text=['Min Vol'],
            textposition='top center',
            textfont=dict(size=10, color='#00CC96'),
            hovertemplate=f"<b>Min Volatility Portfolio</b><br>Return: {frontier.min_vol_portfolio.expected_return * 100:.3g}%<br>Volatility: {frontier.min_vol_portfolio.volatility * 100:.3g}%<br>Sharpe: {frontier.min_vol_portfolio.sharpe_ratio:.3g}<extra></extra>"
        ))
        
        # Add maximum Sharpe portfolio
        fig.add_trace(go.Scatter(
            x=[frontier.max_sharpe_portfolio.volatility * 100],
            y=[frontier.max_sharpe_portfolio.expected_return * 100],
            mode='markers+text',
            marker=dict(size=18, color='#EF553B', symbol='star', line=dict(width=2, color='white')),
            name='Max Sharpe',
            text=['Max Sharpe'],
            textposition='bottom center',
            textfont=dict(size=10, color='#EF553B'),
            hovertemplate=f"<b>Max Sharpe Portfolio</b><br>Return: {frontier.max_sharpe_portfolio.expected_return * 100:.3g}%<br>Volatility: {frontier.max_sharpe_portfolio.volatility * 100:.3g}%<br>Sharpe: {frontier.max_sharpe_portfolio.sharpe_ratio:.3g}<extra></extra>"
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
            hovertemplate='<b>%{text}</b><br>Return: %{y:.3g}%<br>Volatility: %{x:.3g}%<extra></extra>'
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
                yanchor="top",
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
