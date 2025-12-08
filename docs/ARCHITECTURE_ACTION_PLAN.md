# Architecture Improvement - Action Plan

**Date**: December 8, 2025  
**Priority**: HIGH  
**Owner**: Development Team

---

## Executive Summary

This document provides a **prioritized, actionable plan** to address architectural concerns in the ETF Analysis project. For detailed analysis, see [ARCHITECTURE_REVIEW.md](./ARCHITECTURE_REVIEW.md).

### Current State: ⚠️ **Partial Migration**

The project is transitioning from a monolithic Streamlit application to a modern layered architecture with separate API and frontend. This transition is incomplete, creating technical debt.

### Goal State: ✅ **Clean Layered Architecture**

Complete the migration to achieve:
- Framework-agnostic business logic
- Testable, reusable services
- Modern API and frontend
- Clear separation of concerns

---

## Quick Reference: Priority Matrix

| Action | Impact | Effort | Priority | Timeline |
|--------|--------|--------|----------|----------|
| Complete migration strategy | 🔴 Critical | Low | **P0** | Week 1 |
| Document coding standards | 🔴 Critical | Low | **P0** | Week 1 |
| Refactor top 5 widgets | 🔴 High | High | **P1** | Weeks 3-10 |
| Complete repository pattern | 🟡 High | Medium | **P1** | Weeks 2-4 |
| Unify duplicate code | 🟡 Medium | Medium | **P1** | Weeks 5-8 |
| Add dependency injection | 🟡 Medium | Medium | **P2** | Weeks 4-6 |
| Increase test coverage | 🟡 Medium | High | **P2** | Ongoing |
| Standardize error handling | 🟢 Low | Low | **P3** | Weeks 7-9 |
| Remove dead code | 🟢 Low | Low | **P3** | Week 1 |

---

## Phase 1: Foundation (Weeks 1-2)

### 🔴 P0-1: Finalize Migration Strategy
**Status**: 🟡 Needs Decision  
**Assignee**: Tech Lead  
**Deadline**: End of Week 1

**Task**: Choose one approach:

#### Option A: Full Migration (Recommended ✅)
- **Description**: Complete the migration to layered architecture
- **Approach**: Systematically refactor all widgets to use service layer
- **Timeline**: 18-20 weeks
- **Pros**: Clean architecture, no legacy code, best long-term solution
- **Cons**: Requires sustained effort

#### Option B: Hybrid Approach
- **Description**: Maintain both Streamlit and new architecture
- **Approach**: Clear boundaries, Streamlit for internal tools, API for external
- **Timeline**: 12-14 weeks
- **Pros**: Faster short-term, less risk
- **Cons**: Ongoing maintenance of two systems

#### Option C: New Frontend Only
- **Description**: Freeze Streamlit, focus on Next.js frontend
- **Approach**: No new Streamlit features, all effort on API + frontend
- **Timeline**: 14-16 weeks
- **Pros**: Forces clean separation, clear end goal
- **Cons**: May upset current Streamlit users

**Deliverable**: 
- [ ] Decision documented in `docs/ADR-001-migration-strategy.md`
- [ ] Team alignment meeting completed
- [ ] Timeline communicated to stakeholders

---

### 🔴 P0-2: Establish Coding Standards
**Status**: 🔴 Critical  
**Assignee**: Tech Lead + Senior Devs  
**Deadline**: End of Week 1

**Task**: Document clear standards for:

1. **Where business logic belongs**
   ```python
   ✅ DO: Put in service layer (src/services/)
   ❌ DON'T: Put in widgets, API routes, or repositories
   ```

2. **How to structure new features**
   ```
   ✅ DO: Service → Repository → Database
   ❌ DON'T: Widget → Storage Adapter → Database
   ```

3. **Error handling patterns**
   ```python
   ✅ DO: Raise domain exceptions, handle in API layer
   ❌ DON'T: Return error dicts, catch-all exception handlers
   ```

4. **Testing requirements**
   ```
   ✅ DO: Unit test services, integration test repos, contract test APIs
   ❌ DON'T: Skip tests, mock everything
   ```

**Deliverable**:
- [ ] `docs/CODING_STANDARDS.md` created
- [ ] Examples for each standard provided
- [ ] Team training session conducted
- [ ] PR template updated with standards checklist

**Template**: See Appendix A

---

### 🟢 P0-3: Clean Up Dead Code
**Status**: 🟢 Ready  
**Assignee**: Any Developer  
**Deadline**: End of Week 1  
**Effort**: 2-4 hours

**Tasks**:
- [ ] Investigate `frontend/v0/` - delete if unused
- [ ] Remove commented-out code blocks
- [ ] Delete unused imports
- [ ] Remove obsolete scripts in `scripts/`
- [ ] Update `.gitignore` to exclude build artifacts

**Quick Wins**:
```bash
# Find commented code
rg "# TODO|# FIXME|# XXX|# HACK" --type py

# Find unused imports (use pylint or similar)
pylint --disable=all --enable=unused-import src/

# Large files that might be duplicates
find . -name "*.py" -size +500k
```

---

## Phase 2: Critical Refactoring (Weeks 3-10)

### 🔴 P1-1: Complete Repository Pattern
**Status**: 🟡 In Progress (60% complete)  
**Assignee**: Backend Team  
**Deadline**: End of Week 4  
**Effort**: 1-2 weeks

**Current State**: Repositories exist but not used consistently.

**Task**: Eliminate all direct `storage.storage.*` calls.

**Files to Update** (prioritized):
1. [ ] `src/widgets/portfolio_summary_widget.py`
2. [ ] `src/widgets/correlation_matrix_widget.py`
3. [ ] `src/widgets/monte_carlo_widget.py`
4. [ ] `src/widgets/portfolio_optimizer_widget.py`
5. [ ] `src/widgets/holdings_breakdown_widget.py`
6. [ ] (10 more widgets...)

**Pattern**:
```python
# Before (❌)
class SomeWidget(BaseWidget):
    def render(self):
        data = self.storage.get_price_data(...)

# After (✅)
class SomeWidget(LayeredBaseWidget):
    def __init__(self, price_repo: PriceDataRepository, ...):
        self.price_repo = price_repo
    
    def fetch_data(self, params):
        return self.price_repo.get_price_history(...)
```

**Acceptance Criteria**:
- [ ] Zero direct calls to `storage.storage.*` in widgets
- [ ] All repository methods have tests
- [ ] Documentation updated

---

### 🔴 P1-2: Refactor Top 5 Widgets
**Status**: 🔴 Not Started  
**Assignee**: Backend Team  
**Deadline**: End of Week 10  
**Effort**: 6-8 weeks

**Priority Order** (by business value + complexity):

#### Widget 1: Portfolio Summary (Week 3-4)
- [ ] Extract `PortfolioSummaryService`
- [ ] Move calculations to service
- [ ] Reduce render method to <150 lines
- [ ] Add unit tests (80%+ coverage)
- [ ] Update API endpoint to use service

**Files**:
- `src/widgets/portfolio_summary_widget.py` (424 lines)
- Create: `src/services/portfolio_summary_service.py`
- Update: `src/api/routers/portfolio.py`

#### Widget 2: Correlation Matrix (Week 5-6)
- [ ] Extract `CorrelationService`
- [ ] Implement statistical significance tests
- [ ] Reduce to <200 lines total
- [ ] Add comprehensive tests
- [ ] Document calculations

**Files**:
- `src/widgets/correlation_matrix_widget.py` (~500 lines)
- Create: `src/services/correlation_service.py`
- Spec exists: `specs/002-widget-architecture-refactor/spec.md`

#### Widget 3: Monte Carlo (Week 7-8)
- [ ] Use existing `MonteCarloService` (already good!)
- [ ] Refactor widget to be thin wrapper
- [ ] Remove business logic from widget
- [ ] Add integration tests

**Files**:
- `src/widgets/monte_carlo_widget.py` (440 lines)
- `src/services/monte_carlo_service.py` (already exists ✓)

#### Widget 4: Portfolio Optimizer (Week 9-10)
- [ ] Use existing `OptimizationService`
- [ ] Extract any missing logic
- [ ] Split into smaller components
- [ ] Add visualization tests

**Files**:
- `src/widgets/portfolio_optimizer_widget.py` (1,685 lines!)
- `src/services/optimization_service.py` (already exists ✓)

#### Widget 5: Timeseries Analysis (Week 11-12 - if time permits)
- [ ] Split into multiple smaller widgets
- [ ] Extract `TimeseriesAnalysisService`
- [ ] Create focused components
- [ ] Comprehensive testing

**Files**:
- `src/widgets/timeseries_analysis_widget.py` (2,438 lines!)
- Create: `src/services/timeseries_analysis_service.py`

**Template for Each Widget**:
```python
# Standard layered widget pattern
class RefactoredWidget(LayeredBaseWidget):
    """Widget description."""
    
    def __init__(self, 
                 price_repo: PriceDataRepository,
                 service: SpecificService,
                 widget_id: str):
        super().__init__(widget_id)
        self.price_repo = price_repo
        self.service = service
    
    def fetch_data(self, params: WidgetParams) -> DataFrame:
        """Fetch data from repository."""
        return self.price_repo.get_price_history(
            params.symbols, params.start_date, params.end_date
        )
    
    def calculate(self, data: DataFrame) -> WidgetResults:
        """Perform business logic via service."""
        return self.service.calculate(data)
    
    def render_results(self, results: WidgetResults) -> None:
        """Render UI - Streamlit code only."""
        st.header(self.get_name())
        # UI code only (<100 lines)
```

---

### 🟡 P1-3: Unify Duplicate Implementations
**Status**: 🔴 Not Started  
**Assignee**: Full Stack Team  
**Deadline**: End of Week 8  
**Effort**: 3-4 weeks

**Problem**: Same logic in `src/widgets/` and `src/api/widgets/`

**Solution**: Single source of truth in service layer

**Approach**:
```
Before:
  Streamlit Widget → Business Logic
  API Widget → (Different) Business Logic

After:
  Streamlit Widget → Service Layer ← API Endpoint
                     (Single Logic)
```

**Tasks**:
- [ ] Identify duplicate logic across all 15 widgets
- [ ] Ensure services contain all business logic
- [ ] Update Streamlit widgets to use services
- [ ] Update API widgets to use same services
- [ ] Add regression tests to verify identical behavior
- [ ] Delete duplicate code

**Validation**:
```python
# Both should produce identical results
streamlit_result = widget.render(params)
api_result = service.calculate(params)
assert streamlit_result == api_result
```

---

## Phase 3: Quality & Infrastructure (Weeks 4-12)

### 🟡 P2-1: Implement Dependency Injection
**Status**: 🔴 Not Started  
**Assignee**: Backend Lead  
**Deadline**: End of Week 6  
**Effort**: 2 weeks

**Task**: Add DI container for cleaner dependency management

**Recommended**: `dependency-injector` library

**Implementation**:

1. **Create container** (`src/container.py`):
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Infrastructure
    storage = providers.Singleton(
        DataStorageAdapter,
        use_bigquery=config.use_bigquery
    )
    
    # Repositories
    price_repo = providers.Factory(
        PriceDataRepository,
        storage=storage
    )
    
    instrument_repo = providers.Factory(
        InstrumentRepository,
        storage=storage
    )
    
    # Services
    monte_carlo_service = providers.Factory(
        MonteCarloService,
        price_repo=price_repo
    )
    
    portfolio_service = providers.Factory(
        PortfolioSummaryService,
        price_repo=price_repo,
        instrument_repo=instrument_repo
    )
```

2. **Use in FastAPI** (`src/api/main.py`):
```python
from src.container import Container

container = Container()
container.config.use_bigquery.from_env("USE_BIGQUERY", default="false")

app = FastAPI()

@app.get("/api/portfolio/summary")
async def get_portfolio_summary(
    service: PortfolioSummaryService = Depends(
        lambda: container.portfolio_service()
    )
):
    return service.get_summary()
```

3. **Use in tests**:
```python
def test_portfolio_summary():
    # Override with mocks
    container = Container()
    container.price_repo.override(MockPriceRepo())
    
    service = container.portfolio_service()
    result = service.get_summary()
    
    assert result is not None
```

**Benefits**:
- [ ] Easier testing (swap real for mocks)
- [ ] Clearer dependencies
- [ ] No hard-coded instantiation
- [ ] Single configuration point

---

### 🟡 P2-2: Increase Test Coverage
**Status**: 🟡 Ongoing  
**Assignee**: All Developers  
**Target**: 70%+ overall, 90% services  
**Timeline**: Continuous

**Current Coverage** (estimated):
- Services: ~60%
- Repositories: ~40%
- API: ~30%
- Widgets: ~5%

**Target Coverage**:
- Services: 90%+
- Repositories: 80%+
- API: 70%+
- Domain models: 80%+ (maintain)

**Weekly Goals**:
- Week 4: Set up coverage tracking in CI
- Week 5: Service layer to 80%
- Week 6: Repository layer to 70%
- Week 8: API layer to 60%
- Week 10: Overall to 70%

**Tools**:
```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Fail if below threshold
pytest --cov=src --cov-fail-under=70
```

**Test Types Needed**:
1. **Unit tests** - Services, domain models (fast, no mocks)
2. **Integration tests** - Repositories with test DB
3. **Contract tests** - API endpoints (schema validation)
4. **E2E tests** - Complete user workflows

---

### 🟢 P3-1: Standardize Error Handling
**Status**: 🔴 Not Started  
**Assignee**: Backend Team  
**Deadline**: Week 9  
**Effort**: 1 week

**Task**: Consistent error handling across all layers

**Pattern**:

1. **Define domain exceptions** (`src/domain/exceptions.py`):
```python
class DomainException(Exception):
    """Base exception for all domain errors."""
    pass

class InsufficientDataError(DomainException):
    """Raised when data is insufficient for calculation."""
    pass

class InvalidParameterError(DomainException):
    """Raised when parameters fail validation."""
    pass

class OptimizationFailedError(DomainException):
    """Raised when optimization cannot converge."""
    pass
```

2. **Services raise domain exceptions**:
```python
class CorrelationService:
    def calculate(self, symbols: List[str]):
        if len(symbols) < 2:
            raise InvalidParameterError(
                "Need at least 2 symbols for correlation"
            )
        
        data = self.fetch_data(symbols)
        if len(data) < 30:
            raise InsufficientDataError(
                f"Need at least 30 data points, got {len(data)}"
            )
        
        return self._compute_correlation(data)
```

3. **API translates to HTTP**:
```python
@router.post("/correlation")
async def calculate_correlation(params: CorrelationParams):
    try:
        result = service.calculate(params.symbols)
        return result
    except InvalidParameterError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InsufficientDataError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in correlation")
        raise HTTPException(status_code=500, detail="Internal error")
```

4. **Streamlit handles gracefully**:
```python
def render(self, params):
    try:
        result = self.service.calculate(params)
        self.display_results(result)
    except InvalidParameterError as e:
        st.error(f"Invalid input: {e}")
    except InsufficientDataError as e:
        st.warning(f"Not enough data: {e}")
    except Exception as e:
        st.error("An unexpected error occurred")
        logger.exception("Error in widget")
```

**Tasks**:
- [ ] Define all domain exceptions
- [ ] Update all services to use domain exceptions
- [ ] Update API error handlers
- [ ] Update widget error handling
- [ ] Add exception documentation

---

## Phase 4: Completion (Weeks 13-20)

### 🟡 P2-3: Complete API Implementation
**Target**: 100% feature parity with Streamlit  
**Timeline**: Weeks 13-16

**Tasks**:
- [ ] Audit Streamlit features vs API endpoints
- [ ] Implement missing endpoints
- [ ] Complete authentication
- [ ] Add rate limiting
- [ ] Performance optimization
- [ ] Generate comprehensive API docs

### 🟡 P2-4: Complete Frontend Migration
**Target**: Next.js as primary interface  
**Timeline**: Weeks 17-20

**Tasks**:
- [ ] Implement all widgets in React
- [ ] Connect to all API endpoints
- [ ] Add authentication flow
- [ ] Implement responsive design
- [ ] Add E2E tests
- [ ] Performance optimization
- [ ] Deploy to production

### 🟢 P3-2: Documentation & Training
**Timeline**: Ongoing

**Deliverables**:
- [ ] Architecture decision records (ADRs)
- [ ] API documentation (Swagger)
- [ ] Developer onboarding guide
- [ ] Service layer documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide

---

## Success Metrics

### Technical Metrics

| Metric | Baseline | Target | Method |
|--------|----------|--------|--------|
| **Test Coverage** | 35% | 70%+ | pytest-cov |
| **Average Widget Size** | 500 LOC | <200 LOC | wc -l |
| **Service Coverage** | 60% | 90%+ | pytest-cov |
| **Complexity (widgets)** | 8.7 avg | <5 avg | radon cc |
| **API Response Time** | Unknown | <500ms (p95) | Load testing |
| **Build Time** | ~15 min | <5 min | CI logs |

### Milestone Metrics

| Milestone | Target Date | Completion Criteria |
|-----------|-------------|---------------------|
| **Foundation Complete** | Week 2 | Standards documented, strategy decided |
| **Repositories Done** | Week 4 | Zero direct storage calls in widgets |
| **Top 3 Widgets Refactored** | Week 8 | <200 LOC each, 80%+ test coverage |
| **DI Implemented** | Week 6 | All new code uses DI |
| **70% Test Coverage** | Week 12 | Overall coverage >70% |
| **API Complete** | Week 16 | All Streamlit features in API |
| **Frontend Complete** | Week 20 | Production-ready Next.js app |

---

## Risk Management

### Critical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Breaking existing features** | High | High | Feature flags, parallel running, regression tests |
| **Scope creep** | High | High | Strict phase gates, weekly reviews |
| **Performance issues** | Medium | Medium | Load testing, benchmarks, monitoring |
| **Team availability** | Medium | High | Clear task breakdown, documentation |
| **Data corruption** | Low | Critical | Backups, transaction safety, testing |

### Mitigation Strategies

1. **Feature Flags**: Enable/disable new architecture per feature
   ```python
   if feature_flags.use_new_architecture:
       result = new_service.calculate()
   else:
       result = legacy_widget.calculate()
   ```

2. **Parallel Running**: Keep Streamlit working during migration
3. **Comprehensive Testing**: Prevent regressions
4. **Monitoring**: Track errors and performance
5. **Rollback Plan**: Can revert if needed

---

## Weekly Checklist Template

Copy this for each week:

```markdown
## Week [N] Checklist

### Planned
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### Completed
- [x] Task A (notes)
- [x] Task B (notes)

### Blocked
- [ ] Task X (reason: waiting on Y)

### Metrics
- Test coverage: X% → Y%
- Refactored widgets: N / 5
- PRs merged: N

### Next Week
- [ ] Priority 1
- [ ] Priority 2
```

---

## Quick Start: First Week

**Day 1-2: Decision & Planning**
- [ ] Tech lead reviews full architecture review doc
- [ ] Team meeting: decide migration strategy
- [ ] Create ADR-001 documenting decision
- [ ] Set up project tracking

**Day 3-4: Standards & Cleanup**
- [ ] Write CODING_STANDARDS.md
- [ ] Team training session
- [ ] Clean up dead code
- [ ] Update PR template

**Day 5: Repository Setup**
- [ ] Audit all widget storage usage
- [ ] Create issue for each widget to refactor
- [ ] Assign owners
- [ ] Set up test coverage tracking

**Week 2: Start Execution**
- [ ] Begin repository pattern completion
- [ ] Start Widget 1 refactoring (Portfolio Summary)
- [ ] Set up DI container skeleton

---

## Appendix A: Coding Standards Template

```markdown
# ETF Analysis - Coding Standards

## 1. Architecture Layers

### Service Layer (src/services/)
- Pure business logic
- No framework dependencies
- No direct database access
- Uses repositories only
- Returns domain models

### Repository Layer (src/repositories/)
- Data access only
- Returns domain models
- No business logic
- Abstract interfaces

### Presentation Layer (src/widgets/, frontend/)
- UI code only
- Calls services for logic
- Handles user input
- Displays results

## 2. File Organization

```
src/
├── domain/           # Domain models (Pydantic)
├── services/         # Business logic
├── repositories/     # Data access
├── api/              # FastAPI routes
└── infrastructure/   # External integrations
```

## 3. Naming Conventions

- Services: `*Service` (e.g., `MonteCarloService`)
- Repositories: `*Repository` (e.g., `PriceDataRepository`)
- Domain models: `*DomainModel` or descriptive (e.g., `SimulationResults`)
- Exceptions: `*Error` (e.g., `InsufficientDataError`)

## 4. Error Handling

- Raise domain exceptions in services
- Translate to HTTP in API layer
- Display gracefully in UI
- Always log unexpected errors

## 5. Testing

- Unit test services (90%+ coverage)
- Integration test repositories
- Contract test APIs
- No tests for simple getters/setters
```

---

## Appendix B: Resources

### Documentation
- [Full Architecture Review](./ARCHITECTURE_REVIEW.md)
- [Widget Refactoring Spec](../specs/002-widget-architecture-refactor/spec.md)
- [Migration Spec](../specs/003-architecture-migration/spec.md)

### Tools
- [pytest](https://docs.pytest.org/) - Testing framework
- [dependency-injector](https://python-dependency-injector.ets-labs.org/) - DI container
- [radon](https://radon.readthedocs.io/) - Complexity analysis
- [pytest-cov](https://pytest-cov.readthedocs.io/) - Coverage reporting

### References
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)

---

**Document Version**: 1.0  
**Status**: Active  
**Next Review**: Weekly
