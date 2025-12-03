"""
Constrained Portfolio Optimization Widget

This widget allows users to define custom optimization objectives and constraints
for portfolio construction using non-linear programming.

ARCHITECTURE: Three-Layer Pattern
- UI Layer (_render_*): Streamlit components, user interactions
- Data Layer (_fetch_*, _prepare_*): Storage access, data validation  
- Logic Layer (_calculate_*, _optimize_*, @staticmethod): Pure calculations, testable
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from scipy.optimize import minimize, NonlinearConstraint, LinearConstraint
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.services.storage_adapter import DataStorageAdapter
from src.utils.performance_metrics import calculate_returns
from src.widgets.base_widget import BaseWidget


@dataclass
class ConstraintDefinition:
    """Definition of a portfolio constraint."""
    name: str
    constraint_type: str  # 'linear', 'nonlinear'
    operator: str  # '<=', '>=', '=='
    value: float
    enabled: bool = True


@dataclass
class OptimizationResult:
    """Result of constrained optimization."""
    weights: np.ndarray
    objective_value: float
    expected_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    sortino_ratio: float
    dividend_yield: float
    cvar_5pct: float  # Add CVaR metric
    diversification_ratio: float  # Add diversification metric
    success: bool
    message: str
    constraints_satisfied: Dict[str, bool]
    constraint_violations: Dict[str, float]  # Show HOW MUCH constraints are violated by


class ConstrainedOptimizationWidget(BaseWidget):
    """Widget for constrained portfolio optimization with custom objectives."""
    
    def __init__(self, storage: DataStorageAdapter, widget_id: str = "constrained_optimization"):
        """Initialize the widget.
        
        Parameters:
            storage: Storage adapter for data access
            widget_id: Unique identifier for this widget instance
        """
        super().__init__(storage, widget_id)
    
    def get_name(self) -> str:
        """Return widget display name."""
        return "Constrained Portfolio Optimization"
    
    def get_description(self) -> str:
        """Return widget description."""
        return "Optimize portfolios with custom objectives and multiple constraints using non-linear programming"
    
    def get_scope(self) -> str:
        """Return widget scope."""
        return "multiple"
    
    def _get_session_key(self, key: str) -> str:
        """Generate a unique session state key."""
        return f"{self.widget_id}_{key}"
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render the constrained optimization widget."""
        with st.container(border=True):
            st.markdown("""
            Define custom optimization objectives and constraints for portfolio construction.
            Use non-linear programming to find optimal portfolios subject to multiple constraints.
            """)
            
            # Get instruments for selection
            # Use active_only=False to include ALL instruments
            instruments = self.storage.get_all_instruments(active_only=False)
            if not instruments:
                st.warning("No instruments available. Please add instruments first.")
                return
            
            # Instrument and period selection
            selected_symbols, days = self._render_instrument_and_period_selectors(instruments)
            
            if not selected_symbols or len(selected_symbols) < 2:
                st.info("Please select at least 2 instruments for optimization")
                return
            
            # Include dividends option
            include_dividends = st.checkbox(
                "Include Dividends in Returns",
                value=True,
                help="Calculate total returns (price + dividends) instead of price-only returns",
                key=self._get_session_key("include_dividends")
            )
            
            # Fetch returns data
            returns_df = self._fetch_returns_data(selected_symbols, days, include_dividends)
            
            if returns_df is None or returns_df.empty:
                st.warning("Insufficient price data for selected instruments")
                return
            
            # Main optimization interface
            self._render_optimization_interface(selected_symbols, returns_df, include_dividends)
    
    def _render_instrument_and_period_selectors(self, instruments: List[Dict]) -> Tuple[List[str], int]:
        """Render instrument and period selectors."""
        st.write("**Select instruments for portfolio:**")
        
        # Create symbol options
        portfolio_holdings = sorted([i['symbol'] for i in instruments if i.get('quantity', 0) > 0])
        other_instruments = sorted([i['symbol'] for i in instruments if i.get('quantity', 0) == 0])
        symbol_options = portfolio_holdings + other_instruments
        
        # Default to portfolio holdings
        default_symbols = portfolio_holdings if portfolio_holdings else symbol_options[:5]
        if len(default_symbols) > 5:
            default_symbols = default_symbols[:5]
        
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
    
    def _fetch_returns_data(self, symbols: List[str], days: int, include_dividends: bool) -> Optional[pd.DataFrame]:
        """Fetch returns data for selected instruments."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        returns_data = {}
        
        for symbol in symbols:
            price_df = self.storage.get_price_data(symbol, start_date, end_date)
            
            if price_df is None or len(price_df) < 20:
                continue
            
            if include_dividends:
                dividends = self.storage.get_dividends(symbol, start_date, end_date)
                if dividends:
                    returns_data[symbol] = self._calculate_total_returns(
                        price_df['close'], dividends, start_date, end_date
                    )
                else:
                    returns_data[symbol] = calculate_returns(price_df['close'])
            else:
                returns_data[symbol] = calculate_returns(price_df['close'])
        
        if not returns_data:
            return None
        
        returns_df = pd.DataFrame(returns_data)
        returns_df = returns_df.dropna()
        
        return returns_df if len(returns_df) > 20 else None
    
    def _calculate_total_returns(self, prices: pd.Series, dividends: List[Dict],
                                  start_date: datetime, end_date: datetime) -> pd.Series:
        """Calculate total returns including dividends."""
        div_series = pd.Series(0.0, index=prices.index)
        
        for div in dividends:
            ex_date = pd.to_datetime(div['ex_date'])
            if start_date <= ex_date <= end_date and ex_date in div_series.index:
                div_series[ex_date] = div['amount']
        
        total_values = prices + div_series.cumsum()
        returns = total_values.pct_change().dropna()
        
        return returns
    
    def _render_optimization_interface(self, symbols: List[str], returns_df: pd.DataFrame, include_dividends: bool):
        """Render the main optimization interface."""
        # Two column layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Optimization Objective")
            st.caption("Choose what to maximize or minimize by adjusting portfolio weights")
            
            objective_action = st.radio(
                "Action:",
                options=["Maximize", "Minimize", "Target"],
                horizontal=True,
                key=self._get_session_key("objective_action")
            )
            
            objective_metric = st.selectbox(
                "Metric:",
                options=[
                    "Sharpe Ratio",
                    "Expected Return",
                    "Volatility",
                    "Sortino Ratio",
                    "Maximum Drawdown",
                    "CVaR (5%)",
                    "Diversification Ratio",
                    "Income-Growth Balance"
                ],
                key=self._get_session_key("objective_metric")
            )
            
            # Target value if Target action selected
            target_value = None
            if objective_action == "Target":
                if "Return" in objective_metric:
                    target_value = st.number_input(
                        "Target Return (% annual):",
                        min_value=-10.0,
                        max_value=50.0,
                        value=12.0,
                        step=0.5,
                        key=self._get_session_key("target_value")
                    ) / 100
                elif "Volatility" in objective_metric:
                    target_value = st.number_input(
                        "Target Volatility (% annual):",
                        min_value=1.0,
                        max_value=50.0,
                        value=15.0,
                        step=0.5,
                        key=self._get_session_key("target_value")
                    ) / 100
                elif "Sharpe" in objective_metric:
                    target_value = st.number_input(
                        "Target Sharpe Ratio:",
                        min_value=0.0,
                        max_value=5.0,
                        value=1.5,
                        step=0.1,
                        key=self._get_session_key("target_value")
                    )
            
            # Additional parameters
            if objective_metric == "Income-Growth Balance":
                income_weight = st.slider(
                    "Income Weight (vs Growth):",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.1,
                    key=self._get_session_key("income_weight")
                )
            else:
                income_weight = 0.5
        
        with col2:
            st.subheader("Portfolio Constraints")
            st.caption("Set limits on portfolio metrics that must be satisfied")
            
            # Enable/disable constraints
            constraints = {}
            
            # Return constraint
            enable_return = st.checkbox("Expected Return Constraint", key=self._get_session_key("enable_return"))
            if enable_return:
                col_a, col_b = st.columns(2)
                with col_a:
                    return_type = st.radio("Type:", ["Min", "Max", "Range"], key=self._get_session_key("return_type"), horizontal=True)
                with col_b:
                    if return_type == "Min":
                        min_return = st.number_input("Min (%):", -50.0, 100.0, 8.0, 1.0, key=self._get_session_key("min_return"))
                        constraints['min_return'] = min_return / 100
                    elif return_type == "Max":
                        max_return = st.number_input("Max (%):", -50.0, 100.0, 25.0, 1.0, key=self._get_session_key("max_return"))
                        constraints['max_return'] = max_return / 100
                    else:
                        min_return = st.number_input("Min (%):", -50.0, 100.0, 8.0, 1.0, key=self._get_session_key("min_return"))
                        max_return = st.number_input("Max (%):", -50.0, 100.0, 20.0, 1.0, key=self._get_session_key("max_return"))
                        constraints['min_return'] = min_return / 100
                        constraints['max_return'] = max_return / 100
            
            # Volatility constraint
            enable_vol = st.checkbox("Volatility Constraint", key=self._get_session_key("enable_vol"))
            if enable_vol:
                col_a, col_b = st.columns(2)
                with col_a:
                    vol_type = st.radio("Type:", ["Min", "Max", "Range"], key=self._get_session_key("vol_type"), horizontal=True)
                with col_b:
                    if vol_type == "Min":
                        min_vol = st.number_input("Min (%):", 0.1, 100.0, 5.0, 1.0, key=self._get_session_key("min_vol"))
                        constraints['min_volatility'] = min_vol / 100
                    elif vol_type == "Max":
                        max_vol = st.number_input("Max (%):", 0.1, 100.0, 18.0, 1.0, key=self._get_session_key("max_vol"))
                        constraints['max_volatility'] = max_vol / 100
                    else:
                        min_vol = st.number_input("Min (%):", 0.1, 100.0, 8.0, 1.0, key=self._get_session_key("min_vol"))
                        max_vol = st.number_input("Max (%):", 0.1, 100.0, 18.0, 1.0, key=self._get_session_key("max_vol"))
                        constraints['min_volatility'] = min_vol / 100
                        constraints['max_volatility'] = max_vol / 100
            
            # Sharpe constraint
            enable_sharpe = st.checkbox("Sharpe Ratio Constraint", key=self._get_session_key("enable_sharpe"))
            if enable_sharpe:
                col_a, col_b = st.columns(2)
                with col_a:
                    sharpe_type = st.radio("Type:", ["Min", "Max", "Range"], key=self._get_session_key("sharpe_type"), horizontal=True)
                with col_b:
                    if sharpe_type == "Min":
                        min_sharpe = st.number_input("Min:", 0.0, 5.0, 1.0, 0.1, key=self._get_session_key("min_sharpe"))
                        constraints['min_sharpe'] = min_sharpe
                    elif sharpe_type == "Max":
                        max_sharpe = st.number_input("Max:", 0.0, 5.0, 2.5, 0.1, key=self._get_session_key("max_sharpe"))
                        constraints['max_sharpe'] = max_sharpe
                    else:
                        min_sharpe = st.number_input("Min:", 0.0, 5.0, 1.0, 0.1, key=self._get_session_key("min_sharpe"))
                        max_sharpe = st.number_input("Max:", 0.0, 5.0, 2.5, 0.1, key=self._get_session_key("max_sharpe"))
                        constraints['min_sharpe'] = min_sharpe
                        constraints['max_sharpe'] = max_sharpe
            
            # Concentration constraint
            enable_conc = st.checkbox("Position Size Constraints", key=self._get_session_key("enable_conc"))
            if enable_conc:
                max_weight = st.number_input(
                    "Max Single Position (%):",
                    min_value=1.0,
                    max_value=100.0,
                    value=30.0,
                    step=1.0,
                    key=self._get_session_key("max_weight")
                )
                constraints['max_concentration'] = max_weight / 100
                
                min_weight = st.number_input(
                    "Min Position Size (%) [if held]:",
                    min_value=0.0,
                    max_value=50.0,
                    value=2.0,
                    step=1.0,
                    key=self._get_session_key("min_weight")
                )
                constraints['min_position'] = min_weight / 100
        
        
        
        # Optimize button
        if st.button("Run Optimization", type="primary", use_container_width=True):
            with st.spinner("Running constrained optimization..."):
                result = self._run_optimization(
                    returns_df,
                    symbols,
                    objective_action,
                    objective_metric,
                    target_value,
                    constraints,
                    income_weight
                )
            
            if result is None or not result.success:
                st.error(f"Optimization failed: {result.message if result else 'Unknown error'}")
                return
            
            # Display results
            self._render_optimization_results(symbols, result, returns_df, constraints, 
                                             objective_action, objective_metric, target_value)
    
    def _run_optimization(self, returns_df: pd.DataFrame, symbols: List[str],
                         objective_action: str, objective_metric: str, target_value: Optional[float],
                         constraints: Dict, income_weight: float) -> Optional[OptimizationResult]:
        """Run the constrained optimization."""
        n_assets = len(returns_df.columns)
        
        # Get dividend yields if needed
        dividend_yields = None
        if "Income-Growth" in objective_metric:
            dividend_yields = self._get_dividend_yields(symbols)
        
        # Define objective function based on action + metric
        def objective(weights):
            portfolio_return = np.dot(weights, returns_df.mean() * 252)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * 252, weights)))
            
            # Calculate the metric
            if objective_metric == "Sharpe Ratio":
                metric_value = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
            elif objective_metric == "Expected Return":
                metric_value = portfolio_return
            elif objective_metric == "Volatility":
                metric_value = portfolio_vol
            elif objective_metric == "Sortino Ratio":
                downside_returns = returns_df[returns_df < 0]
                downside_std = np.sqrt(np.dot(weights.T, np.dot(downside_returns.cov() * 252, weights)))
                metric_value = portfolio_return / downside_std if downside_std > 0 else 0
            elif objective_metric == "Maximum Drawdown":
                portfolio_returns = (returns_df * weights).sum(axis=1)
                cumulative = (1 + portfolio_returns).cumprod()
                running_max = cumulative.cummax()
                drawdown = ((cumulative - running_max) / running_max).min()
                metric_value = abs(drawdown)
            elif objective_metric == "CVaR (5%)":
                portfolio_returns = (returns_df * weights).sum(axis=1)
                var = np.percentile(portfolio_returns, 5)
                cvar = portfolio_returns[portfolio_returns <= var].mean()
                metric_value = abs(cvar)
            elif objective_metric == "Diversification Ratio":
                weighted_vol = np.dot(weights, returns_df.std() * np.sqrt(252))
                portfolio_vol_calc = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * 252, weights)))
                metric_value = weighted_vol / portfolio_vol_calc if portfolio_vol_calc > 0 else 0
            elif objective_metric == "Income-Growth Balance":
                portfolio_yield = np.dot(weights, dividend_yields)
                metric_value = income_weight * portfolio_yield + (1 - income_weight) * portfolio_return
            else:
                metric_value = 0
            
            # Apply action
            if objective_action == "Maximize":
                return -metric_value
            elif objective_action == "Minimize":
                return metric_value
            elif objective_action == "Target":
                return abs(metric_value - target_value)
            else:
                return 0
        
        # Set up constraints
        constraint_list = []
        
        # Weights sum to 1
        constraint_list.append({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        
        # Return constraints
        if 'min_return' in constraints:
            constraint_list.append({
                'type': 'ineq',
                'fun': lambda w: np.dot(w, returns_df.mean() * 252) - constraints['min_return']
            })
        if 'max_return' in constraints:
            constraint_list.append({
                'type': 'ineq',
                'fun': lambda w: constraints['max_return'] - np.dot(w, returns_df.mean() * 252)
            })
        
        # Volatility constraints
        if 'min_volatility' in constraints:
            constraint_list.append({
                'type': 'ineq',
                'fun': lambda w: np.sqrt(np.dot(w.T, np.dot(returns_df.cov() * 252, w))) - constraints['min_volatility']
            })
        if 'max_volatility' in constraints:
            constraint_list.append({
                'type': 'ineq',
                'fun': lambda w: constraints['max_volatility'] - np.sqrt(np.dot(w.T, np.dot(returns_df.cov() * 252, w)))
            })
        
        # Sharpe constraints
        if 'min_sharpe' in constraints:
            def sharpe_constraint_min(w):
                ret = np.dot(w, returns_df.mean() * 252)
                vol = np.sqrt(np.dot(w.T, np.dot(returns_df.cov() * 252, w)))
                return (ret / vol) - constraints['min_sharpe'] if vol > 0 else -1e10
            constraint_list.append({'type': 'ineq', 'fun': sharpe_constraint_min})
        if 'max_sharpe' in constraints:
            def sharpe_constraint_max(w):
                ret = np.dot(w, returns_df.mean() * 252)
                vol = np.sqrt(np.dot(w.T, np.dot(returns_df.cov() * 252, w)))
                return constraints['max_sharpe'] - (ret / vol) if vol > 0 else -1e10
            constraint_list.append({'type': 'ineq', 'fun': sharpe_constraint_max})
        
        # Drawdown constraint
        if 'max_drawdown' in constraints:
            def drawdown_constraint(w):
                portfolio_returns = (returns_df * w).sum(axis=1)
                cumulative = (1 + portfolio_returns).cumprod()
                running_max = cumulative.cummax()
                drawdown = ((cumulative - running_max) / running_max).min()
                return constraints['max_drawdown'] + drawdown
            constraint_list.append({'type': 'ineq', 'fun': drawdown_constraint})
        
        # Bounds
        if 'max_concentration' in constraints:
            bounds = tuple((0, constraints['max_concentration']) for _ in range(n_assets))
        else:
            bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Run optimization
        try:
            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraint_list,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )
            
            if not result.success:
                return OptimizationResult(
                    weights=initial_weights,
                    objective_value=0,
                    expected_return=0,
                    volatility=0,
                    sharpe_ratio=0,
                    max_drawdown=0,
                    sortino_ratio=0,
                    dividend_yield=0,
                    cvar_5pct=0,
                    diversification_ratio=0,
                    success=False,
                    message=result.message,
                    constraints_satisfied={},
                    constraint_violations={}
                )
            
            # Apply minimum position constraint if enabled
            weights = result.x
            if 'min_position' in constraints:
                min_pos = constraints['min_position']
                # Zero out positions below minimum
                weights[weights < min_pos] = 0
                # Renormalize
                if weights.sum() > 0:
                    weights = weights / weights.sum()
                else:
                    return OptimizationResult(
                        weights=initial_weights,
                        objective_value=0,
                        expected_return=0,
                        volatility=0,
                        sharpe_ratio=0,
                        max_drawdown=0,
                        sortino_ratio=0,
                        dividend_yield=0,
                        cvar_5pct=0,
                        diversification_ratio=0,
                        success=False,
                        message="No positions meet minimum size requirement",
                        constraints_satisfied={},
                        constraint_violations={}
                    )
            
            # Calculate final metrics
            portfolio_return = np.dot(weights, returns_df.mean() * 252)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * 252, weights)))
            sharpe = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
            
            portfolio_returns = (returns_df * weights).sum(axis=1)
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.cummax()
            max_dd = ((cumulative - running_max) / running_max).min()
            
            downside_returns = returns_df[returns_df < 0]
            downside_std = np.sqrt(np.dot(weights.T, np.dot(downside_returns.cov() * 252, weights)))
            sortino = portfolio_return / downside_std if downside_std > 0 else 0
            
            # Calculate CVaR (5%)
            sorted_returns = np.sort(portfolio_returns.values)
            var_index = int(len(sorted_returns) * 0.05)
            cvar_5pct = sorted_returns[:var_index].mean() if var_index > 0 else sorted_returns[0]
            
            # Calculate diversification ratio
            individual_vols = returns_df.std() * np.sqrt(252)
            weighted_vol = np.dot(weights, individual_vols)
            diversification_ratio = weighted_vol / portfolio_vol if portfolio_vol > 0 else 1.0
            
            div_yield = 0
            if dividend_yields is not None:
                div_yield = np.dot(weights, dividend_yields)
            
            # Check constraint satisfaction WITH violation amounts
            constraints_satisfied = {}
            constraint_violations = {}
            
            if 'min_return' in constraints:
                satisfied = portfolio_return >= constraints['min_return']
                constraints_satisfied['Min Return'] = satisfied
                if not satisfied:
                    constraint_violations['Min Return'] = portfolio_return - constraints['min_return']
            
            if 'max_return' in constraints:
                satisfied = portfolio_return <= constraints['max_return']
                constraints_satisfied['Max Return'] = satisfied
                if not satisfied:
                    constraint_violations['Max Return'] = portfolio_return - constraints['max_return']
            
            if 'min_volatility' in constraints:
                satisfied = portfolio_vol >= constraints['min_volatility']
                constraints_satisfied['Min Volatility'] = satisfied
                if not satisfied:
                    constraint_violations['Min Volatility'] = portfolio_vol - constraints['min_volatility']
            
            if 'max_volatility' in constraints:
                satisfied = portfolio_vol <= constraints['max_volatility']
                constraints_satisfied['Max Volatility'] = satisfied
                if not satisfied:
                    constraint_violations['Max Volatility'] = portfolio_vol - constraints['max_volatility']
            
            if 'min_sharpe' in constraints:
                satisfied = sharpe >= constraints['min_sharpe']
                constraints_satisfied['Min Sharpe'] = satisfied
                if not satisfied:
                    constraint_violations['Min Sharpe'] = sharpe - constraints['min_sharpe']
            
            if 'max_sharpe' in constraints:
                satisfied = sharpe <= constraints['max_sharpe']
                constraints_satisfied['Max Sharpe'] = satisfied
                if not satisfied:
                    constraint_violations['Max Sharpe'] = sharpe - constraints['max_sharpe']
            
            if 'max_concentration' in constraints:
                satisfied = weights.max() <= constraints['max_concentration']
                constraints_satisfied['Max Concentration'] = satisfied
                if not satisfied:
                    constraint_violations['Max Concentration'] = weights.max() - constraints['max_concentration']
            
            return OptimizationResult(
                weights=weights,
                objective_value=result.fun,
                expected_return=portfolio_return,
                volatility=portfolio_vol,
                sharpe_ratio=sharpe,
                max_drawdown=abs(max_dd),
                sortino_ratio=sortino,
                dividend_yield=div_yield,
                cvar_5pct=cvar_5pct,
                diversification_ratio=diversification_ratio,
                success=True,
                message="Optimization successful",
                constraints_satisfied=constraints_satisfied,
                constraint_violations=constraint_violations
            )
            
        except Exception as e:
            return OptimizationResult(
                weights=initial_weights,
                objective_value=0,
                expected_return=0,
                volatility=0,
                sharpe_ratio=0,
                max_drawdown=0,
                sortino_ratio=0,
                dividend_yield=0,
                cvar_5pct=0,
                diversification_ratio=0,
                success=False,
                message=str(e),
                constraints_satisfied={},
                constraint_violations={}
            )
    
    def _get_dividend_yields(self, symbols: List[str]) -> np.ndarray:
        """Get dividend yields for symbols."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        yields = []
        
        for symbol in symbols:
            try:
                dividends = self.storage.get_dividends(symbol, start_date, end_date)
                price_df = self.storage.get_price_data(symbol, start_date, end_date)
                
                if dividends and len(dividends) > 0 and price_df is not None:
                    total_dividends = sum(d['amount'] for d in dividends)
                    avg_price = price_df['close'].mean()
                    yields.append(total_dividends / avg_price if avg_price > 0 else 0.0)
                else:
                    yields.append(0.0)
            except:
                yields.append(0.0)
        
        return np.array(yields)
    
    def _render_optimization_results(self, symbols: List[str], result: OptimizationResult,
                                    returns_df: pd.DataFrame, constraints: Dict,
                                    objective_action: str, objective_metric: str, target_value: Optional[float]):
        """Render optimization results with detailed analysis."""
        if result.success:
            st.success("✓ Optimization completed successfully!")
        else:
            st.error(f"✗ Optimization failed: {result.message}")
            if result.constraint_violations:
                with st.expander("View Constraint Violations", expanded=True):
                    st.warning("**The following constraints could not be satisfied:**")
                    for constraint_name, violation in result.constraint_violations.items():
                        st.write(f"- **{constraint_name}**: Violated by {violation:.4f}")
                    st.info("💡 Try relaxing some constraints or changing the objective")
            return
        
        # Display objective
        st.subheader("Optimization Objective")
        if objective_action == "Target":
            if "Return" in objective_metric:
                st.info(f"**{objective_action} {objective_metric}:** {target_value * 100:.2f}%")
            elif "Volatility" in objective_metric:
                st.info(f"**{objective_action} {objective_metric}:** {target_value * 100:.2f}%")
            else:
                st.info(f"**{objective_action} {objective_metric}:** {target_value:.2f}")
        else:
            st.info(f"**{objective_action} {objective_metric}**")
        
        # Constraint satisfaction status with violation details
        if result.constraints_satisfied:
            st.subheader("Constraint Satisfaction")
            
            all_satisfied = all(result.constraints_satisfied.values())
            if all_satisfied:
                st.success("✓ All constraints satisfied")
            else:
                st.warning("⚠️ Some constraints violated")
            
            # Show constraint details in columns
            constraint_items = list(result.constraints_satisfied.items())
            num_cols = min(4, len(constraint_items))
            cols = st.columns(num_cols)
            
            for idx, (constraint_name, satisfied) in enumerate(constraint_items):
                with cols[idx % num_cols]:
                    status = "✓" if satisfied else "✗"
                    color = "green" if satisfied else "red"
                    violation = result.constraint_violations.get(constraint_name, 0)
                    
                    if satisfied:
                        st.markdown(f":{color}[**{status}** {constraint_name}]")
                    else:
                        st.markdown(f":{color}[**{status}** {constraint_name}]")
                        st.caption(f"Missed by: {abs(violation):.4f}")
        
        st.space(2)
        
        # Portfolio metrics in enhanced grid
        st.subheader("Portfolio Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Expected Return", f"{result.expected_return * 100:.2f}%")
            st.metric("Volatility", f"{result.volatility * 100:.2f}%")
        
        with col2:
            st.metric("Sharpe Ratio", f"{result.sharpe_ratio:.2f}")
            st.metric("Sortino Ratio", f"{result.sortino_ratio:.2f}")
        
        with col3:
            st.metric("Max Drawdown", f"{result.max_drawdown * 100:.2f}%")
            st.metric("CVaR (5%)", f"{result.cvar_5pct * 100:.2f}%")
        
        with col4:
            st.metric("Diversification", f"{result.diversification_ratio:.2f}")
            if result.dividend_yield > 0:
                st.metric("Dividend Yield", f"{result.dividend_yield * 100:.2f}%")
            else:
                st.metric("Concentration", f"{(1/result.diversification_ratio):.2f}")
        
        with col5:
            active_positions = (result.weights > 0.001).sum()
            st.metric("Active Positions", f"{active_positions}/{len(symbols)}")
            max_position = result.weights.max()
            st.metric("Max Position", f"{max_position * 100:.2f}%")
        
        st.space(2)
        
        # Portfolio weights
        st.subheader("Portfolio Allocation")
        
        # Create DataFrame for display
        weights_data = []
        for symbol, weight in zip(symbols, result.weights):
            if weight > 0.001:  # Only show positions > 0.1%
                weights_data.append({
                    'Symbol': symbol,
                    'Weight': f"{weight * 100:.2f}%",
                    'Weight_Value': weight
                })
        
        weights_df = pd.DataFrame(weights_data)
        weights_df = weights_df.sort_values('Weight_Value', ascending=False)
        display_df = weights_df.drop('Weight_Value', axis=1).reset_index(drop=True)
        
        st.dataframe(display_df, width='stretch', hide_index=True)
        
        # Visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=[wd['Symbol'] for wd in weights_data],
                values=[wd['Weight_Value'] for wd in weights_data],
                hole=0.3
            )])
            fig_pie.update_layout(
                title="Portfolio Allocation",
                height=400
            )
            st.plotly_chart(fig_pie, width='stretch')
        
        with col2:
            # Bar chart
            fig_bar = go.Figure(data=[go.Bar(
                x=[wd['Symbol'] for wd in weights_data],
                y=[wd['Weight_Value'] * 100 for wd in weights_data],
                marker_color='steelblue'
            )])
            fig_bar.update_layout(
                title="Position Sizes",
                xaxis_title="Symbol",
                yaxis_title="Weight (%)",
                height=400
            )
            st.plotly_chart(fig_bar, width='stretch')
        
        # Historical performance
        st.space(2)
        st.subheader("Historical Performance")
        
        portfolio_returns = (returns_df * result.weights).sum(axis=1)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cumulative_returns.index,
            y=cumulative_returns.values,
            mode='lines',
            name='Portfolio',
            line=dict(color='steelblue', width=2)
        ))
        
        fig.update_layout(
            title="Cumulative Returns",
            xaxis_title="Date",
            yaxis_title="Cumulative Return",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Export and actionable insights
        st.space(2)
        st.subheader("Export & Next Steps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export button
            export_df = weights_df.copy()
            export_df['Expected_Return_Annual'] = f"{result.expected_return * 100:.2f}%"
            export_df['Volatility_Annual'] = f"{result.volatility * 100:.2f}%"
            export_df['Sharpe_Ratio'] = f"{result.sharpe_ratio:.2f}"
            
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Portfolio as CSV",
                data=csv,
                file_name=f"optimized_portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.info("""
            **💡 Actionable Insights:**
            - Review positions > 20% for concentration risk
            - Consider rebalancing quarterly to maintain weights
            - Monitor constraint satisfaction over time
            - Use Monte Carlo to test this allocation
            """)
        
        # If optimization hit constraints, show suggestions
        if result.constraint_violations:
            with st.expander("💡 Optimization Suggestions", expanded=False):
                st.write("**Your optimization hit some constraint boundaries. Consider:**")
                for name, violation in result.constraint_violations.items():
                    if abs(violation) > 0.001:
                        st.write(f"- Relaxing **{name}** constraint by at least {abs(violation):.2%}")
                st.write("- Trying a different objective function")
                st.write("- Adding more instruments to the universe")
