"""
Portfolio summary widget - shows risk-adjusted performance metrics.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Data fetching and validation (_fetch_*, _prepare_* methods)
- Logic Layer: Pure calculations (_calculate_* static methods)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .layered_base_widget import LayeredBaseWidget
from src.utils.performance_metrics import (
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_omega_ratio,
    calculate_irr,
    calculate_max_drawdown,
    calculate_money_weighted_return,
    calculate_time_weighted_return,
    calculate_dividend_yield,
    calculate_total_return_with_dividends
)


@dataclass
class PortfolioMetrics:
    """Complete portfolio performance metrics."""
    sharpe: float
    sortino: float
    omega: float
    max_dd: float
    total_value: float
    mwr: float
    twr: float
    irr: float
    dividend_yield: float
    total_return_with_divs: float
    has_irr: bool
    portfolio_values: pd.Series = None  # For charting


class PortfolioSummaryWidget(LayeredBaseWidget):
    """Widget showing overall portfolio performance metrics"""
    
    def get_name(self) -> str:
        return "Portfolio Summary"
    
    def get_description(self) -> str:
        return "Risk-adjusted performance metrics: Sharpe, Sortino, Omega ratios and IRR"
    
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
                st.info("No active positions. Add orders to see portfolio metrics.")
                return
            
            # Calculate all metrics
            metrics = self._calculate_all_metrics(holdings)
            
            if metrics is None:
                st.warning("No price data available for performance calculation")
                return
            
            # Render metrics sections
            self._render_risk_metrics(metrics)
            st.space("small")
            self._render_return_metrics(metrics)
            st.space("small")
            self._render_income_metrics(metrics)
            
            # Render charts if we have portfolio values
            if metrics.portfolio_values is not None and len(metrics.portfolio_values) > 0:
                st.space("small")
                self._render_portfolio_chart(metrics.portfolio_values)
    
    def _render_risk_metrics(self, metrics: PortfolioMetrics):
        """Render risk-adjusted performance metrics.
        
        Parameters:
            metrics: Portfolio metrics object
        """
        st.markdown("**Risk-Adjusted Performance**")
        st.caption("Based on actual portfolio value changes including transactions, cash flows, and rebalancing")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Sharpe Ratio", f"{metrics.sharpe:.2f}", help="Return per unit of total risk (actual portfolio performance)")
        
        with col2:
            st.metric("Sortino Ratio", f"{metrics.sortino:.2f}", help="Return per unit of downside risk")
        
        with col3:
            omega_display = f"{metrics.omega:.2f}" if metrics.omega != np.inf else "∞"
            st.metric("Omega Ratio", omega_display, help="Probability-weighted gains vs losses")
        
        with col4:
            st.metric("Max Drawdown", f"{metrics.max_dd*100:.1f}%", help="Largest peak-to-trough decline")
    
    def _render_return_metrics(self, metrics: PortfolioMetrics):
        """Render return and valuation metrics.
        
        Parameters:
            metrics: Portfolio metrics object
        """
        st.markdown("**Returns & Valuation**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Portfolio Value", f"${metrics.total_value:,.2f}")
        
        with col2:
            st.metric("Total Return (MWR)", f"{metrics.mwr*100:.1f}%", help="Money-weighted return (price only)")
        
        with col3:
            st.metric("Total Return (TWR)", f"{metrics.twr*100:.1f}%", help="Time-weighted return")
        
        with col4:
            if metrics.has_irr:
                st.metric("IRR (Annual)", f"{metrics.irr*100:.1f}%", help="Internal rate of return")
            else:
                st.metric("IRR (Annual)", "N/A", help="Need at least 2 cash flows")
    
    def _render_income_metrics(self, metrics: PortfolioMetrics):
        """Render dividend and income metrics.
        
        Parameters:
            metrics: Portfolio metrics object
        """
        st.markdown("**Income**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Dividend Yield", f"{metrics.dividend_yield*100:.2f}%", help="Annual dividend income / portfolio value")
        
        with col2:
            st.metric("Total Return w/ Dividends", f"{metrics.total_return_with_divs*100:.1f}%", help="Price + dividend return")
    
    def _render_portfolio_chart(self, portfolio_values: pd.Series):
        """Render portfolio value and drawdown charts.
        
        Parameters:
            portfolio_values: Portfolio values over time
        """
        st.markdown("**Portfolio Value Over Time**")
        
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Add portfolio value line
        fig.add_trace(go.Scatter(
            x=portfolio_values.index,
            y=portfolio_values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#636EFA', width=2.5),
            hovertemplate='<b>Portfolio Value</b><br>Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>',
            fill='tozeroy',
            fillcolor='rgba(99, 110, 250, 0.1)'
        ))
        
        # Calculate drawdown
        running_max = portfolio_values.cummax()
        drawdown = (portfolio_values - running_max) / running_max * 100
        
        # Add drawdown as secondary trace
        fig.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown,
            mode='lines',
            name='Drawdown',
            line=dict(color='#EF553B', width=2, dash='dot'),
            hovertemplate='<b>Drawdown</b><br>Date: %{x}<br>Drawdown: %{y:.2f}%<extra></extra>',
            yaxis='y2',
            fill='tozeroy',
            fillcolor='rgba(239, 85, 59, 0.1)'
        ))
        
        # Update layout with dual y-axes
        fig.update_layout(
            xaxis=dict(
                title="Date",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128, 128, 128, 0.2)'
            ),
            yaxis=dict(
                title="Portfolio Value ($)",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128, 128, 128, 0.2)',
                tickformat="$,.0f"
            ),
            yaxis2=dict(
                title="Drawdown (%)",
                overlaying='y',
                side='right',
                showgrid=False,
                tickformat=".1f",
                range=[drawdown.min() * 1.2, 5]  # Ensure negative values show properly
            ),
            hovermode='x unified',
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
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    # ========================================================================
    # DATA LAYER - Data fetching and validation methods
    # ========================================================================
    
    def _calculate_all_metrics(self, holdings: List[Dict]) -> PortfolioMetrics:
        """Calculate all portfolio performance metrics.
        
        Parameters:
            holdings: List of holding dictionaries
            
        Returns:
            PortfolioMetrics: All calculated metrics, or None if no data
        """
        # Calculate portfolio value over time
        portfolio_values, total_value = self._fetch_portfolio_values(holdings)
        
        if portfolio_values.empty:
            return None
        
        # Calculate returns
        returns = calculate_returns(portfolio_values)
        
        # Calculate cash flows for IRR
        cash_flows = self._fetch_cash_flows(holdings)
        
        # Calculate dividend metrics
        one_year_ago = datetime.now() - timedelta(days=365)
        dividends_received = self.storage.calculate_total_dividends_received(start_date=one_year_ago)
        
        avg_portfolio_value = portfolio_values.mean()
        dividend_yield = calculate_dividend_yield(dividends_received, avg_portfolio_value)
        
        # Calculate returns (money-weighted and time-weighted)
        cash_flows_without_current = [(date, amt) for date, amt in cash_flows if date != cash_flows[-1][0]]
        mwr = calculate_money_weighted_return(cash_flows_without_current, total_value)
        
        # Get cash flow dates for time-weighted return
        cash_flow_dates = [date for date, _ in cash_flows_without_current]
        twr = calculate_time_weighted_return(portfolio_values, cash_flow_dates)
        
        # Calculate total return including dividends
        total_invested = sum(abs(cf) for _, cf in cash_flows_without_current if cf < 0)
        if total_invested > 0:
            dividend_return = dividends_received / total_invested
            total_return_with_divs = calculate_total_return_with_dividends(mwr, dividend_return)
        else:
            total_return_with_divs = mwr
        
        # Calculate risk metrics
        sharpe = calculate_sharpe_ratio(returns)
        sortino = calculate_sortino_ratio(returns)
        omega = calculate_omega_ratio(returns)
        max_dd = calculate_max_drawdown(portfolio_values)
        
        # Calculate IRR if enough cash flows
        has_irr = len(cash_flows) >= 2
        irr = calculate_irr(cash_flows) if has_irr else 0.0
        
        return PortfolioMetrics(
            sharpe=sharpe,
            sortino=sortino,
            omega=omega,
            max_dd=max_dd,
            total_value=total_value,
            mwr=mwr,
            twr=twr,
            irr=irr,
            dividend_yield=dividend_yield,
            total_return_with_divs=total_return_with_divs,
            has_irr=has_irr,
            portfolio_values=portfolio_values
        )
    
    def _fetch_portfolio_values(self, holdings: List[Dict]) -> Tuple[pd.Series, float]:
        """Fetch price data and calculate portfolio values over time.
        
        Parameters:
            holdings: List of holding dictionaries (pre-enriched with currency conversion)
            
        Returns:
            Tuple[pd.Series, float]: (portfolio_values_series, current_total_value)
        """
        # Get 1 year of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Use pre-calculated values from enriched instrument data
        current_value = sum(h.get('value_base', 0) for h in holdings if h.get('quantity', 0) > 0)
        
        # Collect price data for all holdings to create time series
        # Note: get_price_data automatically converts to base currency (AUD)
        portfolio_df = None
        
        for holding in holdings:
            symbol = holding['symbol']
            quantity = holding.get('quantity', 0)
            
            if quantity <= 0:
                continue
            
            # Price data is automatically converted to AUD by storage layer
            price_df = self.storage.get_price_data(symbol, start_date, end_date)
            
            if price_df is None or price_df.empty:
                continue
            
            # Calculate position value (prices already in AUD)
            position_values = price_df['close'] * quantity
            
            if portfolio_df is None:
                portfolio_df = pd.DataFrame(position_values, columns=[symbol])
            else:
                portfolio_df[symbol] = position_values
        
        if portfolio_df is None or portfolio_df.empty:
            return pd.Series(), current_value
        
        # Forward-fill prices on holidays (when one market closed, use previous price)
        # This prevents artificial drawdowns on days when some markets are closed
        portfolio_df = portfolio_df.ffill().infer_objects(copy=False)
        
        # Sum across all positions to get total portfolio value time series
        portfolio_values = portfolio_df.sum(axis=1)
        
        return portfolio_values, current_value
    
    def _fetch_cash_flows(self, holdings: List[Dict]) -> List[Tuple[datetime, float]]:
        """Fetch cash flows for IRR calculation from orders.
        
        Parameters:
            holdings: List of holding dictionaries
            
        Returns:
            List[Tuple[datetime, float]]: List of (date, cash_flow) tuples
        """
        cash_flows = []
        
        for holding in holdings:
            symbol = holding['symbol']
            orders = self.storage.get_orders(symbol)
            
            for order in orders:
                if order.get('is_active', 1) == 0:
                    continue
                
                # Get price at order date
                order_date = order['order_date']
                order_type = order['order_type']
                volume = order['volume']
                
                # Try to get price from database
                price_df = self.storage.get_price_data(
                    symbol,
                    order_date - timedelta(days=5),
                    order_date + timedelta(days=5)
                )
                
                if price_df is not None and not price_df.empty:
                    # Find closest date - use first available close price
                    close_prices = price_df['close'].dropna()
                    if len(close_prices) > 0:
                        closest_price = close_prices.iloc[0]
                        
                        # Cash flow: negative for buy (outflow), positive for sell (inflow)
                        cash_flow = -closest_price * volume if order_type == 'Buy' else closest_price * volume
                        
                        # Only add if cash flow is valid (not NaN)
                        if pd.notna(cash_flow):
                            cash_flows.append((order_date, cash_flow))
        
        # Add current portfolio value as final cash flow (use value_base from enriched holdings)
        if holdings:
            current_value = sum(h.get('value_base', h.get('value', 0)) for h in holdings)
            
            if current_value > 0:
                cash_flows.append((datetime.now(), current_value))
        
        return cash_flows
