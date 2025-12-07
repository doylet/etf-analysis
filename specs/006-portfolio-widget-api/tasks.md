# Tasks: Portfolio Widget API Integration

**Branch**: `006-portfolio-widget-api` | **Created**: 2025-12-07  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

This task breakdown organizes work by user story to enable independent implementation and testing, following the research phase conclusions and technical architecture defined in the plan.

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Core infrastructure setup that must be completed before user story implementation

- [x] T001 Create widget adapter base infrastructure in src/api/widgets/
- [x] T002 [P] Create widget adapter base class in src/api/widgets/base.py  
- [x] T003 [P] Create widget response schemas in src/api/schemas/widgets.py
- [x] T004 [P] Create widget error handling utilities in src/api/widgets/exceptions.py
- [x] T005 Setup widget router foundation in src/api/routers/widgets.py

**Checkpoint**: Base widget infrastructure ready for specific widget implementations

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services and dependencies that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create widget registry service in src/api/services/widget_registry.py
- [ ] T007 [P] Setup widget authentication and authorization patterns
- [x] T008 [P] Create widget caching service in src/api/services/widget_cache.py  
- [x] T009 Create widget data quality service in src/api/services/data_quality.py
- [x] T010 [P] Create common widget test utilities in tests/unit/api/widgets/utils.py
- [x] T011 Setup widget integration test framework in tests/integration/widgets/
- [ ] T012 [P] Create widget performance monitoring utilities
- [x] T013 Update FastAPI main app to include widget router

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Portfolio Performance Metrics (Priority: P1)

**Goal**: Enable users to access basic portfolio performance metrics through the frontend interface  
**MVP Value**: Core portfolio metrics accessible via web interface instead of backend-only widgets

**Independent Test**: Can make API call to /widgets/portfolio/summary and see metrics displayed in frontend dashboard

### Backend Implementation for User Story 1

- [ ] T014 [P] [US1] Create portfolio summary widget adapter in src/api/widgets/portfolio_summary.py  
- [ ] T015 [US1] Create portfolio summary request/response schemas
- [ ] T016 [US1] Implement portfolio summary calculation logic adapter  
- [ ] T017 [US1] Add portfolio summary endpoint to widget router
- [ ] T018 [P] [US1] Create portfolio summary error handling for insufficient data scenarios
- [ ] T019 [P] [US1] Add portfolio summary caching logic with appropriate TTL

### Frontend Integration for User Story 1

- [ ] T020 [P] [US1] Create portfolio summary widget hook in frontend/v1/src/hooks/use-portfolio-widgets.ts
- [ ] T021 [US1] Update PortfolioSummary.tsx to use new widget API endpoint
- [ ] T022 [US1] Add loading states and error handling for widget API calls
- [ ] T023 [P] [US1] Create widget data quality indicators in UI

### Tests for User Story 1

- [ ] T024 [P] [US1] Create portfolio summary adapter unit tests
- [ ] T025 [P] [US1] Create portfolio summary integration tests  
- [ ] T026 [US1] Create portfolio summary frontend component tests
- [ ] T027 [US1] Create portfolio summary end-to-end tests

**Story Completion Criteria**: Users can see portfolio summary metrics in frontend that match backend widget calculations exactly

---

## Phase 4: User Story 2 - Analyze Portfolio Holdings Breakdown (Priority: P2)  

**Goal**: Enable users to view detailed portfolio allocation breakdowns by sector, geography, and asset class  
**Independent Test**: Can request holdings breakdown via API and see allocation charts in frontend

### Backend Implementation for User Story 2

- [ ] T028 [P] [US2] Create holdings breakdown widget adapter in src/api/widgets/holdings_breakdown.py
- [ ] T029 [US2] Create holdings breakdown request/response schemas with breakdown type enum
- [ ] T030 [US2] Implement sector allocation calculation adapter
- [ ] T031 [P] [US2] Implement geography allocation calculation adapter  
- [ ] T032 [P] [US2] Implement asset class allocation calculation adapter
- [ ] T033 [US2] Add holdings breakdown endpoint with POST method for parameters
- [ ] T034 [US2] Implement concentration risk analysis and warnings
- [ ] T035 [P] [US2] Add diversification score calculation

### Frontend Integration for User Story 2

- [ ] T036 [P] [US2] Create holdings breakdown component in frontend/v1/src/components/HoldingsBreakdown.tsx
- [ ] T037 [US2] Create holdings breakdown widget hook for API integration
- [ ] T038 [US2] Add allocation chart visualization using Recharts
- [ ] T039 [P] [US2] Add breakdown type selector (sector/geography/asset class)
- [ ] T040 [US2] Add concentration risk warnings in UI
- [ ] T041 [P] [US2] Add diversification score display

### Tests for User Story 2

- [ ] T042 [P] [US2] Create holdings breakdown adapter unit tests  
- [ ] T043 [P] [US2] Create holdings breakdown calculation accuracy tests
- [ ] T044 [US2] Create holdings breakdown integration tests
- [ ] T045 [US2] Create holdings breakdown frontend component tests

**Story Completion Criteria**: Users can view portfolio allocation breakdowns with accurate percentages and risk warnings

---

## Phase 5: User Story 3 - Access Advanced Portfolio Analytics (Priority: P3)

**Goal**: Enable sophisticated investors to run correlation analysis, Monte Carlo simulations, and optimization  
**Independent Test**: Can run one advanced widget (correlation matrix) through web interface with accurate results

### Advanced Analytics Backend for User Story 3

- [ ] T046 [P] [US3] Create correlation matrix widget adapter in src/api/widgets/correlation_matrix.py
- [ ] T047 [US3] Create correlation matrix request/response schemas  
- [ ] T048 [US3] Implement correlation calculation logic adapter
- [ ] T049 [P] [US3] Add correlation matrix endpoint with configurable parameters
- [ ] T050 [US3] Create Monte Carlo simulation widget adapter in src/api/widgets/monte_carlo.py
- [ ] T051 [US3] Create Monte Carlo request/response schemas with async support
- [ ] T052 [US3] Implement Monte Carlo simulation logic adapter
- [ ] T053 [P] [US3] Add Monte Carlo endpoint with async task support via Celery
- [ ] T054 [US3] Create portfolio optimization widget adapter in src/api/widgets/optimization.py
- [ ] T055 [US3] Create optimization request/response schemas
- [ ] T056 [US3] Implement optimization calculation logic adapter  
- [ ] T057 [P] [US3] Add portfolio optimization endpoint

### Advanced Analytics Frontend for User Story 3

- [ ] T058 [P] [US3] Create correlation matrix component in frontend/v1/src/components/CorrelationMatrix.tsx
- [ ] T059 [US3] Create correlation matrix visualization using heatmap charts
- [ ] T060 [US3] Create Monte Carlo simulation component with progress tracking
- [ ] T061 [P] [US3] Add async task status polling for long-running simulations
- [ ] T062 [US3] Create Monte Carlo results visualization with probability distributions
- [ ] T063 [P] [US3] Create portfolio optimization component  
- [ ] T064 [US3] Add efficient frontier visualization

### Tests for User Story 3

- [ ] T065 [P] [US3] Create correlation matrix adapter unit tests
- [ ] T066 [P] [US3] Create Monte Carlo simulation adapter unit tests
- [ ] T067 [P] [US3] Create portfolio optimization adapter unit tests  
- [ ] T068 [US3] Create advanced analytics integration tests
- [ ] T069 [US3] Create advanced analytics frontend component tests

**Story Completion Criteria**: Sophisticated users can run advanced analytics with results matching backend widget accuracy

---

## Phase 6: User Story 4 - Configure Analysis Parameters (Priority: P3)

**Goal**: Enable users to customize analysis parameters for tailored investment analysis  
**Independent Test**: Can modify analysis parameters and see results change appropriately

### Parameter Configuration for User Story 4

- [ ] T070 [P] [US4] Create parameter configuration service in src/api/services/widget_parameters.py
- [ ] T071 [US4] Add parameter validation and constraint checking
- [ ] T072 [US4] Create user parameter persistence in database
- [ ] T073 [P] [US4] Add parameter configuration endpoints
- [ ] T074 [US4] Update all widget adapters to accept custom parameters

### Parameter Configuration Frontend for User Story 4

- [ ] T075 [P] [US4] Create parameter configuration component in frontend/v1/src/components/WidgetParameters.tsx  
- [ ] T076 [US4] Add parameter forms for time periods, benchmarks, and risk settings
- [ ] T077 [US4] Create parameter preset management (save/load configurations)
- [ ] T078 [P] [US4] Add parameter validation feedback in UI
- [ ] T079 [US4] Update all widget components to use configured parameters

### Tests for User Story 4

- [ ] T080 [P] [US4] Create parameter configuration service unit tests
- [ ] T081 [P] [US4] Create parameter validation tests  
- [ ] T082 [US4] Create parameter configuration integration tests
- [ ] T083 [US4] Create parameter configuration frontend tests

**Story Completion Criteria**: Users can customize analysis parameters and see consistent results across all widgets

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, monitoring, and production readiness

### Performance & Monitoring

- [ ] T084 [P] Implement comprehensive widget caching strategy with Redis
- [ ] T085 [P] Add widget calculation performance monitoring and alerting
- [ ] T086 [P] Add widget usage analytics and metrics collection  
- [ ] T087 Optimize database queries for widget data access patterns
- [ ] T088 [P] Implement rate limiting for computationally expensive widgets

### Error Handling & Resilience

- [ ] T089 [P] Create comprehensive widget error handling and recovery patterns
- [ ] T090 [P] Add graceful degradation for missing or stale data
- [ ] T091 Add widget health checks and monitoring endpoints
- [ ] T092 [P] Implement circuit breaker patterns for external data dependencies

### Documentation & Deployment

- [ ] T093 [P] Create widget API documentation with interactive examples
- [ ] T094 [P] Create widget integration guide for future widgets
- [ ] T095 Update OpenAPI specifications with all implemented endpoints  
- [ ] T096 [P] Create widget deployment checklist and runbook
- [ ] T097 Add widget API versioning strategy

**Phase Completion Criteria**: Widget API is production-ready with monitoring, documentation, and resilience patterns

---

## Dependencies & Execution Order

### Critical Path (for fastest MVP)

1. **Setup (Phase 1)** → 2. **Foundational (Phase 2)** → 3. **User Story 1** → **MVP Ready**

### User Story Dependencies  

- **US1 (Performance Metrics)**: Foundation only - can start immediately after Phase 2
- **US2 (Holdings Breakdown)**: Foundation only - can run in parallel with US1 after Phase 2  
- **US3 (Advanced Analytics)**: Foundation only - can run in parallel with US1 & US2
- **US4 (Parameter Config)**: Requires US1, US2, US3 widgets to exist (extends their functionality)

### Parallel Execution Opportunities

**After Phase 2 completion**:
- Tasks T014-T027 (US1 Backend & Frontend) can run in parallel
- Tasks T028-T045 (US2 Backend & Frontend) can run in parallel  
- Tasks T046-T069 (US3 Backend & Frontend) can run in parallel

**Within each User Story**:  
- Backend tasks (adapters, schemas, endpoints) can run in parallel with [P] markers
- Frontend tasks (components, hooks, visualization) can run in parallel with [P] markers
- Test tasks can run in parallel with implementation tasks

### Implementation Strategy

**MVP Scope (Minimum Viable Product)**:
- Phase 1: Setup (T001-T005)
- Phase 2: Foundational (T006-T013)  
- User Story 1: Portfolio Performance Metrics (T014-T027)
- Result: Basic portfolio metrics accessible via web interface

**Full Feature Scope**:
- MVP + User Stories 2, 3, 4 + Polish phase
- Result: Complete portfolio widget API with advanced analytics and customization

### Estimated Timeline

- **MVP (US1 only)**: ~2-3 weeks (27 tasks)
- **Full Feature**: ~6-8 weeks (97 tasks)  
- **Parallel Development**: Can reduce timeline by ~40% with proper team coordination

### Risk Mitigation

- **Widget Calculation Accuracy**: Compare API outputs with original widget outputs in tests (T024-T027, T042-T045, T065-T069)
- **Performance Issues**: Implement caching and monitoring early (T008, T012, T084-T085)
- **Data Quality**: Include data quality service from Phase 2 (T009)
- **User Experience**: Implement proper loading/error states (T022, T038, T061)

### Quality Gates

- **Phase 2 Completion**: All foundation services tested and documented
- **Each User Story**: Independent test criteria met, frontend integration working
- **Final Phase**: Performance benchmarks met, documentation complete, production deployment ready