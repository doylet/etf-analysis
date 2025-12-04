"""
Monte Carlo simulation widget - forecast future portfolio scenarios.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Historical data fetching and parameter estimation
- Logic Layer: Monte Carlo simulation engine (_run_* static methods)
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import plotly.graph_objects as go
from scipy.optimize import minimize

from .layered_base_widget import LayeredBaseWidget
from src.utils.performance_metrics import calculate_returns
from config.settings import USE_NEW_SERVICE_LAYER

# Conditional import of compatibility bridge
if USE_NEW_SERVICE_LAYER:
    from src.compat.streamlit_bridge import StreamlitServiceBridge


@dataclass
class RebalancingRecommendation:
    """Recommendation for portfolio rebalancing timing."""
    rebalance_dates: List[datetime]  # Recommended rebalancing dates
    drift_at_rebalance: List[float]  # Weight drift at each rebalancing point
    trigger_threshold: float  # Drift threshold that triggered rebalancing
    avg_drift: float  # Average drift between rebalances
    cost_benefit_ratio: float  # Expected benefit vs transaction cost
    sharpe_improvement: float  # Expected Sharpe ratio improvement
    description: str  # Human-readable recommendation
    # Per-instrument details
    instruments_to_rebalance: List[Dict[str, any]]  # List of dicts with {date, symbol, current_weight, target_weight, drift, action}
    symbols: List[str]  # Instrument symbols for reference


@dataclass
class SimulationResults:
    """Results from Monte Carlo simulation."""
    paths: np.ndarray  # All simulation paths (num_sims x num_steps)
    time_points: np.ndarray  # Time axis in years
    percentiles: Dict[int, np.ndarray]  # Percentile bands over time
    final_values: np.ndarray  # Final portfolio values for all simulations
    num_sims: int
    initial_value: float
    paths_below_initial: int
    percentile_10: float
    percentile_50: float
    percentile_90: float
    # Additional professional metrics
    var_95: float  # Value at Risk at 95% confidence
    cvar_95: float  # Conditional VaR (Expected Shortfall)
    max_drawdown_median: float  # Maximum drawdown in median path
    cagr_median: float  # Compound Annual Growth Rate (median)
    cagr_10th: float  # CAGR at 10th percentile
    cagr_90th: float  # CAGR at 90th percentile
    historical_sharpe: float  # Historical Sharpe ratio of portfolio
    historical_volatility: float  # Historical annualized volatility
    rebalancing_rec: Optional[RebalancingRecommendation] = None  # Rebalancing recommendations


class MonteCarloWidget(LayeredBaseWidget):
    """Widget for Monte Carlo portfolio simulations"""
    
    def get_name(self) -> str:
        return "Monte Carlo Simulation"
    
    def get_description(self) -> str:
        return "Simulate future portfolio scenarios using Monte Carlo methods to understand potential outcomes and risk"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    # ========================================================================
    # UI LAYER - Streamlit rendering methods
    # ========================================================================
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Main render orchestration - UI only.
        
        Parameters:
            instruments: List of instrument dictionaries
            selected_symbols: Optional list of pre-selected symbols
        """
        with st.container(border=True):
            if not instruments:
                st.info("No instruments available")
                return
            
            # Get all instruments (including those not in portfolio)
            # Use active_only=False to include ALL instruments for selection
            all_instruments = self.storage.get_all_instruments(active_only=False)
            
            if not all_instruments:
                st.info("No instruments available for simulation")
                return
            
            # 1. Portfolio Selection
            selected_symbols, weights = self._render_portfolio_selector(all_instruments)
            
            if len(selected_symbols) < 1:
                st.info("Please select at least 1 instrument to simulate")
                return
            
            # 2. Portfolio Statistics
            with st.expander("Portfolio Historical Statistics", expanded=False):
                self._render_portfolio_statistics(selected_symbols, weights)
            
            # 3. Simulation Parameters
            sim_params = self._render_simulation_parameters()
            
            # 4. Run Simulation Button
            if st.button("Run Monte Carlo Simulation", type="primary", width="stretch"):
                # Fetch historical data
                returns_df = self._fetch_returns_data(
                    selected_symbols, 
                    days=730,  # 2 years of history
                    include_dividends=sim_params['include_dividends']
                )
                
                if returns_df is None or returns_df.empty:
                    st.error("Insufficient historical data for simulation")
                    return
                
                # Run simulation (use new service layer if feature flag enabled)
                with st.spinner(f"Running {sim_params['num_sims']:,} simulations..."):
                    if USE_NEW_SERVICE_LAYER:
                        # Use new service layer via compatibility bridge
                        bridge = StreamlitServiceBridge(self.storage)
                        results_dict = bridge.run_monte_carlo_compat(
                            symbols=selected_symbols,
                            weights=weights,
                            returns_df=returns_df,
                            **sim_params
                        )
                        # Convert dict back to SimulationResults dataclass for rendering
                        results = self._dict_to_simulation_results(results_dict)
                    else:
                        # Use original implementation
                        results = self._run_monte_carlo(
                            symbols=selected_symbols,
                            weights=weights,
                            returns_df=returns_df,
                            **sim_params
                        )
                
                # Add weights dict to params for display purposes
                sim_params['weights'] = {symbol: weight for symbol, weight in zip(selected_symbols, weights)}
                
                # Display results
                self._render_simulation_results(results, sim_params)
    
    def _render_portfolio_selector(self, instruments: List[Dict]) -> tuple:
        """Render portfolio selection and weight inputs.
        
        Returns:
            Tuple[List[str], np.ndarray]: (selected_symbols, weights)
        """
        st.markdown("**Select Portfolio:**")
        
        # Separate portfolio holdings from other instruments
        portfolio_holdings = sorted([i['symbol'] for i in instruments if i.get('quantity', 0) > 0])
        other_instruments = sorted([i['symbol'] for i in instruments if i.get('quantity', 0) == 0])
        symbol_options = portfolio_holdings + other_instruments
        
        # Default to portfolio holdings
        default_symbols = portfolio_holdings[:5] if portfolio_holdings else symbol_options[:5]
        
        selected_symbols = st.multiselect(
            "Instruments:",
            options=symbol_options,
            default=default_symbols,
            key=self._get_session_key("instruments")
        )
        
        if not selected_symbols:
            return [], np.array([])
        
        # Weight allocation
        st.markdown("**Portfolio Weights:**")
        
        weight_method = st.selectbox(
            "Weight allocation method:",
            options=["Equal Weights", "Max Sharpe Ratio", "Min Volatility", "Current Portfolio", "Custom"],
            key=self._get_session_key("weight_method"),
            help="Method for determining portfolio weights"
        )
        
        weights = {}
        
        if weight_method == "Equal Weights":
            weight_value = 100.0 / len(selected_symbols)
            for symbol in selected_symbols:
                weights[symbol] = weight_value
            st.caption(f"Each instrument: {weight_value:.1f}%")
        
        elif weight_method == "Current Portfolio":
            # Get current holdings and calculate weights
            # Use the same calculation as holdings breakdown widget for consistency
            instrument_dict = {i['symbol']: i for i in instruments}
            
            # Calculate TOTAL portfolio value (all holdings, not just selected)
            total_portfolio_value = 0.0
            for inst in instruments:
                quantity = inst.get('quantity', 0)
                if quantity > 0:
                    value_aud = inst.get('value_local', 0)
                    if value_aud > 0:
                        total_portfolio_value += value_aud
                    else:
                        # Fallback: calculate from latest price if value not available
                        latest_prices = self.storage.get_latest_prices([inst['symbol']])
                        price = latest_prices.get(inst['symbol'], {}).get('close', 0)
                        total_portfolio_value += quantity * price
            
            # Calculate weights for selected symbols as % of TOTAL portfolio
            symbol_values = {}
            for symbol in selected_symbols:
                inst = instrument_dict.get(symbol, {})
                quantity = inst.get('quantity', 0)
                if quantity > 0:
                    value_aud = inst.get('value_local', 0)
                    if value_aud > 0:
                        symbol_values[symbol] = value_aud
                    else:
                        # Fallback: calculate from latest price if value not available
                        latest_prices = self.storage.get_latest_prices([symbol])
                        price = latest_prices.get(symbol, {}).get('close', 0)
                        symbol_values[symbol] = quantity * price
            
            if total_portfolio_value > 0:
                for symbol in selected_symbols:
                    weights[symbol] = (symbol_values.get(symbol, 0) / total_portfolio_value) * 100
                st.caption("Using current portfolio allocation (% of total portfolio value)")
            else:
                st.warning("No current holdings found. Using equal weights.")
                weight_value = 100.0 / len(selected_symbols)
                for symbol in selected_symbols:
                    weights[symbol] = weight_value
        
        elif weight_method in ["Max Sharpe Ratio", "Min Volatility"]:
            # Fetch returns for optimization
            with st.spinner(f"Calculating optimal weights..."):
                returns_df = self._fetch_returns_data(selected_symbols, days=730, include_dividends=True)
                
                if returns_df is None or returns_df.empty:
                    st.warning("Insufficient data for optimization. Using equal weights.")
                    weight_value = 100.0 / len(selected_symbols)
                    for symbol in selected_symbols:
                        weights[symbol] = weight_value
                else:
                    optimal_weights = self._calculate_optimal_weights(returns_df, weight_method)
                    
                    if optimal_weights is not None:
                        for idx, symbol in enumerate(selected_symbols):
                            weights[symbol] = optimal_weights[idx] * 100
                        st.caption(f"Optimized for {weight_method}")
                    else:
                        st.warning("Optimization failed. Using equal weights.")
                        weight_value = 100.0 / len(selected_symbols)
                        for symbol in selected_symbols:
                            weights[symbol] = weight_value
        
        else:  # Custom
            cols = st.columns(min(3, len(selected_symbols)))
            for idx, symbol in enumerate(selected_symbols):
                col = cols[idx % len(cols)]
                with col:
                    weights[symbol] = st.number_input(
                        f"{symbol} %",
                        min_value=0.0,
                        max_value=100.0,
                        value=100.0 / len(selected_symbols),
                        step=1.0,
                        key=self._get_session_key(f"weight_{symbol}")
                    )
            
            total = sum(weights.values())
            if abs(total - 100.0) > 0.01:
                st.error(f"Weights sum to {total:.1f}%. Must equal 100%")
                return [], np.array([])
        
        # Convert to array
        weight_array = np.array([weights[s] / 100.0 for s in selected_symbols])
        
        # Display weight allocation as a bar chart for visual confirmation
        if weight_method != "Custom":
            with st.expander("View Weight Allocation", expanded=False):
                weight_df = pd.DataFrame({
                    'Symbol': selected_symbols,
                    'Weight (%)': [weights[s] for s in selected_symbols]
                }).sort_values('Weight (%)', ascending=False)
                
                st.dataframe(weight_df, hide_index=True, width="stretch")
        
        return selected_symbols, weight_array
    
    def _render_simulation_parameters(self) -> Dict:
        """Render simulation parameter inputs.
        
        Returns:
            Dict: Simulation parameters
        """
        st.markdown("**Simulation Parameters:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            num_sims = st.slider(
                "Number of simulations",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100,
                key=self._get_session_key("num_sims"),
                help="More simulations = more accurate but slower"
            )
        
        with col2:
            years = st.slider(
                "Time horizon (years)",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
                key=self._get_session_key("years")
            )
        
        with col3:
            initial_value = st.number_input(
                "Initial portfolio value ($)",
                min_value=1000.0,
                max_value=10000000.0,
                value=100000.0,
                step=10000.0,
                key=self._get_session_key("initial_value")
            )
        
        # Advanced options
        with st.expander("Advanced Settings"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                include_dividends = st.toggle(
                    "Include dividends",
                    value=True,
                    key=self._get_session_key("include_dividends"),
                    help="Add dividend yield to expected returns"
                )
            
            with col2:
                confidence_level = st.slider(
                    "Confidence level (%)",
                    min_value=80,
                    max_value=99,
                    value=90,
                    step=1,
                    key=self._get_session_key("confidence"),
                    help="Confidence interval for percentile bands"
                )
            
            with col3:
                estimation_method = st.selectbox(
                    "Parameter estimation",
                    options=["Historical Mean", "Exponentially Weighted"],
                    key=self._get_session_key("estimation"),
                    help="Method for estimating returns and volatility"
                )
            
            st.markdown("**Rebalancing & Contributions:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                enable_contributions = st.checkbox(
                    "Enable periodic contributions",
                    value=False,
                    key=self._get_session_key("enable_contrib"),
                    help="Add regular contributions/withdrawals to simulation"
                )
            
            with col2:
                contribution_amount = st.number_input(
                    "Annual contribution ($)",
                    min_value=-100000.0,
                    max_value=1000000.0,
                    value=10000.0,
                    step=1000.0,
                    disabled=not enable_contributions,
                    key=self._get_session_key("contrib_amount"),
                    help="Positive for contributions, negative for withdrawals"
                )
            
            with col3:
                contribution_frequency = st.selectbox(
                    "Frequency",
                    options=["Annual", "Quarterly", "Monthly"],
                    disabled=not enable_contributions,
                    key=self._get_session_key("contrib_freq"),
                    help="How often contributions/withdrawals occur"
                )
            
            st.markdown("**Rebalancing Analysis:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                enable_rebalancing_analysis = st.checkbox(
                    "Analyze rebalancing timing",
                    value=False,
                    key=self._get_session_key("enable_rebal_analysis"),
                    help="Predict optimal rebalancing dates based on drift from target weights"
                )
            
            with col2:
                drift_threshold = st.slider(
                    "Drift threshold (%)",
                    min_value=5.0,
                    max_value=30.0,
                    value=10.0,
                    step=2.5,
                    disabled=not enable_rebalancing_analysis,
                    key=self._get_session_key("drift_threshold"),
                    help="Trigger rebalancing when any asset drifts this far from target weight"
                )
            
            with col3:
                transaction_cost_pct = st.number_input(
                    "Transaction cost (%)",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.1,
                    step=0.05,
                    disabled=not enable_rebalancing_analysis,
                    key=self._get_session_key("transaction_cost"),
                    help="Estimated cost per rebalancing transaction (% of portfolio)"
                )
            
            # Second row for max rebalances constraint
            col1, col2, col3 = st.columns(3)
            
            with col1:
                max_rebalances_per_year = st.slider(
                    "Max rebalances per year",
                    min_value=1,
                    max_value=12,
                    value=4,
                    step=1,
                    disabled=not enable_rebalancing_analysis,
                    key=self._get_session_key("max_rebalances"),
                    help="Limit rebalancing frequency to reduce transaction costs (e.g., 4 = quarterly, 2 = semi-annual, 1 = annual)"
                )
        
        return {
            'num_sims': num_sims,
            'years': years,
            'initial_value': initial_value,
            'include_dividends': include_dividends,
            'confidence_level': confidence_level,
            'estimation_method': estimation_method,
            'enable_contributions': enable_contributions,
            'contribution_amount': contribution_amount if enable_contributions else 0,
            'contribution_frequency': contribution_frequency,
            'enable_rebalancing_analysis': enable_rebalancing_analysis,
            'drift_threshold': drift_threshold / 100 if enable_rebalancing_analysis else None,
            'transaction_cost_pct': transaction_cost_pct / 100 if enable_rebalancing_analysis else 0,
            'max_rebalances_per_year': max_rebalances_per_year if enable_rebalancing_analysis else None
        }
    
    def _render_simulation_results(self, results: SimulationResults, params: Dict):
        """Display simulation outcomes.
        
        Parameters:
            results: Simulation results
            params: Simulation parameters
        """
        st.subheader("Simulation Results")
        
        # Summary info box
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Simulations Run:** {results.num_sims:,}")
                st.markdown(f"**Time Horizon:** {params['years']} years")
            with col2:
                st.markdown(f"**Initial Value:** ${results.initial_value:,.0f}")
                if params['enable_contributions']:
                    st.markdown(f"**Annual Contribution:** ${params['contribution_amount']:,.0f} ({params['contribution_frequency']})")
                else:
                    st.markdown(f"**Contributions:** None")
            with col3:
                weight_method = st.session_state.get(self._get_session_key('weight_method'), 'Equal Weights')
                st.markdown(f"**Weight Method:** {weight_method}")
                st.markdown(f"**Estimation Method:** {params['estimation_method']}")
        
        # 1. Key Metrics
        self._render_key_metrics(results, params)
        
        
        # 2. Fan Chart
        self._render_fan_chart(results, params)
        
        # 3. Rebalancing Recommendations
        if results.rebalancing_rec:
            self._render_rebalancing_recommendations(results.rebalancing_rec, params)
        
        # 4. Distribution Chart
        self._render_distribution_chart(results, params)
        
        # 5. Percentile Table
        self._render_percentile_table(results)
        
        # 6. Export Results
        self._render_export_options(results, params)
    
    def _render_key_metrics(self, results: SimulationResults, params: Dict):
        """Display key simulation metrics."""
        
        st.markdown("### Key Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Median Final Value",
                f"${results.percentile_50:,.0f}",
                delta=f"{results.cagr_median:.2f}% CAGR"
            )
        
        with col2:
            lower_pct = (100 - params['confidence_level']) // 2
            st.metric(
                f"{lower_pct}th Percentile (Downside)",
                f"${results.percentile_10:,.0f}",
                delta=f"{results.cagr_10th:.2f}% CAGR",
                help=f"Worst-case scenario at {params['confidence_level']}% confidence"
            )
        
        with col3:
            upper_pct = 100 - lower_pct
            st.metric(
                f"{upper_pct}th Percentile (Upside)",
                f"${results.percentile_90:,.0f}",
                delta=f"{results.cagr_90th:.2f}% CAGR",
                help=f"Best-case scenario at {params['confidence_level']}% confidence"
            )
        
        with col4:
            prob_loss = (results.paths_below_initial / results.num_sims * 100)
            st.metric(
                "Probability of Loss",
                f"{prob_loss:.1f}%",
                delta=None,
                help="Percentage of simulations ending below initial value"
            )
        
        st.markdown("### Risk Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Value at Risk (95%)",
                f"${results.var_95:,.0f}",
                delta=f"{((results.var_95 / results.initial_value - 1) * 100):+.1f}%",
                help="5% chance of losing more than this amount",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "Conditional VaR (95%)",
                f"${results.cvar_95:,.0f}",
                delta=f"{((results.cvar_95 / results.initial_value - 1) * 100):+.1f}%",
                help="Average loss in worst 5% of scenarios",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Max Drawdown (Median)",
                f"{results.max_drawdown_median:.1f}%",
                delta=None,
                help="Largest peak-to-trough decline in median path",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "Historical Sharpe Ratio",
                f"{results.historical_sharpe:.2f}",
                delta=None,
                help="Risk-adjusted return based on selected weights (assumes constant allocation)"
            )
    
    def _render_fan_chart(self, results: SimulationResults, params: Dict):
        """Render fan chart showing all simulation paths."""
        
        st.markdown("**Portfolio Value Over Time (Monte Carlo Paths)**")
        
        fig = go.Figure()
        
        # Calculate confidence bands
        lower_pct = (100 - params['confidence_level']) // 2
        upper_pct = 100 - lower_pct
        
        # Add percentile bands (outer, middle, inner)
        bands = [
            (lower_pct, upper_pct, 0.1, f"{params['confidence_level']}% confidence"),
            (25, 75, 0.2, "25-75th percentile"),
            (40, 60, 0.3, "40-60th percentile")
        ]
        
        for lower, upper, opacity, label in bands:
            # Upper band
            fig.add_trace(go.Scatter(
                x=results.time_points,
                y=results.percentiles[upper],
                fill=None,
                mode='lines',
                line_color='rgba(68, 138, 255, 0)',
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Lower band
            fig.add_trace(go.Scatter(
                x=results.time_points,
                y=results.percentiles[lower],
                fill='tonexty',
                mode='lines',
                line_color='rgba(68, 138, 255, 0)',
                fillcolor=f'rgba(68, 138, 255, {opacity})',
                name=label,
                hovertemplate=f'<b>{label}</b><br>Year: %{{x:.1f}}<br>Value: $%{{y:,.0f}}<extra></extra>'
            ))
        
        # Add median line
        fig.add_trace(go.Scatter(
            x=results.time_points,
            y=results.percentiles[50],
            mode='lines',
            line=dict(color='#1f77b4', width=3),
            name='Median (50th percentile)',
            hovertemplate='<b>Median</b><br>Year: %{x:.1f}<br>Value: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add initial value line
        fig.add_hline(
            y=results.initial_value,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="Initial Value",
            annotation_position="right"
        )
        
        fig.update_layout(
            xaxis=dict(
                title="Years",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128, 128, 128, 0.2)'
            ),
            yaxis=dict(
                title="Portfolio Value ($)",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128, 128, 128, 0.2)',
                tickformat='$,.0f'
            ),
            hovermode='x unified',
            height=500,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.8)'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def _render_distribution_chart(self, results: SimulationResults, params: Dict):
        """Histogram of final portfolio values."""
        
        st.markdown("**Distribution of Final Portfolio Values**")
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=results.final_values,
            nbinsx=50,
            name='Final Values',
            marker_color='#636EFA',
            hovertemplate='Value Range: $%{x:,.0f}<br>Count: %{y}<extra></extra>'
        ))
        
        # Add percentile lines
        lower_pct = (100 - params['confidence_level']) // 2
        upper_pct = 100 - lower_pct
        
        percentile_lines = [
            (lower_pct, 'red', f"{lower_pct}th"),
            (50, 'green', 'Median'),
            (upper_pct, 'orange', f"{upper_pct}th")
        ]
        
        for pct, color, label in percentile_lines:
            value = results.percentiles[pct][-1]
            fig.add_vline(
                x=value,
                line_dash="dash",
                line_color=color,
                line_width=2,
                annotation_text=f"{label}: ${value:,.0f}",
                annotation_position="top"
            )
        
        fig.update_layout(
            xaxis=dict(
                title="Final Portfolio Value ($)",
                tickformat='$,.0f'
            ),
            yaxis_title="Frequency",
            height=400,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def _render_percentile_table(self, results: SimulationResults):
        """Display percentile breakdown table."""
        
        st.markdown("**Detailed Percentile Breakdown**")
        
        percentiles_to_show = [5, 10, 25, 50, 75, 90, 95]
        
        table_data = []
        for pct in percentiles_to_show:
            final_value = results.percentiles[pct][-1]
            return_pct = ((final_value / results.initial_value) - 1) * 100
            
            table_data.append({
                'Percentile': f"{pct}th",
                'Final Value': f"${final_value:,.0f}",
                'Total Return': f"{return_pct:+.1f}%",
                'Interpretation': self._get_percentile_interpretation(pct)
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, hide_index=True, width='stretch')
    
    def _render_portfolio_statistics(self, symbols: List[str], weights: np.ndarray):
        """Display historical statistics of the selected portfolio.
        
        Parameters:
            symbols: List of symbols
            weights: Portfolio weights
        """
        # Fetch 2 years of data
        returns_df = self._fetch_returns_data(symbols, days=730, include_dividends=True)
        
        if returns_df is None or returns_df.empty:
            st.warning("Insufficient historical data to calculate portfolio statistics")
            return
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Calculate metrics
        ann_return = portfolio_returns.mean() * 252
        ann_volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (ann_return - 0.04) / ann_volatility if ann_volatility > 0 else 0
        
        # Calculate max drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Historical Return (Ann.)", f"{ann_return*100:.2f}%")
        
        with col2:
            st.metric("Historical Volatility (Ann.)", f"{ann_volatility*100:.2f}%")
        
        with col3:
            st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
        
        with col4:
            st.metric("Max Drawdown", f"{max_drawdown*100:.1f}%", delta_color="inverse")
    
    def _render_rebalancing_recommendations(self, rec: RebalancingRecommendation, params: Dict):
        """Render rebalancing timing recommendations.
        
        Parameters:
            rec: Rebalancing recommendations
            params: Simulation parameters
        """

        st.markdown("### Optimal Rebalancing Analysis")
        
        with st.container(border=True):
            # Summary metrics
            st.markdown(f"**{rec.description}**")
            st.caption(f"Analysis based on {rec.trigger_threshold*100:.1f}% drift threshold")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Recommended Rebalances",
                    f"{len(rec.rebalance_dates)}",
                    help="Number of times to rebalance over the simulation period"
                )
            
            with col2:
                avg_months = (params['years'] * 12) / (len(rec.rebalance_dates) + 1) if rec.rebalance_dates else params['years'] * 12
                st.metric(
                    "Avg Time Between",
                    f"{avg_months:.1f} months",
                    help="Average time between rebalancing events"
                )
            
            with col3:
                st.metric(
                    "Avg Drift at Rebalance",
                    f"{rec.avg_drift*100:.1f}%",
                    help="Average portfolio drift when rebalancing occurs"
                )
            
            with col4:
                benefit_color = "normal" if rec.sharpe_improvement > 0 else "inverse"
                st.metric(
                    "Sharpe Improvement",
                    f"{rec.sharpe_improvement:+.3f}",
                    delta=f"{rec.cost_benefit_ratio:.1f}x cost",
                    delta_color=benefit_color,
                    help="Expected improvement in Sharpe ratio from rebalancing"
                )
        
        # Rebalancing calendar
        if rec.rebalance_dates:
            st.markdown("#### Recommended Rebalancing Dates")
            st.caption("Rebalance by adjusting positions back to your target allocation weights shown below")
            
            # Display target weights for reference
            with st.expander("View Target Allocation Weights", expanded=False):
                target_weights = params.get('weights', {})
                if target_weights:
                    weight_data = [{'Symbol': symbol, 'Target Weight': f"{weight * 100:.2f}%"} 
                                  for symbol, weight in sorted(target_weights.items(), key=lambda x: x[1], reverse=True)]
                    st.dataframe(pd.DataFrame(weight_data), width='stretch', hide_index=True)
            
            # Create DataFrame for display with per-instrument details
            rebal_data = []
            start_date = datetime.now()  # Use simulation start date
            
            for i, date in enumerate(rec.rebalance_dates, 1):
                days_from_start = (date - start_date).days
                months_from_start = days_from_start / 30.44  # Average days per month
                
                # Get instruments that need rebalancing on this date
                instruments_on_date = [item for item in rec.instruments_to_rebalance if item['date'] == date]
                
                if instruments_on_date:
                    # Group by action
                    to_buy = [item for item in instruments_on_date if item['action'] == 'Buy']
                    to_sell = [item for item in instruments_on_date if item['action'] == 'Sell']
                    
                    buy_symbols = ', '.join([f"{item['symbol']} ({abs(item['drift'])*100:.1f}%)" for item in to_buy])
                    sell_symbols = ', '.join([f"{item['symbol']} ({abs(item['drift'])*100:.1f}%)" for item in to_sell])
                    
                    rebal_data.append({
                        'Rebalance #': i,
                        'Date': date.strftime('%d %b %Y'),
                        'Months from Start': f"{months_from_start:.1f}",
                        'Buy (Underweight)': buy_symbols if buy_symbols else 'None',
                        'Sell (Overweight)': sell_symbols if sell_symbols else 'None'
                    })
            
            if rebal_data:
                rebal_df = pd.DataFrame(rebal_data)
                st.dataframe(rebal_df, width='stretch', hide_index=True)
                
                st.caption("Percentages show how much each instrument has drifted from target weight")
            
            # Detailed per-instrument rebalancing view
            with st.expander("View Detailed Rebalancing Actions by Instrument", expanded=False):
                if rec.instruments_to_rebalance:
                    detailed_data = []
                    for item in rec.instruments_to_rebalance:
                        detailed_data.append({
                            'Date': item['date'].strftime('%d %b %Y'),
                            'Instrument': item['symbol'],
                            'Current Weight': f"{item['current_weight']*100:.2f}%",
                            'Target Weight': f"{item['target_weight']*100:.2f}%",
                            'Drift': f"{item['drift']*100:+.1f}%",
                            'Action': item['action']
                        })
                    
                    detailed_df = pd.DataFrame(detailed_data)
                    st.dataframe(detailed_df, width='stretch', hide_index=True)
                else:
                    st.info("No instruments require rebalancing")
            
            # Timeline visualization
            st.markdown("#### Rebalancing Timeline")
            
            fig = go.Figure()
            
            # Add rebalancing events as scatter points
            years_from_start = [(date - rec.rebalance_dates[0]).days / 365.25 for date in rec.rebalance_dates]
            
            fig.add_trace(go.Scatter(
                x=years_from_start,
                y=rec.drift_at_rebalance,
                mode='markers+lines',
                marker=dict(size=12, color='red', symbol='diamond'),
                line=dict(color='lightcoral', width=2, dash='dot'),
                name='Rebalancing Events',
                hovertemplate='<b>Rebalance</b><br>Year: %{x:.1f}<br>Drift: %{y:.1%}<extra></extra>'
            ))
            
            # Add threshold line
            fig.add_hline(
                y=rec.trigger_threshold,
                line_dash="dash",
                line_color="orange",
                annotation_text=f"Drift Threshold ({rec.trigger_threshold*100:.0f}%)",
                annotation_position="right"
            )
            
            fig.update_layout(
                title="Portfolio Drift and Rebalancing Events",
                xaxis_title="Years from Start",
                yaxis_title="Maximum Asset Drift from Target (%)",
                yaxis_tickformat=".0%",
                height=400,
                hovermode='closest',
                showlegend=True
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No rebalancing recommended - portfolio drift stays within threshold throughout the period.")
    
    def _render_export_options(self, results: SimulationResults, params: Dict):
        """Render export options for simulation results.
        
        Parameters:
            results: Simulation results
            params: Simulation parameters
        """

        st.markdown("### Export Simulation Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export percentiles over time
            percentile_df = pd.DataFrame({
                'Year': results.time_points,
                '5th Percentile': results.percentiles[5],
                '10th Percentile': results.percentiles[10],
                '25th Percentile': results.percentiles[25],
                '50th Percentile (Median)': results.percentiles[50],
                '75th Percentile': results.percentiles[75],
                '90th Percentile': results.percentiles[90],
                '95th Percentile': results.percentiles[95]
            })
            
            csv_percentiles = percentile_df.to_csv(index=False)
            st.download_button(
                label="Download Percentiles Over Time (CSV)",
                data=csv_percentiles,
                file_name=f"monte_carlo_percentiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                width="stretch"
            )
        
        with col2:
            # Export final value distribution
            final_values_df = pd.DataFrame({
                'Simulation': range(1, results.num_sims + 1),
                'Final Value': results.final_values,
                'Total Return (%)': ((results.final_values / results.initial_value) - 1) * 100
            })
            
            csv_final = final_values_df.to_csv(index=False)
            st.download_button(
                label="Download Final Values Distribution (CSV)",
                data=csv_final,
                file_name=f"monte_carlo_final_values_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                width="stretch"
            )
    
    @staticmethod
    def _get_percentile_interpretation(pct: int) -> str:
        """Get human-readable interpretation of percentile."""
        if pct <= 10:
            return "Pessimistic scenario"
        elif pct <= 25:
            return "Below average outcome"
        elif pct <= 40:
            return "Slightly below average"
        elif pct <= 60:
            return "Average outcome"
        elif pct <= 75:
            return "Above average outcome"
        elif pct <= 90:
            return "Optimistic scenario"
        else:
            return "Highly optimistic scenario"
    
    # ========================================================================
    # DATA LAYER - Data fetching methods
    # ========================================================================
    
    def _calculate_optimal_weights(self, returns_df: pd.DataFrame, method: str) -> Optional[np.ndarray]:
        """Calculate optimal portfolio weights using mean-variance optimization.
        
        Parameters:
            returns_df: Historical returns DataFrame
            method: Optimization method ("Max Sharpe Ratio" or "Min Volatility")
            
        Returns:
            Optimal weights array, or None if optimization fails
        """
        try:
            n_assets = len(returns_df.columns)
            
            # Calculate expected returns and covariance
            mean_returns = returns_df.mean() * 252  # Annualized
            cov_matrix = returns_df.cov() * 252  # Annualized
            
            # Risk-free rate (approximate)
            risk_free_rate = 0.04
            
            if method == "Max Sharpe Ratio":
                # Maximize Sharpe ratio = minimize negative Sharpe
                def objective(weights):
                    portfolio_return = np.sum(mean_returns * weights)
                    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                    sharpe = (portfolio_return - risk_free_rate) / portfolio_std
                    return -sharpe  # Minimize negative Sharpe
            
            else:  # Min Volatility
                # Minimize portfolio variance
                def objective(weights):
                    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Constraints: weights sum to 1
            constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
            
            # Bounds: weights between 0 and 1 (no shorting)
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # Initial guess: equal weights
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )
            
            if result.success:
                return result.x
            else:
                return None
        
        except Exception as e:
            return None
    
    def _fetch_returns_data(self, symbols: List[str], days: int, 
                            include_dividends: bool = True) -> Optional[pd.DataFrame]:
        """Fetch historical returns for selected instruments."""
        
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
                dividends = self.storage.get_dividends(symbol)
                if dividends and len(dividends) > 0:
                    returns = self._calculate_total_returns(price_df['close'], dividends, start_date, end_date)
                else:
                    returns = calculate_returns(price_df['close'])
            else:
                returns = calculate_returns(price_df['close'])
            
            returns_dict[symbol] = returns
        
        if len(returns_dict) < 1:
            return None
        
        # Combine into DataFrame
        returns_df = pd.DataFrame(returns_dict)
        returns_df = returns_df.ffill().dropna()
        
        return returns_df
    
    # ========================================================================
    # LOGIC LAYER - Monte Carlo simulation engine
    # ========================================================================
    
    @staticmethod
    def _run_monte_carlo(
        symbols: List[str],
        weights: np.ndarray,
        returns_df: pd.DataFrame,
        num_sims: int,
        years: int,
        initial_value: float,
        include_dividends: bool,
        confidence_level: int,
        estimation_method: str = "Historical Mean",
        enable_contributions: bool = False,
        contribution_amount: float = 0,
        contribution_frequency: str = "Annual",
        **kwargs
    ) -> SimulationResults:
        """Run Monte Carlo simulation using geometric Brownian motion.
        
        Parameters:
            symbols: List of instrument symbols
            weights: Portfolio weights (must sum to 1)
            returns_df: Historical returns DataFrame
            num_sims: Number of simulations to run
            years: Time horizon in years
            initial_value: Starting portfolio value
            include_dividends: Whether dividends are included
            confidence_level: Confidence level for percentiles (e.g., 90)
            estimation_method: Method for parameter estimation
            enable_contributions: Whether to include periodic contributions
            contribution_amount: Amount of periodic contribution (can be negative)
            contribution_frequency: Frequency of contributions
            
        Returns:
            SimulationResults: Simulation outcomes
        """
        
        # 1. Estimate parameters from historical data
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        if estimation_method == "Exponentially Weighted":
            # Use exponentially weighted moving average with higher weight on recent data
            span = 60  # Roughly 3 months of trading days
            mu = portfolio_returns.ewm(span=span).mean().iloc[-1] * 252
            sigma = portfolio_returns.ewm(span=span).std().iloc[-1] * np.sqrt(252)
        else:  # Historical Mean
            mu = portfolio_returns.mean() * 252  # Annualized drift
            sigma = portfolio_returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Calculate historical Sharpe ratio
        risk_free_rate = 0.04
        historical_sharpe = (mu - risk_free_rate) / sigma if sigma > 0 else 0
        
        # 2. Simulation parameters
        dt = 1 / 252  # Daily time steps
        num_steps = int(years * 252)
        
        # Determine contribution frequency
        if contribution_frequency == "Monthly":
            contrib_interval = 21  # ~21 trading days per month
        elif contribution_frequency == "Quarterly":
            contrib_interval = 63  # ~63 trading days per quarter
        else:  # Annual
            contrib_interval = 252  # 252 trading days per year
        
        # 3. Generate random paths using geometric Brownian motion with contributions
        # S(t+dt) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z) + contribution
        
        np.random.seed(42)  # For reproducibility
        paths = np.zeros((num_sims, num_steps + 1))
        paths[:, 0] = initial_value
        
        for t in range(1, num_steps + 1):
            Z = np.random.standard_normal(num_sims)
            paths[:, t] = paths[:, t-1] * np.exp(
                (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
            )
            
            # Add contribution at specified intervals
            if enable_contributions and t % contrib_interval == 0:
                # Prorate contribution based on frequency
                if contribution_frequency == "Monthly":
                    periodic_contrib = contribution_amount / 12
                elif contribution_frequency == "Quarterly":
                    periodic_contrib = contribution_amount / 4
                else:  # Annual
                    periodic_contrib = contribution_amount
                
                paths[:, t] += periodic_contrib
        
        # 4. Calculate statistics
        time_points = np.linspace(0, years, num_steps + 1)
        
        # Calculate percentiles
        lower_pct = (100 - confidence_level) // 2
        upper_pct = 100 - lower_pct
        
        percentiles = {}
        for pct in [5, 10, lower_pct, 25, 40, 50, 60, 75, upper_pct, 90, 95]:
            percentiles[pct] = np.percentile(paths, pct, axis=0)
        
        final_values = paths[:, -1]
        paths_below_initial = np.sum(final_values < initial_value)
        
        # Calculate risk metrics
        var_95 = np.percentile(final_values, 5)  # Value at Risk (5th percentile)
        worst_5_percent = final_values[final_values <= var_95]
        cvar_95 = np.mean(worst_5_percent) if len(worst_5_percent) > 0 else var_95
        
        # Calculate max drawdown for median path
        median_path = percentiles[50]
        cumulative_max = np.maximum.accumulate(median_path)
        drawdowns = (median_path - cumulative_max) / cumulative_max
        max_drawdown_median = np.min(drawdowns) * 100  # As percentage
        
        # Calculate CAGR for different percentiles
        cagr_median = ((percentiles[50][-1] / initial_value) ** (1/years) - 1) * 100
        cagr_10th = ((percentiles[lower_pct][-1] / initial_value) ** (1/years) - 1) * 100
        cagr_90th = ((percentiles[upper_pct][-1] / initial_value) ** (1/years) - 1) * 100
        
        # 5. Rebalancing analysis (if enabled)
        rebalancing_rec = None
        if kwargs.get('enable_rebalancing_analysis', False):
            drift_threshold = kwargs.get('drift_threshold', 0.10)
            transaction_cost_pct = kwargs.get('transaction_cost_pct', 0.001)
            max_rebalances_per_year = kwargs.get('max_rebalances_per_year', None)
            
            rebalancing_rec = MonteCarloWidget._analyze_rebalancing_timing(
                symbols=symbols,
                target_weights=weights,
                returns_df=returns_df,
                years=years,
                drift_threshold=drift_threshold,
                transaction_cost_pct=transaction_cost_pct,
                mu=mu,
                sigma=sigma,
                max_rebalances_per_year=max_rebalances_per_year
            )
        
        return SimulationResults(
            paths=paths,
            time_points=time_points,
            percentiles=percentiles,
            final_values=final_values,
            num_sims=num_sims,
            initial_value=initial_value,
            paths_below_initial=paths_below_initial,
            percentile_10=percentiles[lower_pct][-1],
            percentile_50=percentiles[50][-1],
            percentile_90=percentiles[upper_pct][-1],
            var_95=var_95,
            cvar_95=cvar_95,
            max_drawdown_median=max_drawdown_median,
            cagr_median=cagr_median,
            cagr_10th=cagr_10th,
            cagr_90th=cagr_90th,
            historical_sharpe=historical_sharpe,
            historical_volatility=sigma,
            rebalancing_rec=rebalancing_rec
        )
    
    @staticmethod
    def _calculate_total_returns(prices: pd.Series, dividends: List[Dict], 
                                 start_date: datetime, end_date: datetime) -> pd.Series:
        """Calculate total returns including dividends."""
        
        # Price returns
        returns = calculate_returns(prices)
        
        # Add dividend yields on ex-dates
        for div in dividends:
            ex_date = pd.to_datetime(div['ex_date'])
            if start_date <= ex_date <= end_date:
                # Find closest price date
                closest_idx = prices.index.get_indexer([ex_date], method='nearest')[0]
                if closest_idx < len(returns):
                    price = prices.iloc[closest_idx]
                    div_yield = div['amount'] / price if price > 0 else 0
                    returns.iloc[closest_idx] += div_yield
        
        return returns
    
    @staticmethod
    def _analyze_rebalancing_timing(
        symbols: List[str],
        target_weights: np.ndarray,
        returns_df: pd.DataFrame,
        years: int,
        drift_threshold: float,
        transaction_cost_pct: float,
        mu: float,
        sigma: float,
        max_rebalances_per_year: int = None
    ) -> RebalancingRecommendation:
        """Analyze optimal rebalancing timing based on drift from target weights.
        
        Parameters:
            symbols: List of instrument symbols
            target_weights: Target portfolio weights
            returns_df: Historical returns data
            years: Simulation horizon
            drift_threshold: Drift threshold to trigger rebalancing (e.g., 0.10 for 10%)
            transaction_cost_pct: Transaction cost per rebalance (% of portfolio)
            mu: Expected portfolio return
            sigma: Expected portfolio volatility
            max_rebalances_per_year: Maximum rebalances per year (optional constraint)
            
        Returns:
            RebalancingRecommendation: Timing and impact analysis
        """
        # Simulate asset paths to predict weight drift
        n_assets = len(symbols)
        dt = 1 / 252
        num_steps = int(years * 252)
        
        # Get individual asset parameters
        asset_returns = returns_df.mean() * 252
        asset_vols = returns_df.std() * np.sqrt(252)
        correlation_matrix = returns_df.corr().values
        
        # Simulate one median scenario for analysis
        np.random.seed(42)
        asset_paths = np.zeros((n_assets, num_steps + 1))
        asset_paths[:, 0] = 1.0  # Start with normalized prices
        
        # Generate correlated random returns
        L = np.linalg.cholesky(correlation_matrix)
        
        for t in range(1, num_steps + 1):
            Z = np.random.standard_normal(n_assets)
            correlated_Z = L @ Z
            
            for i in range(n_assets):
                asset_paths[i, t] = asset_paths[i, t-1] * np.exp(
                    (asset_returns.iloc[i] - 0.5 * asset_vols.iloc[i]**2) * dt + 
                    asset_vols.iloc[i] * np.sqrt(dt) * correlated_Z[i]
                )
        
        # Track weight evolution and rebalancing points
        current_weights = target_weights.copy()
        rebalance_dates = []
        drift_at_rebalance = []
        instruments_to_rebalance = []  # Track which instruments need rebalancing
        
        start_date = datetime.now()
        
        for t in range(1, num_steps + 1):
            # Calculate current weights based on asset performance
            portfolio_values = asset_paths[:, t] * current_weights
            total_value = portfolio_values.sum()
            current_weights = portfolio_values / total_value
            
            # Calculate maximum drift from target
            weight_drifts = np.abs(current_weights - target_weights)
            max_drift = weight_drifts.max()
            
            # Check if rebalancing is needed
            if max_drift > drift_threshold:
                days_elapsed = t
                rebalance_date = start_date + timedelta(days=days_elapsed)
                rebalance_dates.append(rebalance_date)
                drift_at_rebalance.append(max_drift)
                
                # Record per-instrument rebalancing actions
                for i, symbol in enumerate(symbols):
                    drift_pct = (current_weights[i] - target_weights[i]) / target_weights[i] if target_weights[i] > 0 else 0
                    
                    # Determine action (buy/sell) and amount
                    if abs(current_weights[i] - target_weights[i]) > 0.01:  # Only if drift > 1%
                        if current_weights[i] > target_weights[i]:
                            action = "Sell"
                        else:
                            action = "Buy"
                        
                        instruments_to_rebalance.append({
                            'date': rebalance_date,
                            'symbol': symbol,
                            'current_weight': current_weights[i],
                            'target_weight': target_weights[i],
                            'drift': drift_pct,
                            'action': action
                        })
                
                # Rebalance back to target weights
                current_weights = target_weights.copy()
        
        # Apply max rebalances constraint if specified
        original_num_rebalances = len(rebalance_dates)
        if max_rebalances_per_year is not None:
            max_allowed = max_rebalances_per_year * years
            if original_num_rebalances > max_allowed:
                # Keep only the most important rebalances (highest drift)
                # Create list of (date, drift, index) tuples
                rebalance_info = list(zip(rebalance_dates, drift_at_rebalance, range(len(rebalance_dates))))
                # Sort by drift (descending) and take top max_allowed
                rebalance_info_sorted = sorted(rebalance_info, key=lambda x: x[1], reverse=True)[:max_allowed]
                # Sort back by date to maintain chronological order
                rebalance_info_sorted = sorted(rebalance_info_sorted, key=lambda x: x[0])
                
                # Extract filtered lists
                kept_indices = {info[2] for info in rebalance_info_sorted}
                rebalance_dates = [info[0] for info in rebalance_info_sorted]
                drift_at_rebalance = [info[1] for info in rebalance_info_sorted]
                
                # Filter instruments_to_rebalance to only kept dates
                kept_dates = set(rebalance_dates)
                instruments_to_rebalance = [
                    item for item in instruments_to_rebalance 
                    if item['date'] in kept_dates
                ]
        
        # Calculate metrics
        avg_drift = np.mean(drift_at_rebalance) if drift_at_rebalance else 0
        num_rebalances = len(rebalance_dates)
        
        # Estimate Sharpe improvement from rebalancing
        # Rebalancing maintains risk profile and can improve risk-adjusted returns
        # Benefit increases with drift but is offset by transaction costs
        if num_rebalances > 0:
            # Benefit: reducing variance from drift
            variance_reduction = avg_drift * 0.5  # Heuristic: drift affects volatility
            sharpe_benefit = variance_reduction * (mu / sigma) if sigma > 0 else 0
            
            # Cost: transaction costs
            total_cost = num_rebalances * transaction_cost_pct
            cost_drag_on_sharpe = total_cost / years  # Annualized cost impact
            
            sharpe_improvement = sharpe_benefit - cost_drag_on_sharpe
            cost_benefit_ratio = sharpe_benefit / cost_drag_on_sharpe if cost_drag_on_sharpe > 0 else 0
        else:
            sharpe_improvement = 0
            cost_benefit_ratio = 0
        
        # Generate description
        if num_rebalances == 0:
            description = "Portfolio stays within drift threshold - no rebalancing needed."
        elif max_rebalances_per_year is not None and original_num_rebalances > num_rebalances:
            # Constraint was applied
            description = f"Recommending {num_rebalances} rebalances over {years} years (limited from {original_num_rebalances} by max {max_rebalances_per_year}/year constraint). Kept highest-drift rebalances."
        elif num_rebalances <= 2:
            description = f"Rebalance {num_rebalances} time(s) over {years} years to maintain target allocation."
        elif cost_benefit_ratio < 1:
            description = f"Rebalancing {num_rebalances} times is recommended but benefits may not exceed costs."
        else:
            description = f"Rebalance {num_rebalances} times over {years} years for optimal risk-adjusted returns."
        
        return RebalancingRecommendation(
            rebalance_dates=rebalance_dates,
            drift_at_rebalance=drift_at_rebalance,
            trigger_threshold=drift_threshold,
            avg_drift=avg_drift,
            cost_benefit_ratio=cost_benefit_ratio,
            sharpe_improvement=sharpe_improvement,
            description=description,
            instruments_to_rebalance=instruments_to_rebalance,
            symbols=symbols
        )
    
    @staticmethod
    def _dict_to_simulation_results(results_dict: Dict) -> SimulationResults:
        """Convert dict results from compatibility bridge to SimulationResults dataclass.
        
        This enables the new service layer to return results in the format expected
        by the existing rendering code.
        """
        risk_metrics = results_dict.get('risk_metrics', {})
        
        return SimulationResults(
            paths=results_dict['paths'],
            time_points=results_dict['time_points'],
            percentiles=results_dict['percentiles'],
            final_values=results_dict['final_values'],
            num_sims=len(results_dict['final_values']),
            initial_value=results_dict['paths'][0][0] if len(results_dict['paths']) > 0 else 0,
            paths_below_initial=int(np.sum(results_dict['final_values'] < results_dict['paths'][0][0])),
            percentile_10=np.percentile(results_dict['final_values'], 10),
            percentile_50=results_dict.get('median_outcome', np.percentile(results_dict['final_values'], 50)),
            percentile_90=np.percentile(results_dict['final_values'], 90),
            var_95=risk_metrics.get('var_95', 0.0),
            cvar_95=risk_metrics.get('cvar_95', 0.0),
            max_drawdown_median=risk_metrics.get('max_drawdown_median', 0.0),
            cagr_median=risk_metrics.get('cagr_median', 0.0),
            cagr_10th=risk_metrics.get('cagr_5th', 0.0),  # Note: bridge uses 5th
            cagr_90th=risk_metrics.get('cagr_95th', 0.0),  # Note: bridge uses 95th
            historical_sharpe=risk_metrics.get('historical_sharpe', 0.0),
            historical_volatility=risk_metrics.get('historical_volatility', 0.0),
            rebalancing_rec=None  # Rebalancing analyzed separately
        )

