# Tasks: SOLID Widget Architecture

**Input**: Design documents from `/specs/007-solid-widget-architecture/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and SOLID architecture foundation

- [X] T001 Create TypeScript interfaces directory structure at frontend/v1/src/lib/interfaces/
- [X] T002 [P] Create widget factory base structure at frontend/v1/src/lib/factories/
- [X] T003 [P] Create data providers directory structure at frontend/v1/src/lib/providers/
- [X] T004 [P] Create widget controllers directory structure at frontend/v1/src/lib/controllers/
- [X] T005 [P] Set up widget types definitions at frontend/v1/src/types/widget-types.ts
- [X] T006 Create React Context for widget services at frontend/v1/src/lib/providers/WidgetServicesProvider.tsx

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core interfaces and base implementations needed for all user stories

- [X] T007 Implement IWidgetController interface in frontend/v1/src/lib/interfaces/IWidgetController.ts
- [X] T008 [P] Implement IDataProvider interface in frontend/v1/src/lib/interfaces/IDataProvider.ts
- [X] T009 [P] Implement IWidgetConfiguration interface in frontend/v1/src/lib/interfaces/IWidgetConfiguration.ts
- [X] T010 [P] Implement IWidgetFactory interface in frontend/v1/src/lib/interfaces/IWidgetFactory.ts
- [X] T011 Create base WidgetController abstract class in frontend/v1/src/lib/controllers/BaseWidgetController.ts
- [X] T012 Create base DataProvider abstract class in frontend/v1/src/lib/providers/BaseDataProvider.ts
- [X] T013 Implement WidgetFactory class in frontend/v1/src/lib/factories/WidgetFactory.ts
- [X] T014 Create useWidgetServices custom hook in frontend/v1/src/hooks/use-widget-services.ts
- [X] T015 Create useWidgetController custom hook in frontend/v1/src/hooks/use-widget-controller.ts

## Phase 3: User Story 1 - Developer extends widget functionality without modifying core (Priority P1)

**Story Goal**: Enable widget extension through composition without modifying existing code
**Independent Test**: Create Holdings percentage variant using composition, verify original Holdings unchanged

- [X] T016 [US1] Create HoldingsController extending BaseWidgetController in frontend/v1/src/lib/controllers/HoldingsController.ts
- [X] T017 [P] [US1] Create PortfolioDataProvider implementing IDataProvider in frontend/v1/src/lib/providers/PortfolioDataProvider.ts
- [X] T018 [P] [US1] Implement HoldingsConfiguration type in frontend/v1/src/types/widget-types.ts
- [X] T019 [US1] Refactor Holdings.tsx to use HoldingsController with dependency injection and convert snake_case fields (asset_class→assetClass, market_value→marketValue, current_price→currentPrice) to match Holding interface
- [X] T020 [P] [US1] Create HoldingsPercentageView variant component in frontend/v1/src/components/variants/HoldingsPercentageView.tsx
- [X] T021 [P] [US1] Create HoldingsTableView variant component in frontend/v1/src/components/variants/HoldingsTableView.tsx
- [X] T022 [US1] Update Holdings.tsx to support presentation strategy pattern
- [X] T023 [US1] Register HoldingsController with WidgetFactory in frontend/v1/src/lib/factories/WidgetFactory.ts
- [X] T024 [P] [US1] Write unit tests for HoldingsController in tests/unit/controllers/HoldingsController.test.ts
- [X] T025 [P] [US1] Write unit tests for PortfolioDataProvider in tests/unit/providers/PortfolioDataProvider.test.ts
- [X] T026 [US1] Write integration tests for Holdings variant composition in tests/integration/holdings-variants.test.tsx

## Phase 4: User Story 2 - Easy widget testing through dependency injection (Priority P1)

**Story Goal**: Enable comprehensive unit testing through injected mock dependencies
**Independent Test**: Write complete unit test suite that mocks all dependencies and verifies widget behavior

- [X] T027 [US2] Create MockDataProvider for testing in tests/utils/mocks/MockDataProvider.ts
- [X] T028 [P] [US2] Create mock widget dependencies factory in tests/utils/mocks/createMockDependencies.ts
- [X] T029 [P] [US2] Create mock configuration factory in tests/utils/mocks/createMockConfiguration.ts
- [X] T030 [US2] Implement PortfolioSummaryController extending BaseWidgetController in frontend/v1/src/lib/controllers/PortfolioSummaryController.ts
- [X] T031 [P] [US2] Create MarketDataProvider implementing IDataProvider in frontend/v1/src/lib/providers/MarketDataProvider.ts
- [X] T032 [US2] Refactor PortfolioSummary.tsx to use PortfolioSummaryController with dependency injection
- [X] T033 [US2] Register PortfolioSummaryController with WidgetFactory in frontend/v1/src/lib/factories/WidgetFactory.ts
- [X] T034 [P] [US2] Write comprehensive unit tests for PortfolioSummaryController in tests/unit/controllers/PortfolioSummaryController.test.ts
- [ ] T035 [P] [US2] Write error handling tests using mock failures in tests/unit/controllers/error-handling.test.ts
- [ ] T036 [P] [US2] Write loading state tests using mock delays in tests/unit/controllers/loading-states.test.ts
- [ ] T037 [US2] Create test utilities for widget testing patterns in tests/utils/widget-test-utils.ts

## Phase 5: User Story 3 - Reusable widget components across different contexts (Priority P2)

**Story Goal**: Enable same widget logic in different presentations (dashboard, reports, mobile)
**Independent Test**: Render same widget in multiple layout contexts with consistent behavior

- [ ] T038 [US3] Create presentation strategy interfaces in frontend/v1/src/lib/interfaces/IPresentationStrategy.ts
- [ ] T039 [P] [US3] Implement CompactPresentationStrategy in frontend/v1/src/lib/strategies/CompactPresentationStrategy.ts
- [ ] T040 [P] [US3] Implement DetailedPresentationStrategy in frontend/v1/src/lib/strategies/DetailedPresentationStrategy.ts
- [ ] T041 [P] [US3] Implement MobilePresentationStrategy in frontend/v1/src/lib/strategies/MobilePresentationStrategy.ts
- [ ] T042 [US3] Create CorrelationMatrixController extending BaseWidgetController in frontend/v1/src/lib/controllers/CorrelationMatrixController.ts
- [ ] T043 [US3] Refactor CorrelationMatrix.tsx to use presentation strategies
- [ ] T044 [US3] Create MonteCarloController extending BaseWidgetController in frontend/v1/src/lib/controllers/MonteCarloController.ts
- [ ] T045 [P] [US3] Create SimulationDataProvider implementing IDataProvider in frontend/v1/src/lib/providers/SimulationDataProvider.ts
- [ ] T046 [US3] Refactor MonteCarloSimulation.tsx to use MonteCarloController with presentation strategies
- [ ] T047 [US3] Register CorrelationMatrixController and MonteCarloController with WidgetFactory
- [ ] T048 [P] [US3] Write tests for presentation strategy switching in tests/integration/presentation-strategies.test.tsx
- [ ] T049 [P] [US3] Write responsive layout tests in tests/integration/responsive-layouts.test.tsx

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, developer experience, and final integration

- [ ] T050 Add widget performance monitoring in frontend/v1/src/lib/monitoring/WidgetPerformanceMonitor.ts
- [ ] T051 [P] Create widget debug utilities in frontend/v1/src/lib/debug/widget-debug-utils.ts
- [ ] T052 [P] Add widget configuration validation utilities in frontend/v1/src/lib/validation/config-validators.ts
- [ ] T053 [P] Create widget development DevTools in frontend/v1/src/lib/devtools/WidgetDevTools.tsx
- [ ] T054 Implement widget lazy loading optimization in frontend/v1/src/lib/optimization/LazyWidgetLoader.tsx
- [ ] T055 [P] Add widget caching layer optimization in frontend/v1/src/lib/cache/WidgetCacheManager.ts
- [ ] T056 [P] Create migration utilities for legacy widgets in frontend/v1/src/lib/migration/LegacyWidgetAdapter.ts
- [ ] T057 Update dashboard page to use new widget architecture in frontend/v1/src/app/dashboard/page.tsx
- [ ] T058 [P] Add comprehensive end-to-end tests in tests/e2e/widget-architecture.test.ts
- [ ] T059 [P] Update developer documentation with new architecture examples
- [ ] T060 Perform final integration testing and performance validation

## Dependencies

### User Story Completion Order:
1. **Phase 1-2**: Complete foundational setup before any user stories
2. **Phase 3 (US1)**: Must complete before US3 (presentation strategies depend on controller pattern)
3. **Phase 4 (US2)**: Can run in parallel with US1 after Phase 2
4. **Phase 5 (US3)**: Depends on US1 controller patterns
5. **Phase 6**: Depends on completion of all user stories

### Parallel Execution Opportunities:

**Phase 3 (US1) Parallel Groups:**
- Group A: T017, T020, T021, T024, T025 (independent file creation)
- Group B: T016, T019, T022 (dependent controller implementation)

**Phase 4 (US2) Parallel Groups:**
- Group A: T027, T028, T029, T031 (mock utilities and providers)
- Group B: T034, T035, T036 (test writing after controllers exist)

**Phase 5 (US3) Parallel Groups:**
- Group A: T039, T040, T041, T045 (strategy implementations)
- Group B: T048, T049 (integration testing)

## Implementation Strategy

### MVP Scope (US1 Only):
- Holdings widget with SOLID architecture
- Basic dependency injection
- Single presentation variant
- **Estimated effort**: 40% of total project

### Incremental Delivery:
- **Week 1**: Phase 1-2 (Foundation) + US1 core controller
- **Week 2**: US1 completion + US2 testing infrastructure  
- **Week 3**: US2 completion + US3 presentation strategies
- **Week 4**: US3 completion + Phase 6 polish

### Success Validation:
- Each user story has independent test criteria
- MVP (US1) can be deployed and validated separately
- Each phase produces working, testable increments
- Performance benchmarks maintained throughout