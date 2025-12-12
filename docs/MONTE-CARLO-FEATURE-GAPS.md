# Monte Carlo Widget - Feature Gap Analysis

**Purpose**: Document missing functionality in the React/Next.js frontend compared to the original Streamlit widget specification.

**Source of Truth**: `/src/widgets/monte_carlo_widget.py` (Streamlit UI methods)  
**Current Implementation**: `/frontend/v1/src/app/dashboard/widgets/MonteCarloWidget.tsx`

---

## Executive Summary

The React implementation covers **~40%** of the Streamlit widget's functionality. Major missing features include:

1. ❌ **Portfolio Selection UI** - No instrument picker or weight allocation controls
2. ❌ **Portfolio Statistics Display** - No historical metrics expander
3. ❌ **Advanced Simulation Controls** - Missing years input, initial value input, contribution settings, rebalancing analysis
4. ❌ **Fan Chart Visualization** - Only histogram shown, no percentile bands over time
5. ❌ **Rebalancing Recommendations** - Complete feature missing
6. ❌ **Percentile Table** - No detailed breakdown with interpretations
7. ❌ **Export Options** - No CSV download functionality
8. ❌ **Interactive "Run Simulation" Button** - Auto-fetches instead of user-triggered

---

## Detailed Feature Comparison

### 1. Portfolio Selection & Weight Allocation

#### Streamlit Implementation (`_render_portfolio_selector`)
```python
# Multi-select for instruments (portfolio holdings listed first)
selected_symbols = st.multiselect(
    "Instruments:",
    options=symbol_options,
    default=default_symbols,
    key=self._get_session_key("instruments")
)

# Weight allocation methods
weight_method = st.selectbox(
    "Weight allocation method:",
    options=["Equal Weights", "Max Sharpe Ratio", "Min Volatility", 
             "Current Portfolio", "Custom"],
    help="Method for determining portfolio weights"
)

# Custom weight inputs (when selected)
for symbol in selected_symbols:
    weights[symbol] = st.number_input(
        f"{symbol} %",
        min_value=0.0,
        max_value=100.0,
        value=weight_value,
        step=1.0
    )

# Weight visualization
with st.expander("View Weight Allocation", expanded=False):
    st.dataframe(weight_df, hide_index=True, width="stretch")
```

#### React Implementation
- ❌ **MISSING**: No instrument selection UI
- ❌ **MISSING**: No weight allocation method selector
- ❌ **MISSING**: No custom weight inputs
- ❌ **MISSING**: No weight visualization table/chart
- ⚠️ **IMPACT**: Cannot simulate different portfolio compositions
- ⚠️ **IMPACT**: Cannot test optimization strategies (Max Sharpe, Min Volatility)

**Implementation Priority**: 🔴 **HIGH** - Core feature for flexible analysis

---

### 2. Portfolio Historical Statistics

#### Streamlit Implementation (`_render_portfolio_statistics`)
```python
with st.expander("Portfolio Historical Statistics", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Historical Return (Ann.)", f"{ann_return*100:.2f}%")
    
    with col2:
        st.metric("Historical Volatility (Ann.)", f"{ann_volatility*100:.2f}%")
    
    with col3:
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
    
    with col4:
        st.metric("Max Drawdown", f"{max_drawdown*100:.1f}%", delta_color="inverse")
```

#### React Implementation
- ✅ **PARTIAL**: Shows Sharpe ratio and volatility in "Risk Metrics" section
- ❌ **MISSING**: No historical return metric
- ❌ **MISSING**: No max drawdown metric
- ❌ **MISSING**: Not in collapsible expander (always visible or hidden)
- ⚠️ **IMPACT**: Users don't see baseline performance before running simulation

**Implementation Priority**: 🟡 **MEDIUM** - Nice-to-have context

---

### 3. Simulation Parameters

#### Streamlit Implementation (`_render_simulation_parameters`)
```python
# Basic parameters
num_sims = st.slider("Number of simulations", 100, 10000, 1000, step=100)
years = st.slider("Time horizon (years)", 1, 30, 10, step=1)
initial_value = st.number_input("Initial portfolio value ($)", 
                                min_value=1000.0, 
                                max_value=10000000.0, 
                                value=100000.0, 
                                step=10000.0)

# Advanced Settings (in expander)
with st.expander("Advanced Settings"):
    # Estimation & confidence
    include_dividends = st.toggle("Include dividends", value=True)
    confidence_level = st.slider("Confidence level (%)", 80, 99, 90, step=1)
    estimation_method = st.selectbox("Parameter estimation",
                                    ["Historical Mean", "Exponentially Weighted"])
    
    # Contributions
    enable_contributions = st.checkbox("Enable periodic contributions", value=False)
    contribution_amount = st.number_input("Annual contribution ($)", 
                                         min_value=-100000.0, 
                                         max_value=1000000.0, 
                                         value=10000.0, 
                                         disabled=not enable_contributions)
    contribution_frequency = st.selectbox("Frequency",
                                         ["Annual", "Quarterly", "Monthly"],
                                         disabled=not enable_contributions)
    
    # Rebalancing Analysis
    enable_rebalancing_analysis = st.checkbox("Analyze rebalancing timing", value=False)
    drift_threshold = st.slider("Drift threshold (%)", 5.0, 30.0, 10.0, step=2.5)
    transaction_cost_pct = st.number_input("Transaction cost (%)", 0.0, 2.0, 0.1, step=0.05)
    max_rebalances_per_year = st.slider("Max rebalances per year", 1, 12, 4, step=1)
```

#### React Implementation
```tsx
// Basic controls (2x2 grid)
<select value={numSimulations}>  {/* 1K, 5K, 10K, 25K */}
<select value={timeHorizonDays}> {/* 30d, 90d, 180d, 252d, 504d */}
<select value={estimationMethod}> {/* Historical Mean, Exp. Weighted */}
<select value={confidenceLevel}> {/* 90%, 95%, 99% */}

// Checkboxes
<input type="checkbox" checked={includeDividends} />
<input type="checkbox" checked={enableContributions} />

// Contribution fields (conditional)
{enableContributions && (
  <input type="number" value={contributionAmount} />
  <select value={contributionFrequency}> {/* Monthly, Quarterly, Annual */}
)}
```

**Feature Gaps**:
- ❌ **MISSING**: Years input (uses days dropdown instead of 1-30 year range)
- ❌ **MISSING**: Initial value input (API defaults used, not user-configurable)
- ❌ **MISSING**: Full simulation range (100-10,000 in Streamlit vs. fixed options in React)
- ❌ **MISSING**: Rebalancing analysis toggle
- ❌ **MISSING**: Drift threshold slider
- ❌ **MISSING**: Transaction cost input
- ❌ **MISSING**: Max rebalances per year constraint
- ⚠️ **IMPACT**: Cannot analyze long-term scenarios (10-30 years)
- ⚠️ **IMPACT**: Cannot configure starting capital
- ⚠️ **IMPACT**: Cannot predict optimal rebalancing timing

**Implementation Priority**: 
- 🔴 **HIGH**: Years/initial value inputs (core simulation flexibility)
- 🟡 **MEDIUM**: Rebalancing analysis (advanced professional feature)

---

### 4. Run Simulation Control

#### Streamlit Implementation
```python
if st.button("Run Monte Carlo Simulation", type="primary", width="stretch"):
    # Fetch historical data
    returns_df = self._fetch_returns_data(...)
    
    # Run simulation
    with st.spinner(f"Running {sim_params['num_sims']:,} simulations..."):
        results = self._run_monte_carlo(...)
    
    # Display results
    self._render_simulation_results(results, sim_params)
```

#### React Implementation
```tsx
// Auto-fetches when component mounts or params change
const { data: simulation, loading, error, cacheHit } = useMonteCarloSimulation({
  portfolioId,
  numSimulations,
  timeHorizonDays,
  // ... other params
});
```

**Feature Gaps**:
- ❌ **MISSING**: Explicit "Run Simulation" button (user control)
- ❌ **MISSING**: Loading spinner with progress message
- ✅ **IMPLEMENTED**: Auto-refresh via React Query (different UX pattern)
- ⚠️ **IMPACT**: Users cannot control when expensive calculation runs
- ⚠️ **IMPACT**: Changing any parameter immediately triggers re-fetch

**Implementation Priority**: 🟡 **MEDIUM** - UX preference (auto-fetch is valid pattern, but button gives more control)

---

### 5. Simulation Results Display

#### Streamlit Implementation (`_render_simulation_results`)

**Summary Info Box**:
```python
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Simulations Run:** {results.num_sims:,}")
        st.markdown(f"**Time Horizon:** {params['years']} years")
    with col2:
        st.markdown(f"**Initial Value:** ${results.initial_value:,.0f}")
        st.markdown(f"**Annual Contribution:** ${params['contribution_amount']:,.0f} ...")
    with col3:
        st.markdown(f"**Weight Method:** {weight_method}")
        st.markdown(f"**Estimation Method:** {params['estimation_method']}")
```

#### React Implementation
```tsx
// Simulation parameters shown in "Simulation Parameters" card
<div className="space-y-2 text-sm">
  <div className="flex justify-between">
    <span>Initial Value:</span>
    <span>{formatCurrency(simulation?.simulation_params?.initial_value || 0)}</span>
  </div>
  <div className="flex justify-between">
    <span>Time Horizon:</span>
    <span>{(simulation?.simulation_params?.time_horizon_years || 0).toFixed(2)} years</span>
  </div>
  <div className="flex justify-between">
    <span>Simulations:</span>
    <span>{(simulation?.simulation_params?.num_simulations || 0).toLocaleString()}</span>
  </div>
</div>
```

**Feature Gaps**:
- ❌ **MISSING**: Contribution amount/frequency display
- ❌ **MISSING**: Weight method display
- ❌ **MISSING**: Estimation method display
- ✅ **IMPLEMENTED**: Initial value, time horizon, num simulations

**Implementation Priority**: 🟢 **LOW** - Informational context

---

### 6. Key Performance Metrics

#### Streamlit Implementation (`_render_key_metrics`)
```python
st.markdown("### Key Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Median Final Value", f"${results.percentile_50:,.0f}",
              delta=f"{results.cagr_median:.2f}% CAGR")

with col2:
    st.metric(f"{lower_pct}th Percentile (Downside)", 
              f"${results.percentile_10:,.0f}",
              delta=f"{results.cagr_10th:.2f}% CAGR",
              help=f"Worst-case scenario at {params['confidence_level']}% confidence")

with col3:
    st.metric(f"{upper_pct}th Percentile (Upside)", 
              f"${results.percentile_90:,.0f}",
              delta=f"{results.cagr_90th:.2f}% CAGR",
              help=f"Best-case scenario at {params['confidence_level']}% confidence")

with col4:
    st.metric("Probability of Loss", f"{prob_loss:.1f}%",
              help="Percentage of simulations ending below initial value")

st.markdown("### Risk Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Value at Risk (95%)", f"${results.var_95:,.0f}",
              delta=f"{((results.var_95 / results.initial_value - 1) * 100):+.1f}%",
              help="5% chance of losing more than this amount",
              delta_color="inverse")

with col2:
    st.metric("Conditional VaR (95%)", f"${results.cvar_95:,.0f}",
              delta=f"{((results.cvar_95 / results.initial_value - 1) * 100):+.1f}%",
              help="Average loss in worst 5% of scenarios",
              delta_color="inverse")

with col3:
    st.metric("Max Drawdown (Median)", f"{results.max_drawdown_median:.1f}%",
              help="Largest peak-to-trough decline in median path",
              delta_color="inverse")

with col4:
    st.metric("Historical Sharpe Ratio", f"{results.historical_sharpe:.2f}",
              help="Risk-adjusted return based on selected weights")
```

#### React Implementation
```tsx
// Key metrics (4 MetricCards)
<MetricCard title="Expected Return" value={formatPercent(statistics.mean_return_percent / 100)} />
<MetricCard title="Value at Risk (95%)" value={formatCurrency(var95)} />
<MetricCard title="Best Case (90%)" value={formatCurrency(percentiles["90"])} />
<MetricCard title="Loss Probability" value={formatPercent(statistics.probability_of_loss)} />
```

**Feature Gaps**:
- ❌ **MISSING**: Median final value with CAGR delta
- ❌ **MISSING**: 10th percentile with CAGR delta
- ❌ **MISSING**: 90th percentile with CAGR delta (shows value but not CAGR)
- ❌ **MISSING**: Conditional VaR (CVaR/Expected Shortfall)
- ❌ **MISSING**: Max drawdown metric
- ❌ **MISSING**: VaR shown as % return from initial value
- ✅ **IMPLEMENTED**: VaR 95%, probability of loss, Sharpe ratio, volatility

**Implementation Priority**: 🔴 **HIGH** - Missing critical professional metrics (CVaR, drawdown, CAGR)

---

### 7. Fan Chart Visualization

#### Streamlit Implementation (`_render_fan_chart`)
```python
st.markdown("**Portfolio Value Over Time (Monte Carlo Paths)**")

fig = go.Figure()

# Add percentile bands (outer, middle, inner)
bands = [
    (lower_pct, upper_pct, 0.1, f"{params['confidence_level']}% confidence"),
    (25, 75, 0.2, "25-75th percentile"),
    (40, 60, 0.3, "40-60th percentile")
]

for lower, upper, opacity, label in bands:
    # Upper and lower bands with fill
    fig.add_trace(go.Scatter(..., fill='tonexty', fillcolor=f'rgba(68, 138, 255, {opacity})'))

# Add median line
fig.add_trace(go.Scatter(x=results.time_points, y=results.percentiles[50], 
                         line=dict(color='#1f77b4', width=3), 
                         name='Median (50th percentile)'))

# Add initial value line
fig.add_hline(y=results.initial_value, line_dash="dash", 
              annotation_text="Initial Value")

st.plotly_chart(fig, width='stretch')
```

#### React Implementation
- ❌ **MISSING**: Fan chart completely absent
- ✅ **IMPLEMENTED**: Histogram of final values only
- ⚠️ **IMPACT**: Cannot visualize paths over time
- ⚠️ **IMPACT**: Cannot see confidence bands evolution
- ⚠️ **IMPACT**: Cannot observe median trajectory vs. initial value

**Implementation Priority**: 🔴 **HIGH** - Critical visualization for understanding simulation dynamics

**Implementation Notes**:
- Need time-series data from API (`percentiles_over_time` or similar)
- Use Recharts `<AreaChart>` with multiple `<Area>` layers for percentile bands
- Add reference line for initial value

---

### 8. Distribution Chart (Histogram)

#### Streamlit Implementation (`_render_distribution_chart`)
```python
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
for pct, color, label in percentile_lines:
    value = results.percentiles[pct][-1]
    fig.add_vline(x=value, line_dash="dash", line_color=color,
                  annotation_text=f"{label}: ${value:,.0f}")

st.plotly_chart(fig, width='stretch')
```

#### React Implementation
```tsx
// Simple histogram with bars
<div className="space-y-1">
  {histogramData.map((bucket, index) => (
    <div key={index} className="flex items-center gap-2 text-sm">
      <div className="w-32 text-xs">{formatCurrency(bucket.midpoint)}</div>
      <div className="flex-1 bg-muted rounded-full h-2">
        <div className="h-full bg-blue-500" style={{ width: `${barWidth}%` }} />
      </div>
      <div className="w-12 text-xs">{bucket.percentage.toFixed(1)}%</div>
    </div>
  ))}
</div>
```

**Feature Gaps**:
- ❌ **MISSING**: Vertical lines for key percentiles (10th, 50th, 90th)
- ❌ **MISSING**: Plotly/Recharts proper histogram chart
- ✅ **IMPLEMENTED**: Basic bar visualization with percentages

**Implementation Priority**: 🟡 **MEDIUM** - Current implementation functional but could be enhanced

---

### 9. Percentile Table

#### Streamlit Implementation (`_render_percentile_table`)
```python
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
```

**Interpretation Helper**:
```python
@staticmethod
def _get_percentile_interpretation(pct: int) -> str:
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
```

#### React Implementation
```tsx
// Only shows 3 percentiles (10th, 50th, 90th) in cards
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  <div className="text-center p-3 border rounded-lg">
    <div className="text-sm">10th Percentile</div>
    <div className="text-lg font-bold">{formatCurrency(percentiles["10"])}</div>
    <div className="text-xs">{formatPercent((percentiles["10"] - initialValue) / initialValue)}</div>
  </div>
  {/* ... 50th and 90th ... */}
</div>
```

**Feature Gaps**:
- ❌ **MISSING**: Comprehensive table with 7 percentiles (5, 10, 25, 50, 75, 90, 95)
- ❌ **MISSING**: Human-readable interpretations ("Pessimistic scenario", "Optimistic scenario", etc.)
- ❌ **MISSING**: Total return % column
- ✅ **IMPLEMENTED**: Shows 10th, 50th, 90th with values and returns

**Implementation Priority**: 🟡 **MEDIUM** - Educational/interpretive feature

---

### 10. Rebalancing Recommendations

#### Streamlit Implementation (`_render_rebalancing_recommendations`)
```python
st.markdown("### Optimal Rebalancing Analysis")

with st.container(border=True):
    st.markdown(f"**{rec.description}**")  # e.g., "Recommend rebalancing 3 times..."
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Recommended Rebalances", f"{len(rec.rebalance_dates)}",
                  help="Number of times to rebalance over simulation period")
    
    with col2:
        avg_months = (params['years'] * 12) / (len(rec.rebalance_dates) + 1)
        st.metric("Avg Time Between", f"{avg_months:.1f} months")
    
    with col3:
        st.metric("Avg Drift at Rebalance", f"{rec.avg_drift*100:.1f}%")
    
    with col4:
        st.metric("Sharpe Improvement", f"{rec.sharpe_improvement:+.3f}",
                  delta=f"{rec.cost_benefit_ratio:.1f}x cost")

# Rebalancing calendar
st.markdown("#### Recommended Rebalancing Dates")
rebal_df = pd.DataFrame([...])  # Date, Time, Max Drift %, Instruments Affected
st.dataframe(rebal_df, width='stretch', hide_index=True)

# Detailed per-instrument view
with st.expander("View Detailed Rebalancing Actions by Instrument", expanded=False):
    inst_rebal_df = pd.DataFrame([...])  # Date, Instrument, Current %, Target %, Drift %, Action
    st.dataframe(inst_rebal_df, width='stretch')

# Timeline visualization
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=years_from_start,
    y=rec.drift_at_rebalance,
    mode='markers+lines',
    marker=dict(size=12, color='red', symbol='diamond'),
    name='Rebalancing Events'
))
fig.add_hline(y=rec.trigger_threshold, line_dash="dash", 
              annotation_text=f"Drift Threshold ({rec.trigger_threshold*100:.0f}%)")
st.plotly_chart(fig, width='stretch')
```

#### React Implementation
- ❌ **MISSING**: Entire rebalancing recommendation feature absent
- ⚠️ **IMPACT**: Cannot predict when to rebalance portfolio
- ⚠️ **IMPACT**: Cannot analyze cost/benefit of rebalancing strategy
- ⚠️ **IMPACT**: Cannot see which instruments need adjustment

**Implementation Priority**: 🟡 **MEDIUM** - Advanced professional feature (requires backend support)

**Implementation Notes**:
- Requires API endpoint to return `rebalancing_rec` object
- Need to add UI toggle in parameters section
- Build table component for rebalancing calendar
- Build chart for drift timeline

---

### 11. Export Options

#### Streamlit Implementation (`_render_export_options`)
```python
st.markdown("### Export Simulation Data")

col1, col2 = st.columns(2)

with col1:
    # Export percentiles over time
    percentile_df = pd.DataFrame({
        'Year': results.time_points,
        '5th Percentile': results.percentiles[5],
        '10th Percentile': results.percentiles[10],
        # ... all percentiles ...
        '95th Percentile': results.percentiles[95]
    })
    
    csv_percentiles = percentile_df.to_csv(index=False)
    st.download_button(
        label="Download Percentiles Over Time (CSV)",
        data=csv_percentiles,
        file_name=f"monte_carlo_percentiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
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
        mime="text/csv"
    )
```

#### React Implementation
- ❌ **MISSING**: Export buttons completely absent
- ⚠️ **IMPACT**: Cannot export data for external analysis (Excel, Python notebooks, etc.)

**Implementation Priority**: 🟡 **MEDIUM** - Professional workflow feature

**Implementation Notes**:
- Use browser's Blob API for client-side CSV generation
- Add "Export" button/dropdown to widget header
- Export options: 
  1. Percentiles over time (if fan chart data available)
  2. Final values distribution (from scenarios array)
  3. Summary statistics (all metrics in one CSV)

---

## Summary Table

| Feature | Streamlit | React | Priority | Effort |
|---------|-----------|-------|----------|--------|
| **Portfolio Selection** | ✅ Full instrument picker + weight methods | ❌ Missing | 🔴 HIGH | Large |
| **Weight Allocation UI** | ✅ 5 methods + custom inputs | ❌ Missing | 🔴 HIGH | Large |
| **Portfolio Statistics Expander** | ✅ 4 historical metrics | ⚠️ Partial | 🟡 MEDIUM | Small |
| **Years Input (1-30)** | ✅ Slider | ❌ Days dropdown | 🔴 HIGH | Small |
| **Initial Value Input** | ✅ Number input | ❌ API default | 🔴 HIGH | Small |
| **Sim Range (100-10K)** | ✅ Slider | ⚠️ Dropdown | 🟢 LOW | Small |
| **Rebalancing Analysis** | ✅ Full feature | ❌ Missing | 🟡 MEDIUM | Large |
| **Run Simulation Button** | ✅ User control | ⚠️ Auto-fetch | 🟡 MEDIUM | Medium |
| **CAGR Metrics** | ✅ Median, 10th, 90th | ❌ Missing | 🔴 HIGH | Small |
| **CVaR Metric** | ✅ Displayed | ❌ Missing | 🔴 HIGH | Small |
| **Max Drawdown Metric** | ✅ Displayed | ❌ Missing | 🔴 HIGH | Small |
| **Fan Chart** | ✅ Plotly with bands | ❌ Missing | 🔴 HIGH | Large |
| **Histogram with Percentile Lines** | ✅ Plotly chart | ⚠️ Simple bars | 🟡 MEDIUM | Medium |
| **Percentile Table (7 rows)** | ✅ With interpretations | ⚠️ 3 cards | 🟡 MEDIUM | Small |
| **Rebalancing Recommendations** | ✅ Calendar + timeline + actions | ❌ Missing | 🟡 MEDIUM | Large |
| **Export CSV** | ✅ 2 download buttons | ❌ Missing | 🟡 MEDIUM | Small |

---

## Implementation Roadmap

### Phase 1: Critical Metrics & Controls (Sprint 1)
**Goal**: Restore core simulation flexibility and professional metrics

1. **Add Years Input** (1-30 years slider or number input)
   - Replace days dropdown with years-focused UI
   - Update API call to convert years → days
   - **Effort**: 1 hour

2. **Add Initial Value Input** ($1K - $10M)
   - Number input with step=$10K
   - Update API params
   - **Effort**: 1 hour

3. **Add CAGR Deltas to Metric Cards**
   - Update API response to include CAGR for 10th, 50th, 90th percentiles
   - Display in MetricCard `subtitle` prop
   - **Effort**: 2 hours

4. **Add CVaR and Max Drawdown Metrics**
   - Add to "Risk Metrics" section
   - Ensure API returns these values
   - **Effort**: 1 hour

**Total**: ~5 hours

---

### Phase 2: Fan Chart Visualization (Sprint 2)
**Goal**: Add time-series percentile band chart

1. **Update API Response**
   - Return `percentiles_over_time` object with time points and percentile arrays
   - **Effort**: 2 hours (backend)

2. **Build Fan Chart Component**
   - Use Recharts `<AreaChart>` with layered `<Area>` components
   - Add percentile bands: 10-90, 25-75, 40-60 with decreasing opacity
   - Add median line (bold)
   - Add initial value reference line (dashed)
   - **Effort**: 4 hours

3. **Integrate into Widget**
   - Place above histogram
   - Add toggle to switch between fan chart and histogram views
   - **Effort**: 1 hour

**Total**: ~7 hours

---

### Phase 3: Portfolio Selection UI (Sprint 3)
**Goal**: Allow custom portfolio composition

1. **Build Instrument Multi-Select**
   - Dropdown/combobox with search
   - Show portfolio holdings first
   - **Effort**: 3 hours

2. **Build Weight Allocation UI**
   - Dropdown for method: Equal Weights, Max Sharpe, Min Volatility, Current Portfolio, Custom
   - Conditional custom weight inputs (sliders or number inputs)
   - Weight visualization (bar chart or table)
   - **Effort**: 6 hours

3. **Update API Integration**
   - Pass `selected_symbols` and `weights` array to API
   - Handle portfolio composition in backend
   - **Effort**: 3 hours

**Total**: ~12 hours

---

### Phase 4: Rebalancing Analysis (Sprint 4)
**Goal**: Add optimal rebalancing prediction feature

1. **Backend Calculation**
   - Implement `_analyze_rebalancing_timing` in Python
   - Return `RebalancingRecommendation` object
   - **Effort**: 4 hours (backend)

2. **Rebalancing Metrics Section**
   - Display recommended rebalance count, avg time between, drift, Sharpe improvement
   - **Effort**: 2 hours

3. **Rebalancing Calendar Table**
   - Table with dates, max drift, instruments affected
   - Expandable per-instrument details
   - **Effort**: 3 hours

4. **Drift Timeline Chart**
   - Line chart with diamond markers for rebalance events
   - Horizontal line for drift threshold
   - **Effort**: 2 hours

**Total**: ~11 hours

---

### Phase 5: Polish & Enhancements (Sprint 5)
**Goal**: Complete feature parity and UX improvements

1. **Percentile Table**
   - Expand to 7 rows (5, 10, 25, 50, 75, 90, 95)
   - Add interpretation column
   - **Effort**: 2 hours

2. **Export Functionality**
   - CSV export for percentiles over time
   - CSV export for final values distribution
   - **Effort**: 2 hours

3. **Run Simulation Button**
   - Add explicit button (optional - discuss UX trade-offs)
   - **Effort**: 2 hours

4. **Historical Statistics Expander**
   - Add collapsible section for portfolio stats
   - **Effort**: 1 hour

**Total**: ~7 hours

---

## Total Implementation Effort

- **Phase 1** (Critical): 5 hours
- **Phase 2** (Fan Chart): 7 hours
- **Phase 3** (Portfolio Selection): 12 hours
- **Phase 4** (Rebalancing): 11 hours
- **Phase 5** (Polish): 7 hours

**Grand Total**: ~42 hours (~5-6 days of focused development)

---

## API Schema Changes Required

### Current Response (Inferred)
```typescript
interface MonteCarloData {
  scenarios: { final_value: number }[];
  percentiles: { "10": number; "50": number; "90": number; /* ... */ };
  statistics: {
    mean_final_value: number;
    mean_return_percent: number;
    probability_of_loss: number;
    cagr_median: number;
    cagr_10th: number;
    cagr_90th: number;
    historical_sharpe: number;
    historical_volatility: number;
    max_drawdown_median: number;
  };
  var_95: number;
  var_99: number;
  simulation_params: {
    num_simulations: number;
    time_horizon_years: number;
    initial_value: number;
  };
}
```

### Required Additions
```typescript
interface MonteCarloData {
  // ... existing fields ...
  
  // For fan chart
  percentiles_over_time: {
    time_points: number[];  // Years from start (e.g., [0, 0.25, 0.5, ...])
    percentiles: {
      5: number[];
      10: number[];
      25: number[];
      40: number[];
      50: number[];
      60: number[];
      75: number[];
      90: number[];
      95: number[];
    };
  };
  
  // For enhanced metrics
  statistics: {
    // ... existing fields ...
    cvar_95: number;  // Conditional VaR (Expected Shortfall)
  };
  
  // For rebalancing analysis (conditional)
  rebalancing_rec?: {
    rebalance_dates: string[];  // ISO date strings
    drift_at_rebalance: number[];
    trigger_threshold: number;
    avg_drift: number;
    cost_benefit_ratio: number;
    sharpe_improvement: number;
    description: string;
    instruments_to_rebalance: {
      date: string;
      symbol: string;
      current_weight: number;
      target_weight: number;
      drift: number;
      action: string;
    }[];
    symbols: string[];
  };
  
  // For portfolio historical stats
  historical_stats?: {
    annualized_return: number;
    annualized_volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
  };
}
```

---

## Notes

- **Streamlit Widget Path**: `/src/widgets/monte_carlo_widget.py`
- **React Widget Path**: `/frontend/v1/src/app/dashboard/widgets/MonteCarloWidget.tsx`
- **API Endpoint**: `/api/widgets/portfolio/monte-carlo`
- **Backend Adapter**: `/src/api/widgets/monte_carlo.py`

This document serves as the specification for closing the feature gap between the original Streamlit design and the current React implementation.
