# Architecture Visualization - Current vs Target

This document provides visual representations of the architecture concerns and target state.

---

## Current State: ⚠️ Mixed Architecture

### Problem: Three Parallel Paradigms

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT STATE (PROBLEMATIC)                   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Streamlit UI    │         │   FastAPI REST   │         │  Next.js Frontend│
│   (Legacy)       │         │      (New)       │         │    (Modern)      │
│                  │         │                  │         │                  │
│ - 15+ widgets    │         │ - 10+ endpoints  │         │ - React 19      │
│ - Monolithic     │         │ - JWT auth       │         │ - shadcn/ui     │
│ - 500+ LOC avg   │         │ - OpenAPI docs   │         │ - TypeScript    │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
         │ INCONSISTENT               │ EMERGING                   │ INCOMPLETE
         │ PATTERNS                   │ CLEAN                      │ COVERAGE
         │                            │                            │
         ▼                            ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Business Logic Layer                      │
│  ┌────────────────┐         ┌─────────────────┐                │
│  │ Widget Logic   │         │ Service Layer   │                │
│  │ (Mixed in UI)  │◄────────┤ (Framework-Free)│                │
│  │                │         │                 │                │
│  │ - 7,500+ LOC   │         │ - 2,500 LOC     │                │
│  │ - Untestable   │         │ - Testable ✓    │                │
│  │ - Hard to reuse│         │ - Reusable ✓    │                │
│  └────────┬───────┘         └────────┬────────┘                │
└───────────┼──────────────────────────┼──────────────────────────┘
            │                          │
            ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Data Access Layer                        │
│  ┌─────────────────┐         ┌──────────────────┐              │
│  │ Direct Storage  │         │  Repositories    │              │
│  │ (Anti-pattern)  │         │  (Clean ✓)       │              │
│  │                 │         │                  │              │
│  │ - 15 widgets    │         │ - 4 repos        │              │
│  │ - Tight coupling│         │ - Abstracted ✓   │              │
│  └────────┬────────┘         └────────┬─────────┘              │
└───────────┼──────────────────────────┼──────────────────────────┘
            └──────────┬───────────────┘
                       ▼
            ┌──────────────────────┐
            │   Storage Adapter    │
            │   (Adapter Pattern)  │
            └──────────┬───────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
    ┌──────────┐            ┌──────────────┐
    │  SQLite  │            │   BigQuery   │
    │  (Dev)   │            │   (Prod)     │
    └──────────┘            └──────────────┘
```

### Issues Illustrated

1. **🔴 Three UI Layers** → Confusion, duplication
2. **🔴 Business Logic Split** → Some in widgets, some in services
3. **🟡 Data Access Inconsistent** → Direct storage + repositories
4. **🟡 Testing Gaps** → Can't test widget logic without Streamlit

---

## Target State: ✅ Clean Layered Architecture

### Solution: Single Clear Path

```
┌─────────────────────────────────────────────────────────────────┐
│                    TARGET STATE (CLEAN)                          │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                             │
│  ┌────────────────┐              ┌──────────────────┐            │
│  │  Next.js UI    │              │  Mobile App      │            │
│  │  (Primary)     │              │  (Future)        │            │
│  │                │              │                  │            │
│  │ - React 19     │              │ - React Native   │            │
│  │ - shadcn/ui    │              │ - Same API       │            │
│  │ - TypeScript   │              │                  │            │
│  └────────┬───────┘              └────────┬─────────┘            │
│           │                               │                       │
│           └───────────────┬───────────────┘                       │
└───────────────────────────┼───────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ▼
                 ┌──────────────────────┐
                 │     REST API         │
                 │     (FastAPI)        │
                 │                      │
                 │ - JWT Auth          │
                 │ - Validation        │
                 │ - Rate Limiting     │
                 │ - OpenAPI Docs      │
                 └──────────┬───────────┘
                            │
                            │ Domain Models
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                              │
│                                                                   │
│               ┌────────────────────────────┐                     │
│               │    Service Layer           │                     │
│               │  (Pure Business Logic)     │                     │
│               │                            │                     │
│               │  ┌──────────────────────┐  │                     │
│               │  │ MonteCarloService    │  │                     │
│               │  │ OptimizationService  │  │                     │
│               │  │ RiskAnalysisService  │  │                     │
│               │  │ CorrelationService   │  │                     │
│               │  │ RebalancingService   │  │                     │
│               │  └──────────────────────┘  │                     │
│               │                            │                     │
│               │  ✓ Framework-agnostic      │                     │
│               │  ✓ Testable (no mocks)     │                     │
│               │  ✓ Reusable everywhere     │                     │
│               └────────────┬───────────────┘                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             │ Domain Models
                             ▼
┌───────────────────────────────────────────────────────────────────┐
│                        DOMAIN LAYER                               │
│                                                                   │
│               ┌────────────────────────────┐                     │
│               │    Domain Models           │                     │
│               │    (Pydantic)              │                     │
│               │                            │                     │
│               │  - SimulationParameters    │                     │
│               │  - SimulationResults       │                     │
│               │  - PortfolioSummary        │                     │
│               │  - OptimizationRequest     │                     │
│               │                            │                     │
│               │  ✓ Strong typing           │                     │
│               │  ✓ Validation rules        │                     │
│               │  ✓ Business rules          │                     │
│               └────────────┬───────────────┘                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             │ Domain Objects
                             ▼
┌───────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                           │
│                                                                   │
│               ┌────────────────────────────┐                     │
│               │   Repository Interfaces    │                     │
│               │                            │                     │
│               │  - InstrumentRepository    │                     │
│               │  - PriceDataRepository     │                     │
│               │  - OrderRepository         │                     │
│               │  - DividendRepository      │                     │
│               │                            │                     │
│               │  ✓ Abstract interfaces     │                     │
│               │  ✓ Swappable impls         │                     │
│               └────────────┬───────────────┘                     │
│                            │                                     │
│           ┌────────────────┴────────────────┐                   │
│           ▼                                 ▼                   │
│  ┌─────────────────┐              ┌─────────────────┐          │
│  │  SQLite Impl    │              │ BigQuery Impl   │          │
│  │  (Development)  │              │ (Production)    │          │
│  └────────┬────────┘              └────────┬────────┘          │
└───────────┼──────────────────────────────┼─────────────────────┘
            │                              │
            ▼                              ▼
      ┌──────────┐                  ┌──────────────┐
      │  SQLite  │                  │   BigQuery   │
      │   DB     │                  │   Dataset    │
      └──────────┘                  └──────────────┘
```

### Benefits Illustrated

1. **✅ Single UI** → Clear primary interface (Next.js)
2. **✅ Clean Service Layer** → All business logic in one place
3. **✅ Consistent Data Access** → Always through repositories
4. **✅ Framework Independence** → Can swap UI or DB without touching logic
5. **✅ Testable** → Each layer independently testable

---

## Widget Refactoring Example

### Before: Monolithic Widget (❌)

```
┌─────────────────────────────────────────────────────────┐
│          correlation_matrix_widget.py (500 LOC)         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  class CorrelationMatrixWidget:                         │
│                                                         │
│      def render(self, instruments, selected_symbols):   │
│                                                         │
│          ┌──────────────────────────────────────┐      │
│          │  CONCERN 1: UI Input                 │      │
│          │  - st.header()                       │      │
│          │  - st.multiselect()                  │      │
│          │  - st.date_input()                   │      │
│          │                            50 lines  │      │
│          └──────────────────────────────────────┘      │
│                                                         │
│          ┌──────────────────────────────────────┐      │
│          │  CONCERN 2: Data Fetching            │      │
│          │  - self.storage.get_price_data()     │      │
│          │  - Data cleaning                     │      │
│          │  - Validation                        │      │
│          │                           100 lines  │      │
│          └──────────────────────────────────────┘      │
│                                                         │
│          ┌──────────────────────────────────────┐      │
│          │  CONCERN 3: Business Logic           │      │
│          │  - Calculate returns                 │      │
│          │  - Compute correlation matrix        │      │
│          │  - Statistical significance tests    │      │
│          │  - Find strong correlations          │      │
│          │                           200 lines  │      │
│          └──────────────────────────────────────┘      │
│                                                         │
│          ┌──────────────────────────────────────┐      │
│          │  CONCERN 4: Visualization            │      │
│          │  - Create heatmap                    │      │
│          │  - Format chart                      │      │
│          │  - st.plotly_chart()                 │      │
│          │                           100 lines  │      │
│          └──────────────────────────────────────┘      │
│                                                         │
│          ┌──────────────────────────────────────┐      │
│          │  CONCERN 5: Additional UI            │      │
│          │  - Display table                     │      │
│          │  - Show metrics                      │      │
│          │  - Export options                    │      │
│          │                            50 lines  │      │
│          └──────────────────────────────────────┘      │
│                                                         │
└─────────────────────────────────────────────────────────┘

Problems:
❌ Cannot test business logic without Streamlit
❌ Cannot reuse in API
❌ Hard to understand flow
❌ Difficult to modify safely
❌ High complexity (cyclomatic complexity: 15+)
```

### After: Layered Widget (✅)

```
┌──────────────────────────────────────────────────────────────────┐
│                  REFACTORED ARCHITECTURE                         │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│     correlation_matrix_widget.py (150 LOC)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  class CorrelationMatrixWidget(LayeredBaseWidget):     │
│                                                         │
│      def fetch_data(self, params):                     │
│          """Get data via repository (50 LOC)"""        │
│          return self.price_repo.get_price_history(     │
│              params.symbols,                           │
│              params.start_date,                        │
│              params.end_date                           │
│          )                                             │
│                                                         │
│      def calculate(self, data):                        │
│          """Delegate to service (10 LOC)"""            │
│          return self.correlation_service.calculate(    │
│              price_data=data,                          │
│              method=params.method                      │
│          )                                             │
│                                                         │
│      def render_results(self, results):                │
│          """Display UI only (90 LOC)"""                │
│          st.header("Correlation Matrix")               │
│          self._render_heatmap(results.matrix)          │
│          self._render_table(results.significant)       │
│          self._render_metrics(results.stats)           │
│                                                         │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴────────────┐
                ▼                        ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│ correlation_service.py   │   │ price_data_repository.py │
│        (200 LOC)         │   │         (150 LOC)        │
├──────────────────────────┤   ├──────────────────────────┤
│                          │   │                          │
│ class CorrelationService:│   │ class PriceDataRepository│
│                          │   │                          │
│   def calculate(self,    │   │   def get_price_history( │
│       price_data,        │   │       symbols,           │
│       method='pearson'): │   │       start_date,        │
│                          │   │       end_date):         │
│     # Pure logic         │   │     # Data access only   │
│     # No UI              │   │     # Returns domain obj │
│     # No storage         │   │                          │
│     # Testable ✓         │   │     # Testable ✓         │
│                          │   │                          │
│     return CorrelationResults│   return PriceHistory    │
│                          │   │                          │
└──────────────────────────┘   └──────────────────────────┘

Benefits:
✅ Business logic testable without Streamlit
✅ Can reuse service in API
✅ Clear, focused responsibilities
✅ Easy to modify safely
✅ Low complexity (cyclomatic complexity: <5)
```

---

## Data Flow Comparison

### Current: Inconsistent Paths (❌)

```
Path 1: Streamlit Widget
┌──────────┐     ┌─────────────┐     ┌──────────┐
│ Widget   │────▶│ Storage     │────▶│ Database │
│ render() │     │ Adapter     │     │          │
└──────────┘     └─────────────┘     └──────────┘
   (Mixed)         (Direct call)       (SQL/BQ)

Path 2: API Endpoint (New)
┌──────────┐     ┌─────────┐     ┌────────────┐     ┌──────────┐
│ API      │────▶│ Service │────▶│ Repository │────▶│ Database │
│ Route    │     │ Layer   │     │            │     │          │
└──────────┘     └─────────┘     └────────────┘     └──────────┘
   (Clean)        (Logic)         (Data access)      (SQL/BQ)

Problem: Two different patterns for same functionality!
```

### Target: Single Path (✅)

```
ALL Requests follow same pattern:

┌──────────┐     ┌──────────┐     ┌─────────┐     ┌────────────┐     ┌──────────┐
│ UI       │────▶│ API      │────▶│ Service │────▶│ Repository │────▶│ Database │
│ (Any)    │     │ Route    │     │ Layer   │     │            │     │          │
└──────────┘     └──────────┘     └─────────┘     └────────────┘     └──────────┘
 React/Vue        FastAPI          Pure Logic      Data Access        SQL/BigQuery
 Streamlit        (HTTP/JSON)      (Testable)      (Abstracted)       (Storage)
 Mobile

Benefits:
✅ One path to understand
✅ Consistent testing approach
✅ Single source of truth
✅ Easy to debug
```

---

## Technical Debt Visualization

### Debt Accumulation Over Time

```
Technical Debt Level
    ▲
    │                                    ╱─────  Current State
    │                                 ╱──
 🔴 │                              ╱──
High│                           ╱──
    │                        ╱──
    │                     ╱──
 🟡 │                  ╱──
Med │               ╱──
    │            ╱──
    │         ╱──
 🟢 │      ╱──                          ─────── Target State
Low │───────────────────────────────────────────────────▶ Time
    │
    0    2     4     6     8    10    12    14    16    18    20 weeks
         │                                 │
         └─ Migration Started              └─ Migration Complete
```

### Debt by Component

```
Component                Current Debt    Target
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Widgets                  ████████████    ░░        (500+ LOC avg → <200)
Testing                  ██████████░░    ░░        (35% → 70%+)
Architecture             ████████░░░░    ░░        (3 paradigms → 1)
Documentation            ████░░░░░░░░    ░░        (Partial → Complete)
Code Duplication         ████████░░░░    ░░        (2 impls → 1)
Error Handling           ██████░░░░░░    ░░        (Inconsistent → Standard)

Legend: █ = Debt  ░ = Acceptable
```

---

## Migration Timeline Visualization

### 20-Week Roadmap

```
Week:   1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18   19   20
        │────│────│────│────│────│────│────│────│────│────│────│────│────│────│────│────│────│────│────│
Phase 1 │████│████│
        │         │
Phase 2 │         │████│████│████│████│████│████│████│████│
        │                                                   │
Phase 3 │                 │████│████│████│████│████│████│████│████│
        │                                                               │
Phase 4 │                                                               │████│████│████│████│████│████│████│

Legend:
████ Phase 1: Foundation (Standards, cleanup)
████ Phase 2: Refactoring (Widgets, repositories)  
████ Phase 3: Quality (Testing, DI, error handling)
████ Phase 4: Completion (API, frontend, docs)
```

### Phase Breakdown

```
┌──────────────────────────────────────────────────────────────┐
│ Phase 1: Foundation (Weeks 1-2)                              │
├──────────────────────────────────────────────────────────────┤
│ ✓ Decide migration strategy                                  │
│ ✓ Document coding standards                                  │
│ ✓ Clean up dead code                                         │
│ ✓ Set up metrics tracking                                    │
└──────────────────────────────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ Phase 2: Critical Refactoring (Weeks 3-10)                   │
├──────────────────────────────────────────────────────────────┤
│ ✓ Complete repository pattern                                │
│ ✓ Refactor top 5 widgets                                     │
│   - Portfolio Summary                                        │
│   - Correlation Matrix                                       │
│   - Monte Carlo                                              │
│   - Portfolio Optimizer                                      │
│   - Timeseries Analysis                                      │
│ ✓ Unify duplicate implementations                            │
└──────────────────────────────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ Phase 3: Quality & Infrastructure (Weeks 4-12 overlap)       │
├──────────────────────────────────────────────────────────────┤
│ ✓ Implement dependency injection                             │
│ ✓ Increase test coverage to 70%+                             │
│ ✓ Standardize error handling                                 │
│ ✓ Add monitoring and logging                                 │
└──────────────────────────────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ Phase 4: Completion (Weeks 13-20)                            │
├──────────────────────────────────────────────────────────────┤
│ ✓ Complete API implementation                                │
│ ✓ Complete frontend migration                                │
│ ✓ Documentation and training                                 │
│ ✓ Production deployment                                      │
│ ✓ Celebrate! 🎉                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Risk vs Impact Matrix

```
                    IMPACT
                    ▲
            High    │  📌 Complete          │  🔴 Breaking
                    │     Migration         │     Existing
                    │     Strategy          │     Features
                    │                       │
                    │  ────────────────────────────────
                    │                       │
            Medium  │  📋 Add Tests         │  🟡 Performance
                    │                       │     Degradation
                    │  📚 Documentation     │
                    │                       │
                    │  ────────────────────────────────
                    │                       │
            Low     │  🧹 Clean Dead        │  📊 Scope
                    │     Code              │     Creep
                    │                       │
                    └───────────────────────────────────▶
                          Low         Medium      High
                                   PROBABILITY

Legend:
🔴 High priority mitigation needed
🟡 Medium priority mitigation planned  
📌 Decision required
🧹 Quick wins
📋 Ongoing effort
```

---

## Conclusion

These visualizations demonstrate:

1. **Current State** - Multiple architectures creating confusion
2. **Target State** - Clean layered architecture with clear separation
3. **Migration Path** - Systematic refactoring over 20 weeks
4. **Expected Benefits** - Testable, maintainable, scalable codebase

**Next Step**: Review [ARCHITECTURE_ACTION_PLAN.md](./ARCHITECTURE_ACTION_PLAN.md) for detailed implementation steps.

---

**Version**: 1.0  
**Last Updated**: December 8, 2025
