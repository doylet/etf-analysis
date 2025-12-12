# ETF Analysis Widgets - Complete Feature Gap Analysis

**Document Purpose**: Comprehensive comparison of Streamlit widget specifications vs. React implementations across all 14 widgets.

**Analysis Date**: December 11, 2025  
**Branch**: 007-solid-widget-architecture

---

## Executive Summary

This document analyzes feature gaps between the original Streamlit widget UI specifications (source of truth) and current React/Next.js implementations. The Streamlit widgets contain dormant UI code that represents the intended functionality and user experience.

### Overall Coverage Statistics

| Widget | Coverage | Missing Features | Priority |
|--------|----------|------------------|----------|
| Monte Carlo Simulation | ~40% | Portfolio selection, fan chart, rebalancing, export | 🔴 HIGH |
| Portfolio Optimizer | ~50% | 7 optimization modes, efficient frontier controls, recommendations | 🔴 HIGH |
| Correlation Matrix | ~35% | Custom symbols, portfolio aggregation, benchmark pivots | 🔴 HIGH |
| Benchmark Comparison | ~60% | Instrument selection, period controls, cumulative chart | 🟡 MEDIUM |
| Portfolio Summary | ~55% | MWR/TWR/IRR, portfolio value chart | 🟡 MEDIUM |
| Holdings Breakdown | ~70% | Sector/type breakdown, multi-currency display | 🟡 MEDIUM |
| Constrained Optimization | ~30% | Constraint builder, feasibility analysis, sensitivity | 🔴 HIGH |
| Portfolio Transition | ~25% | Target builder, step-by-step plan, transition chart | 🔴 HIGH |
| Timeseries Analysis | ~20% | 15+ statistical tests, diagnostics, portfolio-level | 🔴 HIGH |
| Dividend Analysis | ~45% | Cash flow tracker, manual entry, yield projections | 🟡 MEDIUM |
| News/Event Analysis | ~10% | Full feature missing | 🔴 HIGH |
| Performance Widget | ~65% | Historical metrics table | 🟡 MEDIUM |

### Key Patterns Across Widgets

**Common Missing Features**:
1. ❌ **Instrument Selection UI** - Most widgets lack multi-select for custom portfolio composition
2. ❌ **Advanced Controls** - Expanders, toggles, multi-stage workflows missing
3. ❌ **Interactive Charts** - Plotly charts reduced to simple visualizations
4. ❌ **Export Functionality** - No CSV downloads across any widgets
5. ❌ **Calculation Triggers** - Auto-fetch instead of user-controlled "Calculate" buttons
6. ❌ **Help Text/Tooltips** - Missing contextual guidance from Streamlit help parameters

---

## Widget-by-Widget Analysis

---

## 1. Monte Carlo Simulation Widget

**Files**:
- Streamlit: `/src/widgets/monte_carlo_widget.py`
- React: `/frontend/v1/src/app/dashboard/widgets/MonteCarloWidget.tsx`

**Coverage**: ~40% | **Priority**: 🔴 **HIGH**

### Missing Features

#### 🔴 Portfolio Selection & Weight Allocation
**Streamlit Implementation**:
```python
def _render_portfolio_selector(self, instruments: List[Dict]) -> tuple:
    # Multi-select with portfolio holdings prioritized
    selected_symbols = st.multiselect("Instruments:", options=symbol_options, default=default_symbols)
    
    # Weight allocation methods
    weight_method = st.selectbox("Weight allocation method:",
        options=["Equal Weights", "Max Sharpe Ratio", "Min Volatility", 
                 "Current Portfolio", "Custom"])
    
    # Custom weight inputs
    if weight_method == "Custom":
        for symbol in selected_symbols:
            weights[symbol] = st.number_input(f"{symbol} %", min_value=0.0, max_value=100.0)
    
    # Weight visualization table
    with st.expander("View Weight Allocation", expanded=False):
        st.dataframe(weight_df)
```

**React**: ❌ Completely missing

**Impact**: Cannot simulate different portfolio compositions or test optimization strategies

---

#### 🔴 Advanced Simulation Parameters
**Streamlit Implementation**:
```python
# Basic
years = st.slider("Time horizon (years)", min_value=1, max_value=30, value=10)
initial_value = st.number_input("Initial portfolio value ($)", value=100000.0)

# Advanced Settings Expander
with st.expander("Advanced Settings"):
    # Contributions
    enable_contributions = st.checkbox("Enable periodic contributions")
    contribution_amount = st.number_input("Annual contribution ($)", min_value=-100000.0, max_value=1000000.0)
    contribution_frequency = st.selectbox("Frequency", ["Annual", "Quarterly", "Monthly"])
    
    # Rebalancing Analysis
    enable_rebalancing_analysis = st.checkbox("Analyze rebalancing timing")
    drift_threshold = st.slider("Drift threshold (%)", 5.0, 30.0, 10.0)
    transaction_cost_pct = st.number_input("Transaction cost (%)", 0.0, 2.0, 0.1)
    max_rebalances_per_year = st.slider("Max rebalances per year", 1, 12, 4)
```

**React**: ⚠️ Partial (has contributions but missing rebalancing analysis entirely)

**Impact**: Cannot analyze long-term scenarios, rebalancing strategies, or configure starting capital

---

#### 🔴 Fan Chart Visualization
**Streamlit Implementation**:
```python
def _render_fan_chart(self, results: SimulationResults, params: Dict):
    fig = go.Figure()
    
    # Percentile bands (outer, middle, inner)
    bands = [
        (lower_pct, upper_pct, 0.1, f"{params['confidence_level']}% confidence"),
        (25, 75, 0.2, "25-75th percentile"),
        (40, 60, 0.3, "40-60th percentile")
    ]
    
    for lower, upper, opacity, label in bands:
        fig.add_trace(go.Scatter(..., fill='tonexty', fillcolor=f'rgba(68, 138, 255, {opacity})'))
    
    # Median line + initial value reference
    fig.add_trace(go.Scatter(x=results.time_points, y=results.percentiles[50], line=dict(width=3)))
    fig.add_hline(y=results.initial_value, line_dash="dash")
```

**React**: ❌ Missing (only histogram shown)

**Impact**: Cannot visualize confidence bands over time or see median trajectory evolution

---

#### 🔴 Rebalancing Recommendations
**Streamlit Implementation**:
```python
def _render_rebalancing_recommendations(self, rec: RebalancingRecommendation, params: Dict):
    st.markdown("### Optimal Rebalancing Analysis")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Recommended Rebalances", f"{len(rec.rebalance_dates)}")
    with col2: st.metric("Avg Time Between", f"{avg_months:.1f} months")
    with col3: st.metric("Avg Drift at Rebalance", f"{rec.avg_drift*100:.1f}%")
    with col4: st.metric("Sharpe Improvement", f"{rec.sharpe_improvement:+.3f}")
    
    # Rebalancing calendar
    st.markdown("#### Recommended Rebalancing Dates")
    st.dataframe(rebal_df)  # Date, Time, Max Drift %, Instruments Affected
    
    # Per-instrument details
    with st.expander("View Detailed Rebalancing Actions by Instrument"):
        st.dataframe(inst_rebal_df)  # Date, Instrument, Current %, Target %, Drift %, Action
    
    # Timeline chart
    fig.add_trace(go.Scatter(x=years_from_start, y=rec.drift_at_rebalance, 
                            mode='markers+lines', marker=dict(symbol='diamond')))
    fig.add_hline(y=rec.trigger_threshold, line_dash="dash")
```

**React**: ❌ Completely missing

**Impact**: Cannot predict optimal rebalancing timing or analyze cost/benefit of rebalancing strategies

---

#### 🟡 Professional Risk Metrics
**Streamlit**:
- CAGR for 10th, 50th, 90th percentiles
- Conditional VaR (CVaR/Expected Shortfall)
- Max drawdown in median path
- Value at Risk with % return deltas

**React**: ⚠️ Partial (has VaR but missing CVaR, CAGR deltas, max drawdown)

---

#### 🟡 Export Functionality
**Streamlit**:
```python
def _render_export_options(self, results: SimulationResults, params: Dict):
    col1, col2 = st.columns(2)
    
    with col1:
        csv_percentiles = percentile_df.to_csv(index=False)
        st.download_button("Download Percentiles Over Time (CSV)", data=csv_percentiles, 
                          file_name=f"monte_carlo_percentiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    with col2:
        csv_final = final_values_df.to_csv(index=False)
        st.download_button("Download Final Values Distribution (CSV)", data=csv_final,
                          file_name=f"monte_carlo_final_values_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
```

**React**: ❌ Missing

---

### Implementation Roadmap

**Phase 1** (5 hours): Years input, initial value, CAGR metrics, CVaR
**Phase 2** (7 hours): Fan chart with percentile bands
**Phase 3** (12 hours): Portfolio selection & weight allocation UI
**Phase 4** (11 hours): Rebalancing analysis feature
**Phase 5** (7 hours): Percentile table, export, polish

**Total**: ~42 hours

---

## 2. Portfolio Optimizer Widget

**Files**:
- Streamlit: `/src/widgets/portfolio_optimizer_widget.py` (1686 lines)
- React: `/frontend/v1/src/app/dashboard/widgets/PortfolioOptimizerWidget.tsx` (304 lines)

**Coverage**: ~50% | **Priority**: 🔴 **HIGH**

### Missing Features

#### 🔴 7 Optimization Modes (Only 4 in React)
**Streamlit Modes**:
1. ✅ Custom Weights (React: ⚠️ Partial - no current portfolio comparison)
2. ✅ Efficient Frontier (React: ✅ Has basic version)
3. ✅ Target Return (React: ✅ Has)
4. ❌ Max Diversification - **MISSING**
5. ❌ Min Drawdown - **MISSING**
6. ❌ Mean-CVaR - **MISSING**
7. ❌ Max Income-Growth - **MISSING**

**Streamlit Implementation (Max Diversification)**:
```python
def _render_max_diversification_mode(self, symbols: List[str], returns_df: pd.DataFrame):
    st.markdown("**Maximum Diversification**")
    st.caption("Maximize the ratio of weighted volatilities to portfolio volatility")
    
    if st.button("Calculate Max Diversification Portfolio", type="primary"):
        with st.spinner("Optimizing..."):
            result = self._calculate_max_diversification_portfolio(returns_df)
        
        if result:
            self._render_portfolio_metrics(symbols, result.metrics, returns_df)
            self._render_instrument_recommendations(symbols, result.weights, "Max Diversification")
```

**React**: ❌ Not available in mode dropdown

---

#### 🔴 Instrument-Level Recommendations
**Streamlit Implementation**:
```python
def _render_instrument_recommendations(self, symbols: List[str], optimal_weights: np.ndarray, 
                                       mode_name: str):
    st.markdown(f"**{mode_name} - Recommended Actions**")
    
    # Get current positions
    current_weights = self._get_current_weights(symbols)
    
    # Calculate actions needed
    actions = []
    for i, symbol in enumerate(symbols):
        current_pct = current_weights[i] * 100
        target_pct = optimal_weights[i] * 100
        diff = target_pct - current_pct
        
        if abs(diff) > 1.0:  # Threshold for actionable change
            action = "BUY" if diff > 0 else "SELL"
            actions.append({
                'Symbol': symbol,
                'Current %': f"{current_pct:.2f}%",
                'Target %': f"{target_pct:.2f}%",
                'Change': f"{diff:+.2f}%",
                'Action': action
            })
    
    if actions:
        st.dataframe(pd.DataFrame(actions), hide_index=True, width='stretch')
        st.caption("Actions show portfolio adjustments needed to reach optimal allocation")
    else:
        st.success("✅ Current portfolio is already close to optimal allocation")
```

**React**: ⚠️ Partial (shows weights but not BUY/SELL actions)

---

#### 🔴 Efficient Frontier Interactive Controls
**Streamlit Implementation**:
```python
def _render_efficient_frontier_mode(self, symbols: List[str], returns_df: pd.DataFrame):
    # Number of portfolios control
    num_portfolios = st.slider("Number of portfolios to generate:", 20, 200, 50, step=10)
    
    # Risk-free rate
    risk_free_rate = st.number_input("Risk-free rate (%):", min_value=0.0, max_value=10.0, 
                                     value=4.0, step=0.1) / 100
    
    # Allow short selling toggle
    allow_short = st.checkbox("Allow short selling (negative weights)", value=False)
    
    if st.button("Generate Efficient Frontier", type="primary"):
        with st.spinner(f"Calculating {num_portfolios} portfolios..."):
            frontier = self._calculate_efficient_frontier(returns_df, num_portfolios, 
                                                          risk_free_rate, allow_short)
        
        self._render_efficient_frontier_chart(frontier, symbols, returns_df)
        
        # Show key portfolios
        st.markdown("**Key Portfolios**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Minimum Volatility Portfolio**")
            self._render_portfolio_metrics(symbols, frontier.min_vol_portfolio, returns_df)
        with col2:
            st.markdown("**Maximum Sharpe Ratio Portfolio**")
            self._render_portfolio_metrics(symbols, frontier.max_sharpe_portfolio, returns_df)
```

**React**: ⚠️ Basic chart only, missing controls for number of portfolios, risk-free rate, short selling

---

#### 🟡 Current vs. Optimal Comparison
**Streamlit**: Shows side-by-side comparison with improvement metrics
**React**: ⚠️ Partial - has improvement section but not detailed comparison

---

#### 🟡 Portfolio Metrics Detail
**Streamlit**: Expected return, volatility, Sharpe, Sortino, max drawdown, tracking error
**React**: Only expected return, risk, Sharpe

---

### Implementation Roadmap

**Phase 1** (8 hours): Add Max Diversification, Min Drawdown modes
**Phase 2** (6 hours): Add Mean-CVaR, Max Income-Growth modes
**Phase 3** (4 hours): Efficient frontier controls (num portfolios, risk-free rate, short selling)
**Phase 4** (3 hours): Detailed instrument recommendations with BUY/SELL actions
**Phase 5** (3 hours): Additional metrics (Sortino, tracking error, max drawdown)

**Total**: ~24 hours

---

## 3. Correlation Matrix Widget

**Files**:
- Streamlit: `/src/widgets/correlation_matrix_widget.py` (729 lines)
- React: `/frontend/v1/src/app/dashboard/widgets/CorrelationMatrixWidget.tsx`

**Coverage**: ~35% | **Priority**: 🔴 **HIGH**

### Missing Features

#### 🔴 Custom Symbol Addition
**Streamlit Implementation**:
```python
def _render_custom_symbols(self):
    st.markdown("**Add Custom Symbols**")
    st.caption("Add any symbol (stocks, ETFs, indices) for correlation analysis")
    
    # Show available presets
    with st.expander("📊 Quick Add - Common Benchmarks"):
        cols = st.columns(4)
        for i, (symbol, name) in enumerate(self.AVAILABLE_INSTRUMENTS.items()):
            if cols[i % 4].button(f"{symbol}\n{name}", key=f"add_{symbol}"):
                # Add to custom symbols list
                ...
    
    # Manual symbol input
    col1, col2 = st.columns([3, 1])
    with col1:
        new_symbol = st.text_input("Enter symbol:", placeholder="e.g., AAPL, MSFT, ^GSPC",
                                   key=self._get_session_key("new_symbol"))
    with col2:
        if st.button("Add", type="primary"):
            # Validate and add symbol
            validated = validate_symbol(new_symbol.upper())
            if validated:
                custom_symbols.append(validated)
                st.success(f"✅ Added {validated}")
    
    # Show current custom symbols with remove buttons
    render_removable_list(custom_symbols, "Custom Symbols", 
                         self._get_session_key("custom_symbols"))
```

**React**: ❌ Missing - cannot add benchmarks or custom symbols

**Impact**: Cannot compare portfolio against SPY, QQQ, bonds, gold, or any external instruments

---

#### 🔴 Portfolio Aggregation Option
**Streamlit Implementation**:
```python
def _render_portfolio_aggregate_option(self) -> bool:
    st.markdown("**Portfolio Analysis Mode**")
    
    aggregate = st.checkbox(
        "Aggregate portfolio as single instrument",
        value=False,
        help="Combine all holdings into one weighted portfolio for correlation analysis",
        key=self._get_session_key("aggregate")
    )
    
    if aggregate:
        st.info("📊 Portfolio will be treated as a single weighted basket for correlation")
    
    return aggregate
```

**React**: ❌ Missing

**Impact**: Cannot analyze portfolio-level correlations vs. individual holdings

---

#### 🔴 Portfolio-Benchmark Pivot Table
**Streamlit Implementation**:
```python
def _render_portfolio_benchmark_comparison(self, pivot_df: pd.DataFrame):
    st.markdown("**Portfolio vs. Benchmarks**")
    st.caption("Correlation of portfolio holdings against selected benchmarks")
    
    # Pivot table: Holdings as rows, Benchmarks as columns
    st.dataframe(pivot_df.style.background_gradient(cmap='RdYlGn', vmin=-1, vmax=1)
                              .format("{:.2f}"),
                 width='stretch')
    
    # Interpretation guide
    with st.expander("📖 Interpretation Guide"):
        st.markdown("""
        - **Green (0.7 to 1.0)**: Strong positive correlation - assets move together
        - **Yellow (0.3 to 0.7)**: Moderate correlation
        - **Red (-1.0 to 0.3)**: Low or negative correlation - good diversification
        """)
```

**React**: ❌ Missing

---

#### 🟡 Key Correlation Pairs
**Streamlit**:
```python
def _render_key_pairs(self, pairs_df: pd.DataFrame):
    st.markdown("**Key Correlation Pairs**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Highest Correlations** (Redundancy Risk)")
        high_corr = pairs_df.nlargest(10, 'Correlation')
        st.dataframe(high_corr, hide_index=True)
    
    with col2:
        st.markdown("**Lowest Correlations** (Diversification Benefit)")
        low_corr = pairs_df.nsmallest(10, 'Correlation')
        st.dataframe(low_corr, hide_index=True)
```

**React**: ⚠️ Shows statistics but not detailed pair tables

---

#### 🟡 Fetch Missing Data Button
**Streamlit**: Has explicit button to fetch data for symbols not in local database
**React**: Auto-fetches (no user control)

---

### Implementation Roadmap

**Phase 1** (5 hours): Custom symbol input with validation and quick-add benchmarks
**Phase 2** (3 hours): Portfolio aggregation toggle and calculation
**Phase 3** (4 hours): Portfolio-benchmark pivot table with color gradients
**Phase 4** (2 hours): Key correlation pairs tables (highest/lowest)
**Phase 5** (2 hours): Fetch missing data control

**Total**: ~16 hours

---

## 4. Benchmark Comparison Widget

**Files**:
- Streamlit: `/src/widgets/benchmark_comparison_widget.py` (463 lines)
- React: `/frontend/v1/src/app/dashboard/widgets/BenchmarkComparisonWidget.tsx`

**Coverage**: ~60% | **Priority**: 🟡 **MEDIUM**

### Missing Features

#### 🟡 Instrument Selection Checkboxes
**Streamlit Implementation**:
```python
def _render_instrument_selection(self, holdings: List[Dict]) -> List[Dict]:
    st.write("**Select instruments to include in comparison:**")
    
    # Checkbox grid (3 columns)
    selected_symbols = render_holdings_selection_grid(
        holdings=holdings,
        session_key=session_key,
        checkbox_key_prefix=self._get_session_key("instrument"),
        num_columns=3,
        label_formatter=lambda h: f"{h['symbol']} ({h.get('name', '')})"
    )
    
    return [h for h in holdings if h['symbol'] in selected_symbols]
```

**React**: ❌ Missing - uses entire portfolio

**Impact**: Cannot selectively compare subset of holdings

---

#### 🟡 Cumulative Returns Chart
**Streamlit**: Full Plotly chart with both portfolio and benchmark cumulative returns
**React**: ❌ Missing any chart

---

#### 🟡 Side-by-Side Performance Comparison
**Streamlit**:
```python
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Portfolio**")
    st.metric("Total Return", f"{metrics.portfolio_total_return:.1f}%")
    st.metric("Sharpe Ratio", f"{metrics.portfolio_sharpe:.2f}")
    st.metric("Volatility (Annual)", f"{metrics.portfolio_vol:.1f}%")

with col2:
    st.markdown(f"**{self.BENCHMARKS[benchmark_symbol]}**")
    st.metric("Total Return", f"{metrics.benchmark_total_return:.1f}%")
    st.metric("Sharpe Ratio", f"{metrics.benchmark_sharpe:.2f}")
    st.metric("Volatility (Annual)", f"{metrics.benchmark_vol:.1f}%")
```

**React**: ⚠️ Shows metrics but not in side-by-side comparison format

---

### Implementation Roadmap

**Phase 1** (3 hours): Instrument selection checkboxes
**Phase 2** (3 hours): Cumulative returns chart
**Phase 3** (1 hour): Side-by-side comparison layout

**Total**: ~7 hours

---

## 5. Portfolio Summary Widget

**Files**:
- Streamlit: `/src/widgets/portfolio_summary_widget.py` (425 lines)
- React: `/frontend/v1/src/app/dashboard/widgets/PortfolioSummaryWidget.tsx`

**Coverage**: ~55% | **Priority**: 🟡 **MEDIUM**

### Missing Features

#### 🟡 Return Calculation Methods
**Streamlit Implementation**:
```python
def _render_return_metrics(self, metrics: PortfolioMetrics):
    st.markdown("**Return Metrics**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Money-Weighted Return (MWR)", f"{metrics.mwr*100:.2f}%",
                 help="Return accounting for timing and size of cash flows")
    
    with col2:
        st.metric("Time-Weighted Return (TWR)", f"{metrics.twr*100:.2f}%",
                 help="Return independent of cash flows - better for manager evaluation")
    
    with col3:
        if metrics.has_irr:
            st.metric("Internal Rate of Return (IRR)", f"{metrics.irr*100:.2f}%",
                     help="Effective annual return considering cash flows")
        else:
            st.caption("IRR: Requires transaction history")
```

**React**: ❌ Missing MWR, TWR, IRR metrics

**Impact**: Cannot differentiate between personal performance (MWR) and investment performance (TWR)

---

#### 🟡 Portfolio Value Chart
**Streamlit**: Line chart showing portfolio value over time
**React**: ❌ Missing

---

#### 🟡 Income Metrics Section
**Streamlit**:
```python
def _render_income_metrics(self, metrics: PortfolioMetrics):
    st.markdown("**Income Metrics**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Dividend Yield", f"{metrics.dividend_yield*100:.2f}%")
    
    with col2:
        st.metric("Total Return (with dividends)", f"{metrics.total_return_with_divs*100:.2f}%")
```

**React**: ⚠️ Partial - has some income data but not separate section

---

### Implementation Roadmap

**Phase 1** (4 hours): Add MWR, TWR, IRR calculations and display
**Phase 2** (3 hours): Portfolio value line chart
**Phase 3** (1 hour): Income metrics section

**Total**: ~8 hours

---

## 6. Holdings Breakdown Widget

**Files**:
- Streamlit: `/src/widgets/holdings_breakdown_widget.py` (211 lines)
- React: `/frontend/v1/src/app/dashboard/widgets/HoldingsBreakdownWidget.tsx`

**Coverage**: ~70% | **Priority**: 🟡 **MEDIUM**

### Missing Features

#### 🟡 Breakdown Type Selector
**Streamlit Implementation**:
```python
breakdown_by = st.selectbox(
    "Breakdown by:",
    options=['Individual', 'Sector', 'Type'],
    key=self._get_session_key("breakdown")
)

if breakdown_by == 'Individual':
    # Show individual holdings table
elif breakdown_by == 'Sector':
    # Group by sector and show pie chart
elif breakdown_by == 'Type':
    # Group by instrument type (Stock, ETF, Bond, etc.)
```

**React**: ⚠️ Partial - shows individual only, missing sector and type groupings

---

#### 🟡 Multi-Currency Display
**Streamlit**:
```python
if has_currency:
    # Multi-currency view
    display_df = holdings_data.df[['Symbol', 'Name', 'Currency', 'Quantity', 
                                   'Price', 'Value', 'Value (AUD)', 'Allocation %']]
    st.dataframe(display_df)
else:
    # Simple view (backward compatible)
    display_df = holdings_data.df[['Symbol', 'Name', 'Quantity', 
                                   'Price', 'Value', 'Allocation %']]
```

**React**: Shows only single currency

---

#### 🟡 Pie Chart Visualizations
**Streamlit**: Has pie charts for sector and type breakdowns
**React**: Shows only tabular data

---

### Implementation Roadmap

**Phase 1** (2 hours): Add sector and type breakdown modes
**Phase 2** (2 hours): Multi-currency display with local and base currency
**Phase 3** (2 hours): Pie charts for sector/type breakdowns

**Total**: ~6 hours

---

## 7. Constrained Optimization Widget

**Files**:
- Streamlit: `/src/widgets/constrained_optimization_widget.py`
- React: `/frontend/v1/src/app/dashboard/widgets/ConstrainedOptimizationWidget.tsx`

**Coverage**: ~30% | **Priority**: 🔴 **HIGH**

### Missing Features

#### 🔴 Constraint Builder Interface
**Streamlit Implementation**:
```python
def _render_constraint_builder(self):
    st.markdown("**Build Constraints**")
    
    # Weight constraints
    with st.expander("⚖️ Weight Constraints", expanded=True):
        for symbol in symbols:
            col1, col2 = st.columns(2)
            with col1:
                min_weight = st.number_input(f"{symbol} Min %", 0.0, 100.0, 0.0, key=f"min_{symbol}")
            with col2:
                max_weight = st.number_input(f"{symbol} Max %", 0.0, 100.0, 100.0, key=f"max_{symbol}")
    
    # Group constraints
    with st.expander("🏷️ Group Constraints"):
        st.multiselect("Technology sector max:", symbols)
        st.number_input("Max allocation %:", 0.0, 100.0, 30.0)
    
    # Risk constraints
    with st.expander("📉 Risk Constraints"):
        st.number_input("Max portfolio volatility %:", 0.0, 100.0, 20.0)
        st.number_input("Max drawdown %:", 0.0, 100.0, 15.0)
    
    # Return constraints
    with st.expander("📈 Return Constraints"):
        st.number_input("Min expected return %:", 0.0, 100.0, 10.0)
```

**React**: ❌ Missing entire constraint builder interface

---

#### 🔴 Feasibility Analysis
**Streamlit**:
```python
if st.button("Check Feasibility"):
    feasibility = self._check_constraint_feasibility(constraints, returns_df)
    
    if feasibility.is_feasible:
        st.success("✅ Constraints are feasible - solution exists")
    else:
        st.error("❌ Constraints are infeasible")
        st.markdown("**Conflicting Constraints:**")
        for conflict in feasibility.conflicts:
            st.warning(f"• {conflict}")
```

**React**: ❌ Missing

---

#### 🔴 Sensitivity Analysis
**Streamlit**:
```python
with st.expander("🔬 Sensitivity Analysis"):
    if st.button("Run Sensitivity Analysis"):
        # Vary each constraint ±10% and show impact on optimal portfolio
        sensitivity_results = self._run_sensitivity_analysis(constraints, returns_df)
        
        st.markdown("**Impact of Constraint Changes**")
        st.dataframe(sensitivity_df)  # Constraint, -10%, Base, +10%, Impact Score
```

**React**: ❌ Missing

---

### Implementation Roadmap

**Phase 1** (6 hours): Constraint builder UI (weight, group, risk, return)
**Phase 2** (4 hours): Feasibility checker with conflict detection
**Phase 3** (4 hours): Sensitivity analysis tool
**Phase 4** (2 hours): Constraint visualization and validation

**Total**: ~16 hours

---

## 8. Portfolio Transition Widget

**Files**:
- Streamlit: `/src/widgets/portfolio_transition_widget.py`
- React: `/frontend/v1/src/app/dashboard/widgets/PortfolioTransitionWidget.tsx`

**Coverage**: ~25% | **Priority**: 🔴 **HIGH**

### Missing Features

#### 🔴 Target Portfolio Builder
**Streamlit Implementation**:
```python
def _render_target_portfolio_builder(self, instruments: List[Dict], total_value: float):
    st.markdown("**Design Target Portfolio**")
    st.caption(f"Current portfolio value: ${total_value:,.2f}")
    
    # Method selector
    build_method = st.radio("Build method:",
        ["Scratch (Manual)", "Optimize", "Model Portfolio", "Current + Adjustments"])
    
    if build_method == "Scratch (Manual)":
        # Add instruments manually with target allocations
        target_positions = []
        for symbol in st.multiselect("Select instruments:", all_symbols):
            weight = st.slider(f"{symbol} allocation:", 0.0, 100.0, 10.0)
            target_positions.append({'symbol': symbol, 'weight': weight})
    
    elif build_method == "Optimize":
        # Use optimizer to build target
        objective = st.selectbox("Objective:", ["Max Sharpe", "Min Volatility", "Target Return"])
        # ... optimization logic
    
    elif build_method == "Model Portfolio":
        # Load from predefined models
        model = st.selectbox("Model:", ["60/40 Balanced", "Aggressive Growth", "Conservative Income"])
        target_positions = self._load_model_portfolio(model)
    
    elif build_method == "Current + Adjustments":
        # Start with current and allow tweaks
        st.markdown("**Current Positions (editable)**")
        for holding in current_holdings:
            new_weight = st.number_input(f"{holding['symbol']}:", value=holding['weight'])
    
    return target_positions
```

**React**: ❌ Missing - no target portfolio builder

---

#### 🔴 Step-by-Step Transition Plan
**Streamlit Implementation**:
```python
def _render_transition_plan(self, plan: Dict, num_steps: int, transaction_cost_pct: float):
    st.markdown(f"### Transition Plan ({num_steps} Steps)")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Cost", f"${plan['total_cost']:,.2f}")
    with col2: st.metric("Tax Impact", f"${plan['tax_impact']:,.2f}")
    with col3: st.metric("Tracking Error", f"{plan['tracking_error']:.2f}%")
    with col4: st.metric("Time to Complete", f"{num_steps} periods")
    
    # Step-by-step breakdown
    for i, step in enumerate(plan['steps'], 1):
        with st.expander(f"Step {i} - {step['date']}"):
            st.markdown("**Actions:**")
            
            # Sells first
            if step['sells']:
                st.markdown("**Sell:**")
                st.dataframe(pd.DataFrame(step['sells']))  # Symbol, Shares, Price, Proceeds
            
            # Then buys
            if step['buys']:
                st.markdown("**Buy:**")
                st.dataframe(pd.DataFrame(step['buys']))  # Symbol, Shares, Price, Cost
            
            # Portfolio state after step
            st.markdown(f"**Portfolio after step {i}:**")
            st.dataframe(step['portfolio_state'])
```

**React**: ❌ Missing

---

#### 🔴 Transition Cost Analysis
**Streamlit**: Breaks down costs by transaction costs, tax impact, market impact, opportunity cost
**React**: ❌ Missing

---

#### 🔴 Transition Visualization
**Streamlit**: Animated chart showing portfolio composition changing over transition steps
**React**: ❌ Missing

---

### Implementation Roadmap

**Phase 1** (8 hours): Target portfolio builder with 4 build methods
**Phase 2** (6 hours): Transition plan generator with step-by-step breakdown
**Phase 3** (3 hours): Cost analysis (transaction, tax, market impact)
**Phase 4** (4 hours): Transition visualization chart

**Total**: ~21 hours

---

## 9. Timeseries Analysis Widget

**Files**:
- Streamlit: `/src/widgets/timeseries_analysis_widget.py` (2400+ lines)
- React: `/frontend/v1/src/app/dashboard/widgets/TimeseriesAnalysisWidget.tsx`

**Coverage**: ~20% | **Priority**: 🔴 **HIGH**

### Missing Features

**Note**: This is the largest and most complex widget with 15+ statistical tests and analyses.

#### 🔴 Statistical Tests (Most Missing)

**Streamlit Has**:
1. ❌ Stationarity Analysis (ADF, KPSS, PP tests)
2. ❌ Mean Reversion Analysis (Half-life calculation)
3. ❌ Cointegration Analysis (Johansen, Engle-Granger tests)
4. ❌ Autocorrelation Analysis (ACF, PACF plots)
5. ❌ Volatility Clustering (ARCH effects)
6. ❌ Diagnostic Tests (Normality, Heteroskedasticity)
7. ❌ Granger Causality Tests
8. ❌ Rolling Statistics (window-based metrics)
9. ❌ Structural Break Detection (CUSUM, Chow test)
10. ❌ Portfolio-Level Stationarity
11. ❌ Portfolio Mean Reversion
12. ❌ Portfolio Diagnostics
13. ❌ Portfolio Autocorrelation
14. ❌ Portfolio Volatility Analysis
15. ❌ Portfolio Rolling Stats

**React Has**: Basic price chart only

---

#### 🔴 Analysis Mode Selector
**Streamlit**:
```python
mode = st.radio("Analysis Mode:",
    ["Individual Instruments", "Pairwise Analysis", "Portfolio-Level"],
    key=self._get_session_key("mode"))

if mode == "Individual Instruments":
    analysis_type = st.selectbox("Analysis Type:",
        ["Stationarity", "Mean Reversion", "Autocorrelation", "Volatility Clustering",
         "Diagnostics", "Rolling Statistics", "Structural Breaks"])
    
elif mode == "Pairwise Analysis":
    analysis_type = st.selectbox("Analysis Type:",
        ["Cointegration", "Granger Causality"])
    
elif mode == "Portfolio-Level":
    analysis_type = st.selectbox("Analysis Type:",
        ["Portfolio Stationarity", "Portfolio Mean Reversion", "Portfolio Diagnostics",
         "Portfolio Autocorrelation", "Portfolio Volatility", "Portfolio Rolling Stats"])
```

**React**: ❌ No analysis mode selection

---

#### 🔴 Example: Stationarity Analysis
**Streamlit**:
```python
def _render_stationarity_results(self, results: StationarityResults, symbol: str):
    st.markdown(f"### Stationarity Analysis - {symbol}")
    
    # Test results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ADF Test", "✅ Stationary" if results.adf_stationary else "❌ Non-Stationary")
        st.caption(f"p-value: {results.adf_pvalue:.4f}")
    
    with col2:
        st.metric("KPSS Test", "✅ Stationary" if results.kpss_stationary else "❌ Non-Stationary")
        st.caption(f"p-value: {results.kpss_pvalue:.4f}")
    
    with col3:
        st.metric("PP Test", "✅ Stationary" if results.pp_stationary else "❌ Non-Stationary")
        st.caption(f"p-value: {results.pp_pvalue:.4f}")
    
    # Interpretation
    if results.adf_stationary and results.kpss_stationary:
        st.success("✅ Series is stationary - mean and variance are constant over time")
    elif not results.adf_stationary and not results.kpss_stationary:
        st.error("❌ Series is non-stationary - differencing recommended")
    else:
        st.warning("⚠️ Mixed results - series may be trend-stationary")
    
    # Recommendations
    with st.expander("📖 Recommendations"):
        if not results.adf_stationary:
            st.markdown("**Suggested actions:**")
            st.markdown("1. Apply first-differencing: `returns = prices.diff()`")
            st.markdown("2. Or log-differencing: `log_returns = np.log(prices).diff()`")
            st.markdown("3. Re-test stationarity after transformation")
```

**React**: ❌ Not available

---

### Implementation Roadmap

**Note**: Due to extreme complexity, this should be phased carefully.

**Phase 1** (10 hours): Basic tests (Stationarity, Mean Reversion, Autocorrelation)
**Phase 2** (8 hours): Cointegration and Granger Causality
**Phase 3** (8 hours): Diagnostics and Volatility Clustering
**Phase 4** (8 hours): Rolling Statistics and Structural Breaks
**Phase 5** (10 hours): Portfolio-level analyses

**Total**: ~44 hours (largest widget implementation)

**Alternative**: Consider splitting into multiple specialized widgets

---

## 10. Dividend Analysis Widget

**Files**:
- Streamlit: `/src/widgets/dividend_analysis_widget.py`
- React: `/frontend/v1/src/app/dashboard/widgets/DividendAnalysisWidget.tsx`

**Coverage**: ~45% | **Priority**: 🟡 **MEDIUM**

### Missing Features

#### 🟡 Cash Flow Tracker
**Streamlit**:
```python
def _render_cash_flow_tracker(self, holdings: List[Dict]):
    st.markdown("**Dividend Cash Flow Tracker**")
    st.caption("Track upcoming and historical dividend payments")
    
    # Upcoming dividends
    st.markdown("**Upcoming Payments (Next 90 days)**")
    upcoming = self._get_upcoming_dividends(holdings, days=90)
    if upcoming:
        st.dataframe(upcoming)  # Date, Symbol, Amount, Yield, Days Until
        st.metric("Total Expected (90 days)", f"${sum(upcoming['Amount']):,.2f}")
    
    # Historical payments
    st.markdown("**Payment History**")
    historical = self._get_dividend_history(holdings, days=365)
    st.dataframe(historical)
    
    # Cash flow chart
    monthly_cashflow = historical.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].sum()
    st.bar_chart(monthly_cashflow)
```

**React**: ❌ Missing cash flow tracking

---

#### 🟡 Manual Dividend Entry
**Streamlit**:
```python
def _render_manual_entry_form(self, holdings: List[Dict]):
    st.markdown("**Manual Dividend Entry**")
    st.caption("Add dividend payments not captured automatically")
    
    with st.form("dividend_entry"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            symbol = st.selectbox("Symbol:", [h['symbol'] for h in holdings])
        with col2:
            amount = st.number_input("Amount ($):", min_value=0.0, step=0.01)
        with col3:
            date = st.date_input("Payment Date:")
        with col4:
            submitted = st.form_submit_button("Add Entry")
        
        if submitted:
            self._save_manual_dividend(symbol, amount, date)
            st.success(f"✅ Added ${amount:.2f} dividend for {symbol}")
```

**React**: ❌ Missing

---

#### 🟡 Dividend Yield Projections
**Streamlit**: Projects next 12 months based on trailing yields
**React**: ⚠️ Partial

---

### Implementation Roadmap

**Phase 1** (4 hours): Cash flow tracker with upcoming/historical tables
**Phase 2** (3 hours): Manual dividend entry form
**Phase 3** (2 hours): Monthly cash flow chart
**Phase 4** (2 hours): Yield projections

**Total**: ~11 hours

---

## 11. News/Event Analysis Widget

**Files**:
- Streamlit: `/src/widgets/news_event_analysis_widget.py`
- React: `/frontend/v1/src/app/dashboard/widgets/NewsEventAnalysisWidget.tsx`

**Coverage**: ~10% | **Priority**: 🔴 **HIGH**

### Status

This widget is essentially **completely missing** from React implementation.

**Streamlit Features**:
- News article fetching and analysis
- Event impact correlation (earnings, splits, dividends vs. price movements)
- Sentiment analysis
- Event timeline visualization
- Price reaction charts around events

**React**: Basic placeholder or minimal news display

---

### Implementation Roadmap

**Full Implementation**: ~30 hours (complete rebuild required)

---

## 12. Performance Widget

**Files**:
- Streamlit: `/src/widgets/performance_widget.py`
- React: `/frontend/v1/src/app/dashboard/widgets/PerformanceWidget.tsx`

**Coverage**: ~65% | **Priority**: 🟡 **MEDIUM**

### Missing Features

#### 🟡 Performance Metrics Table
**Streamlit**:
```python
def _render_performance_table(self, metrics: List[PerformanceMetrics]):
    st.markdown("**Holdings Performance**")
    
    table_data = []
    for metric in metrics:
        table_data.append({
            'Symbol': metric.symbol,
            'Total Return': f"{metric.total_return:.2f}%",
            'Volatility': f"{metric.volatility:.2f}%",
            'Sharpe Ratio': f"{metric.sharpe:.2f}",
            'Max Drawdown': f"{metric.max_drawdown:.2f}%",
            'YTD Return': f"{metric.ytd_return:.2f}%"
        })
    
    # Sortable table
    st.dataframe(pd.DataFrame(table_data), hide_index=True, width='stretch',
                 column_config={
                     "Total Return": st.column_config.NumberColumn("Total Return", format="%.2f%%"),
                     # ...
                 })
```

**React**: ⚠️ Shows summary metrics but not detailed table

---

### Implementation Roadmap

**Phase 1** (2 hours): Performance metrics table
**Phase 2** (2 hours): Sortable columns and formatting

**Total**: ~4 hours

---

## 13. Constrained Optimization Widget

**(Already covered above as Widget #7)**

---

## 14. News/Event Analysis Widget

**(Already covered above as Widget #11)**

---

## Summary Table: All Widgets

| Widget | Lines (Streamlit) | Lines (React) | Coverage | Missing Hours | Priority |
|--------|-------------------|---------------|----------|---------------|----------|
| Monte Carlo | 1,520 | 436 | 40% | 42 | 🔴 HIGH |
| Portfolio Optimizer | 1,686 | 304 | 50% | 24 | 🔴 HIGH |
| Correlation Matrix | 729 | ~200 | 35% | 16 | 🔴 HIGH |
| Timeseries Analysis | 2,400+ | ~150 | 20% | 44 | 🔴 HIGH |
| Constrained Opt | ~800 | ~150 | 30% | 16 | 🔴 HIGH |
| Portfolio Transition | ~600 | ~100 | 25% | 21 | 🔴 HIGH |
| News/Event Analysis | ~750 | ~50 | 10% | 30 | 🔴 HIGH |
| Benchmark Comparison | 463 | ~200 | 60% | 7 | 🟡 MEDIUM |
| Portfolio Summary | 425 | ~150 | 55% | 8 | 🟡 MEDIUM |
| Holdings Breakdown | 211 | ~150 | 70% | 6 | 🟡 MEDIUM |
| Dividend Analysis | ~300 | ~120 | 45% | 11 | 🟡 MEDIUM |
| Performance | ~150 | ~100 | 65% | 4 | 🟡 MEDIUM |

**Total Implementation Effort**: ~229 hours (~29 days)

---

## Priority Implementation Order

### Phase 1: Critical Feature Completions (High Priority)

**Order**: Monte Carlo → Portfolio Optimizer → Correlation Matrix

These three are most-used and have significant missing functionality.

**Estimated**: ~82 hours

---

### Phase 2: Advanced Analysis Tools (High Priority)

**Order**: Constrained Optimization → Portfolio Transition → Timeseries Analysis

Professional features for advanced users.

**Estimated**: ~81 hours

---

### Phase 3: Core Portfolio Tools (Medium Priority)

**Order**: Benchmark Comparison → Portfolio Summary → Dividend Analysis → Holdings Breakdown → Performance

General portfolio management and reporting.

**Estimated**: ~36 hours

---

### Phase 4: News/Events (High Priority but Separate)

Can be developed in parallel by separate developer.

**Estimated**: ~30 hours

---

## Common Patterns to Accelerate Development

### 1. Reusable Components Needed

- **InstrumentMultiSelect**: Used by 8+ widgets
- **WeightAllocator**: Used by 4 widgets
- **MetricComparison**: Side-by-side before/after displays
- **ExportButton**: CSV download functionality
- **ExpandableSection**: Collapsible advanced settings
- **ChartWithControls**: Chart + configuration in one component

Creating these once saves ~20 hours across all widgets.

---

### 2. API Response Standardization

Many widgets need similar data structures:
- Time-series data with percentiles
- Optimization results with weights
- Statistical test results with p-values
- Historical performance metrics

Standardizing API contracts reduces frontend complexity.

---

### 3. Chart Library Strategy

**Decision Point**: Continue with Recharts or adopt Plotly.js?

- **Recharts**: Simpler, React-native, limited features
- **Plotly.js**: Feature-complete, matches Streamlit charts

**Recommendation**: Adopt Plotly.js for complex widgets (efficient frontier, fan charts, heatmaps) to match Streamlit functionality.

---

## Conclusion

The Streamlit widgets represent a comprehensive financial analysis platform with **~12,000 lines of UI specification code**. Current React implementation covers roughly **40-50% of intended functionality** with significant gaps in:

1. Interactive controls and multi-stage workflows
2. Advanced optimization and analysis modes
3. Statistical testing and diagnostics
4. Export and data portability
5. Professional-grade visualizations

**Total effort to reach feature parity**: ~229 hours (~6 weeks with 1 developer, or 3 weeks with 2 developers)

This document serves as the roadmap for closing these gaps systematically.
