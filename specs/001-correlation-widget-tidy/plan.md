# Implementation Plan: Correlation Matrix Widget UI Improvements

**Branch**: `001-correlation-widget-tidy` | **Date**: 2025-12-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-correlation-widget-tidy/spec.md`

## Summary

Reorganize the correlation matrix widget UI to provide clear visual separation between portfolio holdings, benchmark instruments, and custom symbols. Primary approach: use Streamlit expanders to create collapsible sections for each instrument category, add select all/deselect all functionality, and implement custom symbol management with add/remove capabilities. All changes must adhere to Professional UI Standards (Constitution Principle IV) and remain within the bordered container structure.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Streamlit 1.39+, pandas, numpy, plotly  
**Storage**: SQLite (via storage_adapter) - no schema changes required  
**Testing**: Manual UI testing, visual verification  
**Target Platform**: Web browser via Streamlit  
**Project Type**: Single web application (Streamlit dashboard)  
**Performance Goals**: Widget render time <2 seconds with 20+ instruments  
**Constraints**: All UI elements must remain within `st.container(border=True)` block  
**Scale/Scope**: Single widget file (~400 LOC), handling up to 50 total instruments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Data Persistence First
✅ **PASS** - No changes to data persistence layer. All selections stored in Streamlit session state (ephemeral by design for UI state).

### Principle II: Calculation Transparency  
✅ **PASS** - No changes to correlation calculation logic.

### Principle III: Widget Modularity
✅ **PASS** - Changes are isolated to correlation_matrix_widget.py. No cross-widget dependencies introduced.

### Principle IV: Professional UI Standards
✅ **PASS** - This feature specifically enforces this principle:
- Proper use of `st.container(border=True)` (existing, preserved)
- Use of `st.expander()` for organization
- Use of `st.divider()` for section breaks
- All content properly indented within container

### Principle V: Code Readability
✅ **PASS** - Refactoring will improve readability:
- Extract selection UI into helper methods
- Clear, descriptive variable names
- Logical organization of UI sections

### Forbidden Practice 1: HEREDOCs
✅ **PASS** - No code generation or dynamic execution. Pure Streamlit UI components.

### Forbidden Practice 2: Global Mutable State
✅ **PASS** - Using Streamlit session state exclusively (per constitution guidelines).

### Forbidden Practice 3: Silent Failures
✅ **PASS** - Symbol addition provides feedback, invalid inputs show warnings.

**Overall**: ✅ **ALL GATES PASSED** - Proceed with implementation.

## Project Structure

### Documentation (this feature)

```text
specs/001-correlation-widget-tidy/
├── plan.md              # This file
├── spec.md              # Feature specification (created)
├── research.md          # Phase 0: UI patterns, Streamlit best practices
├── data-model.md        # Phase 1: Session state structure (N/A - using existing)
├── quickstart.md        # Phase 1: Testing guide
└── contracts/           # N/A - no API contracts for UI work
```

### Source Code (repository root)

```text
src/
├── widgets/
│   ├── base_widget.py                    # [UNCHANGED] Base class interface
│   ├── correlation_matrix_widget.py      # [MODIFIED] Main changes here
│   ├── portfolio_summary_widget.py       # [UNCHANGED]
│   ├── benchmark_comparison_widget.py    # [UNCHANGED]
│   ├── holdings_breakdown_widget.py      # [UNCHANGED]
│   ├── performance_widget.py             # [UNCHANGED]
│   └── dividend_analysis_widget.py       # [UNCHANGED]
├── controllers/
│   └── dashboard.py                      # [UNCHANGED]
├── services/
│   └── storage_adapter.py                # [UNCHANGED]
└── utils/
    └── performance_metrics.py            # [UNCHANGED]

# No test directory changes - manual UI testing
```

**Structure Decision**: Single file modification approach. All changes isolated to `correlation_matrix_widget.py` to maintain widget modularity (Constitution Principle III). No new files needed as this is UI reorganization within existing widget.

## Complexity Tracking

> No constitutional violations - this section intentionally left empty.

---

## Phase 0: Outline & Research

### Research Tasks

1. **Streamlit Expander Best Practices**
   - How to manage expanded state in session state
   - Performance with multiple expanders
   - Nested container behavior (expander inside bordered container)

2. **Session State Patterns**
   - Current session state keys used: `{widget_id}_selected_holdings`, `{widget_id}_selected_additional`
   - Need to add: `{widget_id}_custom_symbols_list` (separate from selected)
   - Pattern for "select all" / "deselect all" functionality

3. **UI Layout Patterns**
   - Optimal column count for checkbox grids (currently 4)
   - Button placement for bulk actions
   - Custom symbol input + remove button layout

### Known Answers

**Q**: Does Streamlit support removing items from lists in session state?  
**A**: Yes, direct list manipulation works: `st.session_state[key].remove(item)`

**Q**: Can expanders be placed inside bordered containers?  
**A**: Yes, confirmed working pattern in Streamlit

**Q**: How to handle "select all" without causing rerun loop?  
**A**: Use button click to update session state, then let natural rerun refresh UI

### Research Deliverable

Create `research.md` documenting:
- Expander state management patterns
- Session state structure for custom symbols
- Bulk selection implementation approach
- Code examples from Streamlit docs

---

## Phase 1: Design & Contracts

### Data Model

**Session State Structure** (document in `data-model.md`):

```python
# Current keys (existing):
st.session_state[f"{widget_id}_selected_holdings"]     # List[str] - selected holding symbols
st.session_state[f"{widget_id}_selected_additional"]   # List[str] - selected benchmarks + custom symbols (mixed)
st.session_state[f"{widget_id}_period"]                # str - time period selection
st.session_state[f"{widget_id}_include_portfolio"]     # bool - portfolio aggregate checkbox
st.session_state[f"{widget_id}_custom_symbol"]         # str - text input for custom symbol

# New keys (to be added):
# None needed - custom symbols are already in selected_additional list

# Custom symbol extraction pattern:
# custom_symbols = [s for s in selected_additional if s not in self.AVAILABLE_INSTRUMENTS]
# This filters runtime to distinguish user-added symbols from predefined benchmarks
# Custom symbols persist in selected_additional until explicitly removed via UI
```

**UI Component Hierarchy**:
```
st.container(border=True)                              # Existing outer container
├── Time Period Selection                              # [UNCHANGED]
├── st.divider()                                      # [NEW]
├── st.expander("Portfolio Holdings (N)")              # [NEW - was flat checkboxes]
│   ├── [Select All] [Deselect All] buttons          # [NEW]
│   └── Checkbox grid (4 columns)                      # [REFACTORED]
├── st.expander("Portfolio Aggregate")                 # [NEW - was standalone checkbox]
│   └── Checkbox + explanation                         # [REFACTORED]
├── st.divider()                                      # [NEW]
├── st.expander("Benchmark Instruments")               # [NEW - was flat checkboxes]
│   ├── [Select All] [Deselect All] buttons          # [NEW]
│   └── Checkbox grid (4 columns)                      # [REFACTORED]
├── st.divider()                                      # [NEW]
├── st.expander("Custom Symbols (M)", expanded=True)   # [NEW]
│   ├── Custom symbol list with remove buttons        # [NEW]
│   └── Add symbol input + button                     # [REFACTORED]
└── [Rest of widget: data fetching, heatmap, stats]   # [UNCHANGED]
```

### Quickstart Guide

Create `quickstart.md` with:
1. How to test the UI changes
2. Checklist for visual verification
3. Session state debugging tips
4. Screenshots of before/after (optional)

### UI Wireframe

```
╔═══════════════════════════════════════════════════════════╗
║ Correlation Matrix Widget                                 ║
╠═══════════════════════════════════════════════════════════╣
║ Time Period: [6 Months ▼]                                ║
║ ─────────────────────────────────────────────────────────║
║ ▶ Portfolio Holdings (3)                                  ║
║   [Select All] [Deselect All]                            ║
║   ☑ VGS    ☑ VAS    ☑ IVV                               ║
║                                                           ║
║ ▶ Portfolio Aggregate                                     ║
║   ☑ Include Portfolio (aggregate of selected holdings)   ║
║                                                           ║
║ ─────────────────────────────────────────────────────────║
║ ▼ Benchmark Instruments                                   ║
║   [Select All] [Deselect All]                            ║
║   ☐ SPY - S&P 500        ☐ EFA - EAFE                   ║
║   ☑ QQQ - Nasdaq 100     ☐ EEM - Emerging Markets       ║
║   ☐ DIA - Dow Jones      ☐ AGG - US Bonds               ║
║   ...                                                     ║
║                                                           ║
║ ─────────────────────────────────────────────────────────║
║ ▼ Custom Symbols (2)                                      ║
║   AAPL    [×]                                            ║
║   VEU.AX  [×]                                            ║
║                                                           ║
║   Add Symbol: [____________]  [Add]                      ║
║ ─────────────────────────────────────────────────────────║
║ [Calculating correlations spinner...]                    ║
║ [Heatmap display]                                        ║
║ [Statistics display]                                     ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Phase 2: Implementation Plan (High-Level)

**Note**: Detailed task breakdown will be created by `/speckit.tasks` command in `tasks.md`

### Implementation Approach

**Strategy**: Incremental refactoring - extract current functionality into helper methods, then rebuild UI using expanders.

**Key Implementation Steps**:

1. **Refactor Current Code** (maintain functionality)
   - Extract holdings checkbox rendering to `_render_holdings_selection()`
   - Extract benchmark checkbox rendering to `_render_benchmark_selection()`
   - Extract custom symbol input to `_render_custom_symbols()`
   - **Docstring Requirements**: Each helper method must include: purpose summary, parameters with type hints, return value description, session state keys accessed/modified, side effects (e.g., st.rerun() calls)

2. **Add Expander Structure**
   - Wrap holdings section in expander with dynamic count
   - Wrap benchmarks section in expander
   - Create custom symbols expander with list display

3. **Implement Bulk Selection**
   - Add select all/deselect all buttons for holdings
   - Add select all/deselect all buttons for benchmarks
   - Update session state on button clicks

4. **Implement Custom Symbol Management**
   - Display custom symbols as removable chips/list items
   - Add remove button functionality
   - Preserve add symbol input functionality

5. **Visual Polish**
   - Add st.divider() between major sections
   - Adjust column counts if needed
   - Add tooltips where helpful
   - Verify all indentation within container

6. **Testing**
   - Test all selection scenarios
   - Verify session state persistence
   - Check edge cases (no holdings, many customs, etc.)
   - Visual regression check against constitution standards

### Files to Modify

1. `src/widgets/correlation_matrix_widget.py`
   - Estimated changes: ~150 lines modified/added
   - No breaking changes to BaseWidget interface
   - All changes within `render()` method and new helper methods

### Testing Checklist

- [ ] Holdings selection works (individual + select all)
- [ ] Benchmark selection works (individual + select all)
- [ ] Custom symbols can be added
- [ ] Custom symbols can be removed
- [ ] Session state persists across interactions
- [ ] Expanders expand/collapse correctly
- [ ] All content within bordered container
- [ ] Dividers appear between sections
- [ ] Portfolio aggregate checkbox in logical position
- [ ] No console errors or warnings
- [ ] Performance acceptable with 20+ instruments
- [ ] Constitution compliance verified

---

## Success Metrics

**Technical Metrics**:
- Code follows constitution (verified by checklist)
- Widget render time remains <2s
- No increase in session state memory usage
- Zero regressions in correlation calculation

**UX Metrics** (manual verification):
- Visual hierarchy is immediately clear
- Users can find each section in <3 seconds
- Custom symbol management is intuitive
- Bulk selection reduces clicks by 80% for "all" scenarios

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Session state bugs | Low | Medium | Thorough testing, isolated changes |
| UI performance degradation | Low | Low | Profile with 50 instruments, optimize if needed |
| Breaking existing functionality | Low | High | Incremental approach, test each step |
| Streamlit version incompatibility | Very Low | Medium | Using standard components, no experimental APIs |

---

## Next Steps

1. ✅ Spec created (`spec.md`)
2. ✅ Plan created (`plan.md`)
3. ✅ Constitution check passed
4. ⏳ Phase 0: Create `research.md` (Streamlit patterns)
5. ⏳ Phase 1: Create `data-model.md` (session state structure)
6. ⏳ Phase 1: Create `quickstart.md` (testing guide)
7. ⏳ Phase 2: Run `/speckit.tasks` to generate detailed task breakdown
8. ⏳ Implementation
9. ⏳ Testing & validation
10. ⏳ Merge to master

**Status**: Ready for Phase 0 research
