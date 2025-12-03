"""
Portfolio Transition Widget

Helps plan strategic transitions from current portfolio to target portfolio,
including new instruments and allocations. Shows what to buy/sell and in what order.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .base_widget import BaseWidget


class TransitionAction:
    """Represents a single buy/sell action in the transition plan."""
    def __init__(self, symbol: str, action: str, shares: float, value_aud: float, 
                 current_weight: float, target_weight: float, priority: int):
        self.symbol = symbol
        self.action = action  # "Buy", "Sell", "Hold"
        self.shares = shares
        self.value_aud = value_aud
        self.current_weight = current_weight
        self.target_weight = target_weight
        self.priority = priority  # Lower number = higher priority


class PortfolioTransitionWidget(BaseWidget):
    """Widget for planning portfolio transitions from current to target allocation."""
    
    def get_name(self) -> str:
        return "Portfolio Transition Planner"
    
    def get_description(self) -> str:
        return "Plan transitions from current to target portfolio with new instruments and allocations"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    def _get_session_key(self, key: str) -> str:
        """Generate unique session state key."""
        return f"{self.widget_id}_{key}"
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render the portfolio transition widget."""
        with st.container(border=True):
            st.markdown("""
            Plan your transition from current portfolio to a target allocation. 
            Specify new instruments, target weights, and get a prioritized action plan.
            """)
            
            # Get current portfolio
            if instruments is None:
                instruments = self.storage.get_all_instruments(active_only=True)
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                st.warning("No current holdings found. Add instruments to your portfolio first.")
                return
            
            # Calculate current portfolio value and weights
            current_portfolio = self._calculate_current_portfolio(holdings)
            total_value = current_portfolio['total_value']
            
            st.markdown(f"**Current Portfolio Value:** ${total_value:,.2f} AUD")
            
            # Two-column layout for current and target
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Current Portfolio")
                self._render_current_portfolio(current_portfolio)
            
            with col2:
                st.subheader("Target Portfolio")
                target_portfolio = self._render_target_portfolio_builder(instruments, total_value)
            
            # Transition Parameters
            st.subheader("Transition Parameters")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                transition_method = st.selectbox(
                    "Transition method:",
                    options=["Immediate (1 step)", "Gradual (Multiple steps)", "Custom phases"],
                    key=self._get_session_key("method"),
                    help="How quickly to transition to target allocation"
                )
            
            with col2:
                if transition_method != "Immediate (1 step)":
                    num_steps = st.number_input(
                        "Number of steps:",
                        min_value=2,
                        max_value=12,
                        value=4,
                        key=self._get_session_key("num_steps"),
                        help="How many rebalancing steps to use"
                    )
                else:
                    num_steps = 1
            
            with col3:
                transaction_cost_pct = st.number_input(
                    "Transaction cost (%):",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.1,
                    step=0.05,
                    key=self._get_session_key("transaction_cost"),
                    help="Estimated cost per transaction (brokerage + spreads)"
                )
            
            with col4:
                optimization_priority = st.selectbox(
                    "Optimization priority:",
                    options=["Minimize transactions", "Minimize cost", "Tax efficient", "Balanced"],
                    key=self._get_session_key("priority"),
                    help="What to optimize for in the transition plan"
                )
            
            # Calculate and display transition plan
            if st.button("Generate Transition Plan", type="primary", width="stretch"):
                if not target_portfolio:
                    st.error("Please specify at least one target instrument")
                    return
                
                # Validate target weights sum to 100%
                total_weight = sum(item['weight'] for item in target_portfolio)
                if abs(total_weight - 100.0) > 0.01:
                    st.error(f"Target weights must sum to 100% (currently {total_weight:.1f}%)")
                    return
                
                with st.spinner("Calculating optimal transition plan..."):
                    transition_plan = self._calculate_transition_plan(
                        current_portfolio,
                        target_portfolio,
                        num_steps,
                        transaction_cost_pct / 100,
                        optimization_priority
                    )
                
                # Store in session state
                st.session_state[self._get_session_key("plan")] = transition_plan
            
            # Display plan if available
            if self._get_session_key("plan") in st.session_state:
                plan = st.session_state[self._get_session_key("plan")]
                self._render_transition_plan(plan, num_steps, transaction_cost_pct / 100)
    
    def _calculate_current_portfolio(self, holdings: List[Dict]) -> Dict:
        """Calculate current portfolio metrics."""
        portfolio_data = []
        total_value = 0.0
        
        # Get latest prices
        symbols = [h['symbol'] for h in holdings]
        latest_prices = self.storage.get_latest_prices(symbols)
        
        for holding in holdings:
            symbol = holding['symbol']
            quantity = holding.get('quantity', 0)
            
            # Get current price
            price_data = latest_prices.get(symbol, {})
            current_price = price_data.get('close', holding.get('price', 0))
            
            value_aud = quantity * current_price
            total_value += value_aud
            
            portfolio_data.append({
                'symbol': symbol,
                'quantity': quantity,
                'price': current_price,
                'value': value_aud
            })
        
        # Calculate weights
        for item in portfolio_data:
            item['weight'] = (item['value'] / total_value * 100) if total_value > 0 else 0
        
        return {
            'data': portfolio_data,
            'total_value': total_value
        }
    
    def _render_current_portfolio(self, current_portfolio: Dict):
        """Display current portfolio breakdown."""
        df = pd.DataFrame(current_portfolio['data'])
        
        # Format for display
        display_df = df[['symbol', 'quantity', 'value', 'weight']].copy()
        display_df['value'] = display_df['value'].apply(lambda x: f"${x:,.2f}")
        display_df['weight'] = display_df['weight'].apply(lambda x: f"{x:.1f}%")
        display_df.columns = ['Symbol', 'Shares', 'Value (AUD)', 'Weight']
        
        st.dataframe(display_df, width="stretch", hide_index=True)
        
        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=df['symbol'],
            values=df['weight'],
            hole=0.3,
            textinfo='label+percent',
            textposition='auto'
        )])
        fig.update_layout(
            title="Current Allocation",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, width="stretch")
    
    def _render_target_portfolio_builder(self, instruments: List[Dict], total_value: float) -> List[Dict]:
        """Render UI for building target portfolio."""
        st.markdown("Define your target allocation:")
        
        # Quick load options
        col1, col2 = st.columns([3, 1])
        with col1:
            preset = st.selectbox(
                "Load preset:",
                options=["Custom", "Equal Weight Top 5", "60/40 Stocks/Bonds", "Risk Parity"],
                key=self._get_session_key("preset")
            )
        
        # Get available symbols
        all_symbols = sorted([i['symbol'] for i in instruments])
        
        # Number of target instruments
        num_targets = st.number_input(
            "Number of target instruments:",
            min_value=1,
            max_value=30,
            value=5,
            key=self._get_session_key("num_targets")
        )
        
        target_portfolio = []
        
        st.markdown("**Target Instruments & Weights:**")
        
        # Create input fields for each target
        for i in range(num_targets):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                symbol = st.selectbox(
                    f"Instrument {i+1}:",
                    options=all_symbols,
                    key=self._get_session_key(f"target_symbol_{i}"),
                    label_visibility="collapsed"
                )
            
            with col2:
                weight = st.number_input(
                    f"Weight {i+1}:",
                    min_value=0.0,
                    max_value=100.0,
                    value=100.0 / num_targets if i < num_targets else 0.0,
                    step=0.1,
                    format="%.1f",
                    key=self._get_session_key(f"target_weight_{i}"),
                    label_visibility="collapsed"
                )
            
            with col3:
                st.markdown(f"<div style='padding-top: 8px;'>{weight:.1f}%</div>", unsafe_allow_html=True)
            
            if symbol and weight > 0:
                target_portfolio.append({
                    'symbol': symbol,
                    'weight': weight,
                    'target_value': total_value * weight / 100
                })
        
        # Show total weight
        total_weight = sum(item['weight'] for item in target_portfolio)
        if abs(total_weight - 100.0) > 0.01:
            st.warning(f"⚠️ Total weight: {total_weight:.1f}% (should be 100%)")
        else:
            st.success(f"✓ Total weight: {total_weight:.1f}%")
        
        return target_portfolio
    
    def _calculate_transition_plan(
        self,
        current_portfolio: Dict,
        target_portfolio: List[Dict],
        num_steps: int,
        transaction_cost_pct: float,
        optimization_priority: str
    ) -> Dict:
        """Calculate optimal transition plan from current to target portfolio."""
        
        # Build complete picture of all instruments
        current_dict = {item['symbol']: item for item in current_portfolio['data']}
        target_dict = {item['symbol']: item for item in target_portfolio}
        
        all_symbols = set(list(current_dict.keys()) + list(target_dict.keys()))
        total_value = current_portfolio['total_value']
        
        # Calculate differences
        actions = []
        for symbol in all_symbols:
            current_value = current_dict.get(symbol, {}).get('value', 0)
            current_weight = current_dict.get(symbol, {}).get('weight', 0)
            current_quantity = current_dict.get(symbol, {}).get('quantity', 0)
            
            target_value = target_dict.get(symbol, {}).get('target_value', 0)
            target_weight = target_dict.get(symbol, {}).get('weight', 0)
            
            value_diff = target_value - current_value
            
            if abs(value_diff) > 1.0:  # Only if difference > $1
                if value_diff > 0:
                    action = "Buy"
                    priority = self._calculate_priority(
                        symbol, "Buy", value_diff, current_weight, target_weight, optimization_priority
                    )
                else:
                    action = "Sell"
                    priority = self._calculate_priority(
                        symbol, "Sell", abs(value_diff), current_weight, target_weight, optimization_priority
                    )
                
                # Get current price for share calculation
                current_price = current_dict.get(symbol, {}).get('price', 0)
                if current_price == 0:
                    # Need to fetch price for new instruments
                    latest_prices = self.storage.get_latest_prices([symbol])
                    current_price = latest_prices.get(symbol, {}).get('close', 0)
                
                shares = abs(value_diff) / current_price if current_price > 0 else 0
                
                actions.append(TransitionAction(
                    symbol=symbol,
                    action=action,
                    shares=shares,
                    value_aud=abs(value_diff),
                    current_weight=current_weight,
                    target_weight=target_weight,
                    priority=priority
                ))
        
        # Sort by priority
        actions.sort(key=lambda x: x.priority)
        
        # Create step-by-step plan
        if num_steps == 1:
            steps = [actions]
        else:
            steps = self._split_into_steps(actions, num_steps, optimization_priority)
        
        # Calculate costs and metrics
        total_transaction_value = sum(action.value_aud for action in actions)
        total_cost = total_transaction_value * transaction_cost_pct
        num_transactions = len(actions)
        
        return {
            'steps': steps,
            'total_value': total_value,
            'total_transaction_value': total_transaction_value,
            'total_cost': total_cost,
            'num_transactions': num_transactions,
            'current_portfolio': current_portfolio,
            'target_portfolio': target_portfolio
        }
    
    def _calculate_priority(
        self,
        symbol: str,
        action: str,
        value: float,
        current_weight: float,
        target_weight: float,
        optimization_priority: str
    ) -> int:
        """Calculate priority score for an action (lower = higher priority)."""
        
        weight_diff = abs(target_weight - current_weight)
        
        if optimization_priority == "Minimize transactions":
            # Prioritize largest changes first
            return int(1000 - value)
        
        elif optimization_priority == "Minimize cost":
            # Prioritize sells before buys (free up cash)
            if action == "Sell":
                return int(1000 - value)
            else:
                return int(2000 - value)
        
        elif optimization_priority == "Tax efficient":
            # Prioritize sells with losses, delay gains
            # For now, prioritize sells before buys
            if action == "Sell":
                return int(1000 - value)
            else:
                return int(2000 - value)
        
        else:  # Balanced
            # Mix of value and weight difference
            score = weight_diff * 100 + (value / 1000)
            return int(1000 - score)
    
    def _split_into_steps(
        self,
        actions: List[TransitionAction],
        num_steps: int,
        optimization_priority: str
    ) -> List[List[TransitionAction]]:
        """Split actions into multiple steps."""
        
        if optimization_priority == "Minimize cost":
            # All sells first, then buys
            sells = [a for a in actions if a.action == "Sell"]
            buys = [a for a in actions if a.action == "Buy"]
            
            # Distribute sells and buys across steps
            step_size = max(1, len(actions) // num_steps)
            steps = []
            
            for i in range(num_steps):
                step = []
                start_idx = i * step_size
                end_idx = start_idx + step_size if i < num_steps - 1 else len(actions)
                
                # Add sells first
                for sell in sells[start_idx:min(end_idx, len(sells))]:
                    step.append(sell)
                
                # Then buys
                buy_start = max(0, start_idx - len(sells))
                buy_end = max(0, end_idx - len(sells))
                for buy in buys[buy_start:buy_end]:
                    step.append(buy)
                
                if step:
                    steps.append(step)
            
            return steps
        
        else:
            # Evenly distribute actions
            step_size = max(1, len(actions) // num_steps)
            steps = []
            
            for i in range(num_steps):
                start_idx = i * step_size
                end_idx = start_idx + step_size if i < num_steps - 1 else len(actions)
                step = actions[start_idx:end_idx]
                if step:
                    steps.append(step)
            
            return steps
    
    def _render_transition_plan(self, plan: Dict, num_steps: int, transaction_cost_pct: float):
        """Display the complete transition plan."""
        st.subheader("Transition Plan")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Transactions",
                f"{plan['num_transactions']}"
            )
        
        with col2:
            st.metric(
                "Transaction Volume",
                f"${plan['total_transaction_value']:,.0f}"
            )
        
        with col3:
            st.metric(
                "Estimated Costs",
                f"${plan['total_cost']:,.2f}",
                delta=f"{transaction_cost_pct * 100:.2f}%"
            )
        
        with col4:
            st.metric(
                "Number of Steps",
                f"{num_steps}"
            )
        
        # Step-by-step actions
        st.markdown("### Action Plan")
        
        for step_idx, step_actions in enumerate(plan['steps'], 1):
            with st.expander(f"**Step {step_idx} of {num_steps}** ({len(step_actions)} actions)", expanded=(step_idx == 1)):
                
                # Create DataFrame for this step
                step_data = []
                for action in step_actions:
                    step_data.append({
                        'Symbol': action.symbol,
                        'Action': action.action,
                        'Shares': f"{action.shares:.2f}",
                        'Value (AUD)': f"${action.value_aud:,.2f}",
                        'Current Weight': f"{action.current_weight:.1f}%",
                        'Target Weight': f"{action.target_weight:.1f}%",
                        'Change': f"{action.target_weight - action.current_weight:+.1f}%"
                    })
                
                df = pd.DataFrame(step_data)
                
                # Color-code action column
                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Action": st.column_config.TextColumn(
                            "Action",
                            help="Buy or Sell"
                        )
                    }
                )
                
                # Step summary
                step_value = sum(action.value_aud for action in step_actions)
                step_cost = step_value * transaction_cost_pct
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Step {step_idx} Volume:** ${step_value:,.2f}")
                with col2:
                    st.markdown(f"**Step {step_idx} Cost:** ${step_cost:,.2f}")
        
        # Visualization
        st.markdown("### Transition Visualization")
        self._render_transition_chart(plan)
        
        # Export options
        st.markdown("### Export Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Copy to Clipboard", width="stretch"):
                clipboard_text = self._generate_clipboard_text(plan)
                st.code(clipboard_text, language=None)
        
        with col2:
            csv_data = self._generate_csv_export(plan)
            st.download_button(
                "Download CSV",
                data=csv_data,
                file_name=f"transition_plan_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width="stretch"
            )
    
    def _render_transition_chart(self, plan: Dict):
        """Create visualization showing current vs target allocation."""
        
        # Prepare data
        current_data = plan['current_portfolio']['data']
        target_data = plan['target_portfolio']
        
        # Get all symbols
        all_symbols = set([item['symbol'] for item in current_data] + 
                         [item['symbol'] for item in target_data])
        
        symbols = sorted(list(all_symbols))
        current_weights = []
        target_weights = []
        
        current_dict = {item['symbol']: item['weight'] for item in current_data}
        target_dict = {item['symbol']: item['weight'] for item in target_data}
        
        for symbol in symbols:
            current_weights.append(current_dict.get(symbol, 0))
            target_weights.append(target_dict.get(symbol, 0))
        
        # Create grouped bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Current',
            x=symbols,
            y=current_weights,
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Target',
            x=symbols,
            y=target_weights,
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title="Current vs Target Allocation",
            xaxis_title="Instrument",
            yaxis_title="Weight (%)",
            barmode='group',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width="stretch")
    
    def _generate_clipboard_text(self, plan: Dict) -> str:
        """Generate text for clipboard copy."""
        lines = ["PORTFOLIO TRANSITION PLAN", "=" * 50, ""]
        
        for step_idx, step_actions in enumerate(plan['steps'], 1):
            lines.append(f"STEP {step_idx}:")
            lines.append("-" * 30)
            
            for action in step_actions:
                lines.append(
                    f"{action.action.upper():6} {action.shares:8.2f} shares of {action.symbol:6} "
                    f"(${action.value_aud:,.2f}) | {action.current_weight:.1f}% → {action.target_weight:.1f}%"
                )
            
            lines.append("")
        
        lines.append(f"Total Transactions: {plan['num_transactions']}")
        lines.append(f"Total Volume: ${plan['total_transaction_value']:,.2f}")
        lines.append(f"Estimated Costs: ${plan['total_cost']:,.2f}")
        
        return "\n".join(lines)
    
    def _generate_csv_export(self, plan: Dict) -> str:
        """Generate CSV for download."""
        lines = ["Step,Symbol,Action,Shares,Value_AUD,Current_Weight_%,Target_Weight_%,Change_%"]
        
        for step_idx, step_actions in enumerate(plan['steps'], 1):
            for action in step_actions:
                change = action.target_weight - action.current_weight
                lines.append(
                    f"{step_idx},{action.symbol},{action.action},{action.shares:.2f},"
                    f"{action.value_aud:.2f},{action.current_weight:.1f},"
                    f"{action.target_weight:.1f},{change:+.1f}"
                )
        
        return "\n".join(lines)
