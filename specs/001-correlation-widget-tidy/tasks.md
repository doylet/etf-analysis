# Tasks: Correlation Matrix Widget UI Improvements

**Input**: Design documents from `/specs/001-correlation-widget-tidy/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Tests**: NOT REQUIRED - Manual UI testing only (per spec NFR2)

**Organization**: Tasks organized incrementally - each phase builds cleanly on the previous

## Format: `- [ ] [ID] [P?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Phase 1: Setup & Preparation

**Purpose**: Ensure clean working environment and branch setup

- [X] T001 Verify feature branch `001-correlation-widget-tidy` is active and spec/plan docs exist
- [X] T002 Create backup of `src/widgets/correlation_matrix_widget.py` for reference
- [X] T003 [P] Review Streamlit expander documentation for state management patterns
- [X] T004 [P] Review current session state usage in correlation_matrix_widget.py

---

## Phase 2: Refactor Current Code (Maintain Functionality)

**Purpose**: Extract current UI rendering into helper methods without changing behavior

**⚠️ CRITICAL**: After each task, manually test that widget still works exactly as before

- [X] T005 Extract holdings checkbox rendering to `_render_holdings_selection()` method in src/widgets/correlation_matrix_widget.py
- [X] T006 Extract benchmark checkbox rendering to `_render_benchmark_selection()` method in src/widgets/correlation_matrix_widget.py
- [X] T007 Extract custom symbol input/display to `_render_custom_symbols()` method in src/widgets/correlation_matrix_widget.py
- [X] T008 Test widget functionality - verify all selections still work after refactoring

**Checkpoint**: Widget works identically to before - code is just organized into methods

---

## Phase 3: Implement Expander Structure

**Purpose**: Add expander UI components while preserving functionality

- [X] T009 Wrap holdings section in `st.expander()` with dynamic count display in src/widgets/correlation_matrix_widget.py
- [X] T010 Move portfolio aggregate checkbox into dedicated expander section in src/widgets/correlation_matrix_widget.py
- [X] T011 Wrap benchmarks section in `st.expander()` in src/widgets/correlation_matrix_widget.py
- [X] T012 Create custom symbols expander with list display in src/widgets/correlation_matrix_widget.py
- [X] T013 Test widget - verify expanders expand/collapse and all selections persist

**Checkpoint**: Widget now uses expanders - sections are collapsible and clearly organized

---

## Phase 4: Add Bulk Selection Controls

**Purpose**: Implement select all / deselect all functionality

- [X] T014 Add "Select All" button for holdings in `_render_holdings_selection()` in src/widgets/correlation_matrix_widget.py
- [X] T015 Add "Deselect All" button for holdings in `_render_holdings_selection()` in src/widgets/correlation_matrix_widget.py
- [X] T016 Add "Select All" button for benchmarks in `_render_benchmark_selection()` in src/widgets/correlation_matrix_widget.py
- [X] T017 Add "Deselect All" button for benchmarks in `_render_benchmark_selection()` in src/widgets/correlation_matrix_widget.py
- [X] T018 Test bulk selection buttons - verify they update session state correctly without rerun loops

**Checkpoint**: Users can quickly select/deselect all items in each category

---

## Phase 5: Enhance Custom Symbol Management

**Purpose**: Display custom symbols as a manageable list with remove functionality

- [X] T019 Separate custom symbols from AVAILABLE_INSTRUMENTS list in `_render_custom_symbols()` in src/widgets/correlation_matrix_widget.py
- [X] T020 Display custom symbols as individual rows with remove buttons in src/widgets/correlation_matrix_widget.py
- [X] T021 Implement remove button click handler to delete from session state in src/widgets/correlation_matrix_widget.py
- [X] T022 Add validation feedback for symbol addition (already exists, empty input) in src/widgets/correlation_matrix_widget.py
- [X] T023 Test custom symbol add/remove - verify clean add/remove cycle and UI feedback

**Checkpoint**: Custom symbols are clearly displayed and easily removed

---

## Phase 6: Visual Polish & UI Standards

**Purpose**: Apply Professional UI Standards (Constitution Principle IV)

- [X] T024 Add `st.divider()` between time period selection and holdings section in src/widgets/correlation_matrix_widget.py
- [X] T025 Add `st.divider()` between portfolio aggregate and benchmarks section in src/widgets/correlation_matrix_widget.py
- [X] T026 Add `st.divider()` between benchmarks and custom symbols section in src/widgets/correlation_matrix_widget.py
- [X] T027 Add helpful tooltip to portfolio aggregate checkbox explaining aggregation in src/widgets/correlation_matrix_widget.py
- [X] T028 Verify all content remains properly indented within `st.container(border=True)` in src/widgets/correlation_matrix_widget.py
- [X] T029 Update expander titles to show counts using format "Section Name (X)" for total items or "Section Name (X/Y selected)" for selections (e.g., "Portfolio Holdings (3/5 selected)", "Custom Symbols (2)") in src/widgets/correlation_matrix_widget.py
- [X] T030 Test visual appearance - verify clean spacing, borders, and professional look

**Checkpoint**: Widget has professional appearance with clear visual hierarchy

---

## Phase 7: Testing & Validation

**Purpose**: Comprehensive testing against acceptance criteria from spec.md

### Functional Testing

- [ ] T031 Test: Select/deselect individual holdings - verify persistence across reruns
- [ ] T032 Test: Use "Select All" for holdings - verify all selected immediately
- [ ] T033 Test: Use "Deselect All" for holdings - verify all deselected immediately
- [ ] T034 Test: Select/deselect individual benchmarks - verify persistence
- [ ] T035 Test: Use "Select All" for benchmarks - verify all selected
- [ ] T036 Test: Use "Deselect All" for benchmarks - verify all deselected
- [ ] T037 Test: Add custom symbol (e.g., AAPL) - verify it appears in custom section
- [ ] T038 Test: Add duplicate symbol - verify warning message appears
- [ ] T039 Test: Add empty symbol - verify validation message
- [ ] T040 Test: Remove custom symbol - verify immediate removal and correlation matrix updates
- [ ] T041 Test: Portfolio aggregate checkbox - verify aggregation works correctly
- [ ] T042 Test: Expanders - verify expand/collapse works smoothly

### Visual & UX Testing

- [ ] T043 Test: Verify all content within bordered container (no overflow)
- [ ] T044 Test: Verify dividers appear between major sections
- [ ] T045 Test: Verify expander titles show correct counts
- [ ] T046 Test: Check layout with 0 holdings (edge case)
- [ ] T047 Test: Check layout with 10+ holdings (many items)
- [ ] T048 Test: Check layout with 5+ custom symbols (many customs)
- [ ] T049 Test: Verify responsive layout at different browser widths

### Constitution Compliance

- [ ] T050 Verify: No global mutable state used (only session state)
- [ ] T051 Verify: No HEREDOCs or string-based code generation
- [ ] T052 Verify: Descriptive variable names throughout
- [ ] T053 Verify: Helper methods have clear docstrings
- [ ] T054 Verify: Error messages are user-friendly and actionable
- [ ] T055 Verify: Professional UI Standards followed (Principle IV)

### Performance Testing

- [ ] T056 Test: Widget render time with 3 holdings + 12 benchmarks + 5 customs
- [ ] T057 Test: Select All performance with 20+ items
- [ ] T058 Test: Session state memory usage is reasonable
- [ ] T059 Verify: No performance regression vs original implementation

**Checkpoint**: All tests pass - widget is production ready

---

## Phase 8: Documentation & Cleanup

**Purpose**: Final polish and documentation

- [ ] T060 Add/update docstrings for new helper methods in src/widgets/correlation_matrix_widget.py
- [ ] T061 Remove backup file created in T002
- [ ] T062 Create quickstart.md testing guide in specs/001-correlation-widget-tidy/
- [ ] T063 Update spec.md with actual implementation notes (if deviations occurred)
- [ ] T064 Take screenshots of before/after UI for documentation (optional)
- [ ] T065 Code review - verify code readability and adherence to constitution

**Checkpoint**: Feature is documented and ready for merge

---

## Dependencies & Execution Order

### Phase Dependencies (STRICT - Cannot skip)

1. **Phase 1 (Setup)**: No dependencies - start here
2. **Phase 2 (Refactor)**: Requires Phase 1 complete
3. **Phase 3 (Expanders)**: Requires Phase 2 complete (needs extracted methods)
4. **Phase 4 (Bulk Selection)**: Requires Phase 3 complete (needs expander structure)
5. **Phase 5 (Custom Symbols)**: Requires Phase 3 complete (needs expander structure)
6. **Phase 6 (Visual Polish)**: Requires Phases 3-5 complete (needs full UI structure)
7. **Phase 7 (Testing)**: Requires Phase 6 complete (test final implementation)
8. **Phase 8 (Documentation)**: Requires Phase 7 complete (document what works)

### Within Each Phase

- Tasks within a phase should generally be done in order
- Tasks marked [P] can be done in parallel
- After refactoring tasks (T005-T007), test before proceeding
- After UI changes (T009-T012), test before proceeding
- After bulk selection (T014-T017), test before proceeding
- After custom symbol changes (T019-T022), test before proceeding

### Critical Test Points

- ✅ After T008: Verify refactoring didn't break anything
- ✅ After T013: Verify expanders work and selections persist
- ✅ After T018: Verify bulk selection without rerun loops
- ✅ After T023: Verify custom symbol lifecycle
- ✅ After T030: Verify visual polish and constitution compliance
- ✅ After T059: All acceptance tests pass

---

## Parallel Opportunities

### Setup Phase (T001-T004)
```bash
# Can run simultaneously:
- T003 Review Streamlit docs
- T004 Review current session state
```

### Refactor Phase (T005-T007)
These MUST be sequential - each builds on render() method structure

### Testing Phase (T031-T059)
All test tasks can potentially run in parallel if using automated testing, but since we're doing manual testing, do them systematically in groups:

**Group 1 - Basic Functionality** (T031-T036): Test selection mechanics
**Group 2 - Custom Symbols** (T037-T040): Test custom symbol lifecycle
**Group 3 - Visual** (T043-T049): Test appearance and layout
**Group 4 - Compliance** (T050-T055): Code review checks
**Group 5 - Performance** (T056-T059): Performance validation

---

## Implementation Strategy

### Recommended Approach: Incremental with Testing

1. **Days 1-2**: Setup + Refactor (T001-T008)
   - Extract methods
   - Test that nothing breaks
   - **Commit**: "Refactor: Extract UI rendering methods"

2. **Day 2-3**: Add Expanders (T009-T013)
   - Add expander structure
   - Test all expanders work
   - **Commit**: "Feature: Add expander sections for organization"

3. **Day 3**: Bulk Selection (T014-T018)
   - Add select all buttons
   - Test button functionality
   - **Commit**: "Feature: Add select/deselect all buttons"

4. **Day 4**: Custom Symbol Management (T019-T023)
   - Enhance custom symbol UI
   - Test add/remove cycle
   - **Commit**: "Feature: Improve custom symbol management"

5. **Day 4-5**: Visual Polish (T024-T030)
   - Add dividers and tooltips
   - Test visual appearance
   - **Commit**: "Polish: Apply professional UI standards"

6. **Day 5**: Testing (T031-T059)
   - Comprehensive testing
   - Fix any issues found
   - **Commit**: "Test: Validate all acceptance criteria"

7. **Day 5**: Documentation (T060-T065)
   - Write docs
   - Final review
   - **Commit**: "Docs: Add testing guide and code documentation"

8. **Day 6**: Merge
   - Create PR
   - Review
   - Merge to master

### Stop Points for Validation

- **After T008**: Widget still works - safe to continue
- **After T013**: Expanders work - major UI change validated
- **After T023**: All new features implemented - ready for polish
- **After T030**: Feature complete - ready for full testing
- **After T059**: All tests pass - ready for documentation
- **After T065**: Fully documented - ready for merge

---

## Success Metrics (from spec.md)

✅ Users can easily distinguish between holdings, benchmarks, and custom symbols  
✅ Custom symbols can be added and removed through the UI  
✅ Visual hierarchy is clear with proper use of expanders/dividers  
✅ All selections persist correctly in session state  
✅ Widget remains within st.container(border=True) per constitution  
✅ Code follows Professional UI Standards (Principle IV)  
✅ No regression in correlation calculation accuracy

---

## Estimated Effort

- **Setup & Refactor** (T001-T008): 1-2 hours
- **Expanders** (T009-T013): 1 hour
- **Bulk Selection** (T014-T018): 1 hour
- **Custom Symbols** (T019-T023): 1-1.5 hours
- **Visual Polish** (T024-T030): 1 hour
- **Testing** (T031-T059): 1.5-2 hours
- **Documentation** (T060-T065): 0.5-1 hour

**Total**: ~7-9 hours (matches plan.md estimate of ~5 hours minimum + testing buffer)

---

## Notes

- All tasks modify single file: `src/widgets/correlation_matrix_widget.py`
- No database changes required
- No new dependencies required
- Constitution compliance verified throughout
- Manual testing sufficient (no automated test infrastructure needed)
- Each commit should be deployable for Streamlit app testing
- Stop and test frequently - better to catch issues early
