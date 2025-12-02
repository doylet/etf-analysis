# Widget Backups

This folder contains reference implementations and backups from the widget architecture refactoring project.

## Files

### Pre-Migration Backups (created before layered architecture migration)

- **correlation_matrix_widget_pre_migration.py** - Correlation matrix widget before layered architecture (feature 001 improvements included)
- **portfolio_summary_widget_original.py** - Original portfolio summary widget
- **dividend_analysis_widget_original.py** - Original dividend analysis widget
- **benchmark_comparison_widget_original.py** - Original benchmark comparison widget
- **performance_widget_original.py** - Original performance widget
- **holdings_breakdown_widget_original.py** - Original holdings breakdown widget

### Reference Implementations

### correlation_matrix_widget_refactored.py
**Purpose**: Proof-of-concept refactored widget using layered architecture  
**Feature**: 002-widget-architecture-refactor  
**Status**: Reference implementation demonstrating the three-layer pattern  

**Architecture**:
- UI Layer: Streamlit rendering methods
- Data Layer: Storage access and validation  
- Logic Layer: Pure calculation functions (unit testable)

**Key Features**:
- 45-line orchestration `render()` method (vs 350+ original)
- 8 unit-testable pure functions (@staticmethod)
- Typed result structures (CorrelationAnalysis dataclass)
- Complete separation of concerns

### correlation_matrix_widget.py.original
**Purpose**: Original correlation matrix widget backup for comparison  
**Created**: During feature 002 specification phase  
**Status**: Archived reference

## Related Documentation

See `specs/002-widget-architecture-refactor/` for complete documentation:
- `README.md` - Overview and navigation
- `spec.md` - Requirements and user stories
- `plan.md` - Technical architecture
- `quickstart.md` - Migration guide
- `visual-comparison.md` - Before/after examples
- `summary.md` - Comprehensive analysis

## Current Production Widgets

Production widgets are in `src/widgets/`:
- `correlation_matrix_widget.py` - Current (feature 001 improvements applied)
- `layered_base_widget.py` - New base class for future refactoring
- Other widgets - Original monolithic structure

## Future Migration

When ready to migrate widgets to the layered architecture:
1. Review this reference implementation
2. Follow migration guide in `specs/002-widget-architecture-refactor/quickstart.md`
3. Use `layered_base_widget.py` as base class
4. Migrate gradually, one widget at a time
