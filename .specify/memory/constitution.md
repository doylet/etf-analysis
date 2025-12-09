<!--
Sync Impact Report:
Version: 1.2.0 → 1.3.0
Action: Added Frontend Architecture Principles and removed Streamlit-specific rules
Changes:
  - MINOR version bump: Added new Core Principle VI (Frontend Architecture)
  - Removed all Streamlit-specific UI standards from Principle IV
  - Updated Principle IV to be framework-agnostic (Professional UI Standards)
  - Removed Forbidden Practice #4 (Streamlit-specific divider rules)
  - Added Frontend-specific forbidden and required practices
  - Rationale: Project now uses dual architecture (Python backend + React frontend)
Templates Status:
  - spec-template.md: ⚠️ Review UI component patterns for framework-agnostic approach
  - plan-template.md: ⚠️ Update to reflect frontend/backend architecture patterns
  - All other templates: ✅ No updates required
Affected Code:
  - frontend/v1/src/**/*.tsx: ✅ Already follows new frontend principles
  - frontend/v1/src/app/dashboard/page.tsx: ✅ Properly uses React.memo and useCallback
  - frontend/v1/src/hooks/use-portfolio-widgets.ts: ✅ Structured error handling in place
Previous Report:
Version: 1.1.0 → 1.2.0
Action: Amendment to forbid st.divider()
Changes:
  - MINOR version bump: Added new forbidden practice (st.divider())
  - Updated Principle IV: Professional UI Standards to remove st.divider() requirement
  - Added Forbidden Practice #4: st.divider() usage
  - Rationale: st.divider() creates excessive visual noise and inconsistent spacing
-->

# ETF Analysis Dashboard Constitution

## Core Principles

### I. Data Persistence First
All financial data MUST be persisted to the database layer. No calculations should rely solely on in-memory data that cannot be reconstructed from persisted state. Price data, orders, dividends, and cash flows MUST be stored in the appropriate database tables with proper timestamps and audit trails.

**Rationale**: Financial analysis requires historical accuracy and reproducibility. Loss of in-memory data should never compromise portfolio calculations or performance metrics.

### II. Calculation Transparency
All financial metrics and calculations MUST use well-documented, industry-standard formulas. Each calculation function MUST include docstrings explaining the methodology and expected inputs/outputs. Complex calculations MUST be unit-tested with known examples.

**Rationale**: Users need to trust the numbers. Transparent, verifiable calculations build confidence and enable debugging.

### III. Widget Modularity
Dashboard widgets MUST follow the BaseWidget interface and remain independent. Each widget MUST be self-contained with its own render logic, data fetching, and state management. Widgets MUST NOT directly depend on other widgets' internal state.

**Rationale**: Modular widgets enable flexible dashboard composition, easier testing, and independent feature development.

### IV. Professional UI Standards
User interfaces MUST maintain consistent, professional presentation. Components MUST use appropriate containers with clear visual hierarchy. Section spacing MUST be consistent and intentional. Interactive elements MUST include helpful tooltips and accessible labels. Visual design MUST prioritize data legibility and user comprehension.

**Rationale**: Consistent, professional UI presentation enhances user experience and maintainability across all interface layers.

### V. Code Readability
Code MUST prioritize readability over cleverness. Variable names MUST be descriptive. Complex logic MUST be broken into well-named functions. Magic numbers MUST be replaced with named constants.

**Rationale**: This is a financial application where correctness is paramount. Clear code enables verification and reduces bugs.

### VI. Frontend Architecture (React/Next.js)
Frontend components MUST be optimized for performance and type safety. Components receiving frequently changing props MUST use `React.memo()` with proper `displayName`. Event handlers and callbacks MUST be wrapped in `useCallback()` with correct dependencies. Expensive computations MUST use `useMemo()`. All data-fetching hooks MUST return structured states: `{ data, loading, error }`. HTTP errors MUST be categorized and provide user-friendly messages. All component props and API responses MUST have TypeScript interfaces.

**Rationale**: Financial dashboards render complex widgets that update frequently. Performance optimization prevents unnecessary re-renders and resource waste. Type safety prevents runtime errors with financial data. Clear error states enable users to understand and resolve issues.

## Code Quality Standards

### Forbidden Practices

The following practices are **EXPRESSLY FORBIDDEN** in this codebase:

1. **HEREDOCs and Multi-line String Literals for Code Generation**
   - MUST NOT use triple-quoted strings ("""...""") to generate code that will be executed
   - MUST NOT use string concatenation to build executable code
   - MUST NOT use `eval()`, `exec()`, or similar dynamic code execution on constructed strings
   - **Exception**: Multi-line strings are acceptable for documentation, SQL queries (with parameterization), and display text
   - **Rationale**: HEREDOCs obscure code structure, bypass syntax checking, complicate debugging, and introduce security risks

2. **Global Mutable State**
   - MUST NOT use global variables that change during execution
   - MUST use Streamlit session state or function parameters for state management
   - **Rationale**: Global state makes testing difficult and creates hidden dependencies

3. **Silent Failures**
   - MUST NOT catch exceptions without logging or user notification
   - MUST NOT return None without documenting why
   - MUST provide clear error messages to users when operations fail
   - **Rationale**: Financial applications require transparency about data quality and operation status

4. **The `any` Type in TypeScript**
   - MUST NOT use `any` type except for documented edge cases with clear justification
   - MUST use proper TypeScript types and interfaces for all props and state
   - MUST type API responses to match backend schemas
   - **Exception**: Third-party library compatibility where types are unavailable
   - **Rationale**: Type safety prevents runtime errors with financial data and catches bugs at compile time

### Required Practices

1. **Type Hints**
   - All function signatures MUST include type hints for parameters and return values
   - Use `typing.Optional`, `typing.List[Dict]`, etc. for clarity

2. **Docstrings**
   - All public functions and classes MUST have docstrings
   - Docstrings MUST explain purpose, parameters, return values, and any side effects

3. **Error Handling**
   - Database operations MUST handle connection failures gracefully
   - API calls MUST handle network errors and rate limits
   - User-facing errors MUST be clear and actionable

4. **Frontend Performance Optimization**
   - Components MUST use `React.memo()` when receiving props that change frequently
   - All memoized components MUST have `displayName` set for debugging
   - Event handlers MUST be wrapped in `useCallback()` with correct dependencies
   - Expensive computations MUST be wrapped in `useMemo()` with correct dependencies
   - Component state MUST be local unless explicitly shared

5. **Frontend Error States**
   - Data-fetching hooks MUST return `{ data, loading, error }` structure
   - HTTP status codes MUST be categorized: 401 (auth), 403 (permission), 422 (validation), 500 (server)
   - Error messages MUST be user-friendly and actionable
   - Network failures MUST display fallback UI, not crash the application

6. **Frontend Accessibility**
   - All interactive elements MUST be keyboard navigable
   - Financial metrics MUST include `aria-label` or screen reader text
   - Color MUST NOT be the only indicator of positive/negative values (use +/- symbols)
   - WCAG AA compliance MUST be maintained for contrast ratios

## Storage Architecture

### Database Layer Requirements

1. **Schema Integrity**
   - All tables MUST have appropriate primary keys and foreign key constraints
   - Timestamps MUST be stored as datetime objects, not strings
   - Monetary values MUST use appropriate decimal precision

2. **Data Fetching Separation**
   - Price data fetching (yfinance) MUST be separate from database storage
   - Storage adapter MUST provide consistent interface regardless of backend (SQLite, BigQuery)
   - Failed API fetches MUST NOT corrupt existing data

3. **Query Optimization**
   - Date range queries MUST use proper indexes
   - Bulk operations MUST be used when inserting multiple records
   - Connection pooling MUST be implemented for production deployments

## Governance

This constitution supersedes all other development practices and preferences. When a pull request or code change conflicts with these principles, the constitution takes precedence.

### Amendment Process

1. Amendments MUST be proposed with clear justification
2. Amendment proposals MUST include impact analysis on existing code
3. Approved amendments MUST increment version number according to:
   - **MAJOR**: Removal or redefinition of core principles (breaking changes)
   - **MINOR**: Addition of new principles or significant expansions
   - **PATCH**: Clarifications, typo fixes, or non-semantic refinements
4. Amendments MUST update the Sync Impact Report
5. Amendments MUST propagate to affected templates and documentation

### Compliance

- All code reviews MUST verify constitutional compliance
- Violations MUST be corrected before merge
- Complexity that violates simplicity principles MUST be justified in writing
- When constitution conflicts with external library patterns, constitution wins unless explicitly documented otherwise

**Version**: 1.3.0 | **Ratified**: 2025-12-01 | **Last Amended**: 2025-12-09
