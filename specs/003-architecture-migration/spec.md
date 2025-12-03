# Feature Specification: Framework-Agnostic Architecture Migration

**Feature Branch**: `003-architecture-migration`  
**Created**: 2025-12-03  
**Status**: Draft  
**Input**: Migrate application from Streamlit framework to framework-agnostic architecture with separate business logic layer, REST API, and support for bespoke UX design

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Business Logic Extraction (Priority: P1)

As a **developer**, I need the portfolio analysis calculations (Monte Carlo simulation, optimization, risk metrics, correlation analysis) extracted into framework-agnostic service classes, so that I can reuse this core business logic with any frontend framework or API without Streamlit dependencies.

**Why this priority**: This is the foundation of the entire migration. Without extracting business logic, the application remains tightly coupled to Streamlit and cannot support alternative UIs. All other migration work depends on this.

**Independent Test**: Can instantiate service classes (e.g., `MonteCarloService`, `OptimizationService`) in a Python script without any Streamlit imports, call methods with dataclass parameters, and receive structured results. Services can be tested with pytest without mocking Streamlit components.

**Acceptance Scenarios**:

1. **Given** Monte Carlo simulation parameters (symbols, weights, years, simulations, initial value), **When** calling `MonteCarloService.run_simulation()`, **Then** returns structured SimulationResults with paths, percentiles, and risk metrics
2. **Given** portfolio holdings and target weights, **When** calling `OptimizationService.calculate_efficient_frontier()`, **Then** returns list of portfolio points with return/risk/weights
3. **Given** price data and event detection parameters, **When** calling `NewsAnalysisService.detect_surprise_events()`, **Then** returns list of detected events with statistical significance
4. **Given** extracted services, **When** running pytest test suite, **Then** achieves 80%+ code coverage without Streamlit dependencies

---

### User Story 2 - REST API Implementation (Priority: P2)

As an **API consumer** (future frontend developer or external integration), I need RESTful endpoints that expose all portfolio analysis capabilities, so that I can build custom user interfaces or integrate portfolio analysis into other applications without being locked into Streamlit.

**Why this priority**: Once business logic is extracted (P1), the API layer enables any frontend to consume the functionality. This unlocks the ability to build the bespoke UX and supports future integrations.

**Independent Test**: Can make HTTP requests to API endpoints (e.g., `POST /api/simulation/monte-carlo`, `GET /api/portfolio/summary`) with JSON payloads and receive JSON responses with analysis results. Can be tested with curl, Postman, or automated API tests without any UI.

**Acceptance Scenarios**:

1. **Given** API is running, **When** sending `POST /api/simulation/monte-carlo` with valid simulation parameters, **Then** receives 200 response with simulation results JSON
2. **Given** API is running, **When** sending `GET /api/portfolio/instruments` with authentication token, **Then** receives list of user's tracked instruments
3. **Given** API is running, **When** sending `POST /api/optimization/efficient-frontier` with symbol list, **Then** receives optimal portfolio allocations
4. **Given** long-running simulation request, **When** requesting status via task ID, **Then** receives progress updates and final results when complete
5. **Given** invalid authentication token, **When** making any API request, **Then** receives 401 Unauthorized response

---

### User Story 3 - Domain Model Definition (Priority: P1)

As a **developer**, I need strongly-typed domain models (using Pydantic or dataclasses) for all business entities (portfolios, simulations, optimization results, instruments), so that I have clear contracts between layers and can validate data throughout the system.

**Why this priority**: Domain models are essential for both service layer (P1) and API layer (P2). They provide type safety, validation, and clear documentation of data structures. Should be completed alongside or immediately after service extraction.

**Independent Test**: Can instantiate domain models with valid data and they validate correctly. Invalid data raises clear validation errors. Models can be serialized to/from JSON for API consumption.

**Acceptance Scenarios**:

1. **Given** valid simulation parameters, **When** creating `SimulationParameters` model, **Then** model validates and can be serialized to JSON
2. **Given** invalid parameters (e.g., negative years), **When** creating domain model, **Then** raises ValidationError with clear message
3. **Given** `SimulationResults` model, **When** serializing to JSON, **Then** produces API-compatible response format
4. **Given** API JSON payload, **When** deserializing to domain model, **Then** creates valid model instance or raises validation error

---

### User Story 4 - Repository Pattern Implementation (Priority: P2)

As a **developer**, I need repository interfaces that abstract database operations for instruments, orders, price data, and dividends, so that I can cleanly separate data access concerns and potentially swap storage implementations without affecting business logic.

**Why this priority**: Repositories provide clean data access for services (P1) and API layer (P2). While the current storage adapter works, repositories offer better domain-focused APIs and testability.

**Independent Test**: Can interact with repositories through clean domain-focused methods (e.g., `InstrumentRepository.find_by_symbol()`, `OrderRepository.get_orders_in_date_range()`) without knowledge of underlying storage adapter or database implementation.

**Acceptance Scenarios**:

1. **Given** instrument symbol, **When** calling `InstrumentRepository.find_by_symbol('AAPL')`, **Then** returns Instrument domain model or None
2. **Given** date range, **When** calling `PriceDataRepository.get_price_history()`, **Then** returns DataFrame with price data for specified range
3. **Given** portfolio holdings, **When** calling `PortfolioRepository.calculate_current_allocation()`, **Then** returns dictionary of symbol weights
4. **Given** repository interface, **When** unit testing services, **Then** can mock repositories without database dependencies

---

### User Story 5 - Backward Compatibility Layer (Priority: P3)

As a **user of the current Streamlit application**, I need the existing UI to continue working while migration occurs, so that I can keep using all portfolio analysis features without disruption during the transition period.

**Why this priority**: Ensures business continuity. Users shouldn't experience downtime. Can be implemented after P1/P2 are stable, allowing gradual migration rather than big-bang replacement.

**Independent Test**: Can run existing Streamlit application and all widgets function identically to pre-migration behavior. New service layer is used under the hood but UX is unchanged.

**Acceptance Scenarios**:

1. **Given** Streamlit app running with compatibility layer, **When** using Monte Carlo widget, **Then** produces identical results to original implementation
2. **Given** Streamlit app with feature flag enabled, **When** toggling between old/new implementation, **Then** both produce consistent results
3. **Given** user with saved widget configurations, **When** loading dashboard, **Then** all preferences and layouts are preserved
4. **Given** migration in progress, **When** accessing any feature, **Then** no visible errors or behavior changes for end users

---

### User Story 6 - New Frontend Foundation (Priority: P3)

As a **product owner**, I need a proof-of-concept new frontend (React/Vue/Svelte) that demonstrates 2-3 simple widgets connected to the REST API, so that I can validate the migration approach and UX design direction before committing to full frontend rebuild.

**Why this priority**: Validates the entire architecture end-to-end. Lower priority because API (P2) must be stable first. Proves feasibility before major frontend investment.

**Independent Test**: Can open new frontend in browser, authenticate, view portfolio summary and holdings breakdown, and see real data from API. No Streamlit involved.

**Acceptance Scenarios**:

1. **Given** new frontend running, **When** user logs in, **Then** sees authentication token stored and can access protected routes
2. **Given** authenticated user, **When** viewing portfolio summary page, **Then** displays total value, returns, and risk metrics from API
3. **Given** holdings breakdown widget, **When** data loads from API, **Then** displays instrument allocation pie chart with correct percentages
4. **Given** new frontend and Streamlit app running simultaneously, **When** comparing outputs, **Then** both display identical data for same user

---

### Edge Cases

- What happens when a service method receives malformed input data (missing required fields, out-of-range values)?
  - Domain models should validate inputs and raise clear ValidationErrors before business logic executes
  
- How does the system handle long-running calculations (10,000 Monte Carlo simulations) in an API context?
  - API should support async task execution with task IDs for status checking and result retrieval
  
- What happens when storage adapter fails (database connection lost, BigQuery quota exceeded)?
  - Repositories should raise domain-specific exceptions that API layer translates to appropriate HTTP error codes
  
- How are concurrent API requests handled when they modify shared data (e.g., adding orders)?
  - Database transactions ensure atomicity; API uses optimistic locking or explicit conflict detection
  
- What happens when user tries to run optimization with insufficient historical data?
  - Services validate data completeness upfront and return structured error results rather than throwing exceptions
  
- How does authentication work across Streamlit app and new API during migration?
  - Compatibility layer shares authentication mechanism (JWT tokens stored in session/cookies work for both)

## Requirements *(mandatory)*

### Functional Requirements

#### Service Layer (P1)

- **FR-001**: System MUST extract all Monte Carlo simulation logic into `MonteCarloService` class with methods accepting SimulationParameters dataclass and returning SimulationResults dataclass
- **FR-002**: System MUST extract portfolio optimization logic into `OptimizationService` class supporting max Sharpe, min volatility, efficient frontier, and constrained optimization methods
- **FR-003**: System MUST extract risk analysis calculations into `RiskAnalysisService` class providing Sharpe ratio, Sortino ratio, VaR, CVaR, max drawdown, and beta calculations
- **FR-004**: System MUST extract news event correlation analysis into `NewsAnalysisService` class with event detection and correlation scoring methods
- **FR-005**: System MUST extract rebalancing analysis into `RebalancingService` class with drift detection and recommendation generation
- **FR-006**: All service methods MUST be pure functions or use dependency injection for storage access (no direct Streamlit dependencies)
- **FR-007**: Service classes MUST accept domain model dataclasses as input and return domain model dataclasses as output
- **FR-008**: System MUST achieve minimum 80% test coverage for all service layer code using pytest

#### Domain Models (P1)

- **FR-009**: System MUST define Pydantic models for SimulationParameters including symbols, weights, years, num_simulations, initial_value, contribution settings, and rebalancing settings
- **FR-010**: System MUST define SimulationResults model including paths, time_points, percentiles, final_values, risk metrics (VaR, CVaR, max drawdown, Sharpe ratio)
- **FR-011**: System MUST define OptimizationRequest model including symbols, constraints, objective function, and time period
- **FR-012**: System MUST define OptimizationResults model including optimal_weights, expected_return, volatility, sharpe_ratio, and efficient_frontier_points
- **FR-013**: System MUST define PortfolioSummary model including total_value, returns (MWR, TWR, IRR), risk_metrics, and dividend_yield
- **FR-014**: System MUST define RebalancingRecommendation model including rebalance_dates, drift_at_rebalance, cost_benefit_ratio, and per-instrument actions
- **FR-015**: All domain models MUST validate input data and raise clear validation errors for invalid values
- **FR-016**: All domain models MUST support JSON serialization/deserialization for API compatibility

#### REST API (P2)

- **FR-017**: System MUST implement FastAPI application with endpoints for portfolio summary, Monte Carlo simulation, optimization, rebalancing, news analysis, and dividend tracking
- **FR-018**: API MUST accept JSON request bodies following domain model schemas and return JSON responses
- **FR-019**: API endpoint `POST /api/simulation/monte-carlo` MUST accept SimulationParameters and return SimulationResults
- **FR-020**: API endpoint `POST /api/optimization/efficient-frontier` MUST accept OptimizationRequest and return OptimizationResults
- **FR-021**: API endpoint `GET /api/portfolio/summary` MUST return PortfolioSummary with current holdings and performance metrics
- **FR-022**: API endpoint `POST /api/rebalancing/analyze` MUST accept drift threshold and return RebalancingRecommendation
- **FR-023**: API endpoint `GET /api/instruments` MUST return list of tracked instruments with pagination support
- **FR-024**: API MUST implement JWT-based authentication for all protected endpoints
- **FR-025**: API MUST validate all request payloads using Pydantic models and return 422 errors for invalid data
- **FR-026**: API MUST return appropriate HTTP status codes (200 success, 400 bad request, 401 unauthorized, 404 not found, 500 server error)
- **FR-027**: API MUST implement async task execution for long-running operations (simulations >1000 iterations) with task status endpoints
- **FR-028**: API MUST include OpenAPI/Swagger documentation accessible at `/docs` endpoint

#### Repository Layer (P2)

- **FR-029**: System MUST implement `InstrumentRepository` with methods: find_by_symbol, find_all_active, search, add, update, remove
- **FR-030**: System MUST implement `OrderRepository` with methods: create, find_by_symbol, find_in_date_range, calculate_holdings_at_date
- **FR-031**: System MUST implement `PriceDataRepository` with methods: get_price_history, get_latest_prices, get_returns, store_prices
- **FR-032**: System MUST implement `DividendRepository` with methods: get_dividends, get_cash_flows, calculate_yield
- **FR-033**: Repository methods MUST return domain models rather than raw dictionaries or database ORM objects
- **FR-034**: Repository implementations MUST use existing `DataStorageAdapter` as underlying storage mechanism
- **FR-035**: Repository interfaces MUST be abstract base classes allowing alternative implementations for testing

#### Compatibility Layer (P3)

- **FR-036**: System MUST provide `StreamlitServiceBridge` class that wraps service layer calls to maintain API compatibility with existing widgets
- **FR-037**: Existing Streamlit widgets MUST be able to toggle between direct service calls and compatibility layer via feature flag
- **FR-038**: Compatibility layer MUST translate between current dict-based returns and new domain model returns
- **FR-039**: System MUST preserve all existing session state management during migration period
- **FR-040**: System MUST maintain backward compatibility with saved dashboard configurations stored in database

#### New Frontend (P3)

- **FR-041**: System MUST implement portfolio summary widget in new frontend framework showing total value, returns, and risk metrics
- **FR-042**: System MUST implement holdings breakdown widget in new frontend showing instrument allocation with pie chart
- **FR-043**: New frontend MUST authenticate users via JWT tokens obtained from API login endpoint
- **FR-044**: New frontend MUST handle API errors gracefully with user-friendly error messages
- **FR-045**: New frontend MUST display loading states during async API calls
- **FR-046**: New frontend MUST validate user inputs client-side before sending to API

### Key Entities

- **SimulationParameters**: Configuration for Monte Carlo simulations including symbols (list), weights (array), time horizon (years), number of simulations, initial portfolio value, contribution settings (amount, frequency), rebalancing parameters (enabled, drift threshold, transaction costs)

- **SimulationResults**: Output from Monte Carlo simulation including all simulation paths (2D array), time points, percentile bands (5th, 10th, 25th, 50th, 75th, 90th, 95th), final portfolio values, risk metrics (VaR, CVaR, max drawdown, Sharpe ratio), rebalancing recommendations

- **OptimizationRequest**: Input for portfolio optimization including symbols to optimize, time period for historical data, optimization objective (max Sharpe, min volatility, target return), constraints (weight bounds, sector limits, turnover constraints)

- **OptimizationResults**: Output from optimization including optimal weights per symbol, expected return, volatility, Sharpe ratio, efficient frontier curve (list of points with return/risk/weights)

- **PortfolioSummary**: Current portfolio state including total value in base currency, instrument holdings with quantities and values, performance metrics (returns: MWR, TWR, IRR; risk: volatility, Sharpe, Sortino, max drawdown), dividend yield

- **RebalancingRecommendation**: Analysis of when to rebalance including recommended dates, portfolio drift at each date, per-instrument actions (buy/sell), cost-benefit analysis, expected Sharpe improvement

- **InstrumentDomainModel**: Tracked instrument including symbol, name, type (stock/ETF/index), sector, currency, quantity held, current value in local and base currency

- **OrderRecord**: Buy/sell transaction including instrument symbol, type (buy/sell), volume (quantity), order date, notes

- **PriceHistory**: Historical price data including symbol, date range, OHLCV data (open, high, low, close, volume), adjusted close, associated dividends

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can run all 15 existing widget calculations through service layer methods without any Streamlit imports in under 5 seconds for typical inputs (50 data points, 1000 simulations)

- **SC-002**: Service layer achieves 80%+ code coverage with unit tests that execute without Streamlit or database dependencies (mocked repositories)

- **SC-003**: REST API handles 100 concurrent requests for portfolio summary endpoint with average response time under 500ms

- **SC-004**: API successfully executes 10,000-iteration Monte Carlo simulation as async task and provides progress updates within 30 seconds total execution time

- **SC-005**: New frontend demo loads portfolio summary and holdings breakdown from API in under 2 seconds on standard broadband connection

- **SC-006**: All 15 existing Streamlit widgets continue to function identically with compatibility layer, producing byte-identical results for same inputs (verified via automated regression tests)

- **SC-007**: API documentation at `/docs` endpoint allows external developer to successfully call 5 core endpoints (portfolio summary, Monte Carlo, optimization, rebalancing, instruments) within 30 minutes of reading docs

- **SC-008**: Domain models reject 100% of invalid inputs (e.g., negative years, weights not summing to 1, missing required fields) with clear validation error messages

- **SC-009**: Repository layer supports swapping from SQLite to PostgreSQL without any changes to service layer code (verified via integration tests against both databases)

- **SC-010**: Migration to new architecture reduces average widget response time by 20% due to removal of Streamlit rendering overhead in service layer

- **SC-011**: 90% of existing codebase complexity is reduced as measured by cyclomatic complexity scores after extracting business logic from UI code

- **SC-012**: Zero downtime during migration - existing Streamlit app remains fully functional at all times while new architecture is built alongside
