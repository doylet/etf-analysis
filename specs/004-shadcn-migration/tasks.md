# Tasks: shadcn/ui Migration & Design System Foundation

**Input**: Design documents from `/specs/004-shadcn-migration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Clean up existing base-ui dependencies and prepare workspace

- [X] T001 Remove existing base-ui dependencies from frontend/v1/package.json
- [X] T002 [P] Backup existing component implementations in src/components/shared/
- [X] T003 Create git branch checkpoint before starting migration

---

## Phase 2: Foundational (Blocking Prerequisites) 

**Purpose**: shadcn/ui installation and core configuration that MUST be complete before component replacement

**⚠️ CRITICAL**: No component migration work can begin until this phase is complete

- [X] T004 Install shadcn/ui CLI and core dependencies in frontend/v1/
- [X] T005 Initialize shadcn/ui project with `npx shadcn-ui@latest init`
- [X] T006 Configure components.json with proper paths and aliases
- [X] T007 Update tailwind.config.js with shadcn/ui theme configuration
- [X] T008 Update tsconfig.json paths for @/ alias resolution
- [X] T009 Create initial src/components/ui/ directory structure
- [X] T010 Validate shadcn/ui CLI installation with test component addition

**Checkpoint**: Foundation ready - component replacement can now begin

---

## Phase 3: User Story 1 - Component System Migration (Priority: P1) 🎯 MVP

**Goal**: Replace all existing base-ui components with shadcn/ui while maintaining Portfolio Summary functionality

**Independent Test**: Portfolio Summary page loads and functions identically to current implementation

### Component Replacement for User Story 1

- [X] T011 [P] [US1] Add shadcn/ui Card component via CLI to src/components/ui/card.tsx
- [X] T012 [P] [US1] Add shadcn/ui Alert component via CLI to src/components/ui/alert.tsx  
- [X] T013 [P] [US1] Add shadcn/ui Skeleton component via CLI to src/components/ui/skeleton.tsx
- [X] T014 [P] [US1] Add shadcn/ui Button component via CLI to src/components/ui/button.tsx
- [X] T015 [US1] Update src/lib/utils.ts to use shadcn/ui cn utility function
- [X] T016 [US1] Create new barrel export in src/components/ui/index.ts
- [X] T017 [US1] Update PortfolioSummary.tsx imports to use shadcn/ui components
- [X] T018 [US1] Verify visual consistency and adjust styling if needed
- [X] T019 [US1] Remove old custom components from src/components/shared/
- [X] T020 [US1] Test Portfolio Summary functionality end-to-end

**Checkpoint**: Portfolio Summary works with shadcn/ui components, zero regressions

---

## Phase 4: User Story 2 - Canonical Project Structure (Priority: P2)

**Goal**: Establish proper shadcn/ui project organization and validate CLI tooling

**Independent Test**: shadcn/ui CLI commands work correctly and components are properly organized

### Project Structure for User Story 2

- [X] T021 [P] [US2] Reorganize remaining components into proper directory structure
- [X] T022 [P] [US2] Create src/components/shared/ for custom components
- [X] T023 [P] [US2] Move feature-specific components to src/components/features/
- [X] T024 [US2] Update all import statements throughout frontend/v1/src/
- [X] T025 [US2] Create component documentation in src/components/README.md
- [X] T026 [US2] Validate shadcn/ui CLI add command works correctly
- [X] T027 [US2] Test import resolution for all component types
- [X] T028 [US2] Clean up unused files and organize barrel exports

**Checkpoint**: Component organization follows shadcn/ui best practices, CLI fully functional

---

## Phase 5: User Story 3 - Bespoke Design System Foundation (Priority: P3)

**Goal**: Create foundation for custom design system built on shadcn/ui

**Independent Test**: Custom theme variables are applied and components respect design tokens

### Design System for User Story 3

- [X] T029 [P] [US3] Define custom color palette in tailwind.config.js
- [X] T030 [P] [US3] Create design tokens file src/lib/design-tokens.ts
- [X] T031 [P] [US3] Define custom CSS variables for theming
- [X] T032 [US3] Create custom component variants extending shadcn/ui
- [X] T033 [US3] Implement brand-specific styling wrapper components
- [X] T034 [US3] Create design system showcase page
- [X] T035 [US3] Document design token usage patterns
- [X] T036 [US3] Add design system guidelines to docs/
- [X] T037 [US3] Test custom theme inheritance across components
- [X] T037.1 [US3] Validate custom theme extension loading and fallback behavior

**Checkpoint**: Design system foundation ready for future customization

---

## Phase 6: Validation & Documentation

**Purpose**: Final validation and project documentation

- [X] T038 Run full build validation and performance testing
- [X] T039 [P] Create migration documentation in docs/shadcn-migration.md
- [X] T040 [P] Update project README with new component structure
- [X] T041 Validate all success criteria from spec.md are met
- [X] T042 Clean up temporary files and backup components

---

## Dependencies & Execution Order

### Sequential Dependencies
1. **Phase 1 → Phase 2**: Must clean up before installing
2. **Phase 2 → Phase 3**: Must have shadcn/ui configured before component replacement
3. **Phase 3 → Phase 4**: Must have working components before reorganization
4. **Phase 4 → Phase 5**: Must have structure in place before design system

### Parallel Opportunities

#### Within Phase 3 (Component Migration)
- T011-T014 can run in parallel (different component additions)
- T021-T023 can run in parallel (different directory operations)
- T029-T031 can run in parallel (different configuration files)
- T039-T040 can run in parallel (different documentation tasks)

---

## Implementation Strategy

### MVP First (P1 User Story Only)

1. Complete Phase 1-2: Setup and Foundation
2. Complete Phase 3: Component System Migration
3. **STOP and VALIDATE**: 
   - Portfolio Summary works identically
   - Build completes successfully
   - No visual regressions detected
4. **MVP Foundation Delivered**: Functional shadcn/ui migration

### Full Feature (P2-P3 Stories)

5. Complete Phase 4: Project Structure
6. Complete Phase 5: Design System Foundation
7. Complete Phase 6: Validation & Documentation
8. **Feature Complete**: Full migration with design system foundation

### Success Validation

- [ ] **SC-001**: All Portfolio Summary functionality works identically
- [ ] **SC-002**: shadcn/ui CLI commands execute successfully
- [ ] **SC-003**: Build time within 20% of baseline
- [ ] **SC-004**: Component library includes Card, Button, Alert, Skeleton

**Total Estimated Tasks**: 42
**Parallel Opportunities**: 15 tasks can run in parallel
**Critical Path**: Phases 1-3 for MVP functionality