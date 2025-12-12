# Widget Refactoring Analysis
**Date:** December 12, 2025  
**Scope:** Frontend v1 Dashboard Widgets  
**Objective:** Identify DRY violations, ensure Single Responsibility Principle, extract shared patterns

---

## Executive Summary

Analysis of 14 dashboard widgets reveals significant opportunities for refactoring to improve maintainability, reduce duplication, and ensure single responsibility. The primary concerns are:

1. **796-line MonteCarloWidget** violates Single Responsibility Principle
2. **Duplicated utility functions** across 3+ widgets (formatCurrency, formatPercent, formatDate)
3. **Identical loading/error states** in all 14 widgets
4. **Repeated form control patterns** (selects, sliders, inputs)
5. **Manual metric displays** instead of using existing UI components
6. **Complex state management** (12+ useState in MonteCarloWidget)

**Estimated Impact:** 40% reduction in widget LOC, elimination of all duplicate code, improved testability.

---

## Current State Analysis

### Widget Inventory

| Widget | LOC | Complexity | SRP Compliance | Key Issues |
|--------|-----|-----------|----------------|------------|
| MonteCarloWidget | 796 | Very High | ❌ Violates | Multiple responsibilities, complex state |
| CorrelationMatrixWidget | 341 | High | ⚠️ Borderline | Insights generation + visualization |
| HoldingsBreakdownWidget | 320 | High | ⚠️ Borderline | Table + breakdown viz |
| PortfolioOptimizerWidget | 304 | High | ⚠️ Borderline | Optimization + chart + recommendations |
| BenchmarkComparisonWidget | 190 | Medium | ✅ Good | Some manual metric displays |
| TimeseriesAnalysisWidget | 159 | Medium | ✅ Good | Clean structure |
| PerformanceWidget | ~100 | Low | ✅ Good | Manual metric displays |
| PortfolioSummaryWidget | ~60 | Low | ✅ Good | Manual metric displays |
| DividendAnalysisWidget | ~98 | Low | ✅ Good | Manual metric displays |
| Others | Varies | Low-Medium | ✅ Good | Minor issues |

### Code Duplication Analysis

#### 1. Utility Functions (HIGH PRIORITY)

**Location:** Multiple widgets  
**Duplication Count:** 3+ widgets

```typescript
// Found in: MonteCarloWidget, HoldingsBreakdownWidget, CorrelationMatrixWidget
const formatPercent = (value: number | undefined | null): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00%';
  }
  return `${(value * 100).toFixed(1)}%`;
};

const formatCurrency = (amount: number | undefined | null): string => {
  if (amount === undefined || amount === null || isNaN(amount)) {
    return '$0.00';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

const formatDate = (dateString: string): string => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return 'Invalid Date';
  }
};
```

**Impact:** 100+ lines of duplicate code  
**Fix:** Extract to `/lib/formatters.ts`

#### 2. Loading/Error States (HIGH PRIORITY)

**Location:** All 14 widgets  
**Pattern:**

```typescript
if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
if (error) return (
  <WidgetInsight
    title="Error Title"
    description={error}
    icon={XCircle}
    variant="destructive"
  />
);
if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;
```

**Impact:** 42+ lines of identical code (3 lines × 14 widgets)  
**Fix:** Create HOC or wrapper component

#### 3. Select Dropdown Pattern (MEDIUM PRIORITY)

**Location:** 7+ widgets  
**Pattern:**

```typescript
<select 
  value={timePeriod} 
  onChange={(e) => setTimePeriod(e.target.value)}
  className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
>
  {periods.map(p => (
    <option key={p.value} value={p.value}>{p.label}</option>
  ))}
</select>
```

**Impact:** 150+ lines of similar code  
**Fix:** Create `<WidgetSelect>` component

#### 4. Manual Metric Displays (MEDIUM PRIORITY)

**Location:** PerformanceWidget, PortfolioSummaryWidget, DividendAnalysisWidget  
**Pattern:**

```typescript
<div className="text-center p-3 bg-muted rounded-md">
  <div className="text-lg font-bold text-foreground">{value}</div>
  <div className="text-xs text-muted-foreground">{label}</div>
</div>
```

**Impact:** 80+ lines that should use MetricCard  
**Fix:** Replace with existing `<MetricCard>` component

#### 5. Shared Constants (LOW PRIORITY)

**Time Periods** - Used in 7+ widgets:
```typescript
const periods = [
  { value: '1W', label: '1 Week' },
  { value: '1M', label: '1 Month' },
  { value: '3M', label: '3 Months' },
  { value: '6M', label: '6 Months' },
  { value: '1Y', label: '1 Year' },
  { value: '2Y', label: '2 Years' },
  { value: '5Y', label: '5 Years' },
];
```

**Impact:** 50+ lines of duplicate arrays  
**Fix:** Extract to `/lib/widget-constants.ts`

---

## Single Responsibility Analysis

### Critical Violation: MonteCarloWidget (796 lines)

**Current Responsibilities:**
1. Configuration state management (12+ useState calls)
2. Simulation parameter controls
3. Portfolio composition UI
4. Rebalancing configuration UI
5. Histogram visualization (30 buckets, SVG generation)
6. Dual-axis timeseries visualization (SVG generation)
7. Metrics display (CAGR, CVaR, Max Drawdown, etc.)
8. Risk insights generation
9. Collapsible section management
10. Drag-and-drop event handling

**Proposed Decomposition:**

```
widgets/
  monte-carlo/
    index.tsx                      # Main orchestration (~100 lines)
    MonteCarloControls.tsx         # Configuration inputs (~150 lines)
    MonteCarloMetrics.tsx          # Statistics display (~100 lines)
    MonteCarloHistogram.tsx        # Histogram viz (~150 lines)
    MonteCarloTimeseries.tsx       # Timeseries viz (~150 lines)
    PortfolioComposition.tsx       # Weight selection (~120 lines)
    RebalancingAnalysis.tsx        # Rebalancing display (~100 lines)
    useMonteCarloConfig.ts         # State management hook (~80 lines)
    types.ts                       # TypeScript interfaces
    utils.ts                       # Helper functions
```

**Benefits:**
- Each component < 200 lines
- Single, focused responsibility per component
- Improved testability (can test components in isolation)
- Reusable components (PortfolioComposition, RebalancingAnalysis)
- Easier maintenance and debugging

### Borderline Cases

#### CorrelationMatrixWidget (341 lines)
**Responsibilities:**
- Matrix visualization
- Insight generation
- Statistics calculation

**Recommendation:** Extract insight generation to separate utility function

#### HoldingsBreakdownWidget (320 lines)
**Responsibilities:**
- Holdings table
- Breakdown visualization
- Column definitions

**Recommendation:** Extract column definitions to constants, consider table extraction

#### PortfolioOptimizerWidget (304 lines)
**Responsibilities:**
- Optimizer controls
- Efficient frontier chart
- Weight recommendations

**Recommendation:** Extract chart to separate component if reused elsewhere

---

## Existing UI Components Not Being Used

### Available but Underutilized:

1. **FinancialAmount** (`/components/ui/financial/financial-amount.tsx`)
   - Professional currency formatting with variants
   - **Current:** Widgets use manual `formatCurrency()` functions
   - **Should use:** `<FinancialAmount value={amount} variant="default" />`

2. **PercentageChange** (`/components/ui/financial/percentage-change.tsx`)
   - Automatic trend detection, color coding, icons
   - **Current:** Widgets manually color-code percentages
   - **Should use:** `<PercentageChange value={percent} showIcon />`

3. **LoadingSpinner** (`/components/ui/feedback/loading-states.tsx`)
   - Professional loading states with variants
   - **Current:** Widgets use `<div>Loading...</div>`
   - **Should use:** `<LoadingSpinner size="default" label="Loading data..." />`

4. **ErrorState** (`/components/ui/feedback/error-states.tsx`)
   - Rich error display with retry actions
   - **Current:** Most widgets use WidgetInsight (which is fine)
   - **Note:** WidgetInsight is appropriate for widgets, keep as-is

5. **LoadingCard** (`/components/ui/feedback/loading-states.tsx`)
   - Skeleton loading for cards
   - **Current:** Not used anywhere
   - **Should use:** For initial widget loading states

### Correctly Used Components:

✅ **MetricCard** - Used in BenchmarkComparisonWidget, CorrelationMatrixWidget, MonteCarloWidget  
✅ **WidgetInsight** - Used consistently across all widgets for errors/warnings  
✅ **CacheBadge** - Used in data-heavy widgets  
✅ **DataTable** - Used in HoldingsBreakdownWidget

---

## Recommended Refactoring Plan

### Phase 1: Quick Wins (1-2 days)
**Impact:** High | **Risk:** Low | **LOC Reduction:** ~200 lines

1. **Create `/lib/formatters.ts`**
   ```typescript
   export const formatCurrency = (
     amount: number | undefined | null,
     options?: Intl.NumberFormatOptions
   ): string => {
     if (amount === undefined || amount === null || isNaN(amount)) {
       return '$0.00';
     }
     return new Intl.NumberFormat('en-US', {
       style: 'currency',
       currency: 'USD',
       ...options,
     }).format(amount);
   };

   export const formatPercent = (
     value: number | undefined | null,
     decimals: number = 2
   ): string => {
     if (value === undefined || value === null || isNaN(value)) {
       return '0.00%';
     }
     return `${(value * 100).toFixed(decimals)}%`;
   };

   export const formatDate = (
     dateString: string,
     format: 'short' | 'long' = 'short'
   ): string => {
     if (!dateString) return 'N/A';
     try {
       const options: Intl.DateTimeFormatOptions = format === 'short'
         ? { year: 'numeric', month: 'short', day: 'numeric' }
         : { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
       return new Date(dateString).toLocaleDateString('en-US', options);
     } catch {
       return 'Invalid Date';
     }
   };

   export const formatNumber = (
     value: number | undefined | null,
     options?: Intl.NumberFormatOptions
   ): string => {
     if (value === undefined || value === null || isNaN(value)) {
       return '0';
     }
     return new Intl.NumberFormat('en-US', options).format(value);
   };
   ```

2. **Create `/lib/widget-constants.ts`**
   ```typescript
   export const TIME_PERIODS = [
     { value: '1W', label: '1 Week' },
     { value: '1M', label: '1 Month' },
     { value: '3M', label: '3 Months' },
     { value: '6M', label: '6 Months' },
     { value: '1Y', label: '1 Year' },
     { value: '2Y', label: '2 Years' },
     { value: '5Y', label: '5 Years' },
   ] as const;

   export const COMMON_BENCHMARKS = [
     { value: 'SPY', label: 'S&P 500' },
     { value: 'QQQ', label: 'Nasdaq 100' },
     { value: 'DIA', label: 'Dow Jones' },
     { value: 'IWM', label: 'Russell 2000' },
     { value: 'VTI', label: 'Total US Market' },
     { value: 'EFA', label: 'International' },
     { value: 'AGG', label: 'US Bonds' },
     { value: 'GLD', label: 'Gold' },
   ] as const;

   export const SIMULATION_COUNTS = [
     { value: 1000, label: '1K Simulations' },
     { value: 5000, label: '5K Simulations' },
     { value: 10000, label: '10K Simulations' },
     { value: 25000, label: '25K Simulations' },
   ] as const;
   ```

3. **Replace all formatter functions** in widgets with imports from `/lib/formatters.ts`

4. **Replace manual metric divs** with `<MetricCard>` component
   - PerformanceWidget
   - PortfolioSummaryWidget
   - DividendAnalysisWidget

**Affected Files:**
- MonteCarloWidget.tsx
- HoldingsBreakdownWidget.tsx
- CorrelationMatrixWidget.tsx
- PerformanceWidget.tsx
- PortfolioSummaryWidget.tsx
- DividendAnalysisWidget.tsx
- BenchmarkComparisonWidget.tsx
- TimeseriesAnalysisWidget.tsx

---

### Phase 2: Widget Controls (2-3 days)
**Impact:** High | **Risk:** Medium | **LOC Reduction:** ~250 lines

1. **Create `/components/ui/widget/widget-controls.tsx`**

```typescript
import React from 'react';

interface WidgetSelectProps<T extends string = string> {
  value: T;
  onChange: (value: T) => void;
  options: readonly { value: T; label: string }[];
  disabled?: boolean;
  className?: string;
  label?: string;
}

export function WidgetSelect<T extends string = string>({
  value,
  onChange,
  options,
  disabled = false,
  className = '',
  label,
}: WidgetSelectProps<T>) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-xs text-muted-foreground">{label}</label>
      )}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        disabled={disabled}
        className={`px-2 py-1 text-sm border rounded-md bg-background ${className}`}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

interface WidgetSliderProps {
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  label: string;
  showValue?: boolean;
  disabled?: boolean;
}

export function WidgetSlider({
  value,
  onChange,
  min,
  max,
  step = 1,
  label,
  showValue = true,
  disabled = false,
}: WidgetSliderProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-muted-foreground">
        {label}: {showValue && <span className="font-mono">{value}</span>}
      </label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        disabled={disabled}
        className="w-full"
      />
    </div>
  );
}

interface WidgetNumberInputProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  label: string;
  disabled?: boolean;
}

export function WidgetNumberInput({
  value,
  onChange,
  min,
  max,
  step = 1,
  label,
  disabled = false,
}: WidgetNumberInputProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-muted-foreground">{label}</label>
      <input
        type="number"
        value={value}
        onChange={(e) => {
          const val = Number(e.target.value);
          if (min !== undefined && val < min) return;
          if (max !== undefined && val > max) return;
          onChange(val);
        }}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        className="w-full text-xs border border-border rounded-md px-2 py-1 bg-background"
      />
    </div>
  );
}

interface WidgetCheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  disabled?: boolean;
}

export function WidgetCheckbox({
  checked,
  onChange,
  label,
  disabled = false,
}: WidgetCheckboxProps) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="checkbox"
        id={label}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="rounded border-border"
      />
      <label htmlFor={label} className="text-xs text-muted-foreground cursor-pointer">
        {label}
      </label>
    </div>
  );
}
```

2. **Update all widgets** to use new control components

**Example Before:**
```typescript
<select 
  value={timePeriod} 
  onChange={(e) => setTimePeriod(e.target.value)}
  className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
>
  {periods.map(p => (
    <option key={p.value} value={p.value}>{p.label}</option>
  ))}
</select>
```

**Example After:**
```typescript
import { WidgetSelect } from '@/components/ui/widget/widget-controls';
import { TIME_PERIODS } from '@/lib/widget-constants';

<WidgetSelect
  value={timePeriod}
  onChange={setTimePeriod}
  options={TIME_PERIODS}
  label="Time Period"
/>
```

---

### Phase 3: MonteCarloWidget Decomposition (3-5 days)
**Impact:** Very High | **Risk:** High | **LOC Reduction:** ~600 lines

1. **Create state management hook** `/app/dashboard/widgets/monte-carlo/useMonteCarloConfig.ts`

```typescript
import { useState } from 'react';

export interface MonteCarloConfig {
  numSimulations: number;
  timeHorizonYears: number;
  initialValue: number;
  estimationMethod: 'Historical Mean' | 'Exponentially Weighted';
  confidenceLevel: number;
  includeDividends: boolean;
  enableContributions: boolean;
  contributionAmount: number;
  contributionFrequency: 'Monthly' | 'Quarterly' | 'Annual';
  selectedSymbols: string[];
  weightMethod: 'Equal Weights' | 'Max Sharpe Ratio' | 'Min Volatility' | 'Current Portfolio' | 'Custom';
  customWeights: Record<string, number>;
  showWeightConfig: boolean;
  enableRebalancing: boolean;
  rebalancingFrequency: 'Quarterly' | 'Semi-Annual' | 'Annual';
  driftThreshold: number;
}

export function useMonteCarloConfig(defaults?: Partial<MonteCarloConfig>) {
  const [config, setConfig] = useState<MonteCarloConfig>({
    numSimulations: defaults?.numSimulations ?? 10000,
    timeHorizonYears: defaults?.timeHorizonYears ?? 10,
    initialValue: defaults?.initialValue ?? 100000,
    estimationMethod: defaults?.estimationMethod ?? 'Historical Mean',
    confidenceLevel: defaults?.confidenceLevel ?? 0.95,
    includeDividends: defaults?.includeDividends ?? true,
    enableContributions: defaults?.enableContributions ?? false,
    contributionAmount: defaults?.contributionAmount ?? 0,
    contributionFrequency: defaults?.contributionFrequency ?? 'Annual',
    selectedSymbols: defaults?.selectedSymbols ?? [],
    weightMethod: defaults?.weightMethod ?? 'Current Portfolio',
    customWeights: defaults?.customWeights ?? {},
    showWeightConfig: defaults?.showWeightConfig ?? false,
    enableRebalancing: defaults?.enableRebalancing ?? false,
    rebalancingFrequency: defaults?.rebalancingFrequency ?? 'Annual',
    driftThreshold: defaults?.driftThreshold ?? 5,
  });

  return { config, setConfig };
}
```

2. **Create subcomponents:**

**MonteCarloControls.tsx** (~150 lines):
- Simulation count selector
- Time horizon input
- Initial value input
- Estimation method
- Confidence level
- Dividend/contribution toggles

**MonteCarloMetrics.tsx** (~100 lines):
- CAGR metrics (10th, median, 90th)
- Probability of loss
- VaR and CVaR
- Historical Sharpe/Volatility
- Max Drawdown

**MonteCarloHistogram.tsx** (~150 lines):
- Histogram data calculation (useMemo)
- SVG histogram rendering
- Bucket tooltips

**MonteCarloTimeseries.tsx** (~150 lines):
- Timeseries data calculation (useMemo)
- Dual-axis SVG chart
- Confidence bands
- Drawdown overlay

**PortfolioComposition.tsx** (~120 lines):
- Weight method selector
- Symbol selection
- Custom weight inputs
- Rebalancing toggles
- **REUSABLE** in other widgets!

**RebalancingAnalysis.tsx** (~100 lines):
- Rebalancing metrics display
- Calendar table
- Drift threshold info
- **REUSABLE** in other widgets!

3. **Refactor main component** `index.tsx` (~100 lines):

```typescript
'use client';

import { BarChart3 } from 'lucide-react';
import { CacheBadge } from '@/components/ui/cache-badge';
import { useMonteCarloSimulation } from '@/hooks/use-portfolio-widgets';
import { useMonteCarloConfig } from './useMonteCarloConfig';
import { MonteCarloControls } from './MonteCarloControls';
import { MonteCarloMetrics } from './MonteCarloMetrics';
import { MonteCarloHistogram } from './MonteCarloHistogram';
import { MonteCarloTimeseries } from './MonteCarloTimeseries';
import { PortfolioComposition } from './PortfolioComposition';
import { RebalancingAnalysis } from './RebalancingAnalysis';
import type { ContentType } from '../widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 5 },
  contentType: 'height-heavy' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.0,
  isScrollable: true,
} as const;

interface MonteCarloWidgetProps {
  portfolioId?: string;
  defaultSimulations?: number;
}

export default function MonteCarloWidget({ 
  portfolioId, 
  defaultSimulations = 10000 
}: MonteCarloWidgetProps) {
  const { config, setConfig } = useMonteCarloConfig({ numSimulations: defaultSimulations });
  
  const { data: simulation, loading, isRefreshing, error, cacheHit } = useMonteCarloSimulation({
    portfolioId,
    numSimulations: config.numSimulations,
    timeHorizonDays: Math.round(config.timeHorizonYears * 252),
    initialValue: config.initialValue,
    estimationMethod: config.estimationMethod,
    confidenceLevel: config.confidenceLevel,
    includeDividends: config.includeDividends,
    enableContributions: config.enableContributions,
    contributionAmount: config.contributionAmount,
    contributionFrequency: config.contributionFrequency,
  });

  if (loading) return <LoadingSpinner label="Running simulation..." />;
  if (error) return <WidgetInsight title="Simulation Error" description={error} icon={XCircle} variant="destructive" />;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-start flex-shrink-0">
        <div>
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Monte Carlo Simulation
            {isRefreshing && (
              <span className="text-xs text-muted-foreground animate-pulse">(updating...)</span>
            )}
          </h3>
          <p className="text-xs text-muted-foreground mt-1">
            Risk analysis over {config.timeHorizonYears} years ({config.numSimulations.toLocaleString()} simulations)
          </p>
        </div>
        <CacheBadge show={cacheHit} />
      </div>
      
      <MonteCarloControls config={config} setConfig={setConfig} />
      <PortfolioComposition config={config} setConfig={setConfig} />
      <MonteCarloMetrics simulation={simulation} />
      <MonteCarloHistogram simulation={simulation} />
      <MonteCarloTimeseries simulation={simulation} />
      {config.enableRebalancing && (
        <RebalancingAnalysis 
          recommendations={simulation?.rebalancing_rec}
          driftThreshold={config.driftThreshold}
        />
      )}
    </div>
  );
}
```

**Benefits:**
- Main widget reduced from 796 → ~100 lines
- Each subcomponent has single responsibility
- Components are testable in isolation
- PortfolioComposition and RebalancingAnalysis are reusable
- State management centralized in custom hook

---

### Phase 4: Visualization Components (2-3 days)
**Impact:** Medium | **Risk:** Medium | **LOC Reduction:** ~200 lines

1. **Extract histogram component** if used in multiple places
2. **Extract dual-axis chart** if pattern repeats
3. **Create recharts wrappers** for consistency

**Only proceed if visualizations are reused across multiple widgets.**

---

### Phase 5: Advanced Patterns (Optional, 2-3 days)
**Impact:** Low | **Risk:** Low | **LOC Reduction:** ~100 lines

1. **Create widget state HOC**
2. **Extract common hooks** (useTimePeriodSelect, useBenchmarkSelect)
3. **Improve state management** for other complex widgets

---

## Migration Strategy

### Step-by-Step Approach:

1. **Create new files** (formatters, constants, controls) without modifying widgets
2. **Test new utilities** in isolation
3. **Update one widget at a time** (start with simplest: PortfolioSummaryWidget)
4. **Validate each widget** after refactoring
5. **Run full test suite** after each phase
6. **Create PR per phase** for easier review

### Rollback Plan:

- Keep original widget files as `.tsx.backup` until phase is validated
- Use feature flags if necessary
- Deploy incrementally (one phase at a time)

---

## Success Metrics

### Quantitative Metrics:

- **LOC Reduction:** Target 40% reduction across all widgets
  - MonteCarloWidget: 796 → ~100 lines (-87%)
  - Others: Average 20% reduction
- **Duplication Elimination:** 0 duplicate formatter functions
- **Component Reuse:** 80% of widgets use shared controls
- **Test Coverage:** Increase from current to 80%+ for new components

### Qualitative Metrics:

- **Maintainability:** Easier to locate and fix bugs
- **Readability:** Each component has clear, single purpose
- **Extensibility:** New widgets can reuse existing patterns
- **Developer Experience:** Faster development of new widgets

---

## Risk Assessment

### High Risk Items:

1. **MonteCarloWidget Decomposition** (Phase 3)
   - **Risk:** Breaking existing functionality
   - **Mitigation:** Extensive testing, gradual migration, feature flags
   - **Rollback:** Keep backup of original file

2. **Widget Controls** (Phase 2)
   - **Risk:** Inconsistent behavior across widgets
   - **Mitigation:** Thorough testing of all control types
   - **Rollback:** Easy to revert individual widgets

### Medium Risk Items:

1. **Formatter Extraction** (Phase 1)
   - **Risk:** Subtle behavior differences in number formatting
   - **Mitigation:** Unit tests for all formatters, visual regression tests
   - **Rollback:** Easy to revert per-widget

### Low Risk Items:

1. **Constants Extraction** (Phase 1)
   - **Risk:** Import path changes
   - **Mitigation:** TypeScript will catch errors
   - **Rollback:** Simple search-and-replace

---

## Recommended Immediate Actions

### This Week:

1. ✅ **Review this document** with team
2. ✅ **Get approval** for Phase 1 (Quick Wins)
3. 🔄 **Create `/lib/formatters.ts`**
4. 🔄 **Create `/lib/widget-constants.ts`**
5. 🔄 **Update 3 simple widgets** (PortfolioSummary, Performance, Dividend)

### Next Week:

1. 🔄 **Complete Phase 1** (all widgets using formatters)
2. 🔄 **Start Phase 2** (widget controls)
3. 🔄 **Plan Phase 3** (Monte Carlo decomposition)

---

## Conclusion

The widget codebase has grown organically with significant duplication and some violations of Single Responsibility Principle. The proposed refactoring plan addresses these issues systematically, with low-risk quick wins first, followed by more complex decompositions.

**Key Takeaways:**
- Eliminate 500+ lines of duplicate code
- Break 796-line MonteCarloWidget into 7 focused components
- Create reusable UI components (PortfolioComposition, RebalancingAnalysis)
- Improve maintainability and testability
- Establish patterns for future widget development

**Estimated Timeline:** 10-15 days (2-3 weeks)  
**Estimated ROI:** Very High (code quality, velocity, maintainability)

---

**Next Steps:** Approve Phase 1 and begin implementation.
