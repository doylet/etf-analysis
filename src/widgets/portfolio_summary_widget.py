"""
Portfolio summary widget - shows risk-adjusted performance metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from .base_widget import BaseWidget
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


class PortfolioSummaryWidget(BaseWidget):
    """Widget showing overall portfolio performance metrics"""
    
    def get_name(self) -> str:
        return "Portfolio Summary"
    
    def get_description(self) -> str:
        return "Risk-adjusted performance metrics: Sharpe, Sortino, Omega ratios and IRR"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render portfolio summary with performance metrics"""
        with st.container(border=True):
            if not instruments:
                st.info("No instruments in portfolio")
                return
            
            # Get holdings with quantities > 0
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                st.info("No active positions. Add orders to see portfolio metrics.")
                return
            
            # Calculate portfolio value over time
            portfolio_values, total_value = self._calculate_portfolio_values(holdings)
            
            if portfolio_values.empty:
                st.warning("No price data available for performance calculation")
                return
            
            # Calculate returns
            returns = calculate_returns(portfolio_values)
            
            # Calculate cash flows for IRR
            cash_flows = self._get_cash_flows(holdings)
            
            # Calculate dividend metrics
            one_year_ago = datetime.now() - timedelta(days=365)
            dividends_received = self.storage.calculate_total_dividends_received(start_date=one_year_ago)
            
            # Calculate average portfolio value for dividend yield
            if not portfolio_values.empty:
                avg_portfolio_value = portfolio_values.mean()
                dividend_yield = calculate_dividend_yield(dividends_received, avg_portfolio_value)
            else:
                dividend_yield = 0.0
            
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
            
            # Risk Metrics
            st.markdown("**Risk-Adjusted Performance**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                sharpe = calculate_sharpe_ratio(returns)
                st.metric("Sharpe Ratio", f"{sharpe:.2f}", help="Return per unit of total risk")
            
            with col2:
                sortino = calculate_sortino_ratio(returns)
                st.metric("Sortino Ratio", f"{sortino:.2f}", help="Return per unit of downside risk")
            
            with col3:
                omega = calculate_omega_ratio(returns)
                omega_display = f"{omega:.2f}" if omega != np.inf else "∞"
                st.metric("Omega Ratio", omega_display, help="Probability-weighted gains vs losses")
            
            with col4:
                max_dd = calculate_max_drawdown(portfolio_values)
                st.metric("Max Drawdown", f"{max_dd*100:.1f}%", help="Largest peak-to-trough decline")
            
            
            
            # Returns and Value
            st.markdown("**Returns & Valuation**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Portfolio Value", f"${total_value:,.2f}")
            
            with col2:
                st.metric("Total Return (MWR)", f"{mwr*100:.1f}%", help="Money-weighted return (price only)")
            
            with col3:
                st.metric("Total Return (TWR)", f"{twr*100:.1f}%", help="Time-weighted return")
            
            with col4:
                if len(cash_flows) >= 2:
                    irr = calculate_irr(cash_flows)
                    st.metric("IRR (Annual)", f"{irr*100:.1f}%", help="Internal rate of return")
                else:
                    st.metric("IRR (Annual)", "N/A", help="Need at least 2 cash flows")
            
            
            
            # Dividend Metrics
            st.markdown("**Income**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Dividend Yield", f"{dividend_yield*100:.2f}%", help="Annual dividend income / portfolio value")
            
            with col2:
                st.metric("Total Return w/ Dividends", f"{total_return_with_divs*100:.1f}%", help="Price + dividend return")
    
    def _calculate_portfolio_values(self, holdings: List[Dict]) -> tuple:
        """Calculate portfolio value over time"""
        # Get 1 year of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # First calculate current value using latest prices
        symbols = [h['symbol'] for h in holdings]
        latest_prices = self.storage.get_latest_prices(symbols)
        
        current_value = 0.0
        for holding in holdings:
            symbol = holding['symbol']
            quantity = holding.get('quantity', 0)
            
            if quantity > 0 and symbol in latest_prices:
                price = latest_prices[symbol]['close']
                current_value += quantity * price
        
        # Collect price data for all holdings to create time series
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
            return pd.Series(), current_value
        
        # Sum across all positions to get total portfolio value time series
        portfolio_values = portfolio_df.sum(axis=1)
        
        return portfolio_values, current_value
    
    def _get_cash_flows(self, holdings: List[Dict]) -> List[tuple]:
        """Get cash flows for IRR calculation from orders"""
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
                    # Find closest date
                    closest_price = price_df.iloc[0]['close']
                    
                    # Cash flow: negative for buy (outflow), positive for sell (inflow)
                    cash_flow = -closest_price * volume if order_type == 'Buy' else closest_price * volume
                    cash_flows.append((order_date, cash_flow))
        
        # Add current portfolio value as final cash flow
        if holdings:
            symbols = [h['symbol'] for h in holdings]
            latest_prices = self.storage.get_latest_prices(symbols)
            
            current_value = 0
            for holding in holdings:
                symbol = holding['symbol']
                quantity = holding.get('quantity', 0)
                if symbol in latest_prices:
                    current_value += quantity * latest_prices[symbol]['close']
            
            if current_value > 0:
                cash_flows.append((datetime.now(), current_value))
        
        return cash_flows
