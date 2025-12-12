# Widget Functionality Gap Analysis

**Date**: December 10, 2025  
**Purpose**: Identify missing functionality between backend widget API adapters and frontend implementations

---

## Executive Summary

This analysis compares 12 widget pairs to identify:
1. Backend parameters/options not exposed in frontend
2. Data fields returned by backend but not displayed
3. Missing interactive features
4. Additional metrics available but not visualized

### Overall Findings
- **Critical gaps**: 7 widgets have significant missing functionality
- **Moderate gaps**: 4 widgets have some missing features
- **Minor gaps**: 1 widget is nearly complete

---

## 1. Benchmark Comparison Widget

### Backend Support (`benchmark_comparison.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `time_period` (string: '1W', '1M', '3M', '6M', '1Y', '2Y', '5Y') → maps to days
- `benchmark` (string: SPY, QQQ, DIA, IWM, VTI, EFA, AGG, GLD)

**Returns:**
```python
{
    "portfolio_return": float,
    "benchmark_return": float,
    "alpha": float,
    "beta": float,  # ⚠️ NOT DISPLAYED
    "sharpe_ratio": float,
    "benchmark_sharpe": float,  # ⚠️ NOT DISPLAYED
    "information_ratio": float,  # ⚠️ NOT DISPLAYED
    "portfolio_volatility": float,  # ⚠️ NOT DISPLAYED
    "benchmark_volatility": float,  # ⚠️ NOT DISPLAYED
    "benchmark_symbol": string,
    "period_days": int
}
```

### Frontend Implementation (`BenchmarkComparisonWidget.tsx`)
**Currently Displays:**
- Portfolio Return
- Benchmark Return
- Alpha
- Sharpe Ratio

### Missing Functionality
❌ **Not Displayed:**
1. **Beta** - Market sensitivity metric (critical for risk assessment)
2. **Benchmark Sharpe Ratio** - Comparison baseline
3. **Information Ratio** - Risk-adjusted active return
4. **Portfolio Volatility** - Portfolio risk measure
5. **Benchmark Volatility** - Benchmark risk measure

❌ **Missing Features:**
- No comparison chart/visualization
- No relative performance display (outperformance/underperformance)
- No tracking error calculation display

**Priority**: HIGH - Beta and volatility metrics are essential for risk analysis

---

## 2. Portfolio Summary Widget

### Backend Support (`portfolio_summary.py`)
**Parameters:**
- `portfolio_id` (optional string)

**Returns:**
```python
{
    "total_value": float,
    "total_return": float,
    "total_return_percent": float,  # ⚠️ NOT DISPLAYED
    "day_change": float,  # ⚠️ NOT DISPLAYED
    "day_change_percent": float,  # ⚠️ NOT DISPLAYED
    "positions": int,
    "allocated_cash": float,
    "last_updated": datetime
}
```

### Frontend Implementation (`PortfolioSummaryWidget.tsx`)
**Currently Displays:**
- Total Value
- Total Return (dollar amount)
- Positions count
- Cash (allocated_cash)

### Missing Functionality
❌ **Not Displayed:**
1. **Total Return Percent** - Percentage gain/loss
2. **Day Change** - Daily $ change
3. **Day Change Percent** - Daily % change
4. **Last Updated** - Data freshness indicator

❌ **Missing Features:**
- No color coding for positive/negative total_return (present for total_return but missing for day_change)
- No sparkline or mini trend indicator
- No comparison to previous period

**Priority**: MEDIUM - Day change metrics would significantly improve user experience

---

## 3. Correlation Matrix Widget

### Backend Support (`correlation_matrix.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `time_window_days` (int, default: 252)
- `additional_symbols` (list, default: ['SPY', 'QQQ'])  # ⚠️ NOT CONFIGURABLE
- `include_holdings` (bool, default: True)  # ⚠️ NOT CONFIGURABLE

**Returns:**
```python
{
    "symbols": list,
    "correlation_matrix": list[dict],  # symbol1, symbol2, correlation
    "correlation_pairs": list[dict],  # ⚠️ NOT DISPLAYED
    "benchmark_comparison": list[dict],  # ⚠️ NOT DISPLAYED
    "statistics": {
        "avg_correlation": float,
        "max_correlation": float,
        "min_correlation": float,  # ⚠️ NOT DISPLAYED
        "num_days": int  # ⚠️ NOT DISPLAYED
    },
    "analysis_period": {
        "start_date": string,
        "end_date": string,
        "days_analyzed": int
    }
}
```

### Frontend Implementation (`CorrelationMatrixWidget.tsx`)
**Currently Displays:**
- Correlation heatmap (visual grid)
- Average correlation
- Highest correlation
- Time period (days_analyzed)
- Dynamic insights based on correlation levels

### Missing Functionality
❌ **Not Configurable:**
1. **Additional Symbols** - Cannot add custom benchmarks
2. **Include Holdings** - Cannot toggle portfolio holdings on/off

❌ **Not Displayed:**
1. **Correlation Pairs** - Sorted list of highest/lowest correlations
2. **Benchmark Comparison** - Dedicated benchmark correlation table
3. **Min Correlation** - Lowest correlation value
4. **Num Days** - Actual number of days in calculation

❌ **Missing Features:**
- No ability to filter/search specific ticker pairs
- No export functionality
- No drill-down into specific pair relationships
- No time-series correlation evolution

**Priority**: MEDIUM - Additional symbols configuration would be valuable

---

## 4. Monte Carlo Widget

### Backend Support (`monte_carlo.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `num_simulations` (int, min: 100, max: 10000, default: 1000)
- `time_horizon_days` (int, default: 252)
- `confidence_level` (float, 0.8-0.99, default: 0.95)  # ⚠️ NOT CONFIGURABLE
- `initial_value` (float, optional)  # ⚠️ NOT CONFIGURABLE
- `include_dividends` (bool, default: True)  # ⚠️ NOT CONFIGURABLE
- `estimation_method` (string: 'Historical Mean', 'Exponentially Weighted')  # ⚠️ NOT CONFIGURABLE
- `enable_contributions` (bool, default: False)  # ⚠️ NOT CONFIGURABLE
- `contribution_amount` (float, default: 0)  # ⚠️ NOT CONFIGURABLE
- `contribution_frequency` (string: 'Annual')  # ⚠️ NOT CONFIGURABLE

**Returns:**
```python
{
    "scenarios": list[dict],  # final_value, return_percent, max_drawdown
    "statistics": {
        "mean_final_value": float,
        "std_final_value": float,
        "mean_return_percent": float,
        "probability_of_loss": float,
        "cagr_median": float,
        "cagr_10th": float,  # ⚠️ NOT DISPLAYED
        "cagr_90th": float,  # ⚠️ NOT DISPLAYED
        "historical_sharpe": float,
        "historical_volatility": float,  # ⚠️ NOT DISPLAYED
        "max_drawdown_median": float  # ⚠️ NOT DISPLAYED
    },
    "percentiles": {"10": float, "50": float, "90": float},
    "var_95": float,
    "var_99": float,  # ⚠️ NOT DISPLAYED
    "simulation_params": dict
}
```

### Frontend Implementation (`MonteCarloWidget.tsx`)
**Currently Displays:**
- Expected Return (mean_return_percent)
- Value at Risk 95%
- Best Case (90th percentile)
- Histogram of outcomes
- Key statistics

### Missing Functionality
❌ **Not Configurable:**
1. **Confidence Level** - Cannot adjust VaR confidence (95% hardcoded)
2. **Initial Value** - Cannot set custom starting value
3. **Include Dividends** - Cannot toggle dividend inclusion
4. **Estimation Method** - Cannot switch between historical/exponential weighting
5. **Contributions** - Cannot model regular contributions
6. **Contribution Amount** - No contribution planning
7. **Contribution Frequency** - No periodic contribution modeling

❌ **Not Displayed:**
1. **VaR 99%** - More extreme risk measure
2. **CAGR 10th/90th** - Compound growth rate ranges
3. **Historical Volatility** - Input volatility used
4. **Max Drawdown Median** - Typical maximum loss

❌ **Missing Features:**
- No scenario path visualization
- No interactive percentile selection
- No goal-based planning (e.g., "probability of reaching $X")
- No comparison to deterministic projection

**Priority**: HIGH - Contribution modeling and additional risk metrics are valuable

---

## 5. Holdings Breakdown Widget

### Backend Support (`holdings_breakdown.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `breakdown_type` (string: 'sector', 'geography', 'asset_class', 'all')
- `include_percentages` (bool, default: True)

**Returns:**
```python
{
    "holdings": list[dict],  # symbol, name, quantity, current_price, market_value, sector, geography, asset_class, weight
    "total_positions": int,
    "total_value": float,
    "breakdown_by_sector": list[dict],  # name, value, weight, positions
    "breakdown_by_geography": list[dict],  # ⚠️ NOT DISPLAYED
    "breakdown_by_asset_class": list[dict],  # ⚠️ PARTIALLY DISPLAYED
    "concentration_risk_score": float,  # ⚠️ NOT DISPLAYED
    "last_updated": datetime
}
```

### Frontend Implementation (`HoldingsBreakdownWidget.tsx`)
**Currently Displays:**
- Holdings table with symbol, name, shares, price, value, weight
- Day change and total return per holding
- Breakdown selector (sector, geography, asset_class)
- Visual breakdown display

### Missing Functionality
❌ **Not Displayed:**
1. **Breakdown by Geography** - Geographic diversification not shown
2. **Breakdown by Asset Class** - Asset allocation not properly visualized
3. **Concentration Risk Score** - HHI-based risk metric missing
4. **Last Updated** - Data freshness indicator

❌ **Missing Features:**
- No pie chart visualization for breakdowns
- No drill-down from breakdown to holdings
- No comparison to target allocation
- No rebalancing suggestions

**Priority**: MEDIUM - Concentration risk score would be valuable addition

---

## 6. Dividend Analysis Widget

### Backend Support (`dividend_analysis.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `time_period` (string: 'All', '1Y', '2Y', '5Y')
- `symbol` (string or list, optional)  # ⚠️ NOT CONFIGURABLE

**Returns:**
```python
{
    "total_dividends": float,
    "dividend_yield": float,
    "ytd_dividends": float,  # ⚠️ NOT DISPLAYED
    "all_time_dividends": float,  # ⚠️ NOT DISPLAYED
    "top_dividend_holdings": list[dict],  # symbol, amount, yield
    "holdings_analyzed": int
}
```

### Frontend Implementation (`DividendAnalysisWidget.tsx`)
**Currently Displays:**
- Total Dividends
- Dividend Yield
- Top dividend holdings (symbol, yield)

### Missing Functionality
❌ **Not Configurable:**
1. **Symbol Filter** - Cannot filter by specific symbol(s)

❌ **Not Displayed:**
1. **YTD Dividends** - Year-to-date dividend income
2. **All Time Dividends** - Total historical dividends
3. **Dividend Amount** per holding (only yield shown)

❌ **Missing Features:**
- No dividend payment calendar/timeline
- No dividend growth rate
- No projected annual dividend income
- No ex-dividend date tracking
- No dividend reinvestment modeling

**Priority**: MEDIUM - YTD and historical dividend tracking would be useful

---

## 7. Performance Widget

### Backend Support (`performance.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `time_period` (string: '1W', '1M', '3M', '6M', '1Y', '2Y', '5Y')

**Returns:**
```python
{
    "total_return": float,
    "annualized_return": float,
    "volatility": float,
    "sharpe_ratio": float,
    "holdings_analyzed": int,  # ⚠️ NOT DISPLAYED
    "period_days": int  # ⚠️ NOT DISPLAYED
}
```

### Frontend Implementation (`PerformanceWidget.tsx`)
**Currently Displays:**
- Total Return
- Annualized Return
- Volatility
- Sharpe Ratio

### Missing Functionality
❌ **Not Displayed:**
1. **Holdings Analyzed** - Number of positions in calculation
2. **Period Days** - Actual days in period

❌ **Missing Features:**
- No performance chart/visualization
- No comparison to benchmark
- No performance attribution (which holdings contributed most)
- No rolling returns display
- No calendar year returns
- No risk-adjusted metrics (Sortino, Calmar)

**Priority**: LOW - Core metrics are displayed; visualization would enhance

---

## 8. Timeseries Analysis Widget

### Backend Support (`timeseries_analysis.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `time_period` (string: '1W', '1M', '3M', '6M', '1Y', '2Y', '5Y', 'All')
- `analysis_type` (string: 'Portfolio Overview', 'Stationarity', 'Seasonality', 'Trend Analysis', 'Volatility')
- `symbol` (string or list, optional)  # ⚠️ NOT CONFIGURABLE in UI

**Returns:**
```python
{
    "statistics": {
        "total_return": float,
        "volatility": float,
        "sharpe_ratio": float,
        "max_drawdown": float
    },
    "price_data": list[dict],  # date, value (limited to 100 points)
    "holdings_analyzed": int,
    "period_days": int
}
```

### Frontend Implementation (`TimeseriesAnalysisWidget.tsx`)
**Currently Displays:**
- Analysis type selector
- Time period selector
- Statistics (return, volatility, sharpe, max_drawdown)
- Price data point count

### Missing Functionality
❌ **Not Configurable:**
1. **Symbol Filter** - Cannot filter to specific holdings

❌ **Not Displayed:**
1. **Price Data Visualization** - Chart not rendered (data available)
2. **Stationarity Results** - Analysis type selected but not shown
3. **Seasonality Results** - Analysis type selected but not shown
4. **Trend Analysis Results** - Analysis type selected but not shown
5. **Volatility Analysis Results** - Analysis type selected but not shown

❌ **Missing Features:**
- **CRITICAL**: No chart rendering despite having price_data
- No drawdown visualization
- No cumulative return chart
- No comparison period overlay
- No technical indicators

**Priority**: CRITICAL - Chart visualization is completely missing

---

## 9. Portfolio Optimizer Widget

### Backend Support (`portfolio_optimizer.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `mode` (string: 'Efficient Frontier', 'Max Sharpe', 'Min Volatility', 'Max Return', 'Target Return')
- `time_period` (string: '1M', '3M', '6M', '1Y', '2Y', '5Y')
- `target_return` (float, -100 to 1000, optional)  # ⚠️ NOT CONFIGURABLE
- `include_dividends` (bool, default: True)

**Returns:**
```python
{
    "expected_return": float,
    "expected_risk": float,
    "sharpe_ratio": float,
    "improvement_metrics": {
        "return_improvement": float,
        "risk_reduction": float,
        "sharpe_improvement": float
    },
    "current_return": float,  # ⚠️ NOT DISPLAYED
    "current_risk": float,  # ⚠️ NOT DISPLAYED
    "current_sharpe": float,  # ⚠️ NOT DISPLAYED
    "holdings_analyzed": int
}
```

### Frontend Implementation (`PortfolioOptimizerWidget.tsx`)
**Currently Displays:**
- Mode selector
- Time period selector
- Include dividends toggle
- Expected Return, Risk, Sharpe
- Improvement metrics

### Missing Functionality
❌ **Not Configurable:**
1. **Target Return** - Cannot set target return for 'Target Return' mode

❌ **Not Displayed:**
1. **Current Portfolio Metrics** - Current return, risk, sharpe not shown
2. **Suggested Allocation** - New weights not provided/displayed
3. **Trade Instructions** - How to implement optimization

❌ **Missing Features:**
- No efficient frontier visualization
- No current vs. optimized comparison chart
- No allocation changes table (current → optimized)
- No implementation cost estimate
- No constraint configuration (position limits, sector limits)

**Priority**: HIGH - Need allocation changes and current vs. optimized comparison

---

## 10. Constrained Optimization Widget

### Backend Support (`constrained_optimization.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `objective` (string: 'Max Sharpe', 'Min Volatility', 'Max Return', 'Target Return', 'Risk Parity')
- `max_weight` (float, 1-100%, default: 40%)
- `min_weight` (float, 0-50%, default: 0%)
- `target_return` (float, -100 to 1000, optional)  # ⚠️ NOT CONFIGURABLE

**Returns:**
```python
{
    "optimization_result": {
        "return": float,
        "risk": float,
        "sharpe_ratio": float
    },
    "constraint_violations": list[dict],  # constraint, violation, limit
    "constraints_met": bool,
    "holdings_analyzed": int,
    "constraints_applied": list[string]  # ⚠️ NOT DISPLAYED
}
```

### Frontend Implementation (`ConstrainedOptimizationWidget.tsx`)
**Currently Displays:**
- Objective selector
- Max weight slider (10-100%)
- Min weight slider (0-30%)
- Optimization results (return, risk, sharpe)
- Constraint violations display
- Constraints met indicator

### Missing Functionality
❌ **Not Configurable:**
1. **Target Return** - Target return input missing

❌ **Not Displayed:**
1. **Constraints Applied** - List of all applied constraints
2. **Optimized Allocation** - New position weights
3. **Current Allocation** - Comparison baseline

❌ **Missing Features:**
- No sector constraints
- No risk budget allocation
- No transaction cost consideration
- No tax optimization
- No allocation comparison table

**Priority**: MEDIUM - Needs allocation output for implementation

---

## 11. Portfolio Transition Widget

### Backend Support (`portfolio_transition.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `transition_method` (string: 'Immediate', 'Gradual', 'Tax Optimized', 'Cost Minimized')
- `optimization_priority` (string: 'Cost', 'Speed', 'Tax Efficiency', 'Balance')
- `target_weights` (dict, optional)  # ⚠️ NOT CONFIGURABLE

**Returns:**
```python
{
    "required_trades": list[dict],  # symbol, action, shares, value
    "transition_cost": float,
    "expected_impact": {
        "risk_change": float,
        "return_impact": float
    },
    "holdings_analyzed": int
}
```

### Frontend Implementation (`PortfolioTransitionWidget.tsx`)
**Currently Displays:**
- Transition method selector
- Optimization priority selector
- Required trades (first 5)
- Transition cost
- Risk change

### Missing Functionality
❌ **Not Configurable:**
1. **Target Weights** - Cannot specify target portfolio allocation

❌ **Not Displayed:**
1. **Return Impact** - Expected return change
2. **Tax Impact** - Tax liability estimation
3. **Timeline** - Gradual transition schedule
4. **Market Impact** - Slippage estimation

❌ **Missing Features:**
- No target portfolio input interface
- No trade sequencing (for gradual transitions)
- No tax lot optimization
- No implementation timeline visualization
- Cannot compare transition strategies

**Priority**: HIGH - Needs target weights input to be functional

---

## 12. News Event Analysis Widget

### Backend Support (`news_event_analysis.py`)
**Parameters:**
- `portfolio_id` (optional string)
- `lookback_days` (int: 7, 14, 30, 60, 90)
- `surprise_threshold` (float, 1-20, default: 5.0)

**Returns:**
```python
{
    "sentiment_analysis": {
        "overall_sentiment": float,
        "positive_count": int,  # ⚠️ NOT DISPLAYED
        "negative_count": int,  # ⚠️ NOT DISPLAYED
        "neutral_count": int  # ⚠️ NOT DISPLAYED
    },
    "market_impact": {
        "price_correlation": float,
        "volatility_impact": float  # ⚠️ NOT DISPLAYED
    },
    "events": list[dict],  # title, date, sentiment, source
    "holdings_analyzed": int
}
```

### Frontend Implementation (`NewsEventAnalysisWidget.tsx`)
**Currently Displays:**
- Lookback days selector
- Surprise threshold slider
- Overall sentiment
- Price correlation
- Recent events (first 3)

### Missing Functionality
❌ **Not Displayed:**
1. **Positive/Negative/Neutral Counts** - Sentiment distribution
2. **Volatility Impact** - News effect on volatility

❌ **Missing Features:**
- No sentiment breakdown chart
- No event filtering by sentiment
- No symbol-specific news
- No event impact quantification
- No news source quality indicators
- **NOTE**: Backend returns dummy/simulated data (not real news API integration)

**Priority**: LOW - Widget displays core functionality; backend needs real data source

---

## Priority Summary

### Critical Gaps (Implement First)
1. **Timeseries Analysis** - Chart visualization completely missing
2. **Portfolio Transition** - Needs target weights input
3. **Monte Carlo** - Missing contribution modeling
4. **Portfolio Optimizer** - Needs allocation output

### High Priority Gaps
1. **Benchmark Comparison** - Beta, volatility, information ratio
2. **Optimizer** - Current vs. optimized comparison
3. **Constrained Optimization** - Allocation output

### Medium Priority Gaps
1. **Portfolio Summary** - Day change metrics
2. **Correlation Matrix** - Additional symbols configuration
3. **Holdings Breakdown** - Concentration risk score
4. **Dividend Analysis** - YTD and historical tracking

### Low Priority Gaps
1. **Performance** - Visualization enhancements
2. **News Event Analysis** - Sentiment breakdown (data quality issue)

---

## Recommendations

### Immediate Actions
1. **Add chart rendering** to TimeseriesAnalysisWidget using price_data
2. **Add target weights input** to PortfolioTransitionWidget
3. **Expose contribution parameters** in MonteCarloWidget
4. **Display allocation changes** in PortfolioOptimizerWidget

### Short-term Enhancements
1. Add missing metrics to BenchmarkComparisonWidget
2. Implement day change display in PortfolioSummaryWidget
3. Add current portfolio comparison in optimizer widgets
4. Expose additional_symbols in CorrelationMatrixWidget

### Long-term Features
1. Add interactive charts across all widgets
2. Implement goal-based planning in Monte Carlo
3. Add tax optimization features
4. Enhance news analysis with real data sources

---

## Technical Notes

### Common Patterns Observed
1. **Consistent gaps**: Many widgets return data not displayed
2. **Configuration limitations**: Frontend doesn't expose all backend parameters
3. **Visualization gap**: Backend returns data suitable for charts, but many widgets don't render them
4. **Comparison baseline**: Current portfolio metrics often calculated but not displayed

### Implementation Considerations
1. Some missing features require UI/UX design work
2. Chart libraries need to be selected/integrated
3. Form inputs needed for complex parameters (target weights, constraints)
4. Consider progressive disclosure for advanced options

