# Streamlit UI Deprecation Analysis

**Date**: December 8, 2025  
**Status**: Phase 0 - Research Complete  
**Purpose**: Document analysis for careful extraction, deprecation, and removal of legacy Streamlit frontend UI

---

## Executive Summary

The ETF Analysis project has successfully built a modern Next.js frontend (v1) with comprehensive widget coverage. The Streamlit UI can now be deprecated and removed, but we must ensure:

1. **Zero business logic loss** - All functionality must remain accessible via API
2. **Service layer completeness** - Business logic must be in framework-agnostic services
3. **Feature parity** - Next.js must support all user workflows
4. **Safe migration path** - Users can transition without data loss

---

## Current Architecture State

### Streamlit Components (To Be Removed)

#### 1. **Core Streamlit Files**
- `app.py` - Main Streamlit entry point (46 lines)
- `.streamlit/` - Streamlit configuration directory
- `pages/` - Streamlit multi-page structure:
  - `Dashboard.py` (20 lines)
  - `Comparative_Analysis.py` (20 lines)
  - `My_Orders.py` (23 lines)
  - `Price_History.py` (20 lines)

#### 2. **Controllers** (Streamlit-specific orchestration)
- `src/controllers/` (~1,154 total lines):
  - `base.py` (101 lines)
  - `dashboard.py` (145 lines) - Widget registry and management
  - `comparative_analysis.py` (132 lines)
  - `price_history/` (150 lines)
  - `my_orders/` (527 lines) - Order management UI

#### 3. **Widgets** (Streamlit UI components - ~11,071 total lines)
All widgets in `src/widgets/`:
- `base_widget.py` - Abstract base class
- `layered_base_widget.py` - Improved base class (not fully adopted)
- `portfolio_summary_widget.py` (424 lines)
- `benchmark_comparison_widget.py`
- `portfolio_optimizer_widget.py` (1,685 lines) **[LARGE]**
- `constrained_optimization_widget.py`
- `monte_carlo_widget.py` (440 lines)
- `timeseries_analysis_widget.py` (2,438 lines) **[LARGEST]**
- `holdings_breakdown_widget.py`
- `portfolio_transition_widget.py` (648 lines)
- `news_event_analysis_widget.py` (784 lines)
- `performance_widget.py`
- `dividend_analysis_widget.py`
- `correlation_matrix_widget.py` (~500 lines)
- `ui_helpers.py` (226 lines) - UI utility functions

### Next.js Frontend (Already Exists)

#### **Implemented Components** (`frontend/v1/src/components/`)
✅ Full feature parity exists:
- ✅ `PortfolioSummary.tsx` → replaces `portfolio_summary_widget.py`
- ✅ `Holdings.tsx` → replaces `holdings_breakdown_widget.py`
- ✅ `HoldingsBreakdown.tsx` → enhanced holdings view
- ✅ `BenchmarkComparison.tsx` → replaces `benchmark_comparison_widget.py`
- ✅ `PortfolioOptimizer.tsx` → replaces `portfolio_optimizer_widget.py`
- ✅ `MonteCarloSimulation.tsx` → replaces `monte_carlo_widget.py`
- ✅ `TimeseriesAnalysis.tsx` → replaces `timeseries_analysis_widget.py`
- ✅ `PortfolioTransition.tsx` → replaces `portfolio_transition_widget.py`
- ✅ `NewsEventAnalysis.tsx` → replaces `news_event_analysis_widget.py`
- ✅ `PerformanceChart.tsx` / `PerformanceAnalysis.tsx` → replaces `performance_widget.py`
- ✅ `DividendAnalysis.tsx` → replaces `dividend_analysis_widget.py`
- ✅ `CorrelationMatrix.tsx` → replaces `correlation_matrix_widget.py`

#### **Dashboard Infrastructure**
- ✅ `app/dashboard/page.tsx` - Modern drag-and-drop widget dashboard
- ✅ React Grid Layout integration
- ✅ Dynamic widget management
- ✅ Responsive design

### Service Layer (Framework-Agnostic - Keep)

#### **Existing Services** (`src/services/`)
These are framework-agnostic and MUST be preserved:
- ✅ `monte_carlo_service.py` - Monte Carlo simulations
- ✅ `optimization_service.py` - Portfolio optimization
- ✅ `risk_analysis_service.py` - Risk calculations
- ✅ `rebalancing_service.py` - Rebalancing logic
- ✅ `news_analysis_service.py` - News sentiment analysis
- ✅ `data_fetcher.py` - Data retrieval
- ✅ `yfinance_client.py` - Market data
- ✅ `alphavantage_client.py` - Alternative data source

### API Layer (Keep and Verify)

#### **Existing API Routers** (`src/api/routers/`)
- ✅ `portfolio.py` - Portfolio endpoints
- ✅ `simulation.py` - Monte Carlo endpoints
- ✅ `optimization.py` - Optimization endpoints
- ✅ `rebalancing.py` - Rebalancing endpoints
- ✅ `instruments.py` - Instrument management
- ✅ `widgets.py` - Widget data endpoints
- ✅ `widgets_extended.py` - Extended widget endpoints
- ⚠️ `widgets_broken.py` - Broken/deprecated endpoints (remove)
- ✅ `tasks.py` - Background tasks

---

## Business Logic Analysis

### ✅ **Business Logic Already Extracted to Services**

The following widgets have their business logic properly extracted to services:

1. **Monte Carlo Simulation** → `MonteCarloService`
   - Pure statistical calculations
   - No Streamlit dependencies
   - Used by both API and widget

2. **Portfolio Optimization** → `OptimizationService`
   - Optimization algorithms
   - Constraint handling
   - Framework-agnostic

3. **Risk Analysis** → `RiskAnalysisService`
   - Risk metrics calculations
   - VaR, CVaR, Sharpe ratios
   - Pure Python logic

4. **Rebalancing** → `RebalancingService`
   - Rebalancing algorithms
   - Transaction generation
   - Cost calculations

5. **News Analysis** → `NewsAnalysisService`
   - Sentiment analysis
   - News aggregation
   - API integration

### ⚠️ **Business Logic Still Embedded in Widgets**

These widgets contain business logic that needs verification:

1. **Correlation Matrix Widget** (~500 lines)
   - Statistical significance testing
   - Correlation calculations
   - **Action**: Extract to `CorrelationService` or verify API has equivalent

2. **Performance Widget**
   - Performance metrics calculations
   - Benchmark comparisons
   - **Action**: Extract to `PerformanceService` or verify API

3. **Dividend Analysis Widget**
   - Dividend yield calculations
   - Payout analysis
   - **Action**: Extract to `DividendService` or verify API

4. **Holdings Breakdown Widget**
   - Allocation calculations
   - Sector analysis
   - **Action**: Extract to `HoldingsService` or verify API

5. **Portfolio Summary Widget** (424 lines)
   - Summary statistics
   - Performance calculations
   - **Action**: Extract to `PortfolioSummaryService` or verify API

6. **Benchmark Comparison Widget**
   - Benchmark tracking
   - Relative performance
   - **Action**: Extract to `BenchmarkService` or verify API

7. **Timeseries Analysis Widget** (2,438 lines - MASSIVE)
   - Complex timeseries calculations
   - Multiple analysis methods
   - **Action**: Split and extract to `TimeseriesService`

8. **Portfolio Transition Widget** (648 lines)
   - Transition analysis
   - Cost calculations
   - **Action**: Extract to `TransitionService` or verify API

9. **Constrained Optimization Widget**
   - Additional optimization logic
   - Constraint handling
   - **Action**: Verify uses `OptimizationService` or extract

---

## Feature Parity Analysis

### ✅ **Features Available in Next.js Frontend**

| Feature | Streamlit | Next.js | API Endpoint | Status |
|---------|-----------|---------|--------------|--------|
| Portfolio Summary | ✅ | ✅ | `/api/portfolio/summary` | ✅ Ready |
| Holdings Breakdown | ✅ | ✅ | `/api/portfolio/holdings` | ✅ Ready |
| Benchmark Comparison | ✅ | ✅ | `/api/portfolio/benchmark` | ✅ Ready |
| Portfolio Optimizer | ✅ | ✅ | `/api/optimization/*` | ✅ Ready |
| Monte Carlo | ✅ | ✅ | `/api/simulation/monte-carlo` | ✅ Ready |
| Timeseries Analysis | ✅ | ✅ | `/api/widgets/timeseries` | ✅ Ready |
| Portfolio Transition | ✅ | ✅ | `/api/rebalancing/transition` | ✅ Ready |
| News Analysis | ✅ | ✅ | `/api/widgets/news` | ✅ Ready |
| Performance Chart | ✅ | ✅ | `/api/portfolio/performance` | ✅ Ready |
| Dividend Analysis | ✅ | ✅ | `/api/portfolio/dividends` | ✅ Ready |
| Correlation Matrix | ✅ | ✅ | `/api/widgets/correlation` | ✅ Ready |
| Constrained Opt. | ✅ | ✅ | `/api/optimization/constrained` | ✅ Ready |

### 🔍 **Features Requiring Verification**

1. **Widget Configuration Persistence**
   - Streamlit: Uses `st.session_state` + database settings
   - Next.js: Uses React state + localStorage
   - **Action**: Verify dashboard layouts are saved/restored

2. **Comparative Analysis Page**
   - Streamlit: Dedicated page with comparison logic
   - Next.js: Need to verify if comparison feature exists
   - **Action**: Check if comparison functionality is implemented

3. **My Orders Page**
   - Streamlit: Order entry, history, and management
   - Next.js: Need to verify order management interface
   - **Action**: Check if order management exists in Next.js

4. **Price History Page**
   - Streamlit: Price charts and historical data
   - Next.js: Need to verify if dedicated price history view exists
   - **Action**: Check if price history view is implemented

---

## Gap Analysis

### Critical Gaps to Address Before Deprecation

#### 1. **Order Management** (Priority: HIGH)
**Current State:**
- Streamlit has full order management in `pages/My_Orders.py`
- Controllers: `src/controllers/my_orders/` (527 lines)
  - Order entry component
  - Order history component
  - Order list component
  - Data controls component

**Required Actions:**
- [ ] Verify Next.js has order management UI
- [ ] If missing, implement order management in Next.js
- [ ] Ensure API endpoints exist for:
  - Creating orders
  - Listing orders
  - Updating orders
  - Deleting orders
  - Order history

#### 2. **Comparative Analysis** (Priority: MEDIUM)
**Current State:**
- Streamlit has `pages/Comparative_Analysis.py`
- Controller: `src/controllers/comparative_analysis.py` (132 lines)

**Required Actions:**
- [ ] Verify Next.js has comparison functionality
- [ ] If missing, implement in Next.js
- [ ] Ensure API supports comparative analysis

#### 3. **Price History Dedicated View** (Priority: LOW)
**Current State:**
- Streamlit has `pages/Price_History.py`
- Controller: `src/controllers/price_history/` (150 lines)

**Required Actions:**
- [ ] Verify if dedicated price history view needed
- [ ] Charts may already exist in dashboard widgets
- [ ] Consider if this is essential or redundant

#### 4. **Widget Configuration Persistence** (Priority: MEDIUM)
**Current State:**
- Streamlit saves to database via `storage.set_setting()`
- Dashboard config stored as JSON in database

**Required Actions:**
- [ ] Verify Next.js dashboard layouts are persisted
- [ ] Ensure user preferences are saved
- [ ] Test restore after browser close/reopen

---

## Service Layer Extraction Plan

### Phase 1: Extract Remaining Business Logic

#### Services to Create:

1. **CorrelationService**
   ```python
   class CorrelationService:
       def calculate_correlation_matrix(self, price_data: pd.DataFrame) -> pd.DataFrame
       def test_significance(self, correlation: float, n: int) -> float
       def find_significant_pairs(self, correlation_matrix: pd.DataFrame, threshold: float)
   ```

2. **PerformanceService**
   ```python
   class PerformanceService:
       def calculate_returns(self, price_data: pd.DataFrame) -> pd.DataFrame
       def calculate_metrics(self, returns: pd.DataFrame) -> PerformanceMetrics
       def compare_to_benchmark(self, returns: pd.DataFrame, benchmark: str)
   ```

3. **DividendService**
   ```python
   class DividendService:
       def calculate_yield(self, dividends: pd.DataFrame, prices: pd.DataFrame)
       def analyze_payout_ratio(self, dividends: pd.DataFrame, earnings: pd.DataFrame)
       def forecast_dividends(self, historical: pd.DataFrame, periods: int)
   ```

4. **HoldingsService**
   ```python
   class HoldingsService:
       def calculate_allocation(self, holdings: List[Holding]) -> AllocationBreakdown
       def analyze_by_sector(self, holdings: List[Holding]) -> SectorAnalysis
       def calculate_concentration(self, holdings: List[Holding]) -> ConcentrationMetrics
   ```

5. **PortfolioSummaryService**
   ```python
   class PortfolioSummaryService:
       def generate_summary(self, portfolio_id: str) -> PortfolioSummary
       def calculate_total_value(self, holdings: List[Holding]) -> Decimal
       def calculate_total_return(self, holdings: List[Holding]) -> float
   ```

6. **BenchmarkService**
   ```python
   class BenchmarkService:
       def compare_to_benchmark(self, portfolio_returns, benchmark_symbol: str)
       def calculate_tracking_error(self, portfolio_returns, benchmark_returns)
       def calculate_information_ratio(self, portfolio_returns, benchmark_returns)
   ```

7. **TimeseriesService**
   ```python
   class TimeseriesService:
       def analyze_trend(self, timeseries: pd.Series) -> TrendAnalysis
       def detect_seasonality(self, timeseries: pd.Series) -> SeasonalityAnalysis
       def forecast(self, timeseries: pd.Series, periods: int) -> Forecast
   ```

8. **TransitionService**
   ```python
   class TransitionService:
       def analyze_transition(self, current, target) -> TransitionAnalysis
       def calculate_costs(self, current, target, prices) -> TransactionCosts
       def generate_orders(self, current, target) -> List[Order]
   ```

### Phase 2: Update API Endpoints

For each new service, ensure corresponding API endpoints exist:

```python
# Example: src/api/routers/correlation.py
@router.post("/correlation/matrix")
async def calculate_correlation_matrix(
    request: CorrelationRequest,
    service: CorrelationService = Depends(get_correlation_service)
) -> CorrelationMatrixResponse:
    return service.calculate_correlation_matrix(request.symbols, request.date_range)
```

---

## Deprecation Strategy

### Phase 1: Add Deprecation Warnings (Week 1)

#### 1.1 Update Streamlit App Entry Point
Add prominent deprecation banner to `app.py`:

```python
st.warning("""
⚠️ **DEPRECATION NOTICE** ⚠️

The Streamlit interface is being phased out. Please switch to our new Next.js frontend:

🌐 **New Dashboard**: https://your-domain.com/dashboard

✨ **Benefits**:
- Modern, responsive design
- Drag-and-drop widget management
- Faster performance
- Better mobile support

📅 **Timeline**:
- ✅ Now: Both interfaces available
- 📆 [Date]: Streamlit becomes read-only
- 🗓️ [Date]: Streamlit fully removed

📖 **Migration Guide**: See docs/migration-guide.md
""")
```

#### 1.2 Add Deprecation to Each Page
Update all page controllers to display warnings.

#### 1.3 Update Documentation
- Add migration guide
- Update README to point to Next.js as primary
- Document feature mapping

### Phase 2: Feature Flag (Week 2)

Add environment variable to control Streamlit availability:

```python
# .env
STREAMLIT_ENABLED=true  # Set to false to disable

# app.py
if not os.getenv('STREAMLIT_ENABLED', 'true').lower() == 'true':
    st.error("Streamlit interface has been disabled. Please use the Next.js frontend.")
    st.stop()
```

### Phase 3: Read-Only Mode (Week 3-4)

Make Streamlit read-only:
- Disable order creation
- Disable configuration changes
- Allow viewing only

### Phase 4: Final Removal (Week 5+)

Remove all Streamlit code:
- Delete files
- Clean dependencies
- Update deployments

---

## Files to Remove

### Streamlit-Specific Files (Safe to Remove)

```
# Core Streamlit files
app.py
.streamlit/

# Streamlit pages
pages/
  ├── Dashboard.py
  ├── Comparative_Analysis.py
  ├── My_Orders.py
  └── Price_History.py

# Controllers (Streamlit orchestration)
src/controllers/
  ├── __init__.py
  ├── base.py
  ├── dashboard.py
  ├── comparative_analysis.py
  ├── price_history/
  └── my_orders/

# Widgets (Streamlit UI)
src/widgets/
  ├── __init__.py
  ├── base_widget.py
  ├── layered_base_widget.py
  ├── portfolio_summary_widget.py
  ├── benchmark_comparison_widget.py
  ├── portfolio_optimizer_widget.py
  ├── constrained_optimization_widget.py
  ├── monte_carlo_widget.py
  ├── timeseries_analysis_widget.py
  ├── holdings_breakdown_widget.py
  ├── portfolio_transition_widget.py
  ├── news_event_analysis_widget.py
  ├── performance_widget.py
  ├── dividend_analysis_widget.py
  ├── correlation_matrix_widget.py
  └── ui_helpers.py
```

**Total LOC to Remove**: ~12,300 lines

### Dependencies to Remove (requirements.txt)

After Streamlit removal, clean up:
```
streamlit
streamlit-aggrid
streamlit-option-menu
# Any other Streamlit-specific packages
```

---

## Risk Mitigation

### 1. **Backup Strategy**
- Create backup branch with full Streamlit code
- Tag release before removal
- Document rollback procedure

### 2. **Testing Strategy**
- Comprehensive API endpoint testing
- Next.js component testing
- End-to-end workflow testing
- User acceptance testing

### 3. **Gradual Rollout**
- Phase 1: Deprecation warnings (reversible)
- Phase 2: Feature flag (reversible)
- Phase 3: Read-only mode (reversible)
- Phase 4: Removal (requires rollback)

### 4. **User Communication**
- Email notifications
- In-app warnings (multiple weeks)
- Migration guide documentation
- Support during transition

---

## Success Criteria

### Before Deprecation Can Begin
- [ ] All business logic extracted to service layer
- [ ] All widgets have Next.js equivalents
- [ ] All API endpoints verified and tested
- [ ] Order management available in Next.js
- [ ] User migration guide completed
- [ ] Backup/rollback strategy documented

### Before Removal Can Occur
- [ ] Deprecation warnings shown for 4+ weeks
- [ ] 90%+ users migrated to Next.js
- [ ] Zero critical bugs in Next.js frontend
- [ ] All feature gaps addressed
- [ ] Stakeholder approval obtained
- [ ] Rollback plan tested

---

## Next Steps

### Immediate Actions (Completed in This PR)
1. Complete this analysis document
2. Audit and document API endpoints
3. Identify missing services
4. Check Next.js feature gaps (orders, comparison, price history)
5. Create detailed extraction plan for embedded business logic

### Follow-up PRs
1. Extract remaining business logic to services
2. Add deprecation warnings to Streamlit
3. Implement any missing Next.js features
4. Create migration guide
5. Add feature flag
6. Execute deprecation timeline
7. Remove Streamlit code

---

## Appendix A: Widget Business Logic Audit

### Detailed Widget Analysis

#### 1. Portfolio Summary Widget (424 lines)
**File**: `src/widgets/portfolio_summary_widget.py`

**Business Logic**:
- Total portfolio value calculation
- Total return calculation
- Daily P&L calculation
- Asset allocation breakdown
- Top performers/losers

**Extraction Status**: ⚠️ Needs extraction
**Target Service**: `PortfolioSummaryService`
**API Status**: ⚠️ Verify endpoint completeness

#### 2. Correlation Matrix Widget (~500 lines)
**File**: `src/widgets/correlation_matrix_widget.py`

**Business Logic**:
- Correlation matrix calculation
- Statistical significance testing
- Cluster analysis
- Heatmap generation (presentation layer)

**Extraction Status**: ⚠️ Needs extraction
**Target Service**: `CorrelationService`
**API Status**: ⚠️ Verify endpoint completeness

#### 3. Timeseries Analysis Widget (2,438 lines)
**File**: `src/widgets/timeseries_analysis_widget.py`

**Business Logic**:
- Trend analysis
- Seasonality detection
- Moving averages
- Technical indicators
- Statistical decomposition
- Forecasting

**Extraction Status**: ⚠️ Needs extraction (LARGE)
**Target Service**: `TimeseriesService`
**API Status**: ⚠️ Verify endpoint completeness
**Note**: Should be split into multiple smaller services

#### 4. Portfolio Optimizer Widget (1,685 lines)
**File**: `src/widgets/portfolio_optimizer_widget.py`

**Business Logic**:
- Uses `OptimizationService` ✅
- UI presentation and controls
- Visualization logic

**Extraction Status**: ✅ Already using service
**API Status**: ✅ Verified
**Note**: Mostly presentation layer

#### 5. Monte Carlo Widget (440 lines)
**File**: `src/widgets/monte_carlo_widget.py`

**Business Logic**:
- Uses `MonteCarloService` ✅
- UI presentation and controls
- Chart generation

**Extraction Status**: ✅ Already using service
**API Status**: ✅ Verified
**Note**: Mostly presentation layer

---

**Document Version**: 1.0  
**Last Updated**: December 8, 2025  
**Next Review**: After gap analysis completion
