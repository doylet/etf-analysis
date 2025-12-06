# Tasks: Base UI Library Integration

**Input**: Design documents from `/specs/001-base-ui-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the feature specification, so no test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/v1/src/` for source code, `frontend/v1/` for configuration

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project documentation structure per implementation plan

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core dependencies and configurations that all user stories depend on

- [X] T002 [P] Install @base-ui-components/react dependency in frontend/v1/package.json
- [X] T003 [P] Add Base UI TypeScript interfaces in frontend/v1/src/lib/base-ui-types.ts
- [X] T004 [P] Create Base UI utility functions in frontend/v1/src/lib/base-ui-utils.ts

## Phase 3: User Story 1 - Base UI Library Setup and Configuration (Priority: P1)

**Story Goal**: Frontend developer sets up Base UI library with portal configuration and iOS Safari compatibility

**Independent Test Criteria**: Library installation verified, portal configuration working, no breaking changes to existing functionality

**Implementation Tasks**:

- [X] T005 [US1] Configure portal support in frontend/v1/src/app/layout.tsx with isolation styles
- [X] T006 [US1] Add iOS Safari 26+ compatibility styles to frontend/v1/src/app/globals.css
- [X] T007 [US1] Verify existing dashboard functionality remains intact after Base UI integration (test: navigation, portfolio summary, data loading, authentication flow)
- [X] T008 [US1] Configure build process for Base UI tree-shaking in frontend/v1/next.config.js

## Phase 4: User Story 2 - Example Component Implementation (Priority: P2)

**Story Goal**: Implement working Popover component demonstrating Base UI integration patterns

**Independent Test Criteria**: Popover component functional, accessible, properly styled with Tailwind CSS

**Implementation Tasks**:

- [X] T009 [US2] Create NotificationPopover component in frontend/v1/src/components/ui/notification-popover.tsx
- [X] T010 [US2] Implement ArrowIcon SVG component for popover arrows in frontend/v1/src/components/ui/notification-popover.tsx
- [X] T011 [US2] Add notification popover to dashboard header in frontend/v1/src/app/dashboard/page.tsx
- [X] T012 [US2] Verify Popover accessibility features (keyboard navigation, screen reader support)
- [X] T013 [US2] Test Popover animations and positioning across different screen sizes

## Phase 5: User Story 3 - Documentation and Developer Guidelines (Priority: P3)

**Story Goal**: Provide clear documentation and patterns for consistent Base UI usage

**Independent Test Criteria**: Documentation complete, new developer can implement components following patterns

**Implementation Tasks**:

- [X] T014 [P] [US3] Create Base UI component examples in frontend/v1/src/components/ui/examples/
- [X] T015 [P] [US3] Document Base UI styling patterns in frontend/v1/docs/base-ui-patterns.md
- [X] T016 [US3] Add Base UI accessibility guidelines to frontend/v1/docs/accessibility.md
- [X] T017 [US3] Create component implementation checklist in frontend/v1/docs/component-checklist.md

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Quality assurance and performance optimization

- [X] T018 [P] Measure and document bundle size impact from Base UI integration
- [X] T019 [P] Verify WCAG 2.1 AA compliance for all Base UI components
- [X] T020 [P] Test Base UI components across Chrome, Firefox, Safari, and Edge browsers
- [X] T021 [P] Optimize component development workflow and patterns
- [X] T022 [P] Verify Base UI components work with specific browser versions: Chrome 120+, Firefox 121+, Safari 17+, Edge 120+

## Dependencies

### User Story Completion Order
1. **User Story 1** (Setup) - Must complete before any other stories
2. **User Story 2** (Example) - Depends on US1 setup completion
3. **User Story 3** (Documentation) - Can start after US2 for concrete examples

### Parallel Execution Opportunities

**Within User Story 1**:
- T005, T006 can run in parallel (different files)
- T007 verification after T005-T006 complete
- T008 can run in parallel with verification

**Within User Story 2**:
- T009, T010 can run in parallel if implemented in same file
- T012, T013 can run in parallel (different testing focus)

**Within User Story 3**:
- T014, T015, T016 can all run in parallel (different files)
- T017 should come after others for complete context

**Cross-Story Parallelization**:
- US3 documentation tasks (T014-T016) can start once US2 patterns are established
- Polish tasks (T018-T022) can run in parallel once implementation is complete

## Implementation Strategy

### MVP Scope (Recommended)
- **Phase 1-3 only**: Complete User Story 1 for immediate Base UI foundation
- Delivers: Working Base UI setup with portal configuration
- Value: Foundation ready for component development

### Full Feature Scope
- **All phases**: Complete all user stories for full Base UI integration
- Delivers: Setup + Example component + Documentation + Polish
- Value: Complete developer experience with patterns and guidelines

### Success Criteria per User Story

**US1 Success**: 
- ✅ @base-ui-components/react installed and building
- ✅ Portal configuration working on all target browsers
- ✅ iOS Safari 26+ compatibility verified
- ✅ No breaking changes to existing functionality

**US2 Success**:
- ✅ Popover component fully functional and accessible
- ✅ Component follows established Tailwind styling patterns
- ✅ Smooth animations and responsive behavior
- ✅ Screen reader and keyboard navigation working

**US3 Success**:
- ✅ Complete documentation for Base UI patterns
- ✅ Developer can implement new components in <30 minutes
- ✅ Accessibility guidelines clearly documented
- ✅ Component checklist ensures consistency

**Overall Success**:
- ✅ Bundle size increase <50KB through effective tree-shaking
- ✅ All components pass WCAG 2.1 AA accessibility standards
- ✅ Cross-browser compatibility maintained
- ✅ Development velocity improved by 25% for component implementation