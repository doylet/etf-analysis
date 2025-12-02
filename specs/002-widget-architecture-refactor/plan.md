# Implementation Plan: Widget Architecture Refactoring

**Branch**: `002-widget-architecture-refactor` | **Date**: 2025-12-01 | **Spec**: [spec.md](./spec.md)

## Summary

Refactor widget architecture to separate UI rendering, data fetching, and business logic into distinct layers. Replace monolithic 500-line `render()` methods with layered architecture: data layer fetches and validates, logic layer computes pure functions, UI layer renders. Prove pattern with correlation matrix widget refactor.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Streamlit 1.39+, pandas, numpy, plotly  
**Storage**: SQLite via storage_adapter (no schema changes)  
**Testing**: Manual UI testing (no automated test infrastructure yet)  
**Target Platform**: Local Streamlit dashboard  
**Project Type**: Single project (widget module enhancement)  
**Performance Goals**: Widget render <2s with 20+ instruments  
**Constraints**: Must maintain BaseWidget interface compatibility, zero breaking changes to existing widgets  
**Scale/Scope**: 7 widgets in codebase, refactor 1 as proof of concept

## Constitution Check

*GATE: Must pass before implementation. Constitution compliance is mandatory.*

✅ **Principle I: Data Persistence First** - No changes to persistence layer, widgets still fetch from storage  
✅ **Principle II: Calculation Transparency** - Enhanced by extracting calculations to pure functions with docstrings  
✅ **Principle III: Widget Modularity** - Strengthened by better separation of concerns within widgets  
✅ **Principle IV: Professional UI Standards** - Maintained, UI layer continues using st.space() and containers  
✅ **Principle V: Code Readability** - Significantly improved by layered architecture and smaller functions  

✅ **Forbidden Practice #1 (HEREDOCs)** - Not applicable, no code generation  
✅ **Forbidden Practice #2 (Global State)** - Session state patterns unchanged, still using Streamlit session state  
✅ **Forbidden Practice #3 (Silent Failures)** - Improved by base class error handling patterns  
✅ **Forbidden Practice #4 (st.divider/st.write(""))** - Not affected, UI layer maintains st.space() usage  

✅ **Type Hints Required** - All new methods will have complete type annotations  
✅ **Docstrings Required** - All methods will have comprehensive docstrings  
✅ **Error Handling Required** - Base class provides standard error handling patterns  

**Status**: ✅ ALL GATES PASSED - Constitution compliant architecture

## Project Structure

### Documentation (this feature)

```text
specs/002-widget-architecture-refactor/
├── spec.md              # Feature specification (created)
├── plan.md              # This file (implementation plan)
├── data-model.md        # Architecture patterns and class structure
├── quickstart.md        # Migration guide for other widgets
└── tasks.md             # Detailed task breakdown (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/widgets/
├── base_widget.py                        # Current BaseWidget interface (unchanged)
├── layered_base_widget.py               # NEW: Layered architecture base class
├── correlation_matrix_widget.py          # REFACTORED: Proof of concept
├── correlation_matrix_widget.py.backup   # Backup of original
│
# Other widgets (not modified in this feature)
├── portfolio_summary_widget.py
├── dividend_analysis_widget.py
├── benchmark_comparison_widget.py
├── performance_widget.py
└── holdings_breakdown_widget.py

tests/
└── widgets/                              # NEW: Unit tests for business logic
    ├── test_correlation_calculations.py
    └── test_data_validation.py
```

**Structure Decision**: Single project enhancement - add new `LayeredBaseWidget` class alongside existing `BaseWidget` to enable gradual migration. Refactor one widget (correlation matrix) as proof of concept. Other widgets can migrate later without breaking changes.

## Architecture Layers

### Layer 1: UI Layer (Render Methods)
**Responsibility**: Streamlit component composition, user interactions, display formatting  
**Rules**:
- Only layer that calls `st.*` functions
- Calls data layer to get data
- Calls logic layer to perform calculations
- Manages session state for UI selections
- Handles user input and button clicks
- No business logic or calculations
- Methods: `render()`, `_render_*()` helpers

**Example Methods**:
```python
def render(self, instruments, selected_symbols):
    """Main render orchestration - UI only"""
    
def _render_controls(self):
    """Render period selector and options - returns user selections"""
    
def _render_results(self, correlation_data):
    """Display heatmap and statistics - pure presentation"""
```

### Layer 2: Data Layer (Fetch & Validate)
**Responsibility**: Data retrieval, validation, transformation to analysis-ready format  
**Rules**:
- Only layer that calls `self.storage`
- Validates data quality and completeness
- Returns typed data structures (dicts, dataclasses, DataFrames)
- Handles missing data and API failures
- No UI rendering (no `st.*`)
- No calculations or business logic
- Methods: `_fetch_*()`, `_validate_*()`, `_prepare_*()` helpers

**Example Methods**:
```python
def _fetch_returns_data(self, symbols, start_date, end_date):
    """Fetch and validate price data, return returns dict or validation errors"""
    
def _prepare_analysis_dataset(self, returns_data, include_portfolio):
    """Transform returns into analysis-ready DataFrame with validation"""
```

### Layer 3: Logic Layer (Pure Calculations)
**Responsibility**: Business logic, calculations, analysis algorithms  
**Rules**:
- Pure functions (no side effects)
- No `st.*` calls (no UI)
- No `self.storage` calls (no data access)
- Takes data structures as input
- Returns calculation results
- Unit testable without mocking
- Can be static methods or module-level functions
- Methods: `_calculate_*()`, `_analyze_*()`, `_compute_*()` helpers

**Example Methods**:
```python
@staticmethod
def _calculate_correlation_matrix(returns_df):
    """Calculate correlation matrix from returns DataFrame"""
    
@staticmethod
def _analyze_diversification(correlation_matrix):
    """Analyze diversification metrics from correlation matrix"""
    
@staticmethod
def _find_key_pairs(correlation_matrix, n=5):
    """Find most/least correlated pairs"""
```

## Data Flow Pattern

```
User Interaction (UI Layer)
    ↓
Session State Update (UI Layer)
    ↓
Data Fetch Request (Data Layer)
    ↓
Storage Query (Data Layer → storage)
    ↓
Data Validation (Data Layer)
    ↓
Calculation Request (Logic Layer)
    ↓
Pure Computation (Logic Layer)
    ↓
Result Display (UI Layer)
```

## Migration Strategy

### Phase 1: Create New Base Class
- Implement `LayeredBaseWidget` with standard patterns
- Document layer separation rules
- Provide helper methods for common patterns (error handling, loading states)

### Phase 2: Refactor Correlation Matrix Widget
- Create backup of original
- Extract business logic to static methods
- Extract data fetching to data layer methods
- Simplify render() to orchestration only
- Verify functionality preservation through manual testing

### Phase 3: Documentation & Migration Guide
- Document refactoring process in quickstart.md
- Provide before/after examples
- Create checklist for migrating other widgets
- Include common patterns and anti-patterns

### Future Phases (Not in This Feature)
- Migrate other widgets gradually
- Add unit test infrastructure
- Consider automated testing framework

## Complexity Tracking

> No constitutional violations to justify

This architecture **reduces** complexity by separating concerns and making code more testable and maintainable.

## Session State Patterns

All session state keys MUST follow this pattern:

```python
# Format: f"{self.widget_id}_{purpose}"
f"{self.widget_id}_period"              # User selections
f"{self.widget_id}_selected_holdings"   # Multi-select state
f"{self.widget_id}_include_portfolio"   # Toggle options
f"{self.widget_id}_custom_symbols"      # User-added data
```

## Error Handling Patterns

```python
# Data Layer: Return typed error results
def _fetch_data(self, symbols):
    try:
        data = self.storage.get_data(...)
        if not data:
            return {'status': 'error', 'message': 'No data available', 'symbols': symbols}
        return {'status': 'success', 'data': data}
    except Exception as e:
        return {'status': 'error', 'message': str(e), 'exception': e}

# UI Layer: Display user-friendly errors
result = self._fetch_data(symbols)
if result['status'] == 'error':
    st.error(f"Failed to fetch data: {result['message']}")
    return
```

## Success Metrics

- Render method: <100 lines (currently 350+)
- Helper methods: <50 lines each
- Business logic: Pure functions, unit testable
- Data fetching: Separated from calculations
- UI rendering: Only Streamlit calls
- Session state: Consistent naming pattern
- Error handling: User-friendly messages
- Functionality: 100% preservation verified manually
