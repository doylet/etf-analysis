# Implementation Tasks: Widget Architecture Refactoring

**Branch**: `002-widget-architecture-refactor` | **Date**: 2025-12-01  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Task Execution Strategy

This feature involves migrating production widgets to the new layered architecture. The layered base class and reference implementation already exist. This task list focuses on:

1. Applying the refactored architecture to production widgets
2. Creating unit tests for business logic
3. Validating functionality preservation
4. Documenting the migration

**Parallel Execution**: Tasks marked with [P] can run in parallel within their phase.  
**Dependencies**: Each phase must complete before the next begins.

---

## Phase 1: Setup & Environment Verification (T001-T004)

**Goal**: Verify prerequisites and prepare for migration

### T001 - Verify layered base class exists [P]
**Type**: Verification  
**Files**: `src/widgets/layered_base_widget.py`  
**Action**: Confirm LayeredBaseWidget class is present and has all helper methods  
**Validation**: File exists with 200+ lines, contains session state helpers, error handling patterns

### T002 - Verify reference implementation exists [P]
**Type**: Verification  
**Files**: `src/backups/correlation_matrix_widget_refactored.py`  
**Action**: Confirm refactored proof of concept exists as template  
**Validation**: File exists with three-layer architecture, 45-line render method

### T003 - Review migration guide [P]
**Type**: Documentation  
**Files**: `specs/002-widget-architecture-refactor/quickstart.md`  
**Action**: Read migration checklist and patterns  
**Validation**: Understand 7-step migration process

### T004 - Create git branch for migration
**Type**: Setup  
**Files**: N/A  
**Action**: Create feature branch or verify current branch is appropriate  
**Validation**: On appropriate branch for widget architecture changes

---

## Phase 2: Backup Production Widgets (T005-T011)

**Goal**: Create backups of all current production widgets before modification

### T005 - Backup correlation_matrix_widget.py
**Type**: Backup  
**Files**: `src/widgets/correlation_matrix_widget.py` → `src/backups/correlation_matrix_widget_pre_migration.py`  
**Action**: Copy current production version to backups with descriptive name  
**Validation**: Backup file exists in src/backups/

### T006 - Backup portfolio_summary_widget.py [P]
**Type**: Backup  
**Files**: `src/widgets/portfolio_summary_widget.py` → `src/backups/portfolio_summary_widget_original.py`  
**Action**: Create backup of original  
**Validation**: Backup file created

### T007 - Backup dividend_analysis_widget.py [P]
**Type**: Backup  
**Files**: `src/widgets/dividend_analysis_widget.py` → `src/backups/dividend_analysis_widget_original.py`  
**Action**: Create backup of original  
**Validation**: Backup file created

### T008 - Backup benchmark_comparison_widget.py [P]
**Type**: Backup  
**Files**: `src/widgets/benchmark_comparison_widget.py` → `src/backups/benchmark_comparison_widget_original.py`  
**Action**: Create backup of original  
**Validation**: Backup file created

### T009 - Backup performance_widget.py [P]
**Type**: Backup  
**Files**: `src/widgets/performance_widget.py` → `src/backups/performance_widget_original.py`  
**Action**: Create backup of original  
**Validation**: Backup file created

### T010 - Backup holdings_breakdown_widget.py [P]
**Type**: Backup  
**Files**: `src/widgets/holdings_breakdown_widget.py` → `src/backups/holdings_breakdown_widget_original.py`  
**Action**: Create backup of original  
**Validation**: Backup file created

### T011 - Update backup documentation
**Type**: Documentation  
**Files**: `src/backups/README.md`  
**Action**: Add entries for all new backup files  
**Validation**: README lists all backups with purposes

---

## Phase 3: Migrate Correlation Matrix Widget (T012-T018)

**Goal**: Apply refactored architecture to production correlation matrix widget

### T012 - Replace correlation_matrix_widget.py with refactored version
**Type**: Implementation  
**Files**: `src/widgets/correlation_matrix_widget.py`  
**Action**: Copy content from `src/backups/correlation_matrix_widget_refactored.py` to production file  
**Dependencies**: T005 (backup must exist first)  
**Validation**: Production file now has three-layer architecture with 45-line render method

### T013 - Update imports in correlation_matrix_widget.py
**Type**: Implementation  
**Files**: `src/widgets/correlation_matrix_widget.py`  
**Action**: Change from `from .base_widget import BaseWidget` to `from .layered_base_widget import LayeredBaseWidget`  
**Validation**: Import statement updated, class inherits from LayeredBaseWidget

### T014 - Test correlation widget in dashboard - basic functionality
**Type**: Testing  
**Files**: `src/widgets/correlation_matrix_widget.py`  
**Action**: Run Streamlit app, navigate to correlation widget, verify it renders without errors  
**Validation**: Widget displays, no Python exceptions in console

### T015 - Test correlation widget - holdings selection
**Type**: Testing  
**Files**: `src/widgets/correlation_matrix_widget.py`  
**Action**: Test select all, deselect all, individual selection checkboxes  
**Validation**: Selection controls work identically to original

### T016 - Test correlation widget - benchmark selection
**Type**: Testing  
**Files**: `src/widgets/correlation_matrix_widget.py`  
**Action**: Test benchmark selection, custom symbols, remove functionality  
**Validation**: Benchmark controls work identically to original

### T017 - Test correlation widget - correlation calculations
**Type**: Testing  
**Files**: `src/widgets/correlation_matrix_widget.py`  
**Action**: Select various holdings/benchmarks, verify correlation matrix displays correctly  
**Validation**: Correlation heatmap, statistics, and key pairs display accurate data

### T018 - Test correlation widget - edge cases
**Type**: Testing  
**Files**: `src/widgets/correlation_matrix_widget.py`  
**Action**: Test with missing data, single symbol, custom symbols, portfolio aggregate  
**Validation**: Error handling works, missing data warnings display, edge cases handled gracefully

---

## Phase 4: Create Unit Tests for Correlation Logic (T019-T025)

**Goal**: Add unit tests for pure business logic functions

### T019 - Create test file structure
**Type**: Setup  
**Files**: `tests/widgets/test_correlation_calculations.py`  
**Action**: Use existing test file or verify it has all necessary tests  
**Validation**: Test file exists with imports

### T020 - Add tests for _calculate_correlation_matrix [P]
**Type**: Testing  
**Files**: `tests/widgets/test_correlation_calculations.py`  
**Action**: Test basic correlation, negative correlation, single column edge case  
**Validation**: 3+ test functions for correlation matrix calculation

### T021 - Add tests for _calculate_correlation_pairs [P]
**Type**: Testing  
**Files**: `tests/widgets/test_correlation_calculations.py`  
**Action**: Test pair extraction, sorting, edge cases  
**Validation**: 2+ test functions for correlation pairs

### T022 - Add tests for _validate_custom_symbol [P]
**Type**: Testing  
**Files**: `tests/widgets/test_correlation_calculations.py`  
**Action**: Test valid symbols, invalid characters, length validation, empty strings  
**Validation**: 5+ test functions covering validation logic

### T023 - Add tests for _calculate_benchmark_comparison [P]
**Type**: Testing  
**Files**: `tests/widgets/test_correlation_calculations.py`  
**Action**: Test portfolio vs benchmark correlation extraction  
**Validation**: 2+ test functions for benchmark comparison

### T024 - Add tests for _calculate_correlation_analysis [P]
**Type**: Testing  
**Files**: `tests/widgets/test_correlation_calculations.py`  
**Action**: Test full analysis dataclass construction  
**Validation**: 2+ test functions for complete analysis

### T025 - Run all unit tests
**Type**: Validation  
**Files**: `tests/widgets/test_correlation_calculations.py`  
**Action**: Execute pytest and verify all tests pass  
**Validation**: All tests pass, 15+ assertions successful

---

## Phase 5: Migrate Simpler Widgets (T026-T050)

**Goal**: Apply layered architecture to simpler widgets to build confidence

### T026 - Analyze performance_widget.py complexity
**Type**: Analysis  
**Files**: `src/widgets/performance_widget.py`  
**Action**: Review widget, identify layers, estimate migration effort (should be simpler than correlation)  
**Validation**: Understand widget structure, identify pure functions to extract

### T027 - Refactor performance_widget.py - change base class
**Type**: Implementation  
**Files**: `src/widgets/performance_widget.py`  
**Action**: Change inheritance from BaseWidget to LayeredBaseWidget  
**Dependencies**: T009 (backup must exist)  
**Validation**: Import and class declaration updated

### T028 - Refactor performance_widget.py - extract data layer methods
**Type**: Implementation  
**Files**: `src/widgets/performance_widget.py`  
**Action**: Create `_fetch_*` and `_prepare_*` methods for data operations  
**Validation**: Data fetching logic isolated from business logic

### T029 - Refactor performance_widget.py - extract logic layer methods
**Type**: Implementation  
**Files**: `src/widgets/performance_widget.py`  
**Action**: Create static `_calculate_*` methods for pure calculations  
**Validation**: Business logic extracted to pure functions with type hints

### T030 - Refactor performance_widget.py - restructure render method
**Type**: Implementation  
**Files**: `src/widgets/performance_widget.py`  
**Action**: Simplify render() to orchestration, create `_render_*` helper methods for UI  
**Validation**: render() is <100 lines, calls layer methods appropriately

### T031 - Test performance_widget.py in dashboard
**Type**: Testing  
**Files**: `src/widgets/performance_widget.py`  
**Action**: Run app, verify widget displays correctly, test interactions  
**Validation**: Widget works identically to original, no regressions

### T032 - Analyze dividend_analysis_widget.py complexity
**Type**: Analysis  
**Files**: `src/widgets/dividend_analysis_widget.py`  
**Action**: Review widget structure, identify layers  
**Validation**: Understand widget, ready to refactor

### T033 - Refactor dividend_analysis_widget.py - change base class
**Type**: Implementation  
**Files**: `src/widgets/dividend_analysis_widget.py`  
**Action**: Change inheritance to LayeredBaseWidget  
**Dependencies**: T007 (backup must exist)  
**Validation**: Import and class declaration updated

### T034 - Refactor dividend_analysis_widget.py - extract data layer
**Type**: Implementation  
**Files**: `src/widgets/dividend_analysis_widget.py`  
**Action**: Create data fetching methods  
**Validation**: Data operations isolated

### T035 - Refactor dividend_analysis_widget.py - extract logic layer
**Type**: Implementation  
**Files**: `src/widgets/dividend_analysis_widget.py`  
**Action**: Create pure calculation methods  
**Validation**: Business logic is testable

### T036 - Refactor dividend_analysis_widget.py - restructure render
**Type**: Implementation  
**Files**: `src/widgets/dividend_analysis_widget.py`  
**Action**: Simplify render() orchestration  
**Validation**: render() <100 lines

### T037 - Test dividend_analysis_widget.py in dashboard
**Type**: Testing  
**Files**: `src/widgets/dividend_analysis_widget.py`  
**Action**: Verify functionality preservation  
**Validation**: No regressions

### T038 - Analyze holdings_breakdown_widget.py complexity
**Type**: Analysis  
**Files**: `src/widgets/holdings_breakdown_widget.py`  
**Action**: Review widget structure  
**Validation**: Ready to refactor

### T039 - Refactor holdings_breakdown_widget.py - change base class
**Type**: Implementation  
**Files**: `src/widgets/holdings_breakdown_widget.py`  
**Action**: Change inheritance to LayeredBaseWidget  
**Dependencies**: T010 (backup must exist)  
**Validation**: Class declaration updated

### T040 - Refactor holdings_breakdown_widget.py - extract data layer
**Type**: Implementation  
**Files**: `src/widgets/holdings_breakdown_widget.py`  
**Action**: Create data methods  
**Validation**: Data layer isolated

### T041 - Refactor holdings_breakdown_widget.py - extract logic layer
**Type**: Implementation  
**Files**: `src/widgets/holdings_breakdown_widget.py`  
**Action**: Create calculation methods  
**Validation**: Pure functions extracted

### T042 - Refactor holdings_breakdown_widget.py - restructure render
**Type**: Implementation  
**Files**: `src/widgets/holdings_breakdown_widget.py`  
**Action**: Simplify render orchestration  
**Validation**: render() concise

### T043 - Test holdings_breakdown_widget.py in dashboard
**Type**: Testing  
**Files**: `src/widgets/holdings_breakdown_widget.py`  
**Action**: Verify functionality  
**Validation**: Works correctly

### T044 - Analyze benchmark_comparison_widget.py complexity
**Type**: Analysis  
**Files**: `src/widgets/benchmark_comparison_widget.py`  
**Action**: Review structure  
**Validation**: Ready to refactor

### T045 - Refactor benchmark_comparison_widget.py - apply layered architecture
**Type**: Implementation  
**Files**: `src/widgets/benchmark_comparison_widget.py`  
**Action**: Apply full three-layer refactoring (base class, data, logic, UI layers)  
**Dependencies**: T008 (backup must exist)  
**Validation**: Three layers separated, render() <100 lines

### T046 - Test benchmark_comparison_widget.py in dashboard
**Type**: Testing  
**Files**: `src/widgets/benchmark_comparison_widget.py`  
**Action**: Verify functionality  
**Validation**: Works correctly

### T047 - Analyze portfolio_summary_widget.py complexity
**Type**: Analysis  
**Files**: `src/widgets/portfolio_summary_widget.py`  
**Action**: Review structure (likely most complex after correlation)  
**Validation**: Understand complexity

### T048 - Refactor portfolio_summary_widget.py - apply layered architecture
**Type**: Implementation  
**Files**: `src/widgets/portfolio_summary_widget.py`  
**Action**: Apply full three-layer refactoring  
**Dependencies**: T006 (backup must exist)  
**Validation**: Three layers separated

### T049 - Test portfolio_summary_widget.py in dashboard
**Type**: Testing  
**Files**: `src/widgets/portfolio_summary_widget.py`  
**Action**: Comprehensive functionality testing  
**Validation**: Complex widget works correctly

### T050 - Full dashboard regression test
**Type**: Testing  
**Files**: All widgets  
**Action**: Test complete dashboard workflow - select instruments, view all widgets, verify calculations  
**Validation**: All widgets work together, no interaction issues

---

## Phase 6: Create Unit Tests for All Widgets (T051-T056)

**Goal**: Add unit tests for business logic across all migrated widgets

### T051 - Create test_performance_calculations.py [P]
**Type**: Testing  
**Files**: `tests/widgets/test_performance_calculations.py`  
**Action**: Write unit tests for performance widget pure functions  
**Validation**: 10+ test functions covering performance calculations

### T052 - Create test_dividend_calculations.py [P]
**Type**: Testing  
**Files**: `tests/widgets/test_dividend_calculations.py`  
**Action**: Write unit tests for dividend widget pure functions  
**Validation**: 8+ test functions covering dividend calculations

### T053 - Create test_holdings_calculations.py [P]
**Type**: Testing  
**Files**: `tests/widgets/test_holdings_calculations.py`  
**Action**: Write unit tests for holdings breakdown widget  
**Validation**: 5+ test functions

### T054 - Create test_benchmark_calculations.py [P]
**Type**: Testing  
**Files**: `tests/widgets/test_benchmark_calculations.py`  
**Action**: Write unit tests for benchmark comparison widget  
**Validation**: 8+ test functions

### T055 - Create test_portfolio_calculations.py [P]
**Type**: Testing  
**Files**: `tests/widgets/test_portfolio_calculations.py`  
**Action**: Write unit tests for portfolio summary widget  
**Validation**: 12+ test functions (most complex widget)

### T056 - Run complete test suite
**Type**: Validation  
**Files**: All test files  
**Action**: Execute pytest on all widget tests  
**Validation**: 50+ tests pass, 0 failures

---

## Phase 7: Update Documentation (T057-T062)

**Goal**: Document the completed migration

### T057 - Update quickstart.md with lessons learned
**Type**: Documentation  
**Files**: `specs/002-widget-architecture-refactor/quickstart.md`  
**Action**: Add section on actual migration experience, common patterns discovered  
**Validation**: Migration guide reflects real-world insights

### T058 - Create migration completion summary
**Type**: Documentation  
**Files**: `specs/002-widget-architecture-refactor/migration-summary.md`  
**Action**: Document metrics - line counts before/after, test coverage, debug time improvements  
**Validation**: Comprehensive metrics comparison

### T059 - Update README.md in specs folder
**Type**: Documentation  
**Files**: `specs/002-widget-architecture-refactor/README.md`  
**Action**: Mark feature as completed, update status, link to migration summary  
**Validation**: README reflects completed migration

### T060 - Update constitution.md if needed [P]
**Type**: Documentation  
**Files**: `constitution.md`  
**Action**: Add guidance on layered widget architecture if not already present  
**Validation**: Constitution references three-layer pattern

### T061 - Update project README [P]
**Type**: Documentation  
**Files**: `README.md` (root)  
**Action**: Add note about widget architecture in project documentation  
**Validation**: Root README mentions layered widgets

### T062 - Create widget development guide
**Type**: Documentation  
**Files**: `docs/widget-development-guide.md` (create if needed)  
**Action**: Write comprehensive guide for creating new widgets using LayeredBaseWidget  
**Validation**: New developers can create widgets following the guide

---

## Phase 8: Cleanup & Finalization (T063-T067)

**Goal**: Clean up artifacts and prepare for merge

### T063 - Review all widget files for consistency
**Type**: Code Review  
**Files**: All widgets  
**Action**: Verify all widgets follow same patterns (session state, error handling, docstrings)  
**Validation**: Consistent code style across all widgets

### T064 - Check for unused imports and code
**Type**: Cleanup  
**Files**: All widgets  
**Action**: Remove any dead code, unused imports from refactoring  
**Validation**: Clean, minimal imports

### T065 - Verify type hints completeness
**Type**: Quality  
**Files**: All widgets  
**Action**: Ensure all methods have complete type annotations  
**Validation**: mypy or type checker passes (if available)

### T066 - Update CHANGELOG or release notes
**Type**: Documentation  
**Files**: `CHANGELOG.md` or similar  
**Action**: Document widget architecture refactoring as major enhancement  
**Validation**: Change documented for future reference

### T067 - Prepare merge/commit message
**Type**: Git  
**Files**: N/A  
**Action**: Write comprehensive commit message explaining refactoring scope and benefits  
**Validation**: Commit message is clear and detailed

---

## Summary

**Total Tasks**: 67  
**Parallel Tasks**: 15 (marked with [P])  
**Estimated Complexity**: High (comprehensive refactoring of 6 widgets + tests + documentation)  
**Key Risk**: Preserving functionality while restructuring - extensive testing required  
**Success Criteria**: All widgets work identically to originals, 50+ unit tests pass, render methods <100 lines

## Execution Notes

1. **Incremental Testing**: Test each widget immediately after refactoring before moving to next
2. **Backup Safety**: All backups created before any modifications
3. **Unit Test Value**: Tests prove pure functions work independently, dramatically improving debuggability
4. **Pattern Consistency**: Each widget follows same three-layer pattern for maintainability
5. **Documentation Critical**: Guide future widget development with comprehensive docs
