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

from .layered_base_widget import LayeredBaseWidget
from src.utils.performance_metrics import calculate_returns


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
            all_instruments = self.storage.get_all_instruments()
            
            if not all_instruments:
                st.info("No instruments available for simulation")
                return
            
            # 1. Portfolio Selection
            selected_symbols, weights = self._render_portfolio_selector(all_instruments)
            
            if len(selected_symbols) < 1:
                st.info("Please select at least 1 instrument to simulate")
                return
            
            st.divider()
            
            # 2. Simulation Parameters
            sim_params = self._render_simulation_parameters()
            
            # 3. Run Simulation Button
            if st.button("🎲 Run Monte Carlo Simulation", type="primary", use_container_width=True):
                # Fetch historical data
                returns_df = self._fetch_returns_data(
                    selected_symbols, 
                    days=730,  # 2 years of history
                    include_dividends=sim_params['include_dividends']
                )
                
                if returns_df is None or returns_df.empty:
                    st.error("Insufficient historical data for simulation")
                    return
                
                # Run simulation
                with st.spinner(f"Running {sim_params['num_sims']:,} simulations..."):
                    results = self._run_monte_carlo(
                        symbols=selected_symbols,
                        weights=weights,
                        returns_df=returns_df,
                        **sim_params
                    )
                
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
        col1, col2 = st.columns([3, 1])
        
        with col2:
            equal_weights = st.checkbox("Equal weights", value=True, key=self._get_session_key("equal_weights"))
        
        weights = {}
        if equal_weights:
            weight_value = 100.0 / len(selected_symbols)
            for symbol in selected_symbols:
                weights[symbol] = weight_value
            st.caption(f"Each instrument: {weight_value:.1f}%")
        else:
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
        with st.expander("⚙️ Advanced Settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                include_dividends = st.toggle(
                    "Include dividends in returns",
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
        
        return {
            'num_sims': num_sims,
            'years': years,
            'initial_value': initial_value,
            'include_dividends': include_dividends,
            'confidence_level': confidence_level
        }
    
    def _render_simulation_results(self, results: SimulationResults, params: Dict):
        """Display simulation outcomes.
        
        Parameters:
            results: Simulation results
            params: Simulation parameters
        """
        st.divider()
        st.subheader("📊 Simulation Results")
        
        # 1. Key Metrics
        self._render_key_metrics(results, params)
        
        st.divider()
        
        # 2. Fan Chart
        self._render_fan_chart(results, params)
        
        st.divider()
        
        # 3. Distribution Chart
        self._render_distribution_chart(results, params)
        
        st.divider()
        
        # 4. Percentile Table
        self._render_percentile_table(results)
    
    def _render_key_metrics(self, results: SimulationResults, params: Dict):
        """Display key simulation metrics."""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            median_return = ((results.percentile_50 / results.initial_value) - 1) * 100
            st.metric(
                "Median Final Value",
                f"${results.percentile_50:,.0f}",
                delta=f"{median_return:+.1f}%"
            )
        
        with col2:
            lower_pct = (100 - params['confidence_level']) // 2
            st.metric(
                f"{lower_pct}th Percentile (Downside)",
                f"${results.percentile_10:,.0f}",
                delta=f"{((results.percentile_10 / results.initial_value) - 1) * 100:+.1f}%",
                help=f"Worst-case scenario at {params['confidence_level']}% confidence"
            )
        
        with col3:
            upper_pct = 100 - lower_pct
            st.metric(
                f"{upper_pct}th Percentile (Upside)",
                f"${results.percentile_90:,.0f}",
                delta=f"{((results.percentile_90 / results.initial_value) - 1) * 100:+.1f}%",
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
            
        Returns:
            SimulationResults: Simulation outcomes
        """
        
        # 1. Estimate parameters from historical data
        portfolio_returns = (returns_df * weights).sum(axis=1)
        mu = portfolio_returns.mean() * 252  # Annualized drift
        sigma = portfolio_returns.std() * np.sqrt(252)  # Annualized volatility
        
        # 2. Simulation parameters
        dt = 1 / 252  # Daily time steps
        num_steps = int(years * 252)
        
        # 3. Generate random paths using geometric Brownian motion
        # S(t+dt) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
        # where Z ~ N(0,1)
        
        np.random.seed(42)  # For reproducibility
        paths = np.zeros((num_sims, num_steps + 1))
        paths[:, 0] = initial_value
        
        for t in range(1, num_steps + 1):
            Z = np.random.standard_normal(num_sims)
            paths[:, t] = paths[:, t-1] * np.exp(
                (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
            )
        
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
            percentile_90=percentiles[upper_pct][-1]
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
