# Implementation Plan: SOLID Widget Architecture

**Branch**: `007-solid-widget-architecture` | **Date**: December 9, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-solid-widget-architecture/spec.md`

## Summary

Refactor dashboard widgets (Holdings, CorrelationMatrix, MonteCarloSimulation, PortfolioSummary) to follow SOLID principles through architectural patterns including Data Provider abstraction, Widget Controller separation, Presentation Strategy configuration, and Configuration Factory type safety. Enables 50% reduction in code for new widget variants while achieving 95% test coverage through dependency injection and maintaining backward compatibility.

## Technical Context

**Language/Version**: TypeScript 5.x, React 18+, Next.js 16.x  
**Primary Dependencies**: React, Tailwind CSS, Lucide React icons, Custom hooks (@/hooks/use-portfolio-widgets)  
**Storage**: External API via REST endpoints, React state management, browser cache  
**Testing**: Jest + React Testing Library (unit tests), Cypress (E2E integration tests)  
**Target Platform**: Modern web browsers (Chrome 120+, Firefox 120+, Safari 17+)  
**Project Type**: Web application - React component architecture  
**Performance Goals**: <100ms widget render time, <50ms re-render on data updates, 60fps smooth interactions  
**Constraints**: Maintain existing UI/UX, zero breaking changes during migration, tree-shakeable bundle size  
**Scale/Scope**: 4 existing widgets, ~20 components total, 500+ LOC per widget average

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Widget Modularity Principle**: The SOLID refactoring directly supports "Each widget should have clear responsibilities" by implementing Single Responsibility Principle and Interface Segregation. Widget Controllers will handle presentation logic while Data Providers manage state.

✅ **Professional UI Standards**: Maintains existing Tailwind CSS compact styling and consistent spacing while improving code organization. No visual changes to end-user experience, only improved maintainability.

✅ **Type Safety**: Enhances existing TypeScript interfaces with proper dependency injection contracts and widget configuration types. Strengthens type safety through explicit interface definitions.

**GATE 1**: PASS - No constitutional violations. Widget modularity is enhanced, professional UI standards are preserved, and type safety is strengthened through better architecture.

**POST-PHASE 1 RE-CHECK**:

✅ **Widget Modularity Principle**: Phase 1 deliverables (data-model.md, contracts/, quickstart.md) demonstrate clear separation of concerns. Widget Controllers, Data Providers, and Configuration interfaces follow Single Responsibility Principle.

✅ **Professional UI Standards**: Design maintains existing UI components and Tailwind CSS styling. New architecture is purely internal - no breaking changes to user experience.

✅ **Type Safety**: Comprehensive TypeScript interfaces defined in contracts/ directory provide full type safety for dependency injection, configuration validation, and data flow.

**GATE 2**: PASS - Phase 1 design artifacts comply with constitutional requirements. Ready for Phase 2 implementation planning.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/v1/src/
├── components/
│   ├── Holdings.tsx
│   ├── PortfolioSummary.tsx
│   ├── CorrelationMatrix.tsx
│   └── MonteCarloSimulation.tsx
├── app/dashboard/
│   └── page.tsx
├── hooks/
│   └── use-portfolio-widgets.ts
├── lib/
│   ├── interfaces/
│   │   ├── IWidgetController.ts      # Phase 1 deliverable
│   │   ├── IDataProvider.ts          # Phase 1 deliverable
│   │   └── IWidgetConfiguration.ts   # Phase 1 deliverable
│   ├── controllers/
│   │   ├── HoldingsController.ts     # Phase 1 deliverable  
│   │   ├── PortfolioSummaryController.ts
│   │   ├── CorrelationMatrixController.ts
│   │   └── MonteCarloController.ts
│   ├── providers/
│   │   ├── PortfolioDataProvider.ts  # Phase 1 deliverable
│   │   ├── MarketDataProvider.ts     # Phase 1 deliverable
│   │   └── SimulationDataProvider.ts # Phase 1 deliverable
│   └── factories/
│       └── WidgetFactory.ts          # Phase 1 deliverable
└── types/
    └── widget-types.ts               # Phase 1 deliverable

tests/
├── unit/
│   ├── controllers/
│   ├── providers/
│   └── components/
└── integration/
    └── widget-integration.test.tsx   # Phase 1 deliverable
```

**Structure Decision**: Web application with React components. The SOLID refactoring introduces new directories under `frontend/v1/src/lib/` for controllers, providers, interfaces, and factories. Existing component files will be refactored to use dependency injection while maintaining current file locations. Field naming will be standardized from snake_case (asset_class) to camelCase (assetClass) to follow TypeScript conventions.

## Complexity Tracking

> **No constitutional violations found. This section left empty per .specify framework guidelines.**
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
