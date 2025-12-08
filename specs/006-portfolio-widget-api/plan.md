# Implementation Plan: Portfolio Widget API Integration

**Branch**: `006-portfolio-widget-api` | **Date**: 2025-12-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-portfolio-widget-api/spec.md`

## Summary

Expose existing portfolio analysis widgets (Portfolio Summary, Holdings Breakdown, Correlation Matrix, Monte Carlo, etc.) through REST API endpoints to enable NextJS frontend integration. This leverages the existing FastAPI infrastructure and widget calculation logic while creating JSON-serializable interfaces.

## Technical Context

**Language/Version**: Python 3.11 (confirmed via Dockerfile)  
**Primary Dependencies**: 
- Backend: FastAPI 0.104.1, uvicorn, pydantic 2.5.2, existing widget libraries (pandas, numpy, plotly, scipy, yfinance)
- Frontend: NextJS 16.0.7, React 19.2.0, TypeScript, Tailwind CSS, axios 1.13.2
- Existing widgets: Streamlit-based widget classes with calculation logic

**Storage**: SQLite (development), BigQuery/PostgreSQL (production), existing database models via SQLAlchemy 2.0.23  
**Testing**: pytest with 80% coverage requirement, httpx for API testing, pytest-asyncio  
**Target Platform**: Linux server (FastAPI backend), web browsers (NextJS frontend)  
**Project Type**: Web application (existing backend API + existing frontend app)  
**Performance Goals**: <3 seconds for basic metrics, <30 seconds for complex calculations (Monte Carlo), 99% uptime during market hours  
**Constraints**: Must maintain mathematical accuracy of existing widgets, backward compatibility with Streamlit widgets, JSON-serializable responses only  
**Scale/Scope**: 12 portfolio analysis widgets, estimated 20-30 new API endpoints, integration with existing NextJS components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check ✅
✅ **I. Data Persistence First**: No violations - feature uses existing persistent data layer and database models

✅ **II. Calculation Transparency**: No violations - feature exposes existing well-documented widget calculations through API, maintaining transparency

✅ **III. Widget Modularity**: No violations - feature leverages existing modular widget architecture, adding API layer without changing widget independence

✅ **IV. Professional UI Standards**: No violations - feature focuses on API development, NextJS frontend already follows professional standards

### Post-Design Re-evaluation ✅

✅ **I. Data Persistence First**: CONFIRMED - API adapters use existing DatabaseStorage and persistent data patterns. Widget calculations continue to rely on persisted portfolio data, price history, and transaction records.

✅ **II. Calculation Transparency**: CONFIRMED - Widget adapters preserve original calculation logic from existing widgets. API responses include calculation metadata, data quality scores, and clear error messages. Mathematical formulas remain documented in original widget classes.

✅ **III. Widget Modularity**: CONFIRMED - Widget adapter pattern maintains independence. Each adapter wraps exactly one widget type without cross-dependencies. API layer is additive and doesn't modify existing widget isolation.

✅ **IV. Professional UI Standards**: CONFIRMED - API responses follow professional REST patterns with proper HTTP status codes, structured error responses, and comprehensive OpenAPI documentation. Frontend integration maintains existing NextJS standards.

## Project Structure

### Documentation (this feature)

```text
specs/006-portfolio-widget-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - technical decisions and approach
├── data-model.md        # Phase 1 output - entities and data structures
├── quickstart.md        # Phase 1 output - developer implementation guide
├── contracts/           # Phase 1 output - API specifications
│   └── portfolio-widgets-api.yaml  # OpenAPI 3.0 specification
└── checklists/          # Quality validation
    └── requirements.md  # Specification completeness checklist
```

### Source Code (repository root)

```text
# Web application structure (existing + new additions)
src/
├── models/              # Existing SQLAlchemy models
├── services/            # Existing business logic services
├── widgets/             # Existing Streamlit widget classes (calculation source)
├── api/                 # Existing FastAPI application
│   ├── main.py          # Existing FastAPI app setup
│   ├── dependencies.py  # Existing dependency injection
│   ├── auth.py          # Existing JWT authentication
│   ├── routers/         # Existing API routers
│   └── widgets/         # NEW: Widget API adapters
│       ├── __init__.py
│       ├── base.py      # Base widget adapter class
│       ├── portfolio_summary.py    # Portfolio summary adapter
│       ├── holdings_breakdown.py   # Holdings breakdown adapter
│       ├── correlation_matrix.py   # Correlation analysis adapter
│       ├── monte_carlo.py          # Monte Carlo simulation adapter
│       └── optimization.py         # Portfolio optimization adapter
└── storage/             # Existing data access layer

frontend/v1/             # Existing NextJS application
├── src/
│   ├── components/      # Existing UI components (to be updated)
│   ├── hooks/           # Existing + NEW widget API hooks
│   │   ├── use-portfolio-summary.ts    # Existing
│   │   └── use-portfolio-widgets.ts    # NEW: Widget-specific hooks
│   ├── lib/api/         # Existing API client utilities
│   └── services/        # Existing service layer
└── tests/               # Existing frontend tests

tests/
├── unit/
│   └── api/widgets/     # NEW: Widget adapter unit tests
├── integration/         # Existing API integration tests (to be extended)
└── regression/          # Existing regression tests
```

**Structure Decision**: Extending existing web application structure by adding widget adapters to the current FastAPI backend and new hooks to the existing NextJS frontend. This leverages all existing infrastructure while maintaining clear separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
