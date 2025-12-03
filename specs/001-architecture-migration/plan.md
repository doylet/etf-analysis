# Implementation Plan: Framework-Agnostic Architecture Migration

**Branch**: `001-architecture-migration` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-architecture-migration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Migrate ETF analysis application from tightly-coupled Streamlit framework to a clean hexagonal architecture with framework-agnostic business logic services, REST API layer, and support for bespoke UX frontends. Extract ~10,000 lines of widget code containing portfolio calculations (Monte Carlo simulation, optimization, risk metrics, news correlation analysis) into pure service classes with strongly-typed domain models. Build FastAPI REST endpoints exposing all capabilities. Implement repository pattern for data access. Maintain backward compatibility with existing Streamlit UI during migration via compatibility layer and feature flags.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: 
- Current: Streamlit 1.39+, pandas, numpy, plotly, scipy, yfinance, SQLAlchemy, newsapi-python
- New: FastAPI, Pydantic 2.x, uvicorn, celery (for async tasks), redis (task queue), pytest, pytest-asyncio
**Storage**: SQLite (local dev), PostgreSQL/Cloud SQL (production), BigQuery (optional data warehouse)  
**Testing**: pytest with 80%+ coverage target, pytest-mock for repositories, httpx for API testing  
**Target Platform**: Linux/macOS server (API), web browser (new frontend), existing Streamlit deployment  
**Project Type**: Web application (backend API + multiple frontend options)  
**Performance Goals**: 
- API: 100 concurrent requests, <500ms p95 for summary endpoints, <30s for 10k Monte Carlo simulations
- Service layer: <5s for typical calculations (1000 simulations, 50 data points)
**Constraints**: 
- Zero downtime during migration (existing Streamlit must remain functional)
- Byte-identical results between old and new implementations (regression testing)
- No breaking changes to existing data schema during Phase 0-1
**Scale/Scope**: 
- 15 existing widgets to migrate (~10,000 lines)
- 46 functional requirements across 6 layers
- 6 prioritized user stories (3 P1, 2 P2, 2 P3)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Data Persistence First**: Architecture preserves existing database layer (SQLAlchemy models) and storage adapter pattern. No in-memory-only calculations introduced.

✅ **Calculation Transparency**: Service layer will maintain existing docstrings and unit tests. All formulas remain unchanged from current widget implementations.

✅ **Widget Modularity**: Existing widgets remain independent during migration. Compatibility layer ensures no widget-to-widget dependencies introduced.

✅ **Professional UI Standards**: 
- Phase 0-1: No UI changes (backend-only work)
- Phase 3: New frontend will follow modern component patterns
- Streamlit compatibility layer maintains existing container usage

✅ **Code Readability**: Service extraction improves readability by separating business logic from UI rendering. Type hints via Pydantic enhance clarity.

✅ **Forbidden Practices**: 
- No HEREDOCs or dynamic code generation
- No global mutable state (services use dependency injection)
- No silent failures (Pydantic validation errors, structured error responses)
- No st.divider() in new code (compatibility layer maintains existing usage)

✅ **Required Practices**:
- Type hints: Pydantic models enforce types throughout
- Docstrings: Preserve all existing documentation, add service-layer docs
- Error handling: API layer translates exceptions to HTTP codes, clear user messages

**Gates Status**: ✅ ALL PASSED - No constitution violations. Architecture improves compliance by separating concerns.

## Project Structure

### Documentation (this feature)

```text
specs/001-architecture-migration/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── simulation.yaml  # Monte Carlo API contract (OpenAPI)
│   ├── optimization.yaml # Portfolio optimization API contract
│   ├── portfolio.yaml   # Portfolio summary API contract
│   └── rebalancing.yaml # Rebalancing API contract
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Web application structure (backend + frontend)

# Backend (extending existing src/)
src/
├── domain/                     # NEW: Domain models (P1)
│   ├── __init__.py
│   ├── simulation.py          # SimulationParameters, SimulationResults
│   ├── optimization.py        # OptimizationRequest, OptimizationResults
│   ├── portfolio.py           # PortfolioSummary, InstrumentDomainModel
│   ├── rebalancing.py         # RebalancingRecommendation
│   └── news.py                # SurpriseEvent, EventNewsCorrelation
│
├── services/                   # EXTENDED: Business logic services (P1)
│   ├── __init__.py
│   ├── monte_carlo_service.py      # Extract from monte_carlo_widget.py
│   ├── optimization_service.py     # Extract from portfolio_optimizer_widget.py
│   ├── risk_analysis_service.py    # Extract performance metrics
│   ├── news_analysis_service.py    # Extract from news_event_analysis_widget.py
│   ├── rebalancing_service.py      # Extract rebalancing logic
│   ├── storage_adapter.py          # KEEP: Existing adapter
│   ├── data_fetcher.py             # KEEP: Existing fetcher
│   ├── alphavantage_client.py      # KEEP: Existing client
│   ├── bigquery_client.py          # KEEP: Existing client
│   └── yfinance_client.py          # KEEP: Existing client
│
├── repositories/               # NEW: Repository pattern (P2)
│   ├── __init__.py
│   ├── base.py                # Abstract repository interfaces
│   ├── instrument_repository.py
│   ├── order_repository.py
│   ├── price_data_repository.py
│   └── dividend_repository.py
│
├── api/                        # NEW: FastAPI application (P2)
│   ├── __init__.py
│   ├── main.py                # FastAPI app, middleware, CORS
│   ├── dependencies.py        # Dependency injection (repos, services)
│   ├── auth.py                # JWT authentication
│   ├── tasks.py               # Celery task definitions
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── simulation.py      # POST /api/simulation/monte-carlo
│   │   ├── optimization.py    # POST /api/optimization/efficient-frontier
│   │   ├── portfolio.py       # GET /api/portfolio/summary
│   │   ├── rebalancing.py     # POST /api/rebalancing/analyze
│   │   ├── instruments.py     # GET/POST /api/instruments
│   │   └── tasks.py           # GET /api/tasks/{task_id}
│   └── schemas/               # Pydantic request/response models
│       ├── __init__.py
│       ├── simulation.py
│       ├── optimization.py
│       ├── portfolio.py
│       └── common.py          # Shared schemas (pagination, errors)
│
├── compat/                     # NEW: Compatibility layer (P3)
│   ├── __init__.py
│   └── streamlit_bridge.py    # Wraps services for existing widgets
│
├── models/                     # KEEP: SQLAlchemy ORM models
│   ├── __init__.py
│   └── database.py            # Instrument, Order, PriceData, etc.
│
├── utils/                      # KEEP: Pure utility functions
│   ├── __init__.py
│   ├── performance_metrics.py # Framework-agnostic calculations
│   ├── currency_converter.py
│   ├── gcp_utils.py
│   └── symbol_validation.py
│
├── widgets/                    # EXISTING: Streamlit widgets (modify in P3)
│   ├── ... (15 existing widgets)
│   └── (Updated to use compat layer via feature flags)
│
├── controllers/                # EXISTING: Streamlit controllers (minimal changes)
│   └── ... (existing controllers)
│
└── components/                 # EXISTING: Streamlit components (no changes)
    └── ... (existing components)

# Testing structure
tests/
├── unit/                       # NEW: Service layer unit tests (P1)
│   ├── test_monte_carlo_service.py
│   ├── test_optimization_service.py
│   ├── test_risk_analysis_service.py
│   ├── test_news_analysis_service.py
│   └── test_rebalancing_service.py
│
├── integration/                # NEW: Repository & API tests (P2)
│   ├── test_repositories.py
│   ├── test_api_simulation.py
│   ├── test_api_optimization.py
│   ├── test_api_portfolio.py
│   └── test_api_auth.py
│
├── regression/                 # NEW: Backward compatibility tests (P3)
│   ├── test_widget_parity.py  # Old vs new implementation comparison
│   └── fixtures/              # Known good outputs for regression
│
└── widgets/                    # EXISTING: Widget tests (extend)
    └── ... (existing test files)

# New frontend (proof-of-concept - P3)
frontend/                       # NEW: React/Vue/Svelte frontend
├── src/
│   ├── api/                   # API client functions
│   ├── components/            # Reusable UI components
│   ├── pages/                 # Portfolio summary, holdings breakdown
│   ├── hooks/                 # Custom React hooks / composables
│   ├── stores/                # State management
│   └── utils/                 # Client-side utilities
├── tests/
│   └── ... (frontend tests)
├── package.json
└── vite.config.js / vue.config.js

# Configuration
config/
├── settings.py                # EXISTING: App configuration
└── __init__.py

# Deployment
docker-compose.yml             # NEW: Multi-service deployment
├── streamlit (existing app)
├── fastapi (new API)
├── redis (task queue)
└── postgres (database)

requirements.txt               # EXISTING: Update with new dependencies
requirements-api.txt           # NEW: API-specific requirements
requirements-dev.txt           # NEW: Development/testing requirements
```

**Structure Decision**: Extending existing single-project structure to web application architecture by adding `domain/`, `services/` (business logic), `repositories/`, and `api/` layers within current `src/` directory. This preserves existing code organization while enabling clean separation of concerns. New `frontend/` directory created as sibling to root for proof-of-concept UI. Existing Streamlit app (`pages/`, `widgets/`, `controllers/`) remains unchanged initially, updated via compatibility layer in Phase 3.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - Constitution check passed all gates. Architecture migration improves code quality by:
- Separating UI from business logic (better modularity)
- Adding type safety via Pydantic (better reliability)
- Enabling unit testing without Streamlit dependencies (better testability)
- Maintaining existing persistence and calculation transparency (constitution compliance)
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
