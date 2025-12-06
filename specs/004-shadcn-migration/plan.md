# Implementation Plan: shadcn/ui Migration & Design System Foundation

**Created**: December 6, 2025  
**Feature Branch**: `004-shadcn-migration`  
**Specification**: [spec.md](./spec.md)

## Executive Summary

Replace existing base-ui component library with canonical shadcn/ui implementation while establishing foundations for a bespoke design system. Migration will be executed in phases to maintain functionality and minimize risk.

## Technical Context

### Current State
- NextJS 15+ frontend using custom base-ui components
- Components: Card, Alert, Skeleton, Button in `src/components/shared/`
- Portfolio Summary dashboard as primary use case
- Tailwind CSS for styling with custom utility functions

### Target State
- shadcn/ui component library with canonical project structure
- Components.json configuration for CLI tooling
- Custom design system built on shadcn/ui foundations
- Organized component hierarchy: ui/ (shadcn), shared/ (custom), features/

### Key Technical Decisions
- **Component Strategy**: Replace existing components with shadcn/ui equivalents
- **Migration Approach**: Incremental replacement to maintain functionality
- **Structure**: Follow shadcn/ui conventions with customization layer
- **Theming**: Extend default theme with custom design tokens
- **Constitution Compliance**: This NextJS frontend migration operates independently of the Streamlit dashboard constitution (which applies to backend widgets only). Frontend follows NextJS/React best practices while maintaining data interface compatibility.

## Implementation Phases

### Phase 1: Foundation Setup (P1 - Component System Migration)

**Objective**: Establish shadcn/ui infrastructure and replace core components

#### Step 1: shadcn/ui Installation & Configuration
```bash
npx shadcn-ui@latest init
```
- Install required dependencies (class-variance-authority, clsx, tailwind-merge, @radix-ui/react-slot)
- **Validation Checkpoint**: Verify package.json contains all required dependencies
- Configure components.json with proper paths
- **Error Handling**: If CLI init fails, check Node.js version compatibility and network connectivity
- Update tailwind.config.js with shadcn/ui theme extension
- **Validation Checkpoint**: Verify tailwind.config.js syntax with `npx tailwindcss --help`
- Set up proper TypeScript path mapping
- **Rollback Strategy**: Maintain backup of original config files before any modifications

#### Step 2: Component Replacement
- Replace `src/components/shared/card.tsx` with shadcn/ui Card
- Replace `src/components/shared/alert.tsx` with shadcn/ui Alert  
- Replace `src/components/shared/skeleton.tsx` with shadcn/ui Skeleton
- Replace `src/components/shared/button.tsx` with shadcn/ui Button

#### Step 3: Update Imports & Integration
- Update PortfolioSummary.tsx to use new shadcn/ui components
- Verify visual consistency and functionality
- Run build validation and tests

#### Acceptance Criteria
- ✅ Portfolio Summary renders identically
- ✅ All component interactions work unchanged
- ✅ Build completes successfully without errors
- ✅ TypeScript compilation passes

### Phase 2: Project Structure Optimization (P2 - Canonical Project Structure)

**Objective**: Establish proper component organization and tooling

#### Step 1: Directory Restructuring
```
src/components/
├── ui/              # shadcn/ui components
├── shared/          # Custom reusable components
├── features/        # Feature-specific components
└── [legacy removal] # Remove old base-ui structure
```

#### Step 2: CLI Integration & Validation
- Validate `npx shadcn-ui@latest add [component]` workflow
- Test component addition to correct ui/ directory
- Verify import path resolution with @/ aliases

#### Step 3: Component Organization
- Move existing custom components to appropriate directories
- Create index files for barrel exports
- Document component usage patterns

#### Acceptance Criteria
- ✅ shadcn/ui CLI adds components correctly
- ✅ All imports resolve without issues
- ✅ Clear separation between component types
- ✅ Documentation reflects new structure

### Phase 3: Design System Foundation (P3 - Bespoke Design System)

**Objective**: Create customizable design system built on shadcn/ui

#### Step 1: Custom Theme Configuration
- Define custom color palette in tailwind.config.js
- Establish design tokens for spacing, typography, shadows
- Create CSS custom properties for dynamic theming

#### Step 2: Component Customization Layer
- Extend shadcn/ui components with custom variants
- Create wrapper components for brand-specific styling
- Implement design token integration

#### Step 3: Documentation & Guidelines
- Document custom theme usage patterns
- Create component showcase page
- Establish design system guidelines

#### Acceptance Criteria
- ✅ Custom theme variables apply consistently
- ✅ Components inherit brand styling automatically
- ✅ Design system documentation exists
- ✅ Easy addition of new themed components

## Risk Mitigation

### Technical Risks
- **Visual Regression**: Incremental replacement with side-by-side validation
- **Build Failures**: Comprehensive testing at each phase
- **Import Conflicts**: Clear namespace separation and path mapping

### Rollback Strategy
- Maintain git branches for each phase
- Keep original components until full validation
- Atomic commits for easy reversion

## Validation Strategy

### Testing Approach
- **Visual**: Screenshot comparison before/after
- **Functional**: Automated component testing
- **Integration**: Full Portfolio Summary workflow validation
- **Performance**: Build time and bundle size monitoring

### Success Metrics
- Zero visual regressions in Portfolio Summary
- Build time within 20% of baseline
- All TypeScript compilation passes
- shadcn/ui CLI fully functional

## Dependencies & Prerequisites

### External Dependencies
- shadcn/ui CLI and core packages
- Radix UI primitives
- Class Variance Authority for component variants
- Proper Tailwind CSS configuration

### Team Dependencies
- Frontend development access
- Design system knowledge transfer
- Component testing capabilities

## Timeline Estimate

- **Phase 1**: 2-3 days (core component replacement)
- **Phase 2**: 1-2 days (structure optimization)  
- **Phase 3**: 2-3 days (design system foundation)
- **Total**: 5-8 days for complete migration

## Next Steps

1. Begin Phase 1 with shadcn/ui installation and Card component replacement
2. Validate Portfolio Summary functionality after each component swap
3. Progress through phases with thorough testing at each step
4. Document lessons learned for future component migrations