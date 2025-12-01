# Feature Specification: Correlation Matrix Widget UI Improvements

## Problem Statement

The correlation matrix widget currently has a cluttered and confusing UI for instrument selection. Users need to:
1. Easily distinguish between their portfolio holdings, benchmark instruments, and custom symbols
2. Have a clear, organized interface for selecting which instruments to include in the correlation analysis
3. See their selections clearly with better visual organization

### Current Issues
- Holdings and benchmarks are mixed in the same selection area
- Custom symbols that have been added are not clearly displayed
- The "num_cols" layout could be better organized
- Visual hierarchy is unclear - hard to scan and understand options
- The portfolio aggregate checkbox placement is inconsistent

## User Stories

**As a portfolio analyst**, I want to:
- Clearly see my portfolio holdings separated from benchmark options
- Easily add custom symbols for comparison without confusion
- View all my previous custom symbol additions in a manageable list
- Quickly select/deselect groups of instruments (e.g., all holdings, all benchmarks)

**As a dashboard user**, I want:
- A clean, professional interface that doesn't feel cluttered
- Clear visual separation between different types of instruments
- The ability to remove custom symbols I've added if needed
- Consistent, predictable UI patterns that match other widgets

## Functional Requirements

### FR1: Organized Instrument Selection
- **FR1.1**: Display portfolio holdings in a dedicated expander section (e.g., "Portfolio Holdings (3)")
- **FR1.2**: Display benchmark instruments in a separate expander section (e.g., "Benchmark Instruments")
- **FR1.3**: Display custom symbols in their own expander section with remove buttons (e.g., "Custom Symbols (2)")
- **FR1.4**: Use st.divider() between major sections for clear visual separation

### FR2: Enhanced Custom Symbol Management
- **FR2.1**: Show all previously added custom symbols in a list format
- **FR2.2**: Allow removal of custom symbols with a clear "X" or remove button
- **FR2.3**: Validate symbol input before adding: non-empty, uppercase alphanumeric + dots/dashes only, length 1-10 characters
- **FR2.4**: Show feedback when a symbol is added or removed (success message, duplicate warning, validation error)

### FR3: Selection Management
- **FR3.1**: Provide "Select All" / "Deselect All" buttons for holdings (sets all checkboxes to true/false regardless of current state)
- **FR3.2**: Provide "Select All" / "Deselect All" buttons for benchmarks (sets all checkboxes to true/false regardless of current state)
- **FR3.3**: Remember selections in session state across reruns
- **FR3.4**: Visual indication uses Streamlit's default checkbox styling; expander titles show selection count (e.g., "Portfolio Holdings (3/5 selected)")

### FR4: Portfolio Aggregate
- **FR4.1**: Move portfolio aggregate checkbox to a more prominent position
- **FR4.2**: Add tooltip explaining what "Portfolio" represents
- **FR4.3**: Make it clear this is an aggregate of selected holdings

### FR5: Visual Polish
- **FR5.1**: Use consistent spacing with st.divider()
- **FR5.2**: Use st.expander() for collapsible sections
- **FR5.3**: Align with Professional UI Standards from constitution
- **FR5.4**: Use appropriate column layouts (no more than 4 columns)

## Non-Functional Requirements

### NFR1: Performance
- Widget render time must remain under 2 seconds with 20+ instruments (baseline: current implementation ~1.5s)
- Session state operations should be efficient (list operations O(n) acceptable for <50 items)

### NFR2: Usability
- Changes should be intuitive to existing users
- No learning curve for the improved interface

### NFR3: Maintainability
- Code should follow constitution principles
- Clear separation of concerns in UI sections
- Well-documented state management

## Out of Scope

- Changes to correlation calculation logic
- Changes to heatmap visualization
- Backend data fetching improvements
- Multi-widget state sharing
- Saved instrument selection presets

## Success Criteria

1. ✅ Users can easily distinguish between holdings, benchmarks, and custom symbols
2. ✅ Custom symbols can be added and removed through the UI
3. ✅ Visual hierarchy is clear with proper use of expanders/dividers
4. ✅ All selections persist correctly in session state
5. ✅ Widget remains within st.container(border=True) per constitution
6. ✅ Code follows Professional UI Standards (Principle IV)
7. ✅ No regression in correlation calculation accuracy

## Design Considerations

### Option A: Expanders (Recommended)
```
with st.expander("Portfolio Holdings (3)", expanded=True):
    [Select All] [Deselect All]
    ☑ VGS  ☑ VAS  ☑ IVV

with st.expander("Benchmark Instruments", expanded=False):
    [Select All] [Deselect All]
    ☐ SPY - S&P 500
    ☐ QQQ - Nasdaq 100
    ...

with st.expander("Custom Symbols (2)", expanded=True):
    AAPL  [×]
    VEU.AX  [×]
    [Add Custom Symbol] [___________]
```

### Option B: Tabs
```
Tab: Holdings | Benchmarks | Custom
```

**Recommendation**: Option A (Expanders) - provides better overview and matches Streamlit conventions

## Acceptance Tests

### Test 1: Instrument Selection
1. Open correlation matrix widget
2. Verify holdings are in separate expander
3. Select/deselect individual holdings
4. Use "Select All" button
5. Verify selections persist after interaction

### Test 2: Custom Symbol Management
1. Add a custom symbol (e.g., AAPL)
2. Verify it appears in custom symbols section
3. Add another symbol (e.g., MSFT)
4. Remove one symbol using X button
5. Verify removal is immediate
6. Verify correlation matrix updates correctly

### Test 3: Visual Organization
1. Verify all content is within bordered container
2. Check proper use of st.divider() between sections
3. Verify expanders work correctly
4. Check responsive layout on different screen sizes

### Test 4: Constitution Compliance
1. Verify no global mutable state
2. Verify session state is used correctly
3. Verify no HEREDOCs or string-based code generation
4. Verify descriptive variable names
5. Verify proper error handling

## Dependencies

- Streamlit >= 1.28 (for expander features)
- No new external dependencies required
- Existing session state management
- Existing storage adapter

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Session state complexity | Medium | Clear documentation, careful testing |
| Breaking existing user workflows | Low | Maintain same functionality, improve UX |
| Performance with many custom symbols | Low | Limit to reasonable number (e.g., 20) |

## Timeline Estimate

- Analysis & Design: 1 hour (DONE via this spec)
- Implementation: 2-3 hours
- Testing: 1 hour
- Documentation: 30 minutes

**Total**: ~5 hours
