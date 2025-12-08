# Streamlit UI Deprecation & Removal Plan

**Date**: December 8, 2025  
**Status**: Planning Phase  
**Timeline**: 6-8 weeks  
**Owner**: Development Team

---

## Executive Summary

This document outlines the detailed plan for deprecating and removing the Streamlit frontend UI from the ETF Analysis project. Based on the analysis in `streamlit-deprecation-analysis.md`, we have identified that:

✅ **Ready**: Next.js frontend has feature parity for all core widgets  
⚠️ **Gaps**: Missing order management, comparative analysis, and price history pages  
🔧 **Action Required**: Extract remaining business logic and implement missing features

---

## Timeline Overview

### Week 1-2: Gap Analysis & Business Logic Extraction
- Audit and extract embedded business logic to services
- Verify all API endpoints are complete
- Identify and document all feature gaps

### Week 3-4: Implement Missing Next.js Features
- Implement order management in Next.js
- Implement comparative analysis in Next.js  
- Implement price history view (if needed)
- Add widget configuration persistence

### Week 5: Add Deprecation Warnings
- Add prominent warnings to Streamlit app
- Create migration guide documentation
- Update README and user documentation

### Week 6-7: Feature Flag & Read-Only Mode
- Add feature flag for Streamlit
- Monitor usage analytics
- Make Streamlit read-only
- Communicate timeline to users

### Week 8+: Final Removal
- Archive Streamlit code to backup branch
- Remove Streamlit files from main branch
- Clean up dependencies
- Update deployment configurations

---

## Detailed Action Items

## Phase 1: Business Logic Extraction (Week 1-2)

### 1.1 Extract Services from Large Widgets

#### Priority 1: Timeseries Analysis (2,438 lines)
**File**: `src/widgets/timeseries_analysis_widget.py`

**Services to Extract**:
```python
# src/services/timeseries_service.py
class TimeseriesService:
    """Framework-agnostic timeseries analysis service."""
    
    def analyze_trend(self, data: pd.Series, method: str = 'linear') -> TrendAnalysis:
        """Analyze trend in timeseries data."""
        pass
    
    def detect_seasonality(self, data: pd.Series) -> SeasonalityAnalysis:
        """Detect seasonal patterns."""
        pass
    
    def calculate_moving_averages(self, data: pd.Series, windows: List[int]) -> Dict[str, pd.Series]:
        """Calculate multiple moving averages."""
        pass
    
    def calculate_technical_indicators(self, data: pd.Series) -> TechnicalIndicators:
        """Calculate RSI, MACD, Bollinger Bands, etc."""
        pass
    
    def decompose_timeseries(self, data: pd.Series, model: str = 'additive') -> Decomposition:
        """Perform seasonal decomposition."""
        pass
    
    def forecast(self, data: pd.Series, periods: int, method: str = 'arima') -> Forecast:
        """Generate forecast."""
        pass
```

**API Endpoints to Add**:
```python
# src/api/routers/timeseries.py
@router.post("/timeseries/trend")
async def analyze_trend(request: TrendRequest)

@router.post("/timeseries/seasonality")  
async def detect_seasonality(request: SeasonalityRequest)

@router.post("/timeseries/indicators")
async def calculate_indicators(request: IndicatorsRequest)

@router.post("/timeseries/forecast")
async def generate_forecast(request: ForecastRequest)
```

**Effort Estimate**: 2-3 days

---

#### Priority 2: Portfolio Summary (424 lines)
**File**: `src/widgets/portfolio_summary_widget.py`

**Service to Extract**:
```python
# src/services/portfolio_summary_service.py
class PortfolioSummaryService:
    """Portfolio summary calculations."""
    
    def __init__(self, 
                 instrument_repo: InstrumentRepository,
                 order_repo: OrderRepository,
                 price_repo: PriceDataRepository):
        self.instrument_repo = instrument_repo
        self.order_repo = order_repo
        self.price_repo = price_repo
    
    def generate_summary(self, portfolio_id: Optional[str] = None) -> PortfolioSummary:
        """Generate complete portfolio summary."""
        holdings = self._calculate_holdings()
        metrics = self._calculate_metrics(holdings)
        allocation = self._calculate_allocation(holdings)
        
        return PortfolioSummary(
            total_value=metrics['total_value'],
            total_cost_basis=metrics['total_cost'],
            total_gain_loss=metrics['total_gain'],
            total_gain_loss_pct=metrics['total_gain_pct'],
            holdings=holdings,
            allocation=allocation,
            last_updated=datetime.now()
        )
    
    def _calculate_holdings(self) -> List[Holding]:
        """Calculate current holdings from orders."""
        pass
    
    def _calculate_metrics(self, holdings: List[Holding]) -> Dict:
        """Calculate summary metrics."""
        pass
    
    def _calculate_allocation(self, holdings: List[Holding]) -> AllocationBreakdown:
        """Calculate asset allocation."""
        pass
```

**API Endpoint Status**: ✅ Already exists at `/api/portfolio/summary`  
**Action**: Verify completeness and extract logic from widget

**Effort Estimate**: 1-2 days

---

#### Priority 3: Correlation Matrix (~500 lines)
**File**: `src/widgets/correlation_matrix_widget.py`

**Service to Extract**:
```python
# src/services/correlation_service.py
class CorrelationService:
    """Correlation analysis service."""
    
    def calculate_correlation_matrix(self, 
                                     symbols: List[str],
                                     start_date: date,
                                     end_date: date) -> pd.DataFrame:
        """Calculate correlation matrix for given symbols."""
        price_data = self._fetch_price_data(symbols, start_date, end_date)
        returns = price_data.pct_change().dropna()
        correlation = returns.corr()
        return correlation
    
    def test_significance(self, correlation: float, n: int, alpha: float = 0.05) -> bool:
        """Test if correlation is statistically significant."""
        # t-test for correlation
        t_stat = correlation * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
        return p_value < alpha
    
    def find_significant_pairs(self, 
                              correlation_matrix: pd.DataFrame,
                              threshold: float = 0.7) -> List[CorrelationPair]:
        """Find significantly correlated pairs."""
        pairs = []
        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) >= threshold:
                    pairs.append(CorrelationPair(
                        symbol1=correlation_matrix.index[i],
                        symbol2=correlation_matrix.columns[j],
                        correlation=corr,
                        is_significant=self.test_significance(corr, len(correlation_matrix))
                    ))
        return pairs
    
    def cluster_by_correlation(self, 
                              correlation_matrix: pd.DataFrame,
                              n_clusters: int = 3) -> Dict[int, List[str]]:
        """Cluster symbols by correlation patterns."""
        from sklearn.cluster import AgglomerativeClustering
        
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            affinity='precomputed',
            linkage='average'
        )
        
        # Convert correlation to distance
        distance_matrix = 1 - correlation_matrix
        labels = clustering.fit_predict(distance_matrix)
        
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(correlation_matrix.index[i])
        
        return clusters
```

**API Endpoint**: ⚠️ Exists at `/api/widgets/portfolio/correlation` - verify completeness

**Effort Estimate**: 1-2 days

---

#### Priority 4: Other Widget Services

1. **HoldingsService** (from `holdings_breakdown_widget.py`)
   - Calculate allocation by asset type, sector, currency
   - Calculate concentration metrics (HHI, top N %)
   - Generate rebalancing suggestions

2. **PerformanceService** (from `performance_widget.py`)
   - Calculate returns over various periods
   - Calculate risk-adjusted metrics (Sharpe, Sortino)
   - Calculate drawdowns (max, current)

3. **DividendService** (from `dividend_analysis_widget.py`)
   - Calculate dividend yield
   - Analyze payout ratios
   - Forecast future dividends

4. **BenchmarkService** (from `benchmark_comparison_widget.py`)
   - Compare portfolio to benchmark
   - Calculate tracking error
   - Calculate information ratio and alpha

5. **TransitionService** (from `portfolio_transition_widget.py`)
   - Analyze portfolio transitions
   - Calculate transaction costs
   - Generate optimal transition orders

**Effort Estimate**: 1 week total

---

### 1.2 Create Domain Models

Define Pydantic models for all service inputs/outputs:

```python
# src/domain/portfolio.py
class PortfolioSummary(DomainModel):
    total_value: Decimal
    total_cost_basis: Decimal
    total_gain_loss: Decimal
    total_gain_loss_pct: float
    holdings: List[Holding]
    allocation: AllocationBreakdown
    last_updated: datetime

class AllocationBreakdown(DomainModel):
    by_asset_type: Dict[str, Decimal]
    by_sector: Dict[str, Decimal]
    by_currency: Dict[str, Decimal]
    concentration_hhi: float
    top_5_pct: float

# src/domain/timeseries.py
class TrendAnalysis(DomainModel):
    trend_direction: str  # 'up', 'down', 'flat'
    trend_strength: float
    slope: float
    r_squared: float
    forecast: Optional[List[float]]

class TechnicalIndicators(DomainModel):
    rsi: float
    macd: MACD
    bollinger_bands: BollingerBands
    moving_averages: Dict[int, float]

# src/domain/correlation.py
class CorrelationPair(DomainModel):
    symbol1: str
    symbol2: str
    correlation: float
    is_significant: bool
    p_value: float
```

**Effort Estimate**: 2-3 days

---

### 1.3 Add API Endpoints

For each new service, create corresponding API endpoints:

```python
# src/api/routers/portfolio_summary.py
@router.get("/portfolio/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    portfolio_id: Optional[str] = None,
    service: PortfolioSummaryService = Depends(get_portfolio_summary_service)
):
    return service.generate_summary(portfolio_id)

# src/api/routers/correlation.py
@router.post("/correlation/matrix", response_model=CorrelationMatrixResponse)
async def calculate_correlation(
    request: CorrelationRequest,
    service: CorrelationService = Depends(get_correlation_service)
):
    return service.calculate_correlation_matrix(
        request.symbols,
        request.start_date,
        request.end_date
    )

@router.post("/correlation/significant-pairs", response_model=SignificantPairsResponse)
async def find_significant_pairs(
    request: CorrelationRequest,
    threshold: float = Query(0.7, ge=0, le=1),
    service: CorrelationService = Depends(get_correlation_service)
):
    matrix = service.calculate_correlation_matrix(
        request.symbols,
        request.start_date,
        request.end_date
    )
    pairs = service.find_significant_pairs(matrix, threshold)
    return SignificantPairsResponse(pairs=pairs)
```

**Effort Estimate**: 3-4 days

---

## Phase 2: Implement Missing Next.js Features (Week 3-4)

### 2.1 Order Management

**Current State**: 
- Streamlit has full order management in `pages/My_Orders.py`
- Controllers in `src/controllers/my_orders/` (527 lines)

**Required Next.js Pages**:

```typescript
// frontend/v1/src/app/orders/page.tsx
export default function OrdersPage() {
  return (
    <div>
      <OrderEntryForm />
      <OrderHistoryTable />
      <OrderListComponent />
    </div>
  );
}

// frontend/v1/src/components/orders/OrderEntryForm.tsx
export function OrderEntryForm() {
  // Form for entering new orders
  // - Symbol selection
  // - Order type (buy/sell)
  // - Quantity
  // - Price
  // - Date
}

// frontend/v1/src/components/orders/OrderHistoryTable.tsx
export function OrderHistoryTable() {
  // Display order history
  // - Filterable by symbol, date range
  // - Sortable columns
  // - Edit/delete actions
}
```

**Required API Endpoints** (likely already exist):
- `POST /api/orders` - Create order
- `GET /api/orders` - List orders
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order
- `GET /api/orders/history` - Order history

**Action Items**:
- [ ] Verify API endpoints exist and work correctly
- [ ] Implement OrdersPage in Next.js
- [ ] Implement OrderEntryForm component
- [ ] Implement OrderHistoryTable component
- [ ] Add order validation
- [ ] Add success/error notifications
- [ ] Add tests

**Effort Estimate**: 3-4 days

---

### 2.2 Comparative Analysis

**Current State**:
- Streamlit has `pages/Comparative_Analysis.py`
- Controller: `src/controllers/comparative_analysis.py` (132 lines)
- Likely compares multiple portfolios or instruments

**Required Next.js Pages**:

```typescript
// frontend/v1/src/app/analysis/comparative/page.tsx
export default function ComparativeAnalysisPage() {
  return (
    <div>
      <InstrumentSelector />
      <ComparisonMetricsTable />
      <ComparisonCharts />
    </div>
  );
}

// frontend/v1/src/components/analysis/InstrumentSelector.tsx
export function InstrumentSelector() {
  // Multi-select for instruments to compare
  // Date range selector
  // Benchmark selection
}

// frontend/v1/src/components/analysis/ComparisonMetricsTable.tsx
export function ComparisonMetricsTable() {
  // Side-by-side metrics comparison
  // Returns, volatility, Sharpe, etc.
}

// frontend/v1/src/components/analysis/ComparisonCharts.tsx
export function ComparisonCharts() {
  // Overlaid price charts
  // Returns comparison
  // Risk/return scatter plot
}
```

**Required API Endpoints**:
- `POST /api/analysis/compare` - Compare multiple instruments
- `GET /api/analysis/metrics` - Get comparison metrics

**Action Items**:
- [ ] Analyze Streamlit controller to understand exact functionality
- [ ] Implement ComparativeAnalysisPage in Next.js
- [ ] Implement comparison components
- [ ] Add API endpoints if missing
- [ ] Add tests

**Effort Estimate**: 2-3 days

---

### 2.3 Price History View

**Current State**:
- Streamlit has `pages/Price_History.py`
- Controller: `src/controllers/price_history/` (150 lines)

**Assessment**: 
- May be redundant with dashboard widgets
- Check if standalone page is actually needed
- Price charts likely already in dashboard

**Action**:
- [ ] Review current usage
- [ ] Determine if dedicated page needed
- [ ] If needed, implement simple price history page
- [ ] If not needed, document that charts are in dashboard

**Effort Estimate**: 0-1 days (may not be needed)

---

### 2.4 Widget Configuration Persistence

**Current State**:
- Streamlit saves dashboard config to database via `storage.set_setting()`
- Widget arrangement stored as JSON

**Next.js Implementation**:

```typescript
// frontend/v1/src/hooks/use-dashboard-config.ts
export function useDashboardConfig() {
  const saveLayout = async (layout: Layout[]) => {
    // Save to API endpoint
    await fetch('/api/dashboard/config', {
      method: 'POST',
      body: JSON.stringify({ layout })
    });
  };
  
  const loadLayout = async () => {
    // Load from API
    const response = await fetch('/api/dashboard/config');
    return response.json();
  };
  
  return { saveLayout, loadLayout };
}
```

**Required API Endpoints**:
```python
# src/api/routers/dashboard.py
@router.post("/dashboard/config")
async def save_dashboard_config(config: DashboardConfig, user: User = Depends(get_current_user)):
    # Save to user settings
    pass

@router.get("/dashboard/config")
async def get_dashboard_config(user: User = Depends(get_current_user)):
    # Load from user settings
    pass
```

**Action Items**:
- [ ] Create dashboard config API endpoints
- [ ] Implement useDashboardConfig hook
- [ ] Update dashboard to save/load layouts
- [ ] Test persistence across sessions
- [ ] Add migration for existing Streamlit configs

**Effort Estimate**: 1-2 days

---

## Phase 3: Add Deprecation Warnings (Week 5)

### 3.1 Update Streamlit App

Add prominent deprecation banner to `app.py`:

```python
"""
ETF Analysis Dashboard - Home Page
"""

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

# Load environment variables
load_dotenv()

# DEPRECATION NOTICE - Phase out dates (configure via environment)
DEPRECATION_START = datetime.fromisoformat(
    os.getenv('DEPRECATION_START_DATE', '2025-12-08')
)
STREAMLIT_DISABLE_DATE = DEPRECATION_START + timedelta(weeks=8)
STREAMLIT_REMOVAL_DATE = STREAMLIT_DISABLE_DATE + timedelta(weeks=2)

days_until_disable = (STREAMLIT_DISABLE_DATE - datetime.now()).days
days_until_removal = (STREAMLIT_REMOVAL_DATE - datetime.now()).days

# Get dashboard URL from environment
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:3000/dashboard')

# Show deprecation warning
st.warning(f"""
⚠️ **DEPRECATION NOTICE** ⚠️

The Streamlit interface is being **phased out and will be removed**.

🌐 **New Dashboard**: [{DASHBOARD_URL}]({DASHBOARD_URL})

✨ **Why Switch?**
- Modern, responsive design
- Drag-and-drop widget management
- Faster performance
- Better mobile support
- Same features, better experience

📅 **Important Dates**:
- ✅ **Now - {STREAMLIT_DISABLE_DATE.strftime('%b %d, %Y')}**: Both interfaces available ({days_until_disable} days)
- ⚠️ **{STREAMLIT_DISABLE_DATE.strftime('%b %d, %Y')}**: Streamlit becomes **read-only**
- 🗓️ **{STREAMLIT_REMOVAL_DATE.strftime('%b %d, %Y')}**: Streamlit **fully removed** ({days_until_removal} days)

📖 **Need Help?** [Migration Guide](https://github.com/doylet/etf-analysis/docs/migration-guide.md)

⚠️ **Action Required**: Please switch to the new dashboard before {STREAMLIT_DISABLE_DATE.strftime('%b %d, %Y')}.
""", icon="⚠️")

# Add countdown banner
if days_until_disable <= 14:
    st.error(f"""
    🚨 **URGENT**: Only **{days_until_disable} days** until Streamlit becomes read-only!
    Switch to the new dashboard NOW: [{DASHBOARD_URL}]({DASHBOARD_URL})
    """, icon="🚨")

# Page configuration
st.set_page_config(
    page_title="ETF Analysis Dashboard - Home (DEPRECATED)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add deprecation to sidebar
with st.sidebar:
    st.error("⚠️ This interface is deprecated")
    st.markdown(f"**{days_until_disable} days** until read-only")
    if st.button("Switch to New Dashboard", use_container_width=True):
        st.markdown(f"[Open New Dashboard]({DASHBOARD_URL})")

# ... rest of app.py
```

### 3.2 Add Warnings to All Pages

Update each page in `pages/` to show warnings:

```python
# pages/Dashboard.py
import os
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:3000/dashboard')
st.warning(f"⚠️ This page is deprecated. Use the new dashboard: {DASHBOARD_URL}")

# Similar for all other pages
```

### 3.3 Create Migration Guide

```markdown
# Migration Guide: Streamlit to Next.js Dashboard

## Why Migrate?

The new Next.js dashboard offers:
- Better performance
- Modern UI/UX
- Mobile-friendly
- Drag-and-drop widgets
- Same features

## Feature Mapping

| Streamlit | Next.js Equivalent |
|-----------|-------------------|
| Dashboard page | /dashboard |
| My Orders | /orders |
| Price History | /dashboard (price charts) |
| Comparative Analysis | /analysis/comparative |
| All widgets | Available in /dashboard |

## Migration Steps

1. **Access the new dashboard**: [See DASHBOARD_URL in your deployment]
2. **Your data is safe**: All data is shared between interfaces
3. **Customize layout**: Drag and drop widgets to your preference
4. **Save layout**: Layout is automatically saved
5. **Stop using Streamlit**: Before [STREAMLIT_DISABLE_DATE]

## Getting Help

- Questions? Open an issue
- Problems? Contact support
```

**Effort Estimate**: 1 day

---

## Phase 4: Feature Flag & Monitoring (Week 6)

### 4.1 Add Feature Flag

```python
# .env
STREAMLIT_ENABLED=true
STREAMLIT_READ_ONLY=false

# app.py
import os

STREAMLIT_ENABLED = os.getenv('STREAMLIT_ENABLED', 'true').lower() == 'true'
STREAMLIT_READ_ONLY = os.getenv('STREAMLIT_READ_ONLY', 'false').lower() == 'true'

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:3000/dashboard')

if not STREAMLIT_ENABLED:
    st.error(f"""
    🚫 **Streamlit Interface Disabled**
    
    The Streamlit interface has been disabled. Please use the new Next.js dashboard:
    
    🌐 {DASHBOARD_URL}
    """)
    st.stop()

if STREAMLIT_READ_ONLY:
    st.warning(f"""
    📖 **Read-Only Mode**
    
    The Streamlit interface is now in read-only mode. You can view data but cannot make changes.
    
    To manage your portfolio, use the new dashboard:
    🌐 {DASHBOARD_URL}
    """)
    # Disable all input controls
```

### 4.2 Add Usage Analytics

Track Streamlit usage vs Next.js usage:

```python
# Add analytics to track page views
import logging

logger = logging.getLogger(__name__)

def track_streamlit_usage(page_name: str):
    logger.info(f"Streamlit page accessed: {page_name}")
    # Could also send to analytics service
```

### 4.3 Monitor Migration Progress

Create dashboard to track:
- Streamlit page views over time
- Next.js page views over time
- Active users on each platform
- Feature usage comparison

**Effort Estimate**: 2-3 days

---

## Phase 5: Read-Only Mode (Week 7)

### 5.1 Enable Read-Only Mode

Set `STREAMLIT_READ_ONLY=true` in environment.

### 5.2 Disable Input Controls

```python
# Disable all forms and inputs
if STREAMLIT_READ_ONLY:
    # Override Streamlit input functions
    def disabled_input(*args, **kwargs):
        st.info("This interface is read-only. Use the new dashboard to make changes.")
        return None
    
    st.text_input = disabled_input
    st.button = lambda *args, **kwargs: False
    st.selectbox = lambda *args, **kwargs: None
    # etc.
```

### 5.3 Communicate to Users

- Send email notifications
- Show prominent read-only banner
- Provide migration instructions

**Effort Estimate**: 1 day

---

## Phase 6: Final Removal (Week 8+)

### 6.1 Archive Streamlit Code

```bash
# Create backup branch
git checkout -b archive/streamlit-backup
git push origin archive/streamlit-backup

# Tag the release
git tag -a v1.0-streamlit-final -m "Final Streamlit version before removal"
git push origin v1.0-streamlit-final
```

### 6.2 Remove Files

```bash
# Remove Streamlit files
rm app.py
rm -rf pages/
rm -rf src/controllers/
rm -rf src/widgets/
rm -rf .streamlit/

# Commit removal
git commit -m "Remove deprecated Streamlit UI

All functionality has been migrated to Next.js frontend.
Business logic preserved in service layer.

See docs/streamlit-deprecation-analysis.md for details.
Archive available in branch: archive/streamlit-backup
"
```

### 6.3 Clean Dependencies

Update `requirements.txt`:

```bash
# Remove Streamlit dependencies
- streamlit
- streamlit-aggrid
- streamlit-option-menu
# Any other Streamlit-specific packages
```

### 6.4 Update Documentation

- Update README to remove Streamlit references
- Update deployment docs
- Update architecture docs
- Add historical note about migration

### 6.5 Update Deployments

- Remove Streamlit from Docker files
- Update CI/CD pipelines
- Update deployment scripts
- Verify Next.js is primary interface

**Effort Estimate**: 2-3 days

---

## Success Criteria

### Phase 1: Business Logic Extraction
- [ ] All widget business logic extracted to services
- [ ] All services have unit tests
- [ ] All API endpoints verified and working
- [ ] Zero business logic remains in widgets

### Phase 2: Next.js Feature Parity
- [ ] Order management implemented
- [ ] Comparative analysis implemented
- [ ] Widget config persistence implemented
- [ ] All features tested and working

### Phase 3: Deprecation Warnings
- [ ] Warnings visible on all Streamlit pages
- [ ] Migration guide published
- [ ] User communication sent
- [ ] Help resources available

### Phase 4: Feature Flag
- [ ] Feature flag implemented
- [ ] Analytics tracking enabled
- [ ] Usage data collected
- [ ] Migration progress monitored

### Phase 5: Read-Only Mode
- [ ] Read-only mode enabled
- [ ] All inputs disabled
- [ ] Users notified
- [ ] 90%+ users migrated to Next.js

### Phase 6: Removal
- [ ] Code archived to backup branch
- [ ] Files removed from main branch
- [ ] Dependencies cleaned up
- [ ] Documentation updated
- [ ] Deployments updated
- [ ] Zero regressions in production

---

## Risk Mitigation

### Risk 1: Users Don't Migrate
**Mitigation**:
- Provide clear migration guide
- Show benefits of new interface
- Provide support during transition
- Gradual timeline with warnings
- Make Next.js very appealing

### Risk 2: Missing Functionality
**Mitigation**:
- Thorough feature parity analysis
- User testing before deprecation
- Quick response to feedback
- Can keep Streamlit longer if needed

### Risk 3: Business Logic Loss
**Mitigation**:
- Extract all logic to services first
- Comprehensive test coverage
- API endpoint verification
- Code review of all changes
- Can reference archived code

### Risk 4: Deployment Issues
**Mitigation**:
- Test in staging first
- Gradual rollout
- Monitoring and alerts
- Rollback plan ready
- Keep archived branch available

---

## Rollback Plan

If critical issues arise:

1. **Immediate Rollback** (if in read-only mode):
   - Set `STREAMLIT_ENABLED=true` and `STREAMLIT_READ_ONLY=false`
   - Restore full Streamlit functionality
   - Investigate issues

2. **Full Rollback** (if code removed):
   - Restore from `archive/streamlit-backup` branch
   - Redeploy previous version
   - Fix issues before trying again

3. **Partial Rollback**:
   - Keep Streamlit for specific features
   - Fix Next.js issues
   - Retry deprecation later

---

## Communication Plan

### Week 1-2 (During extraction)
- Internal team updates
- Stakeholder briefing

### Week 5 (Deprecation warnings)
- Email to all users
- In-app banners
- Blog post announcement
- Update documentation

### Week 6 (Feature flag)
- Usage analytics review
- Follow-up email if low migration

### Week 7 (Read-only mode)
- Final warning email
- Prominent read-only banner
- Support channels open

### Week 8+ (Removal)
- Completion announcement
- Thank users for migrating
- Highlight new features

---

## Post-Removal Checklist

After Streamlit is removed:

- [ ] Verify Next.js is production-ready
- [ ] Monitor error rates
- [ ] Collect user feedback
- [ ] Fix any issues quickly
- [ ] Document lessons learned
- [ ] Update project metrics
- [ ] Celebrate successful migration! 🎉

---

**Document Version**: 1.0  
**Last Updated**: December 8, 2025  
**Next Review**: After Phase 1 completion
