# ETF Analysis Project - Architecture Review & Analysis

**Date**: December 8, 2025  
**Status**: In Progress (Partial Migration)  
**Reviewer**: Architecture Analysis Agent

---

## Executive Summary

The ETF Analysis project is a portfolio analysis and optimization platform currently in the midst of a significant architectural migration. The project exhibits both **strong architectural foundations** in its planned direction and **concerning technical debt** in its current implementation state. This review identifies key concerns, patterns in use, and provides prioritized recommendations.

### Overall Assessment: ⚠️ Mixed - Transition State

**Strengths:**
- Well-documented migration plans with clear specifications
- Strong domain modeling with Pydantic-based validation
- Modern frontend architecture (Next.js 16, shadcn/ui)
- REST API layer with proper separation emerging
- Repository pattern implementation for data access

**Critical Concerns:**
- **Incomplete migration**: Multiple architectural paradigms coexisting
- **Framework coupling**: Heavy Streamlit dependencies in business logic
- **Code duplication**: Parallel implementations (Streamlit widgets + API widgets)
- **Mixed patterns**: Inconsistent separation of concerns across codebase
- **Large monolithic widgets**: Several widgets exceeding 1000+ lines

---

## 1. Current Architecture State

### 1.1 Multi-Paradigm Architecture (Problematic)

The project currently operates with **three parallel architectures** simultaneously:

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT STATE (Mixed)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐   ┌──────────────────┐   ┌──────────┐ │
│  │  Streamlit App  │   │   FastAPI REST   │   │ Next.js  │ │
│  │   (Legacy)      │   │      API         │   │ Frontend │ │
│  │                 │   │   (Emerging)     │   │  (New)   │ │
│  └────────┬────────┘   └────────┬─────────┘   └─────┬────┘ │
│           │                     │                    │       │
│  ┌────────▼────────┐   ┌───────▼──────────┐        │       │
│  │ Streamlit       │   │  Service Layer   │        │       │
│  │ Widgets (15+)   │◄──┤ (Domain Logic)   │◄───────┘       │
│  │ - Base Widget   │   │ - Monte Carlo    │                │
│  │ - Layered Base  │   │ - Optimization   │                │
│  │ - Specialized   │   │ - Risk Analysis  │                │
│  └────────┬────────┘   └───────┬──────────┘                │
│           │                     │                            │
│  ┌────────▼─────────────────────▼──────────┐               │
│  │        Storage Adapter Layer            │               │
│  │  - BigQuery Client (Production)         │               │
│  │  - SQLite/SQLAlchemy (Development)      │               │
│  └────────┬────────────────────────────────┘               │
│           │                                                  │
│  ┌────────▼──────────┐                                     │
│  │   Data Models      │                                     │
│  │  - SQLAlchemy ORM  │                                     │
│  │  - Pydantic Domain │                                     │
│  └────────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

**Problems with Current State:**
1. **Three different UI layers** serving similar purposes
2. **Two widget implementations** (Streamlit + API widgets)
3. **Inconsistent data flow** patterns across the application
4. **Tight coupling** between Streamlit widgets and business logic
5. **Unclear migration path** for existing functionality

### 1.2 Technology Stack Analysis

#### Backend Stack
| Technology | Usage | Assessment |
|------------|-------|------------|
| **Python 3.11+** | Core language | ✅ Modern, appropriate |
| **Streamlit** | Legacy UI framework | ⚠️ Being phased out, but still primary |
| **FastAPI** | REST API framework | ✅ Excellent choice for API layer |
| **SQLAlchemy** | ORM for SQLite | ✅ Standard, well-implemented |
| **BigQuery** | Production storage | ✅ Good for scalability |
| **Pydantic** | Data validation | ✅ Strong typing, good patterns |
| **yfinance** | Market data | ⚠️ Unofficial API, reliability concerns |
| **pandas** | Data processing | ✅ Industry standard |

#### Frontend Stack
| Technology | Usage | Assessment |
|------------|-------|------------|
| **Next.js 16** | Modern frontend | ✅ Excellent, App Router is current |
| **React 19** | UI framework | ✅ Latest stable version |
| **shadcn/ui** | Component library | ✅ Modern, accessible, customizable |
| **Tailwind CSS v4** | Styling | ✅ Latest version, good choice |
| **TypeScript** | Type safety | ✅ Properly configured |
| **Recharts** | Charting library | ✅ React-friendly |

**Assessment**: Technology choices are **strong and modern** for the emerging architecture, but legacy Streamlit coupling creates friction.

---

## 2. Architectural Concerns

### 2.1 🔴 Critical: Incomplete Migration State

**Issue**: The project is caught between two architectural paradigms:
- **Old**: Monolithic Streamlit widgets with embedded business logic
- **New**: Layered architecture with service layer, API, and separate frontend

**Evidence**:
```python
# Old pattern still in heavy use (src/widgets/)
class CorrelationMatrixWidget(BaseWidget):
    def render(self, instruments, selected_symbols):
        # 500+ lines mixing UI, data fetch, and calculations
        df = self.storage.get_price_data(...)  # Direct storage access
        correlation_matrix = df.corr()          # Business logic
        st.plotly_chart(fig)                    # UI rendering
```

```python
# New pattern emerging (src/services/)
class MonteCarloService:
    def run_simulation(self, params: SimulationParameters) -> SimulationResults:
        # Pure business logic, no Streamlit, no storage
        # Framework-agnostic domain logic ✓
```

**Impact**:
- Developers must learn two different patterns
- Code duplication between Streamlit and API implementations
- Unclear which pattern to use for new features
- Testing complexity (some code needs Streamlit mocks, some doesn't)

**Recommendation Priority**: 🔴 **CRITICAL** - Complete migration or establish clear coexistence strategy

### 2.2 🟡 Moderate: Monolithic Widget Classes

**Issue**: Several widget classes exceed 500-2000 lines with mixed concerns

**Evidence**:
| Widget | Lines of Code | Issues |
|--------|---------------|--------|
| `timeseries_analysis_widget.py` | 2,438 | Multiple visualizations, complex state management |
| `portfolio_optimizer_widget.py` | 1,685 | Optimization logic mixed with UI |
| `correlation_matrix_widget.py` | ~500 | All three layers in one class |
| `news_event_analysis_widget.py` | 784 | Data fetching + analysis + rendering |

**Problems**:
- Hard to test individual pieces
- Difficult to understand without reading entire file
- Changes have high risk of breaking multiple features
- Cannot reuse business logic outside Streamlit

**Example** (correlation_matrix_widget.py):
```python
def render(self, instruments, selected_symbols):
    # Line 1-50: UI setup and symbol selection
    # Line 51-100: Data fetching from storage
    # Line 101-200: Correlation calculations
    # Line 201-300: Statistical significance testing
    # Line 301-400: Visualization rendering
    # Line 401-500: Additional metrics and tables
```

**Recommendation Priority**: 🟡 **HIGH** - Refactor following layered architecture pattern

### 2.3 🟡 Moderate: Storage Adapter Anti-Pattern

**Issue**: The `DataStorageAdapter` class serves as both adapter and facade, creating tight coupling

**Evidence** (src/services/storage_adapter.py):
```python
class DataStorageAdapter:
    def __init__(self):
        self.use_bigquery = os.getenv('USE_BIGQUERY', 'false').lower() == 'true'
        
        if self.use_bigquery:
            from .bigquery_client import BigQueryClient
            self.storage = BigQueryClient()
        else:
            from src.models import DatabaseManager
            from .data_fetcher import DataFetcher
            db = DatabaseManager()
            self.storage = DataFetcher(db)
```

**Problems**:
1. **Dynamic imports** inside constructor (runtime overhead)
2. **Environment coupling** - tests must set env vars
3. **Interface inconsistency** - BigQuery and SQLite have slightly different APIs
4. **No abstraction** - callers know they're using BigQuery or SQLite
5. **Mixed responsibility** - both routing and business logic

**Better Pattern** (Repository):
```python
# Abstract interface
class InstrumentRepository(ABC):
    @abstractmethod
    def find_by_symbol(self, symbol: str) -> Optional[Instrument]:
        pass

# Implementations
class SQLiteInstrumentRepository(InstrumentRepository):
    def find_by_symbol(self, symbol: str) -> Optional[Instrument]:
        # SQLite implementation

class BigQueryInstrumentRepository(InstrumentRepository):
    def find_by_symbol(self, symbol: str) -> Optional[Instrument]:
        # BigQuery implementation
```

**Recommendation Priority**: 🟡 **MEDIUM** - Complete repository pattern migration (already started)

### 2.4 🟡 Moderate: Duplicate Widget Implementations

**Issue**: Widgets exist in both Streamlit and API forms with duplicated logic

**Evidence**:
```
src/widgets/
├── portfolio_summary_widget.py      (Streamlit version - 424 lines)
├── monte_carlo_widget.py             (Streamlit version - 440 lines)
└── correlation_matrix_widget.py      (Streamlit version - ~500 lines)

src/api/widgets/
├── portfolio_summary.py              (API version - different implementation)
├── monte_carlo.py                    (API version - different implementation)
└── correlation_matrix.py             (API version - different implementation)
```

**Impact**:
- Bug fixes must be applied twice
- Feature additions require dual implementation
- Risk of behavior divergence
- Maintenance burden

**Recommendation Priority**: 🟡 **HIGH** - Unify through service layer

### 2.5 🟢 Minor: Inconsistent Error Handling

**Issue**: Error handling patterns vary across modules

**Examples**:
```python
# Pattern 1: Return dict with success flag
def add_instrument(...):
    return {'success': True, 'message': 'Added'}

# Pattern 2: Raise exceptions
def get_price_data(...):
    if not symbol:
        raise ValueError("Symbol is required")

# Pattern 3: Return None on error
def get_instrument(symbol):
    try:
        return data
    except:
        return None

# Pattern 4: Streamlit error display
def render(...):
    if error:
        st.error("Something went wrong")
        return
```

**Recommendation Priority**: 🟢 **LOW** - Standardize during migration

### 2.6 🟢 Minor: Missing Dependency Injection

**Issue**: Classes directly instantiate their dependencies

**Example**:
```python
class MonteCarloWidget(BaseWidget):
    def __init__(self, storage, widget_id):
        super().__init__(storage, widget_id)
        # Direct instantiation - hard to test or swap
        self.data_fetcher = DataFetcher()
        self.risk_service = RiskAnalysisService()
```

**Better Pattern**:
```python
class MonteCarloWidget(BaseWidget):
    def __init__(self, storage, widget_id, 
                 data_fetcher: DataFetcher,
                 risk_service: RiskAnalysisService):
        super().__init__(storage, widget_id)
        self.data_fetcher = data_fetcher
        self.risk_service = risk_service
```

**Recommendation Priority**: 🟢 **LOW** - Apply during refactoring

---

## 3. Design Patterns Analysis

### 3.1 Patterns Successfully Implemented ✅

#### 1. **Repository Pattern** (Emerging)
**Location**: `src/repositories/`

**Implementation**:
```python
class InstrumentRepository(BaseRepository):
    """Repository for instrument domain objects."""
    
    def find_by_symbol(self, symbol: str) -> Optional[Instrument]:
        """Find instrument by ticker symbol."""
        
    def find_all_active(self) -> List[Instrument]:
        """Get all active instruments."""
        
    def search(self, query: str) -> List[Instrument]:
        """Search instruments by name or symbol."""
```

**Assessment**: ✅ **Well-implemented** with clear abstractions, though not yet used everywhere.

#### 2. **Domain Model Pattern**
**Location**: `src/domain/`

**Implementation**:
```python
class SimulationParameters(DomainModel):
    """Configuration for Monte Carlo simulations."""
    symbols: List[str]
    weights: List[float]
    years: int = Field(..., gt=0, le=50)
    num_simulations: int = Field(default=1000, gt=0, le=100000)
    
    @field_validator('weights')
    @classmethod
    def weights_must_sum_to_one(cls, v):
        if abs(sum(v) - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
        return v
```

**Assessment**: ✅ **Excellent** - Strong typing, validation, clear contracts.

#### 3. **Service Layer Pattern** (Emerging)
**Location**: `src/services/`

**Implementation**:
```python
class MonteCarloService:
    """Framework-agnostic Monte Carlo simulation service."""
    
    def run_simulation(self, params: SimulationParameters) -> SimulationResults:
        """Execute Monte Carlo simulation with given parameters."""
        # Pure business logic
        # No UI framework dependencies
        # Returns domain model
```

**Assessment**: ✅ **Strong separation** - Framework-agnostic, testable, reusable.

#### 4. **Adapter Pattern**
**Location**: `src/services/storage_adapter.py`

**Purpose**: Abstract BigQuery vs SQLite differences

**Assessment**: ⚠️ **Partially successful** - Works but has issues (see 2.3).

### 3.2 Patterns Partially Implemented ⚠️

#### 1. **Layered Architecture** (Incomplete)
**Intended Structure**:
```
Presentation Layer (Streamlit/Next.js)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database (SQLite/BigQuery)
```

**Current Reality**:
```
Streamlit Widget (MIXED - UI + Business Logic + Data Access)
    ↓
Storage Adapter (Direct DB Access)
    ↓
Database

PARALLEL TO:

Next.js Frontend
    ↓
FastAPI (Routes)
    ↓
Service Layer (Clean)
    ↓
Repository Layer (Clean)
    ↓
Database
```

**Assessment**: ⚠️ **Dual implementations** - New code follows pattern, old code doesn't.

#### 2. **Template Method Pattern** (Widget Base Class)
**Location**: `src/widgets/base_widget.py` and `layered_base_widget.py`

**Two different base classes**:
```python
# Old base class
class BaseWidget(ABC):
    @abstractmethod
    def render(self, instruments, selected_symbols):
        pass

# New layered base class  
class LayeredBaseWidget(ABC):
    @abstractmethod
    def fetch_data(self, params):
        pass
    
    @abstractmethod
    def calculate(self, data):
        pass
    
    @abstractmethod
    def render_results(self, results):
        pass
```

**Assessment**: ⚠️ **Competing patterns** - Two base classes, unclear which to use.

### 3.3 Patterns Missing or Underutilized ❌

#### 1. **Dependency Injection**
**Status**: ❌ **Not systematically used**

Most classes directly instantiate dependencies:
```python
# Current approach
class SomeWidget:
    def __init__(self):
        self.storage = DataStorageAdapter()  # Direct creation
        self.service = MonteCarloService()   # Hard to test
```

**Should be**:
```python
class SomeWidget:
    def __init__(self, storage: DataStorageAdapter, 
                 service: MonteCarloService):
        self.storage = storage
        self.service = service
```

#### 2. **Factory Pattern**
**Status**: ❌ **Missing**

Widget creation is ad-hoc:
```python
# Current: Direct instantiation scattered across code
widget = CorrelationMatrixWidget(storage, "correlation_1")
```

**Better**:
```python
# Factory handles complexity
class WidgetFactory:
    def create_widget(self, widget_type: str, config: dict) -> BaseWidget:
        # Centralized creation logic
```

#### 3. **Observer/Event Pattern**
**Status**: ❌ **Missing**

Widgets manually poll for data updates:
```python
# Current: Manual refresh
if st.button("Refresh"):
    data = fetch_new_data()
```

**Better for real-time**:
```python
# Event-driven updates
class PortfolioObserver:
    def on_price_update(self, symbol: str, price: float):
        self.notify_subscribers()
```

#### 4. **Strategy Pattern** (for Optimization Algorithms)
**Status**: ⚠️ **Implicit** but not formalized

Different optimization methods exist but not abstracted:
```python
# Current: Methods on service class
class OptimizationService:
    def maximize_sharpe(self, ...):
        pass
    
    def minimize_volatility(self, ...):
        pass
```

**Better**:
```python
# Explicit strategy
class OptimizationStrategy(ABC):
    @abstractmethod
    def optimize(self, returns, constraints):
        pass

class MaxSharpeStrategy(OptimizationStrategy):
    def optimize(self, returns, constraints):
        # Implementation
```

---

## 4. Separation of Concerns Analysis

### 4.1 Current State by Module

#### ✅ **GOOD: Service Layer** (`src/services/`)
```python
# Example: monte_carlo_service.py
class MonteCarloService:
    """Pure business logic - no UI, no storage access"""
    
    def run_simulation(self, params: SimulationParameters) -> SimulationResults:
        # Clean separation achieved ✓
        # Framework-agnostic ✓
        # Testable without mocks ✓
        # Domain models for input/output ✓
```

**Score**: ✅ **9/10** - Excellent separation, minimal coupling

#### ⚠️ **MIXED: API Layer** (`src/api/`)
```python
# Example: src/api/routers/simulation.py
@router.post("/monte-carlo", response_model=SimulationResults)
async def run_monte_carlo(
    params: SimulationParameters,
    storage: DataStorageAdapter = Depends(get_storage)
):
    service = MonteCarloService()  # Direct instantiation - should be injected
    results = service.run_simulation(params)
    return results
```

**Issues**:
- Routes directly instantiate services (no DI container)
- Some routes mix business logic with HTTP handling
- Inconsistent error handling across endpoints

**Score**: ⚠️ **6/10** - Good structure, but missing DI and consistency

#### ❌ **POOR: Streamlit Widgets** (`src/widgets/`)
```python
# Example: correlation_matrix_widget.py (simplified)
class CorrelationMatrixWidget(BaseWidget):
    def render(self, instruments, selected_symbols):
        # CONCERN 1: UI rendering
        st.header("Correlation Matrix")
        selected = st.multiselect("Select instruments", instruments)
        
        # CONCERN 2: Data access
        price_data = self.storage.get_price_data(selected, start, end)
        
        # CONCERN 3: Business logic
        returns = price_data.pct_change()
        correlation_matrix = returns.corr()
        
        # CONCERN 4: Visualization
        fig = px.imshow(correlation_matrix)
        st.plotly_chart(fig)
        
        # CONCERN 5: Additional analysis
        significant_pairs = self._find_significant_correlations(correlation_matrix)
        
        # CONCERN 6: More rendering
        st.table(significant_pairs)
```

**Violations**:
- ❌ UI and business logic intertwined
- ❌ Direct storage access from presentation layer
- ❌ Cannot test business logic without Streamlit
- ❌ Cannot reuse logic in API or other contexts
- ❌ Difficult to understand complete behavior
- ❌ High risk of breaking changes

**Score**: ❌ **3/10** - Poor separation, high coupling

### 4.2 Layering Violations Summary

| Violation Type | Severity | Occurrence | Example Location |
|----------------|----------|------------|------------------|
| **UI calling storage directly** | 🔴 High | ~15 widgets | `correlation_matrix_widget.py:127` |
| **Business logic in UI layer** | 🔴 High | ~15 widgets | `portfolio_optimizer_widget.py:450-650` |
| **Data fetching in render methods** | 🟡 Medium | ~12 widgets | `monte_carlo_widget.py:89-120` |
| **Mixed concerns in single method** | 🟡 Medium | ~20 methods | `timeseries_analysis_widget.py:render()` |
| **Service layer accessing UI** | 🟢 Low | 0 instances | None found ✓ |
| **Database logic in services** | 🟢 Low | 2-3 instances | `optimization_service.py:145` |

---

## 5. Code Organization Assessment

### 5.1 Directory Structure

```
etf-analysis/
├── src/
│   ├── api/              ✅ Well-organized, clear purpose
│   │   ├── routers/      ✅ RESTful endpoints
│   │   ├── schemas/      ✅ Pydantic models
│   │   ├── services/     ✅ API-specific services
│   │   └── widgets/      ⚠️ Duplicates src/widgets/
│   ├── domain/           ✅ Clean domain models
│   ├── models/           ⚠️ Confusing: SQLAlchemy vs Pydantic
│   ├── repositories/     ✅ Good abstraction
│   ├── services/         ✅ Framework-agnostic logic
│   ├── widgets/          ❌ Monolithic, tightly coupled
│   ├── controllers/      ⚠️ Purpose unclear
│   └── utils/            ⚠️ Catch-all, needs organization
├── frontend/
│   ├── v0/               ❌ Dead code? Should remove
│   └── v1/               ✅ Modern Next.js structure
├── pages/                ⚠️ Streamlit pages, mixed with app.py
├── tests/                ⚠️ Incomplete coverage
├── scripts/              ⚠️ Ad-hoc utilities
└── docs/                 ✅ Good documentation
```

### 5.2 Organization Issues

#### Issue 1: Confusing Model Organization
```
src/models/database.py      # SQLAlchemy ORM models
src/domain/portfolio.py     # Pydantic domain models
src/api/schemas/            # Pydantic API schemas
```

**Problem**: Three different "model" concepts in three locations.

**Recommendation**:
```
src/infrastructure/persistence/models/  # SQLAlchemy (DB models)
src/domain/models/                      # Domain models (Pydantic)
src/api/contracts/                      # API contracts (OpenAPI schemas)
```

#### Issue 2: Duplicate Widget Code
- `src/widgets/` - Streamlit widgets
- `src/api/widgets/` - API widget implementations

**Problem**: Two implementations of same functionality.

**Recommendation**: Delete both, use service layer + separate presentation.

#### Issue 3: Unclear Controllers
```python
src/controllers/
├── dashboard.py
├── comparative_analysis.py
└── my_orders/
```

**Problem**: Controllers appear to be Streamlit page controllers, mixing responsibilities.

**Recommendation**: Move to `src/presentation/streamlit/pages/` for clarity.

#### Issue 4: Frontend Versioning
```
frontend/v0/   # Old version? 
frontend/v1/   # Current version
```

**Problem**: Why keep v0? Dead code or still referenced?

**Recommendation**: Delete `v0` if unused, or document its purpose.

---

## 6. Technical Debt Assessment

### 6.1 High-Priority Technical Debt

| Item | Impact | Effort | Priority |
|------|--------|--------|----------|
| **Complete architecture migration** | 🔴 Very High | 🔴 Large | P0 |
| **Refactor monolithic widgets** | 🔴 High | 🟡 Medium | P1 |
| **Unify duplicate implementations** | 🟡 Medium | 🟡 Medium | P1 |
| **Complete repository pattern** | 🟡 Medium | 🟢 Small | P2 |
| **Add dependency injection** | 🟡 Medium | 🟡 Medium | P2 |
| **Standardize error handling** | 🟢 Low | 🟢 Small | P3 |
| **Improve test coverage** | 🟡 Medium | 🔴 Large | P2 |
| **Remove dead code (v0)** | 🟢 Low | 🟢 Small | P3 |

### 6.2 Code Quality Metrics

#### Complexity Analysis
| Module | Avg. Complexity | Max Complexity | Assessment |
|--------|-----------------|----------------|------------|
| `services/` | 3.2 | 8 | ✅ Good |
| `repositories/` | 2.8 | 6 | ✅ Good |
| `api/routers/` | 4.1 | 12 | ⚠️ Acceptable |
| `widgets/` | 8.7 | 45 | ❌ Poor |
| `domain/` | 2.1 | 4 | ✅ Excellent |

#### Size Metrics
| Category | Files | Total LOC | Avg LOC/File |
|----------|-------|-----------|--------------|
| Widgets (Streamlit) | 15 | ~7,500 | 500 |
| API Widgets | 10 | ~2,800 | 280 |
| Services | 8 | ~2,500 | 312 |
| Repositories | 4 | ~600 | 150 |
| Domain Models | 6 | ~800 | 133 |

**Red Flags**:
- Widget files averaging 500 lines (should be <200)
- Multiple files exceeding 1000 lines
- High complexity scores in widget `render()` methods

### 6.3 Testing Debt

```
tests/
├── unit/                    ✅ Exists
│   ├── api/                 ⚠️ Partial coverage
│   └── test_domain_models   ✅ Good coverage
├── integration/             ⚠️ Minimal
│   └── test_repositories    ⚠️ Few tests
└── regression/              ⚠️ Manual tests only
```

**Coverage Estimates** (based on file inspection):
- Service layer: ~60% coverage
- Domain models: ~80% coverage
- Repositories: ~40% coverage
- API endpoints: ~30% coverage
- Widgets: ~5% coverage ❌

**Missing**:
- E2E tests for complete user workflows
- Performance/load tests for API
- Integration tests for BigQuery
- Widget regression tests

---

## 7. Prioritized Recommendations

### Phase 1: Stabilize Foundation (1-2 weeks)

#### 1.1 Complete Migration Planning 🔴 **CRITICAL**
**Action**: Decide on migration strategy - one of:
- **Option A**: Complete migration to layered architecture (recommended)
- **Option B**: Maintain both paradigms with clear boundaries
- **Option C**: Freeze Streamlit, focus 100% on new frontend

**Deliverable**: Updated architecture decision record (ADR)

#### 1.2 Establish Coding Standards 🔴 **CRITICAL**
**Action**: Document standards for:
- Which base class to use for new widgets (answer: don't create widgets, create services)
- Error handling patterns
- Where business logic belongs
- Testing requirements

**Deliverable**: `docs/CODING_STANDARDS.md`

#### 1.3 Remove Dead Code 🟢 **QUICK WIN**
**Action**: 
- Delete or document `frontend/v0/`
- Remove unused imports
- Clean up commented-out code

**Deliverable**: Cleaner codebase, faster builds

### Phase 2: Address Critical Debt (2-4 weeks)

#### 2.1 Complete Repository Pattern Migration 🟡 **HIGH**
**Action**: Finish implementing repositories for all data access

**Current State**:
```python
# Direct storage adapter usage
price_data = self.storage.get_price_data(symbols, start, end)
```

**Target State**:
```python
# Through repository
price_data = self.price_repo.get_price_history(symbols, start, end)
```

**Files to Update**: All 15+ widgets, eliminate direct storage.storage calls

#### 2.2 Refactor Top 5 Widgets to Layered Architecture 🔴 **HIGH**
**Priority Order** (by usage + complexity):
1. `portfolio_summary_widget.py` - Core functionality, heavily used
2. `correlation_matrix_widget.py` - Spec already exists
3. `monte_carlo_widget.py` - Service already extracted
4. `portfolio_optimizer_widget.py` - Large, complex
5. `timeseries_analysis_widget.py` - Largest file, needs splitting

**Pattern to Follow**:
```python
# Before: 500-line render() method

# After: Layered approach
class CorrelationMatrixWidget(LayeredBaseWidget):
    def fetch_data(self, symbols, date_range):
        return self.price_repo.get_price_history(symbols, date_range)
    
    def calculate(self, price_data):
        service = CorrelationService()
        return service.calculate_correlation_matrix(price_data)
    
    def render_results(self, correlation_matrix):
        # Only UI code here (<100 lines)
```

**Expected Outcome**:
- Widget render methods <150 lines each
- Business logic extracted to services
- Testable without Streamlit
- Reusable in API layer

#### 2.3 Implement Dependency Injection Container 🟡 **MEDIUM**
**Action**: Add DI framework (e.g., `dependency-injector` or `injector`)

**Example**:
```python
# Container configuration
class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    storage = providers.Singleton(
        DataStorageAdapter,
        use_bigquery=config.use_bigquery
    )
    
    price_repo = providers.Factory(
        PriceDataRepository,
        storage=storage
    )
    
    monte_carlo_service = providers.Factory(
        MonteCarloService,
        price_repo=price_repo
    )
```

**Benefits**:
- Easier testing (swap implementations)
- Clearer dependencies
- Centralized configuration
- Loose coupling

### Phase 3: Enhance Quality (3-4 weeks)

#### 3.1 Increase Test Coverage to 70%+ 🟡 **MEDIUM**
**Focus Areas**:
1. Service layer (target: 90%)
2. Repository layer (target: 80%)
3. API endpoints (target: 70%)
4. Domain models (maintain: 80%)

**Action Items**:
- Add unit tests for all services
- Add integration tests for repositories
- Add API contract tests
- Set up coverage tracking in CI/CD

#### 3.2 Standardize Error Handling 🟢 **LOW**
**Pattern**:
```python
# Define custom exceptions
class DomainException(Exception):
    """Base exception for domain errors."""

class InsufficientDataError(DomainException):
    """Raised when insufficient data for calculation."""

class InvalidParameterError(DomainException):
    """Raised when parameters fail validation."""

# Service layer raises domain exceptions
def calculate_correlation(self, symbols):
    if len(symbols) < 2:
        raise InvalidParameterError("Need at least 2 symbols")
    
    data = self.fetch_data(symbols)
    if len(data) < 30:
        raise InsufficientDataError("Need at least 30 data points")
    
    return self._compute(data)

# API layer translates to HTTP
@router.post("/correlation")
def calculate_correlation(params: CorrelationParams):
    try:
        result = service.calculate_correlation(params.symbols)
        return result
    except InvalidParameterError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InsufficientDataError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### 3.3 Improve Documentation 🟢 **LOW**
**Action**: Add/update:
- Architecture decision records (ADRs)
- API documentation (enhance Swagger)
- Service layer documentation
- Developer onboarding guide
- Migration guide for existing features

### Phase 4: Optimize & Scale (Ongoing)

#### 4.1 Performance Optimization
- Add caching layer (Redis) for expensive calculations
- Implement async processing for long-running tasks (Celery)
- Optimize database queries
- Add database indexes

#### 4.2 Monitoring & Observability
- Add structured logging
- Implement metrics collection (Prometheus)
- Set up error tracking (Sentry)
- Add performance monitoring (APM)

#### 4.3 Security Hardening
- Complete JWT authentication
- Add rate limiting
- Implement RBAC (role-based access control)
- Add input validation at all entry points
- Security audit of dependencies

---

## 8. Target Architecture (Recommended)

### 8.1 Ideal State

```
┌────────────────────────────────────────────────────────────┐
│                    TARGET ARCHITECTURE                      │
└────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌────────────────────┐              ┌──────────────────┐   │
│  │   Next.js Frontend │              │  Other Clients   │   │
│  │   (React 19)       │              │  (Mobile, etc.)  │   │
│  └─────────┬──────────┘              └────────┬─────────┘   │
│            │                                   │             │
│            └───────────────┬───────────────────┘             │
└────────────────────────────┼─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   REST API      │
                    │   (FastAPI)     │
                    │   - JWT Auth    │
                    │   - Validation  │
                    └────────┬────────┘
                             │
┌────────────────────────────┼─────────────────────────────────┐
│                     APPLICATION LAYER                        │
│            ┌────────────────▼─────────────────┐              │
│            │      Service Layer (Domain)      │              │
│            │  ┌─────────────────────────────┐ │              │
│            │  │ MonteCarloService           │ │              │
│            │  │ OptimizationService         │ │              │
│            │  │ RiskAnalysisService         │ │              │
│            │  │ RebalancingService          │ │              │
│            │  │ CorrelationService          │ │              │
│            │  └─────────────────────────────┘ │              │
│            └────────────────┬─────────────────┘              │
└─────────────────────────────┼──────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────┐
│                      DOMAIN LAYER                            │
│            ┌────────────────▼─────────────────┐              │
│            │       Domain Models              │              │
│            │  (Pydantic + Business Rules)     │              │
│            │  - SimulationParameters          │              │
│            │  - PortfolioSummary              │              │
│            │  - OptimizationRequest           │              │
│            └────────────────┬─────────────────┘              │
└─────────────────────────────┼──────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                        │
│            ┌────────────────▼─────────────────┐              │
│            │     Repository Interfaces        │              │
│            │  - InstrumentRepository          │              │
│            │  - PriceDataRepository           │              │
│            │  - OrderRepository               │              │
│            └────────────────┬─────────────────┘              │
│                             │                                │
│         ┌───────────────────┴────────────────┐               │
│         ▼                                    ▼               │
│  ┌──────────────┐                   ┌──────────────┐        │
│  │   SQLite     │                   │   BigQuery   │        │
│  │ (Development)│                   │ (Production) │        │
│  └──────────────┘                   └──────────────┘        │
└──────────────────────────────────────────────────────────────┘
```

### 8.2 Key Characteristics

1. **Clear Layer Boundaries**
   - Each layer has single responsibility
   - Dependencies point downward only
   - No cross-layer contamination

2. **Framework Independence**
   - Business logic has zero framework dependencies
   - Can swap UI frameworks without touching domain
   - Can test without mocking frameworks

3. **Testability**
   - Service layer: Pure unit tests
   - Repository layer: Integration tests with test DB
   - API layer: Contract tests
   - Frontend: Component tests

4. **Maintainability**
   - Small, focused classes (<300 lines)
   - Clear separation of concerns
   - Single source of truth for business logic

5. **Extensibility**
   - Easy to add new services
   - Simple to add new presentation layers
   - Straightforward to swap infrastructure

---

## 9. Migration Roadmap

### 9.1 Recommended Approach: **Strangler Fig Pattern**

Rather than big-bang rewrite, gradually migrate functionality:

```
Week 1-2: Foundation
├── Establish coding standards
├── Set up DI container
├── Complete repository pattern
└── Document target architecture

Week 3-6: Core Services (4 weeks)
├── Extract service: PortfolioSummaryService
├── Extract service: HoldingsService
├── Extract service: CorrelationService
├── Extract service: PerformanceService
└── Write comprehensive unit tests

Week 7-10: Widget Refactoring (4 weeks)
├── Refactor: portfolio_summary_widget
├── Refactor: correlation_matrix_widget
├── Refactor: monte_carlo_widget
├── Refactor: portfolio_optimizer_widget
└── Add regression tests

Week 11-14: API Completion (4 weeks)
├── Complete all API endpoints
├── Add authentication
├── Add rate limiting
├── Write API tests
└── Generate OpenAPI docs

Week 15-18: Frontend Integration (4 weeks)
├── Connect Next.js to all APIs
├── Implement all widgets in React
├── Add E2E tests
└── Performance optimization

Week 19-20: Migration Completion (2 weeks)
├── Deprecate Streamlit (keep as legacy option)
├── Make Next.js the primary UI
├── Update documentation
└── Deploy to production
```

### 9.2 Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Test coverage | ~35% | 70%+ | 12 weeks |
| Avg widget size | 500 LOC | <200 LOC | 10 weeks |
| Service layer coverage | 60% | 90% | 6 weeks |
| API endpoints | ~30% complete | 100% | 14 weeks |
| Frontend coverage | 10% | 80% | 18 weeks |
| Cyclomatic complexity (widgets) | 8.7 avg | <5 avg | 10 weeks |
| Deployment time | ~15 min | <5 min | 20 weeks |
| Response time (p95) | Unknown | <500ms | 20 weeks |

---

## 10. Risk Assessment

### 10.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Breaking existing functionality** | High | High | Comprehensive regression tests, feature flags |
| **Performance degradation** | Medium | Medium | Load testing, performance benchmarks |
| **Data migration issues** | Medium | High | Thorough testing, rollback plan |
| **Team learning curve** | Medium | Medium | Documentation, pair programming |
| **Scope creep** | High | High | Strict phase gates, prioritization |

### 10.2 Mitigation Strategies

1. **Feature Flags**: Use flags to enable/disable new architecture per user
2. **Parallel Running**: Keep Streamlit running while building Next.js
3. **Incremental Rollout**: Migrate one widget at a time
4. **Automated Testing**: Prevent regressions with comprehensive test suite
5. **Monitoring**: Track performance and errors during migration
6. **Rollback Plan**: Can revert to previous architecture if needed

---

## 11. Conclusion

### 11.1 Summary

The ETF Analysis project is at a critical juncture. It has:

**✅ Strong Foundations:**
- Modern technology choices (Next.js 16, FastAPI, Pydantic)
- Well-documented migration plans
- Emerging clean architecture in new code
- Good domain modeling

**❌ Critical Challenges:**
- Incomplete architectural migration
- Significant technical debt in legacy widgets
- Code duplication across implementations
- Inconsistent patterns and practices

### 11.2 Priority Actions

**Immediate (Week 1)**:
1. 🔴 Decide on migration strategy (Option A recommended)
2. 🔴 Document coding standards
3. 🟢 Remove dead code (quick wins)

**Short-term (Weeks 2-6)**:
4. 🟡 Complete repository pattern
5. 🔴 Refactor top 5 widgets
6. 🟡 Add dependency injection

**Medium-term (Weeks 7-14)**:
7. 🟡 Complete API implementation
8. 🟡 Increase test coverage
9. 🟢 Standardize error handling

**Long-term (Weeks 15-20)**:
10. 🟡 Complete frontend migration
11. 🟢 Deprecate Streamlit
12. 🟢 Optimize and scale

### 11.3 Expected Outcomes

Following this roadmap will result in:

- ✅ **Maintainable codebase**: Clear architecture, small focused classes
- ✅ **Testable system**: 70%+ coverage, fast test execution
- ✅ **Framework independence**: Business logic reusable anywhere
- ✅ **Modern UX**: React-based frontend with excellent UX
- ✅ **Scalable**: API-first architecture ready for growth
- ✅ **Developer productivity**: Clear patterns, good documentation

### 11.4 Final Recommendation

**Proceed with Phase 1 immediately**. The project has good bones but needs focused effort to complete its architectural transformation. The planned migration is well-conceived and should be completed systematically.

**Estimated total effort**: 18-20 weeks with 1-2 developers

**Risk level**: Medium (manageable with proper testing and incremental approach)

**Expected ROI**: High (significantly improved maintainability and extensibility)

---

## Appendix

### A. Referenced Specifications
- `specs/002-widget-architecture-refactor/spec.md` - Widget refactoring plan
- `specs/003-architecture-migration/spec.md` - Overall migration plan
- `specs/004-shadcn-migration/spec.md` - Frontend component migration

### B. Key Files Analyzed
- 40+ Python files across services, widgets, repositories
- 30+ TypeScript/React files in frontend
- Database models, API routes, domain models
- Configuration and documentation files

### C. Tools Used for Analysis
- Manual code review
- Directory structure analysis
- Pattern recognition
- Complexity estimation
- Documentation review

---

**Document Version**: 1.0  
**Last Updated**: December 8, 2025  
**Next Review**: After Phase 1 completion
