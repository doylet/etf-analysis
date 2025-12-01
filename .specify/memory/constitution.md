<!--
Sync Impact Report:
Version: 1.0.0 → 1.1.0
Action: Amendment to forbid st.divider()
Changes:
  - MINOR version bump: Added new forbidden practice (st.divider())
  - Updated Principle IV: Professional UI Standards to remove st.divider() requirement
  - Added Forbidden Practice #4: st.divider() usage
  - Rationale: st.divider() creates excessive visual noise and inconsistent spacing
Templates Status:
  - spec-template.md: ⚠️ Review references to st.divider() in UI standards
  - plan-template.md: ⚠️ Review UI component patterns
  - All other templates: ✅ No updates required
Affected Code:
  - src/widgets/correlation_matrix_widget.py: ⚠️ Contains 3 st.divider() calls (T024-T026)
  - Action required: Replace st.divider() with blank st.write() or proper spacing
Previous Report:
Version: (none) → 1.0.0
Action: Initial constitution establishment
Changes:
  - Established core principles for ETF Analysis Dashboard
  - Added Code Quality Standards section with HEREDOC prohibition
  - Defined governance structure
Templates Status:
  - All templates: ✅ No updates required (constitution created from scratch)
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
User interfaces MUST use Streamlit's container components properly. All widget content MUST be indented within `st.container(border=True)` blocks. Section spacing MUST use `st.space("small")`, `st.space("medium")`, or `st.space("large")` as appropriate, NOT `st.divider()` or `st.write("")`. Metrics MUST include helpful tooltips via the `help` parameter.

**Rationale**: Consistent, professional UI presentation enhances user experience and maintainability. Visual dividers create excessive noise, and `st.write("")` is a hack - `st.space()` is the proper Streamlit API for whitespace control.

### V. Code Readability
Code MUST prioritize readability over cleverness. Variable names MUST be descriptive. Complex logic MUST be broken into well-named functions. Magic numbers MUST be replaced with named constants.

**Rationale**: This is a financial application where correctness is paramount. Clear code enables verification and reduces bugs.

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

4. **st.divider() and st.write("") for Visual Separation**
   - MUST NOT use `st.divider()` to separate sections or create visual breaks
   - MUST NOT use `st.write("")` or `st.write()` with empty/whitespace-only strings for spacing
   - MUST use `st.space("small")`, `st.space("medium")`, or `st.space("large")` for vertical spacing
   - MUST rely on Streamlit's expander components and container borders for visual hierarchy
   - **Exception**: None - these practices are prohibited in all contexts
   - **Rationale**: `st.divider()` creates excessive visual noise and inconsistent spacing patterns. `st.write("")` is a hack that bypasses Streamlit's proper spacing API. Professional dashboards use `st.space()` for controlled whitespace and rely on component organization rather than explicit divider lines or empty write calls.

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

**Version**: 1.2.0 | **Ratified**: 2025-12-01 | **Last Amended**: 2025-12-01
