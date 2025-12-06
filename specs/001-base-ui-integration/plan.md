# Implementation Plan: Base UI Library Integration

**Branch**: `001-base-ui-integration` | **Date**: December 5, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-base-ui-integration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate Base UI component library (@base-ui-components/react) into the ETF analysis dashboard frontend to provide modern, accessible UI components. Primary requirement is to establish foundational library setup with portal configuration and demonstrate integration through a working Popover component example.

## Technical Context

**Language/Version**: TypeScript 5+ with React 19.2.0 and Next.js 16.0.7  
**Primary Dependencies**: @base-ui-components/react (new), Tailwind CSS 4, Lucide React icons  
**Storage**: N/A (UI library integration)  
**Testing**: Next.js built-in testing, component accessibility testing  
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge), iOS Safari 26+ compatibility  
**Project Type**: Web frontend (Next.js App Router)  
**Performance Goals**: <50KB bundle size increase, tree-shaking effectiveness, <30 min component implementation time  
**Constraints**: Must maintain existing functionality, WCAG 2.1 AA compliance, no breaking changes to current UI  
**Scale/Scope**: Single frontend application, existing dashboard components preserved, incremental component migration capability

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Alignment

✅ **I. Data Persistence First**: N/A - This is a UI library integration that doesn't affect data persistence  
✅ **II. Calculation Transparency**: N/A - No financial calculations are modified  
✅ **III. Widget Modularity**: Base UI integration maintains widget independence and follows modular patterns  
✅ **IV. Professional UI Standards**: Base UI enhances professional standards with accessibility and proper component patterns

### Forbidden Practices Check

✅ **No HEREDOC patterns**: Feature doesn't involve Python string patterns  
✅ **No st.divider() usage**: Feature targets React frontend, not Streamlit  
✅ **Professional UI patterns**: Base UI actively improves UI professionalism

**GATE STATUS: ✅ PASS** - No constitution violations detected. Feature enhances existing standards.

### Post-Design Re-evaluation

✅ **Phase 1 Complete**: All design artifacts created and reviewed  
✅ **No new violations**: Design maintains alignment with all core principles  
✅ **Enhanced standards**: Base UI integration actually improves UI professionalism beyond current standards  
✅ **Modular approach**: Component design preserves widget independence and follows established patterns  

**FINAL GATE STATUS: ✅ APPROVED** - Ready for Phase 2 implementation planning

## Project Structure

### Documentation (this feature)

```text
specs/001-base-ui-integration/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Structure Decision**: Web application structure detected - frontend/backend separation already established. This feature targets the frontend directory:

```text
frontend/v1/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx    # Portal configuration target
│   │   └── globals.css   # Style integration point
│   ├── components/       # Base UI component examples
│   ├── lib/             # Base UI utility functions
│   └── contexts/        # Existing auth context (preserved)
├── package.json         # Dependency installation target
└── tailwind.config.js   # Style integration configuration
```
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected - tracking table not needed.

---

## Phase 0: Research & Decisions

### Research Tasks

#### Task 1: Base UI Library Evaluation
**Question**: Validate Base UI library compatibility with existing Next.js 16.0.7 and React 19.2.0 setup
**Research Approach**: 
- Review Base UI documentation for version compatibility
- Check peer dependency requirements
- Assess bundle size impact and tree-shaking effectiveness

#### Task 2: Tailwind CSS Integration Patterns
**Question**: Determine best practices for integrating Base UI with existing Tailwind CSS 4 setup
**Research Approach**:
- Review Base UI styling architecture and customization options
- Identify potential CSS conflicts and resolution strategies
- Evaluate component theming and design system integration

#### Task 3: Portal Configuration Strategy
**Question**: Identify optimal portal setup for iOS Safari 26+ compatibility and backdrop coverage
**Research Approach**:
- Review iOS Safari viewport changes and backdrop requirements
- Analyze Base UI portal implementation and configuration options
- Test backdrop positioning strategies

**Deliverable**: `research.md` documenting all decisions with rationales and alternatives considered

---

## Phase 1: Design & Contracts

### Design Artifacts

#### Data Model (`data-model.md`)
**Scope**: UI component configuration entities and styling integration patterns
- Component configuration structures
- Portal setup parameters
- Style integration mappings
- Accessibility attribute definitions

#### API Contracts (`contracts/`)
**Scope**: Component interface definitions (if any public APIs are exposed)
- Base UI component wrapper interfaces
- Style customization APIs
- Accessibility helper functions

#### Quick Start Guide (`quickstart.md`)
**Scope**: Developer onboarding and implementation patterns
- Installation and setup instructions
- Component implementation examples
- Common patterns and best practices
- Troubleshooting guide

#### Agent Context Update
**Scope**: Update agent-specific context files with new Base UI technology
- Add @base-ui-components/react to technology stack
- Include component patterns and accessibility guidelines
- Preserve existing manual context additions

**Deliverables**: Complete design documentation and updated agent context

---

## Phase 2: Implementation Planning

**Status**: Deferred to `/speckit.tasks` command - NOT created by `/speckit.plan`
**Scope**: Detailed implementation tasks, file-level changes, and testing strategy
