"""
Time Series Analysis Widget - Econometric analysis including mean reversion, cointegration, and stationarity tests.

ARCHITECTURE: This widget follows the layered architecture pattern:
- UI Layer: Streamlit rendering (_render_* methods)
- Data Layer: Historical data fetching and preparation
- Logic Layer: Statistical tests and econometric analysis (_analyze_* static methods)
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss, coint, acf, pacf, grangercausalitytests
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.graphics.gofplots import qqplot

from .layered_base_widget import LayeredBaseWidget
from src.utils.performance_metrics import calculate_returns


@dataclass
class StationarityResults:
    """Results from stationarity tests."""
    adf_statistic: float
    adf_pvalue: float
    adf_critical_values: Dict[str, float]
    adf_is_stationary: bool
    kpss_statistic: float
    kpss_pvalue: float
    kpss_critical_values: Dict[str, float]
    kpss_is_stationary: bool


@dataclass
class MeanReversionResults:
    """Results from mean reversion analysis."""
    half_life: float
    mean_reversion_speed: float
    equilibrium_level: float
    current_z_score: float
    is_mean_reverting: bool


@dataclass
class CointegrationResults:
    """Results from cointegration analysis."""
    coint_statistic: float
    coint_pvalue: float
    is_cointegrated: bool
    hedge_ratio: float
    spread_mean: float
    spread_std: float
    current_z_score: float


@dataclass
class DiagnosticsResults:
    """Results from diagnostic tests."""
    ljung_box_statistic: float
    ljung_box_pvalue: float
    has_serial_correlation: bool
    jarque_bera_statistic: float
    jarque_bera_pvalue: float
    is_normal: bool
    skewness: float
    kurtosis: float
    variance_ratio: float
    vr_test_statistic: float
    vr_pvalue: float
    is_random_walk: bool


@dataclass
class GrangerResults:
    """Results from Granger causality test."""
    max_lag: int
    causes: bool
    best_lag: int
    best_pvalue: float
    all_pvalues: Dict[int, float]


@dataclass
class StructuralBreakResults:
    """Results from structural break detection."""
    has_break: bool
    break_date: Optional[datetime]
    test_statistic: float
    pre_mean: float
    post_mean: float
    pre_vol: float
    post_vol: float


class TimeSeriesAnalysisWidget(LayeredBaseWidget):
    """Widget for econometric time series analysis"""
    
    def get_name(self) -> str:
        return "Time Series Analysis"
    
    def get_description(self) -> str:
        return "Econometric analysis including mean reversion, cointegration, stationarity tests, and statistical properties"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    # ========================================================================
    # UI LAYER - Streamlit rendering methods
    # ========================================================================
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Main render orchestration.
        
        Parameters:
            instruments: List of instrument dictionaries
            selected_symbols: Optional list of pre-selected symbols
        """
        with st.container(border=True):
            if not instruments:
                st.info("No instruments available")
                return
            
            # Get all instruments for analysis selection
            # Use active_only=False to include ALL instruments
            all_instruments = self.storage.get_all_instruments(active_only=False)
            
            if not all_instruments:
                st.info("No instruments available for analysis")
                return
            
            # Analysis scope selection
            col_scope1, col_scope2 = st.columns([1, 2])
            
            with col_scope1:
                analysis_scope = st.radio(
                    "Analysis Scope:",
                    options=["Portfolio", "Individual Asset"],
                    key=self._get_session_key("analysis_scope"),
                    help="Portfolio analysis uses current holdings; Individual analysis examines single instruments"
                )
            
            with col_scope2:
                if analysis_scope == "Portfolio":
                    st.info("📊 Portfolio analysis uses your current holdings and weights for econometric testing")
                else:
                    st.info("📈 Individual analysis examines single instruments for trading/rebalancing decisions")
            
            st.space(1)
            
            # Analysis type selection based on scope
            if analysis_scope == "Portfolio":
                analysis_type = st.selectbox(
                    "Select Analysis Type:",
                    options=[
                        "Portfolio Stationarity & Returns",
                        "Portfolio Mean Reversion",
                        "Portfolio Diagnostics",
                        "Portfolio Autocorrelation",
                        "Portfolio Volatility Regime",
                        "Portfolio Rolling Statistics",
                        "Portfolio Structural Breaks"
                    ],
                    key=self._get_session_key("analysis_type_portfolio")
                )
            else:
                analysis_type = st.selectbox(
                    "Select Analysis Type:",
                    options=[
                        "Stationarity Tests",
                        "Mean Reversion Analysis",
                        "Cointegration (Pairs)",
                        "Autocorrelation & PACF",
                        "Volatility Clustering",
                        "Diagnostic Tests",
                        "Granger Causality",
                        "Rolling Statistics",
                        "Structural Breaks"
                    ],
                    key=self._get_session_key("analysis_type_individual")
                )
            
            # Route based on scope and type
            if analysis_scope == "Portfolio":
                if analysis_type == "Portfolio Stationarity & Returns":
                    self._render_portfolio_stationarity(instruments)
                elif analysis_type == "Portfolio Mean Reversion":
                    self._render_portfolio_mean_reversion(instruments)
                elif analysis_type == "Portfolio Diagnostics":
                    self._render_portfolio_diagnostics(instruments)
                elif analysis_type == "Portfolio Autocorrelation":
                    self._render_portfolio_autocorrelation(instruments)
                elif analysis_type == "Portfolio Volatility Regime":
                    self._render_portfolio_volatility(instruments)
                elif analysis_type == "Portfolio Rolling Statistics":
                    self._render_portfolio_rolling_stats(instruments)
                elif analysis_type == "Portfolio Structural Breaks":
                    self._render_portfolio_structural_breaks(instruments)
            else:
                if analysis_type == "Stationarity Tests":
                    self._render_stationarity_analysis(all_instruments)
                elif analysis_type == "Mean Reversion Analysis":
                    self._render_mean_reversion_analysis(all_instruments)
                elif analysis_type == "Cointegration (Pairs)":
                    self._render_cointegration_analysis(all_instruments)
                elif analysis_type == "Autocorrelation & PACF":
                    self._render_autocorrelation_analysis(all_instruments)
                elif analysis_type == "Volatility Clustering":
                    self._render_volatility_clustering(all_instruments)
                elif analysis_type == "Diagnostic Tests":
                    self._render_diagnostic_tests(all_instruments)
                elif analysis_type == "Granger Causality":
                    self._render_granger_causality(all_instruments)
                elif analysis_type == "Rolling Statistics":
                    self._render_rolling_statistics(all_instruments)
                elif analysis_type == "Structural Breaks":
                    self._render_structural_breaks(all_instruments)
    
    def _render_stationarity_analysis(self, instruments: List[Dict]):
        """Render stationarity tests (ADF and KPSS)."""
        
        st.markdown("### Stationarity Tests")
        st.caption("Test whether a time series has a unit root (non-stationary) or is trend-stationary")
        
        # Symbol selection
        symbols = sorted([i['symbol'] for i in instruments])
        selected_symbol = st.selectbox(
            "Select instrument:",
            options=symbols,
            key=self._get_session_key("stat_symbol")
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            lookback_days = st.slider(
                "Lookback period (days):",
                min_value=90,
                max_value=730,
                value=365,
                step=30,
                key=self._get_session_key("stat_lookback")
            )
        
        with col2:
            test_on = st.radio(
                "Test on:",
                options=["Price Level", "Returns", "Log Returns"],
                key=self._get_session_key("stat_test_on")
            )
        
        if st.button("Run Stationarity Tests", width="stretch"):
            with st.spinner("Running statistical tests..."):
                # Fetch data
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                price_df = self.storage.get_price_data(selected_symbol, start_date, end_date)
                
                if price_df is None or len(price_df) < 30:
                    st.error("Insufficient data for analysis")
                    return
                
                # Prepare series
                if test_on == "Price Level":
                    series = price_df['close']
                    series_name = "Price"
                elif test_on == "Returns":
                    series = calculate_returns(price_df['close'])
                    series_name = "Returns"
                else:  # Log Returns
                    series = np.log(price_df['close'] / price_df['close'].shift(1))
                    series_name = "Log Returns"
                
                series = series.dropna()
                
                # Run tests
                results = self._test_stationarity(series)
                
                # Display results
                self._render_stationarity_results(results, selected_symbol, series_name, series)
    
    def _render_stationarity_results(self, results: StationarityResults, symbol: str, 
                                     series_name: str, series: pd.Series):
        """Display stationarity test results."""
        

        st.markdown("### Test Results")
        
        # Summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Augmented Dickey-Fuller Test")
            st.markdown("**Null Hypothesis:** Series has a unit root (non-stationary)")
            
            if results.adf_is_stationary:
                st.success(f"✓ Series is **stationary** (reject null hypothesis)")
            else:
                st.warning(f"✗ Series is **non-stationary** (fail to reject null)")
            
            st.metric("Test Statistic", f"{results.adf_statistic:.4f}")
            st.metric("P-value", f"{results.adf_pvalue:.4f}")
            
            with st.expander("Critical Values"):
                for level, value in results.adf_critical_values.items():
                    st.text(f"{level}: {value:.4f}")
        
        with col2:
            st.markdown("#### KPSS Test")
            st.markdown("**Null Hypothesis:** Series is trend-stationary")
            
            if results.kpss_is_stationary:
                st.success(f"✓ Series is **stationary** (fail to reject null)")
            else:
                st.warning(f"✗ Series is **non-stationary** (reject null hypothesis)")
            
            st.metric("Test Statistic", f"{results.kpss_statistic:.4f}")
            st.metric("P-value", f"{results.kpss_pvalue:.4f}")
            
            with st.expander("Critical Values"):
                for level, value in results.kpss_critical_values.items():
                    st.text(f"{level}: {value:.4f}")
        
        # Interpretation

        st.markdown("### Interpretation")
        
        if results.adf_is_stationary and results.kpss_is_stationary:
            st.success("**Both tests indicate stationarity** - The series appears to be stationary.")
        elif not results.adf_is_stationary and not results.kpss_is_stationary:
            st.error("**Both tests indicate non-stationarity** - The series appears to have a unit root.")
        else:
            st.warning("**Tests disagree** - Consider differencing the series or investigating further.")
        
        # Plot
        self._render_series_plot(series, symbol, series_name)
    
    def _render_mean_reversion_analysis(self, instruments: List[Dict]):
        """Render mean reversion analysis with econometric rigor."""
        
        st.markdown("### Mean Reversion Analysis")
        st.caption("Econometrically rigorous mean reversion analysis (tests stationarity first)")
        
        symbols = sorted([i['symbol'] for i in instruments])
        selected_symbol = st.selectbox(
            "Select instrument:",
            options=symbols,
            key=self._get_session_key("mr_symbol")
        )
        
        lookback_days = st.slider(
            "Lookback period (days):",
            min_value=90,
            max_value=730,
            value=365,
            step=30,
            key=self._get_session_key("mr_lookback")
        )
        
        if st.button("Analyze Mean Reversion", width="stretch"):
            with st.spinner("Running econometric analysis..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                price_df = self.storage.get_price_data(selected_symbol, start_date, end_date)
                
                if price_df is None or len(price_df) < 30:
                    st.error("Insufficient data for analysis")
                    return
                
                prices = price_df['close']
                
                # STEP 1: Test stationarity of price series
                st.markdown("#### Step 1: Stationarity Check")
                stat_results = self._test_stationarity(prices)
                
                col1, col2 = st.columns(2)
                with col1:
                    if stat_results.adf_is_stationary:
                        st.success("✓ ADF: Stationary (p={:.4f})".format(stat_results.adf_pvalue))
                    else:
                        st.warning("✗ ADF: Non-stationary (p={:.4f})".format(stat_results.adf_pvalue))
                
                with col2:
                    if stat_results.kpss_is_stationary:
                        st.success("✓ KPSS: Stationary (p={:.4f})".format(stat_results.kpss_pvalue))
                    else:
                        st.warning("✗ KPSS: Non-stationary (p={:.4f})".format(stat_results.kpss_pvalue))
                
                st.space(1)
                
                # STEP 2: Make stationary if needed
                series_to_analyze = prices
                series_name = "Price"
                transformation = "none"
                
                if not (stat_results.adf_is_stationary and stat_results.kpss_is_stationary):
                    st.markdown("#### Step 2: Transform to Stationary Series")
                    st.warning("⚠️ Series is non-stationary. Applying first-difference transformation...")
                    
                    # Apply first difference
                    series_to_analyze = prices.diff().dropna()
                    series_name = "Price Change (First Difference)"
                    transformation = "first_difference"
                    
                    # Re-test stationarity
                    diff_stat = self._test_stationarity(series_to_analyze)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if diff_stat.adf_is_stationary:
                            st.success("✓ After differencing - ADF: Stationary (p={:.4f})".format(diff_stat.adf_pvalue))
                        else:
                            st.error("✗ Still non-stationary after differencing. Mean reversion analysis may be invalid.")
                    
                    with col2:
                        if diff_stat.kpss_is_stationary:
                            st.success("✓ After differencing - KPSS: Stationary (p={:.4f})".format(diff_stat.kpss_pvalue))
                    
                    st.space(1)
                else:
                    st.markdown("#### Step 2: Series is Stationary")
                    st.success("✓ Both tests confirm stationarity. Proceeding with mean reversion analysis...")
                    st.space(1)
                
                # STEP 3: Run mean reversion analysis on stationary series
                st.markdown("#### Step 3: Mean Reversion Properties")
                results = self._analyze_mean_reversion(series_to_analyze, is_differenced=(transformation == "first_difference"))
                
                # Display results
                self._render_mean_reversion_results(results, selected_symbol, series_to_analyze, series_name, transformation)
    
    def _render_mean_reversion_results(self, results: MeanReversionResults, 
                                       symbol: str, series: pd.Series, series_name: str, transformation: str):
        """Display mean reversion results."""
        

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Half-Life (days)", f"{results.half_life:.1f}")
        
        with col2:
            st.metric("Reversion Speed", f"{results.mean_reversion_speed:.4f}")
        
        with col3:
            if transformation == "first_difference":
                st.metric("Equilibrium (Daily Change)", f"${results.equilibrium_level:.4f}")
            else:
                st.metric("Equilibrium Level", f"${results.equilibrium_level:.2f}")
        
        with col4:
            st.metric("Current Z-Score", f"{results.current_z_score:.2f}")
        

        
        # Interpretation
        if results.is_mean_reverting:
            st.success(f"**Mean reverting detected** - Half-life of {results.half_life:.1f} days suggests reversion to equilibrium")
            
            if transformation == "first_difference":
                st.info("🎯 **Trading Implication**: Price changes revert to near-zero, indicating prices oscillate around a stable level. Consider mean-reversion strategies.")
            else:
                st.info(f"🎯 **Trading Implication**: Prices revert toward ${results.equilibrium_level:.2f}. Current z-score of {results.current_z_score:.2f} indicates {'overbought' if results.current_z_score > 1 else 'oversold' if results.current_z_score < -1 else 'neutral'} conditions.")
        else:
            st.warning("**Weak or no mean reversion** - Series may be trending or random walk")
            st.info("💡 **Trading Implication**: Mean-reversion strategies NOT recommended. Consider trend-following or momentum approaches instead.")
        
        with st.expander("Understanding the Metrics"):
            st.markdown("""
            - **Half-Life**: Time (in days) for deviations to revert halfway back to equilibrium
            - **Reversion Speed**: Rate at which deviations dissipate (higher = faster mean reversion)
            - **Equilibrium Level**: Long-term mean level (or mean change if differenced)
            - **Z-Score**: Current deviation from equilibrium in standard deviations
            
            **Econometric Note**: Analysis performed on stationary series. If differencing was applied, 
            results indicate reversion in price *changes*, not price levels.
            """)
        
        st.space(1)
        
        # Plot with equilibrium and bands
        self._render_mean_reversion_plot(series, results, symbol, series_name)
    
    def _render_cointegration_analysis(self, instruments: List[Dict]):
        """Render cointegration (pairs trading) analysis."""
        
        st.markdown("### Cointegration Analysis")
        st.caption("Test for long-run equilibrium relationship between two instruments (pairs trading)")
        
        symbols = sorted([i['symbol'] for i in instruments])
        
        col1, col2 = st.columns(2)
        
        with col1:
            symbol1 = st.selectbox(
                "First instrument:",
                options=symbols,
                key=self._get_session_key("coint_symbol1")
            )
        
        with col2:
            remaining_symbols = [s for s in symbols if s != symbol1]
            symbol2 = st.selectbox(
                "Second instrument:",
                options=remaining_symbols,
                key=self._get_session_key("coint_symbol2")
            )
        
        lookback_days = st.slider(
            "Lookback period (days):",
            min_value=180,
            max_value=730,
            value=365,
            step=30,
            key=self._get_session_key("coint_lookback")
        )
        
        if st.button("Test Cointegration", width="stretch"):
            with st.spinner("Running cointegration test..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                
                price_df1 = self.storage.get_price_data(symbol1, start_date, end_date)
                price_df2 = self.storage.get_price_data(symbol2, start_date, end_date)
                
                if price_df1 is None or price_df2 is None:
                    st.error("Insufficient data for one or both instruments")
                    return
                
                # Align data
                prices1 = price_df1['close']
                prices2 = price_df2['close']
                
                aligned_df = pd.DataFrame({
                    symbol1: prices1,
                    symbol2: prices2
                }).dropna()
                
                if len(aligned_df) < 30:
                    st.error("Insufficient overlapping data")
                    return
                
                # Run analysis
                results = self._analyze_cointegration(
                    aligned_df[symbol1],
                    aligned_df[symbol2]
                )
                
                # Display results
                self._render_cointegration_results(results, symbol1, symbol2, aligned_df)
    
    def _render_cointegration_results(self, results: CointegrationResults,
                                      symbol1: str, symbol2: str, prices_df: pd.DataFrame):
        """Display cointegration results."""
        

        st.markdown("### Cointegration Test Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Test Statistic", f"{results.coint_statistic:.4f}")
            st.metric("P-value", f"{results.coint_pvalue:.4f}")
        
        with col2:
            st.metric("Hedge Ratio", f"{results.hedge_ratio:.4f}")
            st.metric("Spread Std Dev", f"{results.spread_std:.4f}")
        
        with col3:
            st.metric("Spread Mean", f"{results.spread_mean:.4f}")
            st.metric("Current Z-Score", f"{results.current_z_score:.2f}")
        

        
        if results.is_cointegrated:
            st.success(f"**Cointegrated pair detected** (p-value < 0.05) - {symbol1} and {symbol2} have a long-run equilibrium relationship")
            st.info(f"**Trading Signal**: Spread is {abs(results.current_z_score):.2f} standard deviations from mean")
        else:
            st.warning(f"**Not cointegrated** (p-value >= 0.05) - No stable long-run relationship detected")
        
        # Plot spread
        self._render_cointegration_plot(prices_df, results, symbol1, symbol2)
    
    def _render_autocorrelation_analysis(self, instruments: List[Dict]):
        """Render autocorrelation and PACF analysis."""
        
        st.markdown("### Autocorrelation & Partial Autocorrelation Analysis")
        st.caption("ACF shows all correlations, PACF shows direct correlations controlling for intermediate lags")
        
        symbols = sorted([i['symbol'] for i in instruments])
        selected_symbol = st.selectbox(
            "Select instrument:",
            options=symbols,
            key=self._get_session_key("acf_symbol")
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            lookback_days = st.slider(
                "Lookback period (days):",
                min_value=90,
                max_value=730,
                value=365,
                step=30,
                key=self._get_session_key("acf_lookback")
            )
        
        with col2:
            max_lags = st.slider(
                "Maximum lags:",
                min_value=10,
                max_value=50,
                value=20,
                step=5,
                key=self._get_session_key("acf_lags")
            )
        
        if st.button("Calculate ACF & PACF", width="stretch"):
            with st.spinner("Calculating autocorrelation functions..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                price_df = self.storage.get_price_data(selected_symbol, start_date, end_date)
                
                if price_df is None or len(price_df) < 30:
                    st.error("Insufficient data for analysis")
                    return
                
                returns = calculate_returns(price_df['close']).dropna()
                
                # Calculate ACF and PACF using statsmodels
                acf_values = acf(returns, nlags=max_lags, fft=True)
                pacf_values = pacf(returns, nlags=max_lags, method='ywm')
                
                # Display results
                self._render_autocorrelation_results(acf_values, pacf_values, selected_symbol, returns, max_lags)
    
    def _render_volatility_clustering(self, instruments: List[Dict]):
        """Render volatility clustering analysis."""
        
        st.markdown("### Volatility Clustering Analysis")
        st.caption("Analyze whether high volatility periods tend to cluster together (ARCH effects)")
        
        symbols = sorted([i['symbol'] for i in instruments])
        selected_symbol = st.selectbox(
            "Select instrument:",
            options=symbols,
            key=self._get_session_key("vol_symbol")
        )
        
        lookback_days = st.slider(
            "Lookback period (days):",
            min_value=180,
            max_value=730,
            value=365,
            step=30,
            key=self._get_session_key("vol_lookback")
        )
        
        if st.button("Analyze Volatility Clustering", width="stretch"):
            with st.spinner("Analyzing volatility patterns..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                price_df = self.storage.get_price_data(selected_symbol, start_date, end_date)
                
                if price_df is None or len(price_df) < 30:
                    st.error("Insufficient data for analysis")
                    return
                
                returns = calculate_returns(price_df['close']).dropna()
                
                # Calculate rolling volatility
                rolling_vol = returns.rolling(window=20).std() * np.sqrt(252)
                
                # Test for ARCH effects (autocorrelation in squared returns)
                squared_returns = returns ** 2
                arch_acf = self._calculate_acf(squared_returns, 20)
                
                # Display results
                self._render_volatility_clustering_results(
                    returns, rolling_vol, arch_acf, selected_symbol
                )
    
    # ========================================================================
    # VISUALIZATION METHODS
    # ========================================================================
    
    def _render_series_plot(self, series: pd.Series, symbol: str, series_name: str):
        """Plot time series."""
        

        st.markdown("### Time Series Plot")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            mode='lines',
            name=series_name,
            line=dict(color='#1f77b4', width=1)
        ))
        
        fig.update_layout(
            title=f"{symbol} - {series_name}",
            xaxis_title="Date",
            yaxis_title=series_name,
            height=400,
            hovermode='x',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def _render_mean_reversion_plot(self, series: pd.Series, results: MeanReversionResults, symbol: str, series_name: str = "Price"):
        """Plot series with equilibrium level and bands."""
        

        st.markdown(f"### {series_name} vs Equilibrium Level")
        
        fig = go.Figure()
        
        # Series line
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            mode='lines',
            name=series_name,
            line=dict(color='#1f77b4', width=2)
        ))
        
        # Equilibrium line
        fig.add_hline(
            y=results.equilibrium_level,
            line_dash="dash",
            line_color="green",
            annotation_text="Equilibrium",
            annotation_position="right"
        )
        
        # Add ±1 and ±2 std bands
        std_dev = (series - results.equilibrium_level).std()
        
        for i, (mult, color, opacity) in enumerate([(1, 'yellow', 0.1), (2, 'red', 0.05)]):
            fig.add_hrect(
                y0=results.equilibrium_level - mult * std_dev,
                y1=results.equilibrium_level + mult * std_dev,
                fillcolor=color,
                opacity=opacity,
                line_width=0,
                annotation_text=f"±{mult}σ" if i == 1 else None
            )
        
        fig.update_layout(
            title=f"{symbol} - Mean Reversion Analysis",
            xaxis_title="Date",
            yaxis_title=series_name,
            height=500,
            hovermode='x',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def _render_cointegration_plot(self, prices_df: pd.DataFrame, results: CointegrationResults,
                                    symbol1: str, symbol2: str):
        """Plot cointegration spread."""
        

        st.markdown("### Cointegration Spread")
        
        # Calculate spread
        spread = prices_df[symbol1] - results.hedge_ratio * prices_df[symbol2]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Price Series", "Spread (Z-Score)"),
            vertical_spacing=0.12,
            row_heights=[0.5, 0.5]
        )
        
        # Top: Both price series
        fig.add_trace(
            go.Scatter(x=prices_df.index, y=prices_df[symbol1], name=symbol1,
                      line=dict(color='blue', width=1)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=prices_df.index, y=prices_df[symbol2], name=symbol2,
                      line=dict(color='red', width=1)),
            row=1, col=1
        )
        
        # Bottom: Spread as z-score
        z_score_series = (spread - results.spread_mean) / results.spread_std
        
        fig.add_trace(
            go.Scatter(x=spread.index, y=z_score_series, name='Spread Z-Score',
                      line=dict(color='purple', width=1)),
            row=2, col=1
        )
        
        # Add threshold lines
        for threshold, color in [(2, 'red'), (1, 'orange'), (0, 'green'), (-1, 'orange'), (-2, 'red')]:
            fig.add_hline(
                y=threshold,
                line_dash="dash",
                line_color=color,
                line_width=1,
                row=2, col=1
            )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Z-Score", row=2, col=1)
        
        fig.update_layout(
            height=700,
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def _render_autocorrelation_results(self, acf_values: np.ndarray, pacf_values: np.ndarray,
                                        symbol: str, returns: pd.Series, max_lags: int):
        """Display autocorrelation and PACF results."""
        

        st.markdown("### Autocorrelation Functions")
        
        # Create subplot with ACF and PACF
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Autocorrelation Function (ACF)", "Partial Autocorrelation (PACF)"),
            horizontal_spacing=0.12
        )
        
        lags = list(range(len(acf_values)))
        sig_level = 1.96 / np.sqrt(len(returns))
        
        # ACF plot
        acf_colors = ['red' if abs(val) > sig_level else 'blue' for val in acf_values]
        fig.add_trace(
            go.Bar(x=lags, y=acf_values, marker_color=acf_colors, name='ACF', showlegend=False),
            row=1, col=1
        )
        
        # PACF plot
        pacf_colors = ['red' if abs(val) > sig_level else 'blue' for val in pacf_values]
        fig.add_trace(
            go.Bar(x=lags, y=pacf_values, marker_color=pacf_colors, name='PACF', showlegend=False),
            row=1, col=2
        )
        
        # Add significance bounds to both
        for col in [1, 2]:
            fig.add_hline(y=sig_level, line_dash="dash", line_color="red", line_width=1, row=1, col=col)
            fig.add_hline(y=-sig_level, line_dash="dash", line_color="red", line_width=1, row=1, col=col)
        
        fig.update_xaxes(title_text="Lag", row=1, col=1)
        fig.update_xaxes(title_text="Lag", row=1, col=2)
        fig.update_yaxes(title_text="Correlation", row=1, col=1)
        fig.update_yaxes(title_text="Correlation", row=1, col=2)
        
        fig.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Interpretation
        st.space(1)
        acf_significant = np.sum(np.abs(acf_values[1:]) > sig_level)  # Exclude lag 0
        pacf_significant = np.sum(np.abs(pacf_values[1:]) > sig_level)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**ACF Interpretation:**")
            if acf_significant > max_lags * 0.1:
                st.warning(f"Significant autocorrelation at {acf_significant} lags - Predictable patterns exist")
            else:
                st.success("No significant autocorrelation - Returns appear random")
        
        with col2:
            st.markdown("**PACF Interpretation:**")
            if pacf_significant > 0:
                st.warning(f"Significant partial correlation at {pacf_significant} lags - Consider AR({pacf_significant}) model")
            else:
                st.success("No significant partial correlation")
        
        st.space(1)
        with st.expander("Understanding ACF vs PACF"):
            st.markdown("""
            - **ACF (Autocorrelation)**: Measures correlation between values at different lags, including indirect effects
            - **PACF (Partial Autocorrelation)**: Measures direct correlation at each lag, controlling for shorter lags
            - **Use Case**: ACF helps identify MA order, PACF helps identify AR order in ARIMA models
            - **Red bars**: Statistically significant at 95% confidence level
            """)
    
    def _render_volatility_clustering_results(self, returns: pd.Series, rolling_vol: pd.Series,
                                               arch_acf: np.ndarray, symbol: str):
        """Display volatility clustering results."""
        

        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=("Returns", "Rolling Volatility (20-day)", "ACF of Squared Returns"),
            vertical_spacing=0.1,
            row_heights=[0.3, 0.3, 0.4]
        )
        
        # Returns
        fig.add_trace(
            go.Scatter(x=returns.index, y=returns.values, mode='lines',
                      name='Returns', line=dict(color='blue', width=1)),
            row=1, col=1
        )
        
        # Rolling volatility
        fig.add_trace(
            go.Scatter(x=rolling_vol.index, y=rolling_vol.values, mode='lines',
                      name='Volatility', line=dict(color='red', width=1)),
            row=2, col=1
        )
        
        # ACF of squared returns
        lags = list(range(len(arch_acf)))
        colors = ['red' if abs(val) > 1.96/np.sqrt(len(returns)) else 'blue' for val in arch_acf]
        
        fig.add_trace(
            go.Bar(x=lags, y=arch_acf, marker_color=colors, name='ACF'),
            row=3, col=1
        )
        
        # Significance bounds
        sig_level = 1.96 / np.sqrt(len(returns))
        fig.add_hline(y=sig_level, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=-sig_level, line_dash="dash", line_color="red", row=3, col=1)
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_xaxes(title_text="Lag", row=3, col=1)
        fig.update_yaxes(title_text="Returns", row=1, col=1)
        fig.update_yaxes(title_text="Volatility", row=2, col=1)
        fig.update_yaxes(title_text="ACF", row=3, col=1)
        
        fig.update_layout(
            height=900,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Interpretation
        significant_lags = np.sum(np.abs(arch_acf) > sig_level)
        
        if significant_lags > len(arch_acf) * 0.1:
            st.warning(f"**Volatility clustering detected** - ARCH effects present ({significant_lags} significant lags)")
            st.info("High volatility periods tend to be followed by high volatility (and vice versa)")
        else:
            st.success("**No significant volatility clustering** - Volatility appears constant over time")
    
    # ========================================================================
    # PORTFOLIO-FOCUSED ANALYSIS METHODS
    # ========================================================================
    
    def _render_portfolio_stationarity(self, instruments: List[Dict]):
        """Test stationarity of portfolio returns."""
        
        st.markdown("### Portfolio Stationarity & Returns Analysis")
        st.caption("Test if your portfolio returns are stationary (required for many statistical models)")
        
        lookback_days = st.slider(
            "Lookback period (days):",
            min_value=180,
            max_value=730,
            value=365,
            step=30,
            key=self._get_session_key("portfolio_stat_lookback")
        )
        
        if st.button("Analyze Portfolio Returns", width="stretch"):
            with st.spinner("Calculating portfolio returns and running tests..."):
                # Get portfolio holdings (instruments with quantity > 0)
                all_instruments = self.storage.get_all_instruments(active_only=True)
                holdings = [i for i in all_instruments if i.get('quantity', 0) > 0]
                if not holdings or len(holdings) == 0:
                    st.error("No holdings found. Please add positions to your portfolio first.")
                    return
                
                # Calculate portfolio returns
                port_returns, weights_info = self._calculate_portfolio_returns(holdings, lookback_days)
                
                if port_returns is None or len(port_returns) < 30:
                    st.error("Insufficient data to calculate portfolio returns")
                    return
                
                st.markdown("#### Portfolio Composition")
                st.dataframe(pd.DataFrame(weights_info), width='stretch', hide_index=True)
                st.space(1)
                
                # Test stationarity
                st.markdown("#### Stationarity Tests")
                stat_results = self._test_stationarity(port_returns)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Augmented Dickey-Fuller**")
                    if stat_results.adf_is_stationary:
                        st.success(f"✓ Stationary (p={stat_results.adf_pvalue:.4f})")
                        st.caption("Reject null hypothesis of unit root")
                    else:
                        st.warning(f"✗ Non-stationary (p={stat_results.adf_pvalue:.4f})")
                        st.caption("Fail to reject null hypothesis")
                
                with col2:
                    st.markdown("**KPSS Test**")
                    if stat_results.kpss_is_stationary:
                        st.success(f"✓ Stationary (p={stat_results.kpss_pvalue:.4f})")
                        st.caption("Fail to reject null of stationarity")
                    else:
                        st.warning(f"✗ Non-stationary (p={stat_results.kpss_pvalue:.4f})")
                        st.caption("Reject null hypothesis")
                
                st.space(1)
                
                # Overall interpretation
                if stat_results.adf_is_stationary and stat_results.kpss_is_stationary:
                    st.success("**Portfolio returns are stationary** ✓")
                    st.info("🎯 **Implication**: Returns suitable for ARMA/GARCH modeling, mean-reversion strategies, and risk forecasting")
                else:
                    st.warning("**Portfolio returns show non-stationarity**")
                    st.info("💡 **Implication**: Consider using returns-based models or apply differencing. Some statistical models may be invalid.")
                
                # Plot returns
                self._render_series_plot(port_returns, "Portfolio", "Daily Returns")
    
    def _render_portfolio_mean_reversion(self, instruments: List[Dict]):
        """Test mean reversion of portfolio returns."""
        
        st.markdown("### Portfolio Mean Reversion Analysis")
        st.caption("Determine if your portfolio exhibits mean-reverting behavior")
        
        lookback_days = st.slider(
            "Lookback period (days):",
            min_value=180,
            max_value=730,
            value=365,
            step=30,
            key=self._get_session_key("portfolio_mr_lookback")
        )
        
        if st.button("Analyze Portfolio Mean Reversion", width="stretch"):
            with st.spinner("Running analysis..."):
                # Get portfolio holdings (instruments with quantity > 0)
                all_instruments = self.storage.get_all_instruments(active_only=True)
                holdings = [i for i in all_instruments if i.get('quantity', 0) > 0]
                if not holdings or len(holdings) == 0:
                    st.error("No holdings found")
                    return
                
                port_returns, weights_info = self._calculate_portfolio_returns(holdings, lookback_days)
                
                if port_returns is None or len(port_returns) < 30:
                    st.error("Insufficient data")
                    return
                
                # Test stationarity first
                st.markdown("#### Step 1: Check Stationarity")
                stat_results = self._test_stationarity(port_returns)
                
                is_stationary = stat_results.adf_is_stationary and stat_results.kpss_is_stationary
                
                if is_stationary:
                    st.success("✓ Portfolio returns are stationary")
                else:
                    st.warning("⚠️ Returns show signs of non-stationarity")
                
                st.space(1)
                
                # Mean reversion analysis
                st.markdown("#### Step 2: Mean Reversion Properties")
                mr_results = self._analyze_mean_reversion(port_returns, is_differenced=False)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Half-Life (days)", f"{mr_results.half_life:.1f}")
                
                with col2:
                    st.metric("Reversion Speed", f"{mr_results.mean_reversion_speed:.4f}")
                
                with col3:
                    st.metric("Current Z-Score", f"{mr_results.current_z_score:.2f}")
                
                st.space(1)
                
                if mr_results.is_mean_reverting:
                    st.success(f"**Mean reversion detected** - Half-life: {mr_results.half_life:.1f} days")
                    st.info(f"🎯 **Portfolio Strategy Implication**: Returns revert to mean in ~{mr_results.half_life:.0f} days. Consider contrarian rebalancing strategies or selling after strong rallies.")
                else:
                    st.warning("**No significant mean reversion**")
                    st.info("💡 **Portfolio Strategy Implication**: Portfolio shows momentum/trend characteristics. Consider trend-following or momentum-based rebalancing.")
    
    def _render_portfolio_diagnostics(self, instruments: List[Dict]):
        """Run diagnostic tests on portfolio returns."""
        
        st.markdown("### Portfolio Diagnostic Tests")
        st.caption("Comprehensive statistical tests for portfolio returns")
        
        lookback_days = st.slider(
            "Lookback period (days):",
            min_value=180,
            max_value=730,
            value=365,
            step=30,
            key=self._get_session_key("portfolio_diag_lookback")
        )
        
        if st.button("Run Portfolio Diagnostics", width="stretch"):
            with st.spinner("Running tests..."):
                # Get portfolio holdings (instruments with quantity > 0)
                all_instruments = self.storage.get_all_instruments(active_only=True)
                holdings = [i for i in all_instruments if i.get('quantity', 0) > 0]
                if not holdings:
                    st.error("No holdings found")
                    return
                
                port_returns, _ = self._calculate_portfolio_returns(holdings, lookback_days)
                
                if port_returns is None or len(port_returns) < 30:
                    st.error("Insufficient data")
                    return
                
                # Run diagnostics
                diag_results = self._run_diagnostics(port_returns)
                
                # Display results
                self._render_diagnostic_results(diag_results, "Portfolio", port_returns)
                
                # Portfolio-specific interpretation
                st.space(1)
                st.markdown("#### Portfolio Management Implications")
                
                implications = []
                
                if diag_results.has_serial_correlation:
                    implications.append("📊 **Serial Correlation Detected**: Past returns predict future returns. Consider momentum or mean-reversion strategies.")
                
                if not diag_results.is_normal:
                    implications.append("📉 **Non-Normal Distribution**: Fat tails detected. Use robust risk metrics (VaR, CVaR) instead of assuming normality.")
                
                if not diag_results.is_random_walk:
                    implications.append("🎯 **Predictable Patterns**: Returns deviate from random walk. Active management may add value.")
                
                if abs(diag_results.skewness) > 0.5:
                    direction = "negative" if diag_results.skewness < 0 else "positive"
                    implications.append(f"⚠️ **{direction.capitalize()} Skew**: Asymmetric return distribution. {'Crash risk elevated' if diag_results.skewness < 0 else 'Limited downside, capped upside'}.")
                
                if diag_results.kurtosis > 1:
                    implications.append(f"📈 **Fat Tails (Kurtosis={diag_results.kurtosis:.2f})**: Extreme events more likely than normal distribution suggests. Increase diversification.")
                
                for imp in implications:
                    st.info(imp)
                
                if not implications:
                    st.success("✓ Portfolio returns show well-behaved statistical properties")
    
    def _render_portfolio_autocorrelation(self, instruments: List[Dict]):
        """Analyze autocorrelation in portfolio returns."""
        
        st.markdown("### Portfolio Autocorrelation Analysis")
        st.caption("Detect predictable patterns in portfolio returns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lookback_days = st.slider(
                "Lookback period (days):",
                min_value=180,
                max_value=730,
                value=365,
                step=30,
                key=self._get_session_key("portfolio_acf_lookback")
            )
        
        with col2:
            max_lags = st.slider(
                "Maximum lags:",
                min_value=10,
                max_value=50,
                value=20,
                step=5,
                key=self._get_session_key("portfolio_acf_lags")
            )
        
        if st.button("Analyze Portfolio ACF/PACF", width="stretch"):
            with st.spinner("Calculating..."):
                # Get portfolio holdings (instruments with quantity > 0)
                all_instruments = self.storage.get_all_instruments(active_only=True)
                holdings = [i for i in all_instruments if i.get('quantity', 0) > 0]
                if not holdings:
                    st.error("No holdings found")
                    return
                
                port_returns, _ = self._calculate_portfolio_returns(holdings, lookback_days)
                
                if port_returns is None or len(port_returns) < 30:
                    st.error("Insufficient data")
                    return
                
                # Calculate ACF and PACF
                acf_values = acf(port_returns, nlags=max_lags, fft=True)
                pacf_values = pacf(port_returns, nlags=max_lags, method='ywm')
                
                # Display
                self._render_autocorrelation_results(acf_values, pacf_values, "Portfolio", port_returns, max_lags)
                
                # Portfolio implications
                st.space(1)
                st.markdown("#### Portfolio Timing Implications")
                
                sig_level = 1.96 / np.sqrt(len(port_returns))
                acf_sig = np.sum(np.abs(acf_values[1:]) > sig_level)
                
                if acf_sig > 0:
                    st.info(f"🎯 **Tactical Opportunity**: Portfolio shows serial correlation. Consider tactical timing strategies with {acf_sig}-day lookback periods.")
                else:
                    st.success("✓ Returns appear random - consistent with efficient markets. Focus on strategic (buy-and-hold) allocation.")
    
    def _render_portfolio_volatility(self, instruments: List[Dict]):
        """Analyze portfolio volatility regimes."""
        
        st.markdown("### Portfolio Volatility Regime Analysis")
        st.caption("Identify periods of high vs low volatility in your portfolio")
        
        lookback_days = st.slider(
            "Lookback period (days):",
            min_value=180,
            max_value=1095,
            value=730,
            step=30,
            key=self._get_session_key("portfolio_vol_lookback")
        )
        
        if st.button("Analyze Volatility Regimes", width="stretch"):
            with st.spinner("Analyzing..."):
                # Get portfolio holdings (instruments with quantity > 0)
                all_instruments = self.storage.get_all_instruments(active_only=True)
                holdings = [i for i in all_instruments if i.get('quantity', 0) > 0]
                if not holdings:
                    st.error("No holdings found")
                    return
                
                port_returns, _ = self._calculate_portfolio_returns(holdings, lookback_days)
                
                if port_returns is None or len(port_returns) < 30:
                    st.error("Insufficient data")
                    return
                
                # Calculate rolling volatility
                rolling_vol = port_returns.rolling(window=20).std() * np.sqrt(252)
                
                # Calculate ARCH effects
                squared_returns = port_returns ** 2
                arch_acf = acf(squared_returns, nlags=20, fft=True)
                
                # Display
                self._render_volatility_clustering_results(port_returns, rolling_vol, arch_acf, "Portfolio")
                
                # Portfolio management implications
                st.space(1)
                st.markdown("#### Volatility-Based Portfolio Management")
                
                current_vol = rolling_vol.iloc[-1]
                avg_vol = rolling_vol.mean()
                
                st.metric("Current Annualized Volatility", f"{current_vol:.2f}%", 
                         delta=f"{current_vol - avg_vol:+.2f}% vs average")
                
                if current_vol > avg_vol * 1.5:
                    st.warning("⚠️ **High Volatility Regime**: Consider reducing position sizes or hedging")
                elif current_vol < avg_vol * 0.7:
                    st.success("✓ **Low Volatility Regime**: Favorable for increasing exposure or tactical positioning")
                else:
                    st.info("📊 **Normal Volatility Regime**: Maintain strategic allocation")
    
    def _render_portfolio_rolling_stats(self, instruments: List[Dict]):
        """Render rolling statistics for portfolio."""
        
        st.markdown("### Portfolio Rolling Statistics")
        st.caption("Track how portfolio statistical properties evolve over time")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lookback_days = st.slider(
                "Lookback period (days):",
                min_value=365,
                max_value=1825,
                value=1095,
                step=90,
                key=self._get_session_key("portfolio_roll_lookback")
            )
        
        with col2:
            window_days = st.slider(
                "Rolling window (days):",
                min_value=20,
                max_value=180,
                value=60,
                step=10,
                key=self._get_session_key("portfolio_roll_window")
            )
        
        if st.button("Calculate Rolling Statistics", width="stretch"):
            with st.spinner("Calculating..."):
                # Get portfolio holdings (instruments with quantity > 0)
                all_instruments = self.storage.get_all_instruments(active_only=True)
                holdings = [i for i in all_instruments if i.get('quantity', 0) > 0]
                if not holdings:
                    st.error("No holdings found")
                    return
                
                port_returns, _ = self._calculate_portfolio_returns(holdings, lookback_days)
                
                if port_returns is None or len(port_returns) < window_days:
                    st.error("Insufficient data")
                    return
                
                # Display
                self._render_rolling_results(port_returns, "Portfolio", window_days)
    
    def _render_portfolio_structural_breaks(self, instruments: List[Dict]):
        """Detect structural breaks in portfolio returns."""
        
        st.markdown("### Portfolio Structural Break Detection")
        st.caption("Identify regime changes in your portfolio's behavior")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lookback_days = st.slider(
                "Lookback period (days):",
                min_value=365,
                max_value=1825,
                value=1095,
                step=90,
                key=self._get_session_key("portfolio_break_lookback")
            )
        
        with col2:
            min_segment = st.slider(
                "Minimum segment (%):",
                min_value=10,
                max_value=40,
                value=20,
                step=5,
                key=self._get_session_key("portfolio_break_min")
            )
        
        if st.button("Detect Structural Breaks", width="stretch"):
            with st.spinner("Analyzing..."):
                # Get portfolio holdings (instruments with quantity > 0)
                all_instruments = self.storage.get_all_instruments(active_only=True)
                holdings = [i for i in all_instruments if i.get('quantity', 0) > 0]
                if not holdings:
                    st.error("No holdings found")
                    return
                
                port_returns, _ = self._calculate_portfolio_returns(holdings, lookback_days)
                
                if port_returns is None or len(port_returns) < 100:
                    st.error("Insufficient data")
                    return
                
                # Detect breaks
                results = self._detect_structural_break(port_returns, min_segment / 100)
                
                # Display
                self._render_structural_break_results(results, "Portfolio", port_returns)
                
                # Portfolio management implications
                if results.has_break and results.break_date:
                    st.space(1)
                    st.markdown("#### Portfolio Management Implications")
                    
                    mean_change = (results.post_mean - results.pre_mean) / abs(results.pre_mean) * 100 if results.pre_mean != 0 else 0
                    vol_change = (results.post_vol - results.pre_vol) / results.pre_vol * 100 if results.pre_vol != 0 else 0
                    
                    if abs(mean_change) > 20:
                        st.warning(f"⚠️ **Significant Return Shift**: Portfolio returns changed by {mean_change:+.1f}% after break. Review strategy effectiveness.")
                    
                    if abs(vol_change) > 30:
                        st.warning(f"⚠️ **Volatility Regime Change**: Risk increased {vol_change:+.1f}% after break. Consider rebalancing or hedging.")
                    
                    if mean_change < -10 and vol_change > 20:
                        st.error("🚨 **Deteriorating Risk-Return**: Lower returns AND higher volatility. Portfolio strategy may need revision.")
    
    def _calculate_portfolio_returns(self, holdings: List[Dict], lookback_days: int) -> Tuple[Optional[pd.Series], List[Dict]]:
        """Calculate portfolio returns from holdings.
        
        Returns:
            Tuple of (portfolio_returns_series, weights_info_list)
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        # Get latest prices for holdings
        symbols = [h['symbol'] for h in holdings]
        latest_prices = self.storage.get_latest_prices(symbols)
        
        # Calculate total portfolio value and weights
        # Support both 'quantity'/'price' (from get_all_instruments) and 'shares'/'current_price'
        total_value = 0
        for h in holdings:
            quantity = h.get('quantity', h.get('shares', 0))
            price = h.get('price', h.get('current_price', 0))
            # Use latest price if available
            if h['symbol'] in latest_prices:
                price = latest_prices[h['symbol']].get('close', price)
            total_value += quantity * price
        
        if total_value == 0:
            return None, []
        
        # Get returns for each holding
        returns_dict = {}
        weights_info = []
        
        for holding in holdings:
            symbol = holding.get('symbol')
            quantity = holding.get('quantity', holding.get('shares', 0))
            price = holding.get('price', holding.get('current_price', 0))
            # Use latest price if available
            if symbol in latest_prices:
                price = latest_prices[symbol].get('close', price)
            
            position_value = quantity * price
            weight = position_value / total_value
            
            if weight < 0.001:  # Skip tiny positions
                continue
            
            price_df = self.storage.get_price_data(symbol, start_date, end_date)
            if price_df is not None and len(price_df) > 20:
                returns = calculate_returns(price_df['close']).dropna()
                returns_dict[symbol] = returns
                weights_info.append({
                    'Symbol': symbol,
                    'Weight': f"{weight*100:.2f}%",
                    'Value': f"${position_value:,.2f}"
                })
        
        if not returns_dict:
            return None, []
        
        # Align returns
        returns_df = pd.DataFrame(returns_dict).dropna()
        
        if len(returns_df) < 20:
            return None, weights_info
        
        # Calculate portfolio returns as weighted average
        # Build weights array matching returns_df columns
        weights_dict = {}
        for holding in holdings:
            symbol = holding.get('symbol')
            if symbol in returns_df.columns:
                quantity = holding.get('quantity', holding.get('shares', 0))
                price = holding.get('price', holding.get('current_price', 0))
                if symbol in latest_prices:
                    price = latest_prices[symbol].get('close', price)
                weights_dict[symbol] = quantity * price / total_value
        
        weights = np.array([weights_dict.get(col, 0) for col in returns_df.columns])
        weights = weights / weights.sum()  # Normalize
        
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        return portfolio_returns, weights_info
    
    def _render_diagnostic_tests(self, instruments: List[Dict]):
        """Render comprehensive diagnostic tests."""
        
        st.markdown("### Diagnostic Tests")
        st.caption("Comprehensive tests for serial correlation, normality, and random walk hypothesis")
        
        symbols = sorted([i['symbol'] for i in instruments])
        selected_symbol = st.selectbox(
            "Select instrument:",
            options=symbols,
            key=self._get_session_key("diag_symbol")
        )
        
        lookback_days = st.slider(
            "Lookback period (days):",
            min_value=90,
            max_value=730,
            value=365,
            step=30,
            key=self._get_session_key("diag_lookback")
        )
        
        if st.button("Run Diagnostic Tests", width="stretch"):
            with st.spinner("Running diagnostic tests..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                price_df = self.storage.get_price_data(selected_symbol, start_date, end_date)
                
                if price_df is None or len(price_df) < 30:
                    st.error("Insufficient data for analysis")
                    return
                
                returns = calculate_returns(price_df['close']).dropna()
                
                # Run diagnostics
                results = self._run_diagnostics(returns)
                
                # Display results
                self._render_diagnostic_results(results, selected_symbol, returns)
    
    def _render_granger_causality(self, instruments: List[Dict]):
        """Render Granger causality analysis."""
        
        st.markdown("### Granger Causality Test")
        st.caption("Test if one time series helps predict another (X → Y)")
        
        symbols = sorted([i['symbol'] for i in instruments])
        
        col1, col2 = st.columns(2)
        
        with col1:
            symbol_x = st.selectbox(
                "X (Cause):",
                options=symbols,
                key=self._get_session_key("granger_x")
            )
        
        with col2:
            remaining = [s for s in symbols if s != symbol_x]
            symbol_y = st.selectbox(
                "Y (Effect):",
                options=remaining,
                key=self._get_session_key("granger_y")
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            lookback_days = st.slider(
                "Lookback period (days):",
                min_value=180,
                max_value=730,
                value=365,
                step=30,
                key=self._get_session_key("granger_lookback")
            )
        
        with col4:
            max_lag = st.slider(
                "Maximum lag:",
                min_value=1,
                max_value=20,
                value=5,
                key=self._get_session_key("granger_lag")
            )
        
        if st.button("Test Granger Causality", width="stretch"):
            with st.spinner("Running Granger causality test..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                
                price_x = self.storage.get_price_data(symbol_x, start_date, end_date)
                price_y = self.storage.get_price_data(symbol_y, start_date, end_date)
                
                if price_x is None or price_y is None:
                    st.error("Insufficient data for one or both instruments")
                    return
                
                returns_x = calculate_returns(price_x['close']).dropna()
                returns_y = calculate_returns(price_y['close']).dropna()
                
                # Align data
                aligned = pd.DataFrame({
                    'x': returns_x,
                    'y': returns_y
                }).dropna()
                
                if len(aligned) < 50:
                    st.error("Insufficient overlapping data")
                    return
                
                # Run test
                results = self._test_granger_causality(aligned['x'], aligned['y'], max_lag)
                
                # Display
                self._render_granger_results(results, symbol_x, symbol_y)
    
    def _render_rolling_statistics(self, instruments: List[Dict]):
        """Render rolling window statistics."""
        
        st.markdown("### Rolling Statistics")
        st.caption("Analyze how statistical properties change over time using rolling windows")
        
        symbols = sorted([i['symbol'] for i in instruments])
        selected_symbol = st.selectbox(
            "Select instrument:",
            options=symbols,
            key=self._get_session_key("roll_symbol")
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            lookback_days = st.slider(
                "Lookback period (days):",
                min_value=180,
                max_value=1095,
                value=730,
                step=30,
                key=self._get_session_key("roll_lookback")
            )
        
        with col2:
            window_days = st.slider(
                "Rolling window (days):",
                min_value=20,
                max_value=180,
                value=60,
                step=10,
                key=self._get_session_key("roll_window")
            )
        
        if st.button("Calculate Rolling Statistics", width="stretch"):
            with st.spinner("Calculating rolling statistics..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                price_df = self.storage.get_price_data(selected_symbol, start_date, end_date)
                
                if price_df is None or len(price_df) < window_days:
                    st.error("Insufficient data for analysis")
                    return
                
                returns = calculate_returns(price_df['close']).dropna()
                
                # Calculate rolling stats
                self._render_rolling_results(returns, selected_symbol, window_days)
    
    def _render_structural_breaks(self, instruments: List[Dict]):
        """Render structural break detection."""
        
        st.markdown("### Structural Break Detection")
        st.caption("Detect regime changes in mean and volatility using Chow test approach")
        
        symbols = sorted([i['symbol'] for i in instruments])
        selected_symbol = st.selectbox(
            "Select instrument:",
            options=symbols,
            key=self._get_session_key("break_symbol")
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            lookback_days = st.slider(
                "Lookback period (days):",
                min_value=180,
                max_value=1095,
                value=730,
                step=30,
                key=self._get_session_key("break_lookback")
            )
        
        with col2:
            min_segment = st.slider(
                "Minimum segment (%):",
                min_value=10,
                max_value=40,
                value=20,
                step=5,
                key=self._get_session_key("break_min")
            )
        
        if st.button("Detect Structural Breaks", width="stretch"):
            with st.spinner("Detecting structural breaks..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                price_df = self.storage.get_price_data(selected_symbol, start_date, end_date)
                
                if price_df is None or len(price_df) < 100:
                    st.error("Insufficient data for analysis")
                    return
                
                returns = calculate_returns(price_df['close']).dropna()
                
                # Detect breaks
                results = self._detect_structural_break(returns, min_segment / 100)
                
                # Display
                self._render_structural_break_results(results, selected_symbol, returns)
    
    # ========================================================================
    # LOGIC LAYER - Statistical analysis methods
    # ========================================================================
    
    @staticmethod
    def _test_stationarity(series: pd.Series) -> StationarityResults:
        """Run ADF and KPSS stationarity tests.
        
        Parameters:
            series: Time series to test
            
        Returns:
            StationarityResults with test statistics
        """
        # Augmented Dickey-Fuller test
        adf_result = adfuller(series, autolag='AIC')
        adf_statistic = adf_result[0]
        adf_pvalue = adf_result[1]
        adf_critical_values = adf_result[4]
        adf_is_stationary = adf_pvalue < 0.05
        
        # KPSS test
        kpss_result = kpss(series, regression='c', nlags='auto')
        kpss_statistic = kpss_result[0]
        kpss_pvalue = kpss_result[1]
        kpss_critical_values = kpss_result[3]
        kpss_is_stationary = kpss_pvalue > 0.05
        
        return StationarityResults(
            adf_statistic=adf_statistic,
            adf_pvalue=adf_pvalue,
            adf_critical_values=adf_critical_values,
            adf_is_stationary=adf_is_stationary,
            kpss_statistic=kpss_statistic,
            kpss_pvalue=kpss_pvalue,
            kpss_critical_values=kpss_critical_values,
            kpss_is_stationary=kpss_is_stationary
        )
    
    @staticmethod
    def _analyze_mean_reversion(series: pd.Series, is_differenced: bool = False) -> MeanReversionResults:
        """Analyze mean reversion using Ornstein-Uhlenbeck process.
        
        Parameters:
            series: Stationary series (either prices or differenced prices)
            is_differenced: Whether series has been differenced
            
        Returns:
            MeanReversionResults with half-life and other metrics
        """
        # Calculate differences and lags
        series_diff = series.diff().dropna()
        series_lag = series.shift(1).dropna()
        
        # Align series
        df = pd.DataFrame({
            'diff': series_diff,
            'lag': series_lag
        }).dropna()
        
        if len(df) < 10:
            # Insufficient data, return default values
            return MeanReversionResults(
                half_life=np.inf,
                mean_reversion_speed=0,
                equilibrium_level=series.mean(),
                current_z_score=0,
                is_mean_reverting=False
            )
        
        # Fit OU process: dS = theta * (mu - S) * dt + sigma * dW
        # Using OLS: diff = alpha + beta * lag
        X = add_constant(df['lag'])
        model = OLS(df['diff'], X).fit()
        
        alpha = model.params.iloc[0]
        beta = model.params.iloc[1]
        
        # Calculate parameters
        mean_reversion_speed = -beta
        
        # Equilibrium level calculation
        if is_differenced:
            # For differenced series, equilibrium is the mean change (typically near 0)
            equilibrium_level = alpha / mean_reversion_speed if mean_reversion_speed != 0 else series.mean()
        else:
            # For price levels, equilibrium is the long-run price
            equilibrium_level = alpha / mean_reversion_speed if mean_reversion_speed != 0 else series.mean()
        
        # Half-life calculation
        half_life = -np.log(2) / beta if beta < 0 else np.inf
        
        # Current z-score
        current_value = series.iloc[-1]
        std_dev = (series - equilibrium_level).std()
        current_z_score = (current_value - equilibrium_level) / std_dev if std_dev > 0 else 0
        
        # Determine if mean reverting (negative beta and reasonable half-life)
        # For differenced series, be more strict (half-life should be shorter)
        max_half_life = 50 if is_differenced else 100
        is_mean_reverting = beta < 0 and 1 < half_life < max_half_life
        
        return MeanReversionResults(
            half_life=half_life,
            mean_reversion_speed=mean_reversion_speed,
            equilibrium_level=equilibrium_level,
            current_z_score=current_z_score,
            is_mean_reverting=is_mean_reverting
        )
    
    @staticmethod
    def _analyze_cointegration(series1: pd.Series, series2: pd.Series) -> CointegrationResults:
        """Test for cointegration between two series.
        
        Parameters:
            series1: First price series
            series2: Second price series
            
        Returns:
            CointegrationResults with test statistics and hedge ratio
        """
        # Run cointegration test
        coint_statistic, coint_pvalue, crit_values = coint(series1, series2)
        is_cointegrated = coint_pvalue < 0.05
        
        # Calculate hedge ratio using OLS
        X = add_constant(series2)
        model = OLS(series1, X).fit()
        hedge_ratio = model.params[1]
        
        # Calculate spread
        spread = series1 - hedge_ratio * series2
        spread_mean = spread.mean()
        spread_std = spread.std()
        
        # Current z-score
        current_z_score = (spread.iloc[-1] - spread_mean) / spread_std if spread_std > 0 else 0
        
        return CointegrationResults(
            coint_statistic=coint_statistic,
            coint_pvalue=coint_pvalue,
            is_cointegrated=is_cointegrated,
            hedge_ratio=hedge_ratio,
            spread_mean=spread_mean,
            spread_std=spread_std,
            current_z_score=current_z_score
        )
    
    @staticmethod
    def _calculate_acf(series: pd.Series, max_lags: int) -> np.ndarray:
        """Calculate autocorrelation function.
        
        Parameters:
            series: Time series
            max_lags: Maximum number of lags
            
        Returns:
            Array of autocorrelation values
        """
        n = len(series)
        mean = series.mean()
        c0 = np.sum((series - mean) ** 2) / n
        
        acf_values = []
        for k in range(max_lags + 1):
            if k == 0:
                acf_values.append(1.0)
            else:
                ck = np.sum((series[:-k] - mean) * (series[k:] - mean)) / n
                acf_values.append(ck / c0)
        
        return np.array(acf_values)
    
    @staticmethod
    def _run_diagnostics(returns: pd.Series) -> DiagnosticsResults:
        """Run comprehensive diagnostic tests.
        
        Parameters:
            returns: Return series
            
        Returns:
            DiagnosticsResults with all test statistics
        """
        # Ljung-Box test for serial correlation
        lb_result = acorr_ljungbox(returns, lags=[10], return_df=True)
        lb_stat = lb_result['lb_stat'].iloc[0]
        lb_pvalue = lb_result['lb_pvalue'].iloc[0]
        has_serial_correlation = lb_pvalue < 0.05
        
        # Jarque-Bera test for normality
        jb_stat, jb_pvalue = stats.jarque_bera(returns)
        is_normal = jb_pvalue > 0.05
        
        # Calculate moments
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)
        
        # Variance Ratio test (Lo-MacKinlay)
        vr, vr_stat, vr_pvalue = TimeSeriesAnalysisWidget._variance_ratio_test(returns, q=2)
        is_random_walk = vr_pvalue > 0.05
        
        return DiagnosticsResults(
            ljung_box_statistic=lb_stat,
            ljung_box_pvalue=lb_pvalue,
            has_serial_correlation=has_serial_correlation,
            jarque_bera_statistic=jb_stat,
            jarque_bera_pvalue=jb_pvalue,
            is_normal=is_normal,
            skewness=skewness,
            kurtosis=kurtosis,
            variance_ratio=vr,
            vr_test_statistic=vr_stat,
            vr_pvalue=vr_pvalue,
            is_random_walk=is_random_walk
        )
    
    @staticmethod
    def _variance_ratio_test(returns: pd.Series, q: int = 2) -> Tuple[float, float, float]:
        """Variance Ratio test for random walk hypothesis.
        
        Parameters:
            returns: Return series
            q: Number of periods (q=2 means test 2-period vs 1-period variance)
            
        Returns:
            Tuple of (variance_ratio, test_statistic, p_value)
        """
        n = len(returns)
        mu = returns.mean()
        
        # Variance of 1-period returns
        var_1 = np.sum((returns - mu) ** 2) / (n - 1)
        
        # Variance of q-period returns
        q_returns = returns.rolling(window=q).sum().dropna()
        var_q = np.sum((q_returns - q * mu) ** 2) / (len(q_returns) - 1)
        
        # Variance ratio
        vr = var_q / (q * var_1)
        
        # Test statistic (under homoskedasticity assumption)
        test_stat = (vr - 1) * np.sqrt(n * q) / np.sqrt(2 * (q - 1))
        
        # P-value (two-tailed)
        pvalue = 2 * (1 - stats.norm.cdf(abs(test_stat)))
        
        return vr, test_stat, pvalue
    
    @staticmethod
    def _test_granger_causality(series_x: pd.Series, series_y: pd.Series, max_lag: int) -> GrangerResults:
        """Test if X Granger-causes Y.
        
        Parameters:
            series_x: Cause series
            series_y: Effect series  
            max_lag: Maximum lag to test
            
        Returns:
            GrangerResults with test outcomes
        """
        # Prepare data
        data = pd.DataFrame({'y': series_y, 'x': series_x})
        
        # Run Granger test
        try:
            gc_result = grangercausalitytests(data[['y', 'x']], maxlag=max_lag, verbose=False)
            
            # Extract p-values for each lag
            pvalues = {}
            for lag in range(1, max_lag + 1):
                # Use F-test p-value
                pvalues[lag] = gc_result[lag][0]['ssr_ftest'][1]
            
            # Find best (lowest) p-value
            best_lag = min(pvalues, key=pvalues.get)
            best_pvalue = pvalues[best_lag]
            
            causes = best_pvalue < 0.05
            
            return GrangerResults(
                max_lag=max_lag,
                causes=causes,
                best_lag=best_lag,
                best_pvalue=best_pvalue,
                all_pvalues=pvalues
            )
        except Exception as e:
            # Return negative result if test fails
            return GrangerResults(
                max_lag=max_lag,
                causes=False,
                best_lag=1,
                best_pvalue=1.0,
                all_pvalues={i: 1.0 for i in range(1, max_lag + 1)}
            )
    
    @staticmethod
    def _detect_structural_break(returns: pd.Series, min_segment: float = 0.2) -> StructuralBreakResults:
        """Detect structural break using Chow test approach.
        
        Parameters:
            returns: Return series
            min_segment: Minimum segment size as fraction of total
            
        Returns:
            StructuralBreakResults with break point if found
        """
        n = len(returns)
        min_size = int(n * min_segment)
        
        best_stat = 0
        best_idx = None
        
        # Search for break point
        for i in range(min_size, n - min_size):
            pre = returns.iloc[:i]
            post = returns.iloc[i:]
            
            # Calculate F-statistic for mean difference
            pre_mean = pre.mean()
            post_mean = post.mean()
            
            # Pooled variance
            pooled_var = ((len(pre) - 1) * pre.var() + (len(post) - 1) * post.var()) / (n - 2)
            
            if pooled_var > 0:
                # F-stat for testing equal means
                f_stat = ((pre_mean - post_mean) ** 2) / (pooled_var * (1/len(pre) + 1/len(post)))
                
                if f_stat > best_stat:
                    best_stat = f_stat
                    best_idx = i
        
        # Determine if break is significant (F-crit ≈ 3.84 for α=0.05, df1=1, df2=large)
        has_break = best_stat > 10.0  # More conservative threshold
        
        if has_break and best_idx is not None:
            pre = returns.iloc[:best_idx]
            post = returns.iloc[best_idx:]
            
            return StructuralBreakResults(
                has_break=True,
                break_date=returns.index[best_idx],
                test_statistic=best_stat,
                pre_mean=pre.mean(),
                post_mean=post.mean(),
                pre_vol=pre.std() * np.sqrt(252),
                post_vol=post.std() * np.sqrt(252)
            )
        else:
            return StructuralBreakResults(
                has_break=False,
                break_date=None,
                test_statistic=best_stat,
                pre_mean=returns.mean(),
                post_mean=returns.mean(),
                pre_vol=returns.std() * np.sqrt(252),
                post_vol=returns.std() * np.sqrt(252)
            )
    
    # ========================================================================
    # NEW RENDERING METHODS FOR ENHANCED TESTS
    # ========================================================================
    
    def _render_diagnostic_results(self, results: DiagnosticsResults, symbol: str, returns: pd.Series):
        """Display diagnostic test results."""
        
        st.markdown("### Diagnostic Test Results")
        
        # Test results in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Ljung-Box Test**")
            st.caption("Serial Correlation")
            st.metric("Statistic", f"{results.ljung_box_statistic:.4f}")
            st.metric("P-value", f"{results.ljung_box_pvalue:.4f}")
            if results.has_serial_correlation:
                st.error("❌ Serial correlation detected")
            else:
                st.success("✓ No serial correlation")
        
        with col2:
            st.markdown("**Jarque-Bera Test**")
            st.caption("Normality")
            st.metric("Statistic", f"{results.jarque_bera_statistic:.4f}")
            st.metric("P-value", f"{results.jarque_bera_pvalue:.4f}")
            if results.is_normal:
                st.success("✓ Normal distribution")
            else:
                st.warning("⚠ Non-normal distribution")
        
        with col3:
            st.markdown("**Variance Ratio Test**")
            st.caption("Random Walk")
            st.metric("Ratio", f"{results.variance_ratio:.4f}")
            st.metric("P-value", f"{results.vr_pvalue:.4f}")
            if results.is_random_walk:
                st.success("✓ Consistent with random walk")
            else:
                st.warning("⚠ Deviates from random walk")
        
        st.space(1)
        
        # Distribution moments
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown("**Distribution Shape**")
            st.metric("Skewness", f"{results.skewness:.4f}")
            if abs(results.skewness) > 0.5:
                st.caption("Asymmetric distribution")
            else:
                st.caption("Approximately symmetric")
        
        with col5:
            st.markdown("**Tail Behavior**")
            st.metric("Excess Kurtosis", f"{results.kurtosis:.4f}")
            if results.kurtosis > 1:
                st.caption("Fat tails (leptokurtic)")
            elif results.kurtosis < -1:
                st.caption("Thin tails (platykurtic)")
            else:
                st.caption("Normal-like tails")
        
        st.space(1)
        
        # Q-Q plot
        st.markdown("### Quantile-Quantile Plot")
        st.caption("Compare return distribution to normal distribution")
        
        fig = go.Figure()
        
        # Calculate theoretical vs sample quantiles
        sorted_returns = np.sort(returns)
        n = len(sorted_returns)
        theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, n))
        
        fig.add_trace(go.Scatter(
            x=theoretical_quantiles,
            y=sorted_returns,
            mode='markers',
            name='Sample',
            marker=dict(size=4, color='blue', opacity=0.6)
        ))
        
        # Add reference line
        min_val = min(theoretical_quantiles.min(), sorted_returns.min())
        max_val = max(theoretical_quantiles.max(), sorted_returns.max())
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Normal',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            xaxis_title="Theoretical Quantiles",
            yaxis_title="Sample Quantiles",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=True
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def _render_granger_results(self, results: GrangerResults, symbol_x: str, symbol_y: str):
        """Display Granger causality results."""
        
        st.markdown("### Granger Causality Results")
        
        if results.causes:
            st.success(f"**{symbol_x} Granger-causes {symbol_y}** (p < 0.05)")
            st.info(f"Past values of {symbol_x} help predict {symbol_y} beyond what {symbol_y}'s own history provides")
        else:
            st.warning(f"**{symbol_x} does NOT Granger-cause {symbol_y}** (p ≥ 0.05)")
            st.info(f"Past values of {symbol_x} do not significantly improve predictions of {symbol_y}")
        
        st.space(1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Best Lag", f"{results.best_lag}")
        
        with col2:
            st.metric("Best P-value", f"{results.best_pvalue:.4f}")
        
        st.space(1)
        
        # Plot p-values by lag
        st.markdown("### P-values by Lag")
        
        fig = go.Figure()
        
        lags = list(results.all_pvalues.keys())
        pvals = list(results.all_pvalues.values())
        
        colors = ['green' if p < 0.05 else 'red' for p in pvals]
        
        fig.add_trace(go.Bar(
            x=lags,
            y=pvals,
            marker_color=colors,
            name='P-value'
        ))
        
        fig.add_hline(y=0.05, line_dash="dash", line_color="blue", annotation_text="α=0.05")
        
        fig.update_layout(
            xaxis_title="Lag",
            yaxis_title="P-value",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        with st.expander("Understanding Granger Causality"):
            st.markdown("""
            - **Granger Causality**: Tests if past values of X improve forecasts of Y
            - **Does NOT imply**: True causation in the philosophical sense
            - **Interpretation**: If X Granger-causes Y, X contains useful information for predicting Y
            - **Green bars**: Significant at α=0.05 (X helps predict Y at this lag)
            """)
    
    def _render_rolling_results(self, returns: pd.Series, symbol: str, window: int):
        """Display rolling statistics."""
        
        st.markdown("### Rolling Statistics")
        
        # Calculate rolling stats
        rolling_mean = returns.rolling(window=window).mean()
        rolling_std = returns.rolling(window=window).std() * np.sqrt(252)
        rolling_skew = returns.rolling(window=window).skew()
        rolling_kurt = returns.rolling(window=window).kurt()
        
        # Create 4-panel plot
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=(
                f"Rolling Mean ({window}-day)",
                f"Rolling Volatility ({window}-day, annualized)",
                f"Rolling Skewness ({window}-day)",
                f"Rolling Kurtosis ({window}-day)"
            ),
            vertical_spacing=0.08,
            row_heights=[0.25, 0.25, 0.25, 0.25]
        )
        
        # Rolling mean
        fig.add_trace(
            go.Scatter(x=rolling_mean.index, y=rolling_mean.values, mode='lines',
                      name='Mean', line=dict(color='blue', width=1)),
            row=1, col=1
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
        
        # Rolling volatility
        fig.add_trace(
            go.Scatter(x=rolling_std.index, y=rolling_std.values, mode='lines',
                      name='Volatility', line=dict(color='red', width=1)),
            row=2, col=1
        )
        
        # Rolling skewness
        fig.add_trace(
            go.Scatter(x=rolling_skew.index, y=rolling_skew.values, mode='lines',
                      name='Skewness', line=dict(color='green', width=1)),
            row=3, col=1
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=3, col=1)
        
        # Rolling kurtosis
        fig.add_trace(
            go.Scatter(x=rolling_kurt.index, y=rolling_kurt.values, mode='lines',
                      name='Kurtosis', line=dict(color='purple', width=1)),
            row=4, col=1
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=4, col=1)
        
        fig.update_xaxes(title_text="Date", row=4, col=1)
        fig.update_yaxes(title_text="Mean", row=1, col=1)
        fig.update_yaxes(title_text="Volatility", row=2, col=1)
        fig.update_yaxes(title_text="Skewness", row=3, col=1)
        fig.update_yaxes(title_text="Kurtosis", row=4, col=1)
        
        fig.update_layout(
            height=1000,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        st.space(1)
        
        # Summary statistics
        st.markdown("### Statistical Stability")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mean_range = rolling_mean.max() - rolling_mean.min()
            st.metric("Mean Range", f"{mean_range:.4f}")
            if mean_range < returns.std():
                st.caption("Stable mean")
            else:
                st.caption("Variable mean")
        
        with col2:
            vol_range = rolling_std.max() - rolling_std.min()
            st.metric("Volatility Range", f"{vol_range:.2f}%")
            if vol_range < rolling_std.mean():
                st.caption("Stable volatility")
            else:
                st.caption("Time-varying volatility")
        
        with col3:
            skew_changes = np.sum(np.sign(rolling_skew.diff()) != 0)
            st.metric("Skew Sign Changes", f"{skew_changes}")
            st.caption("Distribution shape shifts")
    
    def _render_structural_break_results(self, results: StructuralBreakResults, 
                                         symbol: str, returns: pd.Series):
        """Display structural break results."""
        
        st.markdown("### Structural Break Detection")
        
        if results.has_break and results.break_date:
            st.warning(f"**Structural break detected** at {results.break_date.strftime('%Y-%m-%d')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Pre-Break Period**")
                st.metric("Mean Return", f"{results.pre_mean*100:.3f}%")
                st.metric("Volatility", f"{results.pre_vol:.2f}%")
            
            with col2:
                st.markdown("**Post-Break Period**")
                st.metric("Mean Return", f"{results.post_mean*100:.3f}%")
                st.metric("Volatility", f"{results.post_vol:.2f}%")
            
            st.space(1)
            st.metric("F-Statistic", f"{results.test_statistic:.2f}")
            
            # Calculate changes
            mean_change = ((results.post_mean - results.pre_mean) / abs(results.pre_mean) * 100) if results.pre_mean != 0 else 0
            vol_change = ((results.post_vol - results.pre_vol) / results.pre_vol * 100) if results.pre_vol != 0 else 0
            
            st.info(f"Mean changed by {mean_change:.1f}%, Volatility changed by {vol_change:.1f}%")
        else:
            st.success("**No significant structural break detected**")
            st.info("Statistical properties appear stable over the period")
            st.metric("Max F-Statistic", f"{results.test_statistic:.2f}")
        
        st.space(1)
        
        # Plot returns with break point
        st.markdown("### Returns Time Series")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=returns.index,
            y=returns.values,
            mode='lines',
            name='Returns',
            line=dict(color='blue', width=1)
        ))
        
        # Mark break point if found
        if results.has_break and results.break_date:
            fig.add_vline(
                x=results.break_date,
                line_dash="dash",
                line_color="red",
                line_width=2,
                annotation_text="Break Point",
                annotation_position="top"
            )
            
            # Add pre/post mean lines
            pre_returns = returns[returns.index < results.break_date]
            post_returns = returns[returns.index >= results.break_date]
            
            if len(pre_returns) > 0:
                fig.add_hline(
                    y=results.pre_mean,
                    line_dash="dot",
                    line_color="green",
                    line_width=1,
                    annotation_text="Pre-mean"
                )
            
            if len(post_returns) > 0:
                fig.add_hline(
                    y=results.post_mean,
                    line_dash="dot",
                    line_color="orange",
                    line_width=1,
                    annotation_text="Post-mean"
                )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Returns",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, width='stretch')

