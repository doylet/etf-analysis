# Tasks: Framework-Agnostic Architecture Migration

**Input**: Design documents from `/specs/003-architecture-migration/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Tests**: Tests are included as this is a major refactoring requiring validation at each step.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create new directory structure: `src/domain/`, `src/repositories/`, `src/api/`, `src/compat/`, `tests/unit/`, `tests/integration/`, `tests/regression/`
- [X] T002 Install new dependencies: `pip install fastapi uvicorn pydantic celery redis pytest-asyncio httpx`
- [X] T003 [P] Create `requirements-api.txt` with FastAPI stack dependencies
- [X] T004 [P] Create `requirements-dev.txt` with testing dependencies (pytest-mock, httpx, pytest-asyncio)
- [X] T005 [P] Setup pytest configuration in `pytest.ini` with coverage thresholds (80%+)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create abstract repository base classes in `src/repositories/base.py` with common CRUD interfaces
- [X] T007 [P] Create domain model base class in `src/domain/__init__.py` with JSON serialization helpers
- [X] T008 [P] Setup FastAPI application skeleton in `src/api/main.py` with CORS, middleware, basic health endpoint
- [X] T009 Create dependency injection container in `src/api/dependencies.py` for repositories and services
- [X] T010 Setup JWT authentication utilities in `src/api/auth.py` (token generation, validation, password hashing)
- [X] T011 [P] Create Celery application and task queue configuration in `src/api/tasks.py`
- [X] T012 [P] Create common API response schemas in `src/api/schemas/common.py` (ErrorResponse, PaginatedResponse, TaskStatusResponse)
- [X] T013 Create Docker Compose configuration for local development (FastAPI, Redis, PostgreSQL)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Business Logic Extraction (Priority: P1) 🎯 MVP Foundation

**Goal**: Extract all portfolio analysis calculations into framework-agnostic service classes with domain models

**Independent Test**: Can instantiate services in pure Python script, call methods with dataclass parameters, receive structured results - NO Streamlit imports

### Domain Models for User Story 1

- [X] T014 [P] [US1] Create `SimulationParameters` Pydantic model in `src/domain/simulation.py` with validation (symbols list, weights array summing to 1.0, years ≥1, num_simulations ≥100, initial_value >0, contribution settings, rebalancing settings)
- [X] T015 [P] [US1] Create `SimulationResults` Pydantic model in `src/domain/simulation.py` (paths array, time_points, percentiles dict, final_values, risk metrics: var_95, cvar_95, max_drawdown_median, cagr_*, historical_sharpe, historical_volatility)
- [X] T016 [P] [US1] Create `OptimizationRequest` Pydantic model in `src/domain/optimization.py` (symbols, objective enum, constraints dict, time_period)
- [X] T017 [P] [US1] Create `OptimizationResults` Pydantic model in `src/domain/optimization.py` (optimal_weights dict, expected_return, volatility, sharpe_ratio, efficient_frontier list of points)
- [X] T018 [P] [US1] Create `RebalancingRecommendation` Pydantic model in `src/domain/rebalancing.py` (rebalance_dates, drift_at_rebalance, trigger_threshold, avg_drift, cost_benefit_ratio, sharpe_improvement, instruments_to_rebalance)
- [X] T019 [P] [US1] Create `SurpriseEvent` and `EventNewsCorrelation` models in `src/domain/news.py` (date, event_type, magnitude, statistical_significance, correlated_news)

### Service Extraction for User Story 1

- [X] T020 [US1] Extract `MonteCarloService` from `src/widgets/monte_carlo_widget.py` into `src/services/monte_carlo_service.py`
  - Extract `_run_monte_carlo()` static method (lines ~1093-1263)
  - Method signature: `run_simulation(params: SimulationParameters, returns_df: pd.DataFrame) -> SimulationResults`
  - Preserve all GBM simulation logic, contribution handling, percentile calculations
  - Remove ALL Streamlit dependencies
- [X] T021 [US1] Extract `RebalancingService` from `src/widgets/monte_carlo_widget.py` into `src/services/rebalancing_service.py`
  - Extract `_analyze_rebalancing_timing()` static method (lines ~1297-1474)
  - Method signature: `analyze_timing(params: RebalancingRequest, returns_df: pd.DataFrame) -> RebalancingRecommendation`
  - Preserve drift analysis, cost-benefit calculations
- [X] T022 [US1] Extract `OptimizationService` from `src/widgets/portfolio_optimizer_widget.py` into `src/services/optimization_service.py`
  - Extract `_calculate_optimal_weights()` method
  - Methods: `maximize_sharpe()`, `minimize_volatility()`, `efficient_frontier()`, `constrained_optimization()`
  - Use `OptimizationRequest` and `OptimizationResults` models
- [X] T023 [US1] Create `RiskAnalysisService` in `src/services/risk_analysis_service.py` wrapping `src/utils/performance_metrics.py`
  - Methods: `calculate_sharpe()`, `calculate_sortino()`, `calculate_var()`, `calculate_cvar()`, `calculate_max_drawdown()`, `calculate_beta()`
  - Accept DataFrames or numpy arrays, return structured results
- [X] T024 [US1] Extract `NewsAnalysisService` from `src/widgets/news_event_analysis_widget.py` into `src/services/news_analysis_service.py`
  - Extract event detection logic (volatility spikes, unusual returns, correlation breaks, portfolio shocks)
  - Method signature: `detect_surprise_events(price_data: pd.DataFrame, threshold: float) -> List[SurpriseEvent]`
  - Method signature: `correlate_with_news(events: List[SurpriseEvent], news_data: List[Dict]) -> List[EventNewsCorrelation]`

### Tests for User Story 1

- [ ] T025 [P] [US1] Unit test `MonteCarloService.run_simulation()` in `tests/unit/test_monte_carlo_service.py`
  - Test with synthetic returns data (3 symbols, 252 days)
  - Verify SimulationResults structure, percentiles in order, paths shape correct
  - Test validation: negative years, weights not summing to 1.0
  - Mock storage adapter if needed
  - Target: 80%+ coverage
- [ ] T026 [P] [US1] Unit test `RebalancingService.analyze_timing()` in `tests/unit/test_rebalancing_service.py`
  - Test drift detection with known asset price paths
  - Verify rebalance dates identified correctly
  - Test max_rebalances_per_year constraint
- [ ] T027 [P] [US1] Unit test `OptimizationService` in `tests/unit/test_optimization_service.py`
  - Test max Sharpe, min volatility, efficient frontier
  - Verify weights sum to 1.0, constraints respected
  - Test with 5 symbols, 2 years of synthetic data
- [ ] T028 [P] [US1] Unit test `RiskAnalysisService` in `tests/unit/test_risk_analysis_service.py`
  - Test each risk metric function with known returns
  - Verify calculations match expected values (known Sharpe, VaR, etc.)
- [ ] T029 [P] [US1] Unit test `NewsAnalysisService` in `tests/unit/test_news_analysis_service.py`
  - Test event detection with synthetic volatility spike
  - Test correlation scoring with mock news data

**Checkpoint**: All services can be imported and called without Streamlit. Unit tests pass with 80%+ coverage.

---

## Phase 4: User Story 3 - Domain Model Definition (Priority: P1)

**Goal**: Complete remaining domain models for API layer

**Independent Test**: Can instantiate all models with valid data, models validate correctly, models serialize to/from JSON

### Domain Models for User Story 3

- [X] T030 [P] [US3] Create `PortfolioSummary` Pydantic model in `src/domain/portfolio.py` (total_value, base_currency, holdings list, performance metrics: mwr, twr, irr, sharpe, sortino, volatility, max_drawdown, dividend_yield)
- [X] T031 [P] [US3] Create `InstrumentDomainModel` in `src/domain/portfolio.py` (symbol, name, type enum, sector, currency, quantity, current_value_local, current_value_base, weight_pct)
- [X] T032 [P] [US3] Create `OrderRecord` model in `src/domain/portfolio.py` (symbol, order_type enum, volume, order_date, price, notes)
- [X] T033 [P] [US3] Create `PriceHistory` model in `src/domain/portfolio.py` (symbol, start_date, end_date, prices DataFrame/dict, dividends list)

### Tests for User Story 3

- [X] T034 [P] [US3] Unit test domain models validation in `tests/unit/test_domain_models.py`
  - Test valid `SimulationParameters` creation
  - Test invalid parameters raise ValidationError (negative years, weights sum ≠ 1.0, missing required fields)
  - Test `PortfolioSummary` JSON serialization/deserialization
  - Test all domain models can round-trip through JSON
  - Test enum validation for order types, instrument types

**Checkpoint**: All domain models defined, validated, and JSON-serializable

---

## Phase 5: User Story 4 - Repository Pattern Implementation (Priority: P2)

**Goal**: Create repository interfaces abstracting database operations with domain-focused APIs

**Independent Test**: Can interact with repositories through clean methods, repositories return domain models, can mock repositories for service testing

### Repository Implementation for User Story 4

- [ ] T035 [US4] Implement `InstrumentRepository` in `src/repositories/instrument_repository.py`
  - Methods: `find_by_symbol(symbol: str) -> Optional[InstrumentDomainModel]`
  - Methods: `find_all_active() -> List[InstrumentDomainModel]`
  - Methods: `search(query: str) -> List[InstrumentDomainModel]`
  - Methods: `add(instrument: InstrumentDomainModel) -> InstrumentDomainModel`
  - Methods: `update(symbol: str, updates: Dict) -> InstrumentDomainModel`
  - Methods: `remove(symbol: str) -> bool`
  - Use existing `DataStorageAdapter` as underlying storage
- [ ] T036 [US4] Implement `OrderRepository` in `src/repositories/order_repository.py`
  - Methods: `create(order: OrderRecord) -> OrderRecord`
  - Methods: `find_by_symbol(symbol: str) -> List[OrderRecord]`
  - Methods: `find_in_date_range(start: datetime, end: datetime) -> List[OrderRecord]`
  - Methods: `calculate_holdings_at_date(date: datetime) -> Dict[str, float]`
  - Wrap storage adapter, return domain models
- [ ] T037 [US4] Implement `PriceDataRepository` in `src/repositories/price_data_repository.py`
  - Methods: `get_price_history(symbol: str, start: datetime, end: datetime) -> PriceHistory`
  - Methods: `get_latest_prices(symbols: List[str]) -> Dict[str, float]`
  - Methods: `get_returns(symbol: str, start: datetime, end: datetime) -> pd.Series`
  - Methods: `store_prices(symbol: str, prices: pd.DataFrame) -> bool`
  - Wrap storage adapter's `get_price_data()` method
- [ ] T038 [US4] Implement `DividendRepository` in `src/repositories/dividend_repository.py`
  - Methods: `get_dividends(symbol: str, start: datetime, end: datetime) -> List[Dict]`
  - Methods: `get_cash_flows(symbol: str) -> pd.DataFrame`
  - Methods: `calculate_yield(symbol: str) -> float`
  - Wrap storage adapter's dividend methods
- [ ] T039 [US4] Update `src/services/` to accept repositories via dependency injection
  - Modify services to accept repository interfaces as constructor parameters
  - Services should use repositories instead of direct storage adapter calls

### Tests for User Story 4

- [ ] T040 [P] [US4] Integration test `InstrumentRepository` in `tests/integration/test_repositories.py`
  - Test CRUD operations with real SQLite database
  - Verify domain models returned correctly
  - Test search functionality
- [ ] T041 [P] [US4] Integration test `OrderRepository` in `tests/integration/test_repositories.py`
  - Test order creation and retrieval
  - Test holdings calculation at specific dates
- [ ] T042 [P] [US4] Integration test `PriceDataRepository` in `tests/integration/test_repositories.py`
  - Test price history retrieval
  - Test returns calculation
- [ ] T043 [P] [US4] Unit test service layer with mocked repositories in `tests/unit/test_services_with_repos.py`
  - Mock InstrumentRepository for OptimizationService
  - Verify services work without real database
  - Ensure dependency injection pattern works

**Checkpoint**: Repositories provide clean domain-focused data access. Services work with repositories. Can test services with mocked repos.

---

## Phase 6: User Story 2 - REST API Implementation (Priority: P2)

**Goal**: Build FastAPI endpoints exposing all portfolio analysis capabilities

**Independent Test**: Can make HTTP requests to endpoints with curl/Postman, receive JSON responses, test with httpx without UI

### API Schemas for User Story 2

- [ ] T044 [P] [US2] Create request/response schemas in `src/api/schemas/simulation.py`
  - `SimulationRequest` (wraps `SimulationParameters`)
  - `SimulationResponse` (wraps `SimulationResults`)
  - `TaskStatusResponse` (for async simulation tracking)
- [ ] T045 [P] [US2] Create request/response schemas in `src/api/schemas/optimization.py`
  - `OptimizationRequest` schema
  - `OptimizationResponse` schema
  - `EfficientFrontierResponse` schema
- [ ] T046 [P] [US2] Create request/response schemas in `src/api/schemas/portfolio.py`
  - `PortfolioSummaryResponse` (wraps `PortfolioSummary`)
  - `InstrumentListResponse` (paginated)
  - `InstrumentCreateRequest`, `InstrumentUpdateRequest`
- [ ] T047 [P] [US2] Create request/response schemas in `src/api/schemas/rebalancing.py`
  - `RebalancingRequest` schema
  - `RebalancingResponse` (wraps `RebalancingRecommendation`)

### API Routers for User Story 2

- [ ] T048 [US2] Implement simulation router in `src/api/routers/simulation.py`
  - `POST /api/simulation/monte-carlo` - Accepts SimulationRequest, returns SimulationResponse or TaskStatusResponse for long-running sims
  - Use `MonteCarloService` from dependency injection
  - For >1000 simulations, queue Celery task and return task ID
  - Include OpenAPI documentation with examples
- [ ] T049 [US2] Implement optimization router in `src/api/routers/optimization.py`
  - `POST /api/optimization/max-sharpe` - Returns optimal weights for max Sharpe
  - `POST /api/optimization/min-volatility` - Returns optimal weights for min volatility
  - `POST /api/optimization/efficient-frontier` - Returns list of frontier points
  - Use `OptimizationService` from dependency injection
- [ ] T050 [US2] Implement portfolio router in `src/api/routers/portfolio.py`
  - `GET /api/portfolio/summary` - Returns PortfolioSummaryResponse with current holdings and performance
  - `GET /api/portfolio/holdings` - Returns list of holdings with values and weights
  - Use repositories from dependency injection
- [ ] T051 [US2] Implement instruments router in `src/api/routers/instruments.py`
  - `GET /api/instruments` - Returns paginated list of tracked instruments
  - `GET /api/instruments/{symbol}` - Returns single instrument details
  - `POST /api/instruments` - Add new tracked instrument
  - `PATCH /api/instruments/{symbol}` - Update instrument details
  - `DELETE /api/instruments/{symbol}` - Remove instrument
  - Use `InstrumentRepository` from dependency injection
- [ ] T052 [US2] Implement rebalancing router in `src/api/routers/rebalancing.py`
  - `POST /api/rebalancing/analyze` - Accepts drift threshold, returns RebalancingRecommendation
  - Use `RebalancingService` from dependency injection
- [ ] T053 [US2] Implement tasks router in `src/api/routers/tasks.py`
  - `GET /api/tasks/{task_id}` - Returns task status (pending/running/completed/failed)
  - `GET /api/tasks/{task_id}/result` - Returns task result if completed
  - Query Celery task status

### API Infrastructure for User Story 2

- [ ] T054 [US2] Implement JWT authentication endpoints in `src/api/auth.py`
  - `POST /api/auth/login` - Accepts credentials, returns JWT token
  - `POST /api/auth/refresh` - Refreshes expired token
  - Create authentication dependency for protecting routes
- [ ] T055 [US2] Add authentication to protected routes
  - Apply `Depends(get_current_user)` to all endpoints except `/docs`, `/health`, `/auth/*`
  - Return 401 Unauthorized for invalid/missing tokens
- [ ] T056 [US2] Implement Celery task for long-running Monte Carlo simulations
  - Task definition in `src/api/tasks.py`
  - Accepts SimulationParameters, runs MonteCarloService, stores result
  - Updates task progress for status endpoint
- [ ] T057 [US2] Configure API error handling and validation
  - 422 Unprocessable Entity for Pydantic validation errors
  - 400 Bad Request for business logic errors (insufficient data, invalid constraints)
  - 404 Not Found for missing resources
  - 500 Internal Server Error with logging for unexpected errors
- [ ] T058 [US2] Wire up routers in `src/api/main.py`
  - Include all routers with `/api` prefix
  - Configure CORS for frontend origin
  - Add request logging middleware

### Tests for User Story 2

- [ ] T059 [P] [US2] API integration test for simulation endpoint in `tests/integration/test_api_simulation.py`
  - Test `POST /api/simulation/monte-carlo` with valid parameters
  - Verify 200 response with SimulationResults
  - Test async task creation for large simulations (>5000 iterations)
  - Test task status polling with `GET /api/tasks/{task_id}`
  - Use httpx.AsyncClient for testing
- [ ] T060 [P] [US2] API integration test for optimization endpoints in `tests/integration/test_api_optimization.py`
  - Test max Sharpe, min volatility, efficient frontier endpoints
  - Verify optimal weights returned
  - Test with 5 symbols
- [ ] T061 [P] [US2] API integration test for portfolio endpoints in `tests/integration/test_api_portfolio.py`
  - Test `GET /api/portfolio/summary`
  - Test `GET /api/portfolio/holdings`
  - Verify PortfolioSummary structure
- [ ] T062 [P] [US2] API integration test for instruments CRUD in `tests/integration/test_api_instruments.py`
  - Test GET, POST, PATCH, DELETE for instruments
  - Test pagination on list endpoint
  - Test search functionality
- [ ] T063 [P] [US2] API authentication tests in `tests/integration/test_api_auth.py`
  - Test login with valid credentials returns JWT
  - Test protected endpoints reject missing/invalid tokens (401)
  - Test token refresh
  - Test expired token handling
- [ ] T064 [P] [US2] API validation tests in `tests/integration/test_api_validation.py`
  - Test 422 responses for invalid request bodies
  - Test clear validation error messages (negative years, invalid symbols, weights sum ≠ 1.0)

**Checkpoint**: API fully functional, documented at `/docs`, all endpoints tested, authentication working

---

## Phase 7: User Story 5 - Backward Compatibility Layer (Priority: P3)

**Goal**: Maintain existing Streamlit UI functionality while using new service layer under the hood

**Independent Test**: Run Streamlit app, all widgets function identically to pre-migration, new services used internally

### Compatibility Bridge for User Story 5

- [ ] T065 [US5] Create `StreamlitServiceBridge` in `src/compat/streamlit_bridge.py`
  - Wrapper class that translates between widget dict-based parameters and domain model dataclasses
  - Methods mirroring existing widget `_run_*` static methods
  - Example: `run_monte_carlo_compat(params: Dict) -> Dict` wraps `MonteCarloService.run_simulation()`
  - Converts SimulationResults back to dict for existing widget consumption
- [ ] T066 [US5] Add feature flag system in `config/settings.py`
  - `USE_NEW_SERVICE_LAYER` boolean flag (default: False for safety)
  - Environment variable override: `ETF_USE_NEW_SERVICES=true`
- [ ] T067 [US5] Update `MonteCarloWidget` in `src/widgets/monte_carlo_widget.py`
  - Add conditional import of `StreamlitServiceBridge`
  - If `USE_NEW_SERVICE_LAYER=True`, call bridge methods instead of local `_run_monte_carlo()`
  - Preserve exact same UI rendering logic
  - Test both code paths produce identical results
- [ ] T068 [US5] Update `PortfolioOptimizerWidget` in `src/widgets/portfolio_optimizer_widget.py`
  - Add feature flag check
  - Use `OptimizationService` via bridge when flag enabled
  - Preserve all UI elements unchanged
- [ ] T069 [US5] Update `NewsEventAnalysisWidget` in `src/widgets/news_event_analysis_widget.py`
  - Add feature flag check
  - Use `NewsAnalysisService` via bridge when flag enabled
  - Preserve event detection UI and correlation displays

### Tests for User Story 5

- [ ] T070 [P] [US5] Regression test for Monte Carlo widget in `tests/regression/test_widget_parity.py`
  - Run widget with `USE_NEW_SERVICE_LAYER=False` (old implementation)
  - Run widget with `USE_NEW_SERVICE_LAYER=True` (new service layer)
  - Compare outputs: percentiles, final values, risk metrics
  - Assert byte-identical results (or within floating-point tolerance)
  - Save known-good outputs in `tests/regression/fixtures/monte_carlo_baseline.json`
- [ ] T071 [P] [US5] Regression test for Optimization widget in `tests/regression/test_widget_parity.py`
  - Compare old vs new optimal weights for max Sharpe
  - Compare efficient frontier points
  - Assert identical results
- [ ] T072 [P] [US5] Regression test for all 15 widgets in `tests/regression/test_all_widgets.py`
  - Automated test loading each widget
  - Verify no import errors when flag toggled
  - Verify UI renders without errors (using Streamlit testing utilities if available)
- [ ] T073 [US5] End-to-end Streamlit app test with compatibility layer
  - Launch Streamlit app with `USE_NEW_SERVICE_LAYER=True`
  - Manually test 5 core widgets: Portfolio Summary, Holdings Breakdown, Monte Carlo, Optimizer, News Analysis
  - Verify all features work identically
  - Document any UI differences (should be zero)

**Checkpoint**: Existing Streamlit app works with new service layer. Feature flag allows safe rollback. Regression tests pass.

---

## Phase 8: User Story 6 - New Frontend Foundation (Priority: P3)

**Goal**: Proof-of-concept new frontend demonstrating 2-3 widgets connected to REST API

**Independent Test**: Open new frontend in browser, authenticate, view portfolio summary and holdings, see real data from API

### Frontend Setup for User Story 6

- [ ] T074 [US6] Initialize React/Vue/Svelte frontend project in `frontend/`
  - Run `npm create vite@latest frontend -- --template react-ts` (or Vue/Svelte equivalent)
  - Install dependencies: axios/fetch, chart.js/recharts for visualizations, react-router-dom
  - Configure `vite.config.js` with API proxy to `localhost:8000/api`
- [ ] T075 [P] [US6] Create API client utilities in `frontend/src/api/client.ts`
  - Axios/fetch wrapper with base URL configuration
  - JWT token storage in localStorage
  - Request interceptor to add Authorization header
  - Response interceptor for error handling (401 → redirect to login)
- [ ] T076 [P] [US6] Create authentication service in `frontend/src/api/auth.ts`
  - `login(username, password)` - Call `POST /api/auth/login`
  - `logout()` - Clear token
  - `isAuthenticated()` - Check token existence
  - `getToken()` - Retrieve token from storage

### Frontend Components for User Story 6

- [ ] T077 [US6] Implement Login page in `frontend/src/pages/Login.tsx`
  - Username/password form
  - Call auth service on submit
  - Store JWT token on success
  - Redirect to dashboard
  - Display error messages for failed login
- [ ] T078 [US6] Implement Portfolio Summary widget in `frontend/src/components/PortfolioSummary.tsx`
  - Call `GET /api/portfolio/summary` on mount
  - Display total value, MWR, TWR, IRR, Sharpe ratio, volatility, max drawdown
  - Show loading spinner while fetching
  - Handle errors gracefully (display error message)
- [ ] T079 [US6] Implement Holdings Breakdown widget in `frontend/src/components/HoldingsBreakdown.tsx`
  - Call `GET /api/portfolio/holdings` on mount
  - Display instrument allocation table (symbol, name, quantity, value, weight %)
  - Render pie chart of allocation using chart library
  - Match Streamlit widget visual style
- [ ] T080 [US6] Create Dashboard layout in `frontend/src/pages/Dashboard.tsx`
  - Protected route requiring authentication
  - Grid layout with PortfolioSummary and HoldingsBreakdown widgets
  - Navigation header with logout button
- [ ] T081 [US6] Setup routing in `frontend/src/App.tsx`
  - Routes: `/login`, `/dashboard`
  - Protected route wrapper redirecting unauthenticated users to login
  - Default redirect `/` → `/dashboard` if authenticated, else `/login`

### Tests for User Story 6

- [ ] T082 [P] [US6] Frontend integration test in `frontend/tests/integration/portfolio.test.ts`
  - Test PortfolioSummary component fetches data from API
  - Mock API responses with sample PortfolioSummary JSON
  - Verify component renders values correctly
  - Test error handling (API returns 500)
- [ ] T083 [P] [US6] Frontend integration test for authentication in `frontend/tests/integration/auth.test.ts`
  - Test Login component calls auth API
  - Test successful login stores token and redirects
  - Test protected route redirects unauthenticated users
- [ ] T084 [US6] End-to-end validation: new frontend + API
  - Start FastAPI server: `uvicorn src.api.main:app --reload`
  - Start frontend dev server: `npm run dev`
  - Login via new frontend
  - Verify portfolio summary displays correct data
  - Verify holdings breakdown matches Streamlit version
  - Compare side-by-side: new frontend vs Streamlit showing identical data

**Checkpoint**: New frontend proof-of-concept working. Demonstrates full migration feasibility. API consumption validated.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Baseline Measurement (Required for SC-010, SC-011 validation)

- [ ] T085 Measure baseline Streamlit widget performance in `tests/regression/fixtures/baseline_performance.json`
  - Run 10 representative operations per widget (Monte Carlo 1000 sims, optimization 5 symbols, portfolio summary load, etc.)
  - Record median response time for each operation
  - Save results as JSON: `{"widget_name": {"operation": "duration_ms", ...}, ...}`
  - Baseline for SC-010 (20% improvement target)
- [ ] T086 Measure baseline widget complexity in `tests/regression/fixtures/baseline_complexity.json`
  - Use `radon cc src/widgets/*.py` or `mccabe` to calculate McCabe cyclomatic complexity
  - Calculate average complexity per method across all widget files
  - Save results as JSON: `{"widget_name": {"avg_complexity": N, "max_complexity": M, ...}, ...}`
  - Baseline for SC-011 (90% reduction target)

### Documentation & Polish

- [ ] T087 [P] Create comprehensive API documentation in `docs/api-guide.md`
  - Overview of all endpoints
  - Authentication flow
  - Example requests/responses with curl
  - Error codes reference
- [ ] T088 [P] Create migration guide in `docs/migration-guide.md`
  - How to enable new service layer via feature flag
  - Rollback procedure
  - Testing checklist for developers
- [ ] T089 [P] Add performance monitoring to API
  - Log request duration for all endpoints
  - Add `/api/metrics` endpoint with request counts, average response times
  - Compare against baseline from T085 for SC-010 validation
- [ ] T090 Code cleanup: Remove commented-out old code from widgets after full migration
- [ ] T091 [P] Add API rate limiting middleware (100 requests/minute per user)
  - Implement rate limiting for task status polling (1 req/sec per task, per FR-028)
- [ ] T092 [P] Add comprehensive logging throughout service layer
  - Log all service method calls with parameters
  - Log calculation results for auditing
  - Use structured logging (JSON format)
- [ ] T093 Update README.md with new architecture overview
  - Add architecture diagram (Streamlit + API + Services + Repositories)
  - Document how to run API server
  - Document how to run new frontend
  - Document feature flag usage (USE_NEW_SERVICE_LAYER, ENABLE_API_AUTH, ENABLE_ASYNC_TASKS, ENABLE_FRONTEND_POC)
- [ ] T094 Run full regression test suite before production deployment
  - All 15 widgets tested with new service layer
  - API integration tests pass
  - Frontend tests pass
  - Performance benchmarks meet targets (80%+ coverage, <500ms API, <30s simulation)
  - Validate SC-010: 20% response time improvement vs baseline (T085)
  - Validate SC-011: 90% complexity reduction vs baseline (T086)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - **US1 (P1)** and **US3 (P1)**: Can start immediately after Foundational (no dependencies on each other)
  - **US4 (P2)**: Depends on US1 completion (services must exist before repository integration)
  - **US2 (P2)**: Depends on US1, US3, US4 completion (needs services, domain models, repositories)
  - **US5 (P3)**: Depends on US1 completion (compatibility layer wraps services)
  - **US6 (P3)**: Depends on US2 completion (frontend consumes API)
- **Polish (Phase 9)**: Depends on all user stories being complete

### Critical Path (for fastest MVP)

1. **Setup (Phase 1)** → 2. **Foundational (Phase 2)** → 3. **US1 + US3 (parallel)** → 4. **US4** → 5. **US2** → **MVP API Ready**

### User Story Dependencies

- **US1 (Business Logic)**: Foundation only - can start immediately after Phase 2
- **US3 (Domain Models)**: Foundation only - can run in parallel with US1
- **US4 (Repositories)**: Requires US1 services to exist (T039 modifies services)
- **US2 (REST API)**: Requires US1 (services), US3 (models), US4 (repositories)
- **US5 (Compatibility)**: Requires US1 services (wraps them for Streamlit)
- **US6 (New Frontend)**: Requires US2 API (consumes endpoints)

### Within Each User Story

- **US1**: Domain models (T014-T019) in parallel → Service extraction (T020-T024) in parallel → Tests (T025-T029) in parallel
- **US3**: All domain models (T030-T033) in parallel → Tests (T034)
- **US4**: All repositories (T035-T038) in parallel → Update services (T039) → Tests (T040-T043) in parallel
- **US2**: API schemas (T044-T047) in parallel → API routers (T048-T053) in parallel → Infrastructure (T054-T058) → Tests (T059-T064) in parallel
- **US5**: Bridge (T065) → Feature flag (T066) → Widget updates (T067-T069) in parallel → Tests (T070-T073) in parallel
- **US6**: Setup (T074) → API client (T075-T076) in parallel → Components (T077-T081) → Tests (T082-T084) in parallel

### Parallel Opportunities

- **Phase 1**: T003, T004, T005 can run in parallel (different files)
- **Phase 2**: T007, T008, T011, T012 can run in parallel (different modules)
- **US1 Domain Models**: T014-T019 can all run in parallel (6 different files)
- **US1 Services**: T020-T024 can run in parallel (5 different files)
- **US1 Tests**: T025-T029 can all run in parallel (5 test files)
- **US3 Models**: T030-T033 can run in parallel (same file but different classes)
- **US4 Repos**: T035-T038 can run in parallel (4 different files)
- **US2 Schemas**: T044-T047 can run in parallel (4 different files)
- **US2 Routers**: T048-T053 can run in parallel (6 different files)
- **US5 Widgets**: T067-T069 can run in parallel (3 different widget files)

---

## Parallel Example: User Story 1 Services

```bash
# After domain models complete (T014-T019), launch all service extractions in parallel:
Developer A: "Extract MonteCarloService into src/services/monte_carlo_service.py" (T020)
Developer B: "Extract RebalancingService into src/services/rebalancing_service.py" (T021)
Developer C: "Extract OptimizationService into src/services/optimization_service.py" (T022)
Developer D: "Create RiskAnalysisService in src/services/risk_analysis_service.py" (T023)
Developer E: "Extract NewsAnalysisService into src/services/news_analysis_service.py" (T024)

# Once services complete, launch all tests in parallel:
Developer A: "Unit test MonteCarloService in tests/unit/test_monte_carlo_service.py" (T025)
Developer B: "Unit test RebalancingService in tests/unit/test_rebalancing_service.py" (T026)
Developer C: "Unit test OptimizationService in tests/unit/test_optimization_service.py" (T027)
Developer D: "Unit test RiskAnalysisService in tests/unit/test_risk_analysis_service.py" (T028)
Developer E: "Unit test NewsAnalysisService in tests/unit/test_news_analysis_service.py" (T029)
```

---

## Implementation Strategy

### MVP First (P1 User Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks everything)
3. Complete Phase 3: User Story 1 (Business Logic Extraction)
4. Complete Phase 4: User Story 3 (Domain Models)
5. **STOP and VALIDATE**: 
   - Run all unit tests (80%+ coverage)
   - Import services in pure Python script (no Streamlit)
   - Call MonteCarloService, OptimizationService with sample data
   - Verify structured results returned
6. **MVP Foundation Delivered**: Framework-agnostic service layer ready for API integration

### Full Backend (P1 + P2)

1. Continue from MVP Foundation
2. Complete Phase 5: User Story 4 (Repositories)
3. Complete Phase 6: User Story 2 (REST API)
4. **STOP and VALIDATE**:
   - Test all API endpoints with curl/Postman
   - Verify `/docs` OpenAPI documentation
   - Run API integration test suite
   - Test async task execution (10k simulations)
5. **Backend Delivered**: Fully functional REST API exposing all portfolio analysis

### Full Migration (P1 + P2 + P3)

1. Continue from Full Backend
2. Complete Phase 7: User Story 5 (Compatibility Layer)
3. **STOP and VALIDATE**:
   - Run regression tests (old vs new implementation)
   - Test Streamlit app with feature flag enabled
   - Verify zero behavior changes
4. Complete Phase 8: User Story 6 (New Frontend POC)
5. **STOP and VALIDATE**:
   - Compare new frontend vs Streamlit side-by-side
   - Verify identical data displayed
6. Complete Phase 9: Polish
7. **Production Ready**: Zero downtime migration complete, new frontend validated

### Parallel Team Strategy

With 5 developers (optimal for this project):

**After Foundational Phase completes:**
- Developer 1: US1 domain models (simulation, optimization) + MonteCarloService
- Developer 2: US1 domain models (rebalancing, news) + RebalancingService + NewsAnalysisService  
- Developer 3: US1 OptimizationService + RiskAnalysisService
- Developer 4: US3 domain models (portfolio entities)
- Developer 5: US4 repository base classes

**After US1+US3+US4 complete:**
- Developer 1: API routers (simulation, optimization)
- Developer 2: API routers (portfolio, rebalancing)
- Developer 3: API infrastructure (auth, tasks, error handling)
- Developer 4: Integration tests (API endpoints)
- Developer 5: US5 compatibility bridge

**After US2+US5 complete:**
- Developer 1-2: US6 frontend (React components)
- Developer 3: US6 API client layer
- Developer 4-5: Regression testing, documentation

---

## Notes

- **[P]** tasks = different files, no shared state, can run truly in parallel
- **[Story]** label enables tracking which user story each task belongs to
- **Tests included**: This is major refactoring requiring validation at every step
- **Estimated total**: ~94 tasks organized across 6 user stories (includes 2 baseline measurement tasks for SC-010/SC-011 validation)
- **Critical path duration**: ~4-6 weeks with 1 developer, ~2-3 weeks with 5 developers (assuming 2-3 tasks/day/developer)
- **MVP delivery**: After Phase 4 (US1+US3) - framework-agnostic services ready (~40 tasks, ~2 weeks solo)
- **API delivery**: After Phase 6 (US1+US3+US4+US2) - full REST API (~70 tasks, ~4 weeks solo)
- **Migration complete**: After Phase 8 (all stories) - zero downtime achieved (~85 tasks, ~5 weeks solo)
- Each checkpoint provides a stable state for testing and feedback
- Feature flag in US5 allows gradual rollout and easy rollback
- Regression tests ensure byte-identical results between implementations
