# Feature Specification: Widget Architecture Refactoring

**Feature Branch**: `002-widget-architecture-refactor`  
**Created**: 2025-12-01  
**Status**: Draft  
**Input**: User feedback: "I'm finding the widgets are really hard to understand and maintain."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Adds New Widget (Priority: P1)

A developer needs to create a new widget for dividend tracking. They should be able to focus on business logic without getting tangled in UI state management or data fetching boilerplate.

**Why this priority**: Core maintainability issue - current architecture makes adding widgets painful. This is the foundational problem.

**Independent Test**: Developer can create a new widget by implementing only 3 pure functions (data fetch, calculation, result preparation) and the base class handles all UI orchestration. Widget can be tested with unit tests before any UI rendering.

**Acceptance Scenarios**:

1. **Given** a developer wants a new metric widget, **When** they subclass the new BaseWidget pattern, **Then** they only implement business logic methods without any Streamlit rendering code
2. **Given** a widget's business logic is implemented, **When** unit tests are written, **Then** calculations can be tested independently without rendering UI
3. **Given** a widget needs data from storage, **When** the fetch method returns the data, **Then** the base class handles missing data, errors, and loading states automatically

---

### User Story 2 - Developer Debugs Widget Behavior (Priority: P2)

A developer needs to debug why correlation calculations are incorrect. They should be able to test the calculation logic independently from the 350-line render method.

**Why this priority**: Current monolithic render() methods make debugging extremely difficult. Separation enables targeted testing.

**Independent Test**: Developer can call the calculation method directly with sample data and verify results without running Streamlit app.

**Acceptance Scenarios**:

1. **Given** a widget has a calculation bug, **When** developer extracts sample data, **Then** they can run the calculation method in isolation with print statements or debugger
2. **Given** calculation logic needs modification, **When** tests are run, **Then** test suite runs in <1 second without UI rendering
3. **Given** multiple calculation edge cases exist, **When** parametrized tests are written, **Then** all cases can be verified with clean assertions

---

### User Story 3 - Developer Refactors Existing Widget (Priority: P2)

A developer needs to refactor the correlation matrix widget from 500+ lines to layered architecture. The refactor should preserve all existing functionality while improving maintainability.

**Why this priority**: Proves the architecture works for real, complex widgets. Provides migration template for other widgets.

**Independent Test**: Refactored widget produces identical output to original for all test cases. Can be verified with snapshot testing or manual comparison.

**Acceptance Scenarios**:

1. **Given** the refactored widget, **When** user interacts with UI, **Then** all selections, calculations, and displays work identically to original
2. **Given** the refactored code, **When** code review is performed, **Then** business logic is in pure functions, UI is in render methods, data fetching is in data layer
3. **Given** the new architecture, **When** line count is measured, **Then** render method is <100 lines, helper methods are <50 lines each

---

### User Story 4 - Developer Maintains Widget Consistency (Priority: P3)

A developer needs to ensure all widgets follow the same patterns for session state, error handling, and loading indicators.

**Why this priority**: Consistency reduces cognitive load when switching between widgets. Secondary to core architecture.

**Independent Test**: All widgets use identical patterns for session state keys, error messages, and loading spinners.

**Acceptance Scenarios**:

1. **Given** multiple widgets, **When** session state keys are inspected, **Then** all follow `{widget_id}_{purpose}` pattern
2. **Given** a data fetching error occurs, **When** any widget handles it, **Then** error is displayed with actionable message and logged
3. **Given** a long-running calculation, **When** widget renders, **Then** spinner displays with descriptive message

---

### Edge Cases

- What happens when a widget's calculation method raises an unexpected exception?
- How does the base class handle partial data (some symbols have data, others don't)?
- What if a widget needs custom session state initialization beyond the base pattern?
- How do we handle widgets that need multiple independent data fetches (parallel vs sequential)?
- What if render logic needs to branch significantly based on data characteristics?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Base widget class MUST separate concerns into three layers: UI rendering, data fetching, and business logic
- **FR-002**: Business logic methods MUST be pure functions (no side effects, no Streamlit calls, no storage access)
- **FR-003**: Data fetching methods MUST be the only place that calls `self.storage`
- **FR-004**: Render methods MUST be the only place that calls Streamlit UI functions (`st.*`)
- **FR-005**: Session state management MUST follow consistent naming pattern: `{widget_id}_{purpose}`
- **FR-006**: Base class MUST provide standard error handling for data fetch failures
- **FR-007**: Base class MUST provide standard loading state handling with spinners
- **FR-008**: Business logic functions MUST be testable with unit tests (no mocking required for happy path)
- **FR-009**: Refactored widgets MUST maintain backward compatibility in UI behavior
- **FR-010**: Architecture MUST support widgets with different scopes (portfolio, single, multiple)
- **FR-011**: Data validation MUST occur in data layer before passing to business logic
- **FR-012**: Complex calculations MUST be broken into composable functions (<50 lines each)
- **FR-013**: All layer methods MUST have complete docstrings with parameters, returns, and exceptions
- **FR-014**: Base class MUST handle missing data gracefully with user-friendly messages
- **FR-015**: Architecture MUST not require changes to BaseWidget interface (maintain `render()` signature)

### Key Entities *(include if feature involves data)*

- **Widget Layer Structure**: Three distinct layers (UI, Data, Logic) with clear boundaries
- **Data Transfer Objects**: Typed dictionaries or dataclasses for passing data between layers
- **Calculation Results**: Structured outputs from business logic (not raw DataFrames mixed with UI state)
- **Session State Keys**: Standardized naming convention for widget-specific state

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Correlation matrix widget refactored from 500+ lines to <300 lines with layered architecture
- **SC-002**: Business logic methods are pure functions testable without Streamlit mocking (unit tests run in <1s)
- **SC-003**: Render method in refactored widget is <100 lines focusing only on UI composition
- **SC-004**: Developer can understand widget flow in 5 minutes by reading method signatures and docstrings
- **SC-005**: New widget creation requires <150 lines of code (excluding comments/docstrings)
- **SC-006**: 100% of existing widget functionality preserved (verified through manual testing)
- **SC-007**: Base class provides reusable patterns for data fetching, error handling, and loading states
- **SC-008**: Session state keys follow consistent `{widget_id}_{purpose}` pattern across all methods
