# Professional Design System Documentation

A comprehensive, data-focused design system for financial applications with emphasis on data legibility and professional appearance.

## Table of Contents

1. [Overview](#overview)
2. [Design Tokens](#design-tokens)
3. [Component Library](#component-library)
4. [Theme System](#theme-system)
5. [Animation System](#animation-system)
6. [Usage Guidelines](#usage-guidelines)
7. [Examples](#examples)

---

## Overview

### Purpose

This design system is specifically crafted for financial data applications, prioritizing:

- **Data Legibility**: Tabular numerals, high contrast, semantic coloring
- **Professional Appearance**: Industry-standard visual quality for client presentations
- **Consistency**: Unified patterns across all interface sections
- **Accessibility**: WCAG AA compliance for inclusive design

### Architecture

```
src/
├── lib/
│   ├── design-tokens/     # Core design tokens
│   ├── animations.ts      # Animation utilities
│   └── utils.ts          # Utility functions
├── components/ui/         # Reusable UI components
├── hooks/                # Custom hooks
└── app/                  # Application pages
```

---

## Design Tokens

### Colors

Our color system provides semantic meaning for financial data:

```typescript
// Semantic Financial Colors
const financialColors = {
  gain: 'hsl(142, 76%, 36%)',      // Green for positive values
  loss: 'hsl(0, 84%, 60%)',       // Red for negative values
  neutral: 'hsl(220, 9%, 46%)',   // Gray for neutral values
  warning: 'hsl(45, 93%, 47%)',   // Yellow for warnings
  info: 'hsl(217, 91%, 60%)',     // Blue for information
}

// Professional Color Palette
const colors = {
  primary: 'hsl(214, 100%, 50%)',
  secondary: 'hsl(220, 9%, 46%)',
  background: 'hsl(0, 0%, 100%)',
  surface: 'hsl(210, 20%, 98%)',
  border: 'hsl(214, 32%, 91%)',
}
```

### Typography

Optimized for financial data with tabular numerals:

```css
/* Base typography with tabular numerals */
.tabular-nums {
  font-variant-numeric: tabular-nums;
}

/* Typography scales */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
```

### Spacing

Consistent spacing system based on 4px grid:

```typescript
const spacing = {
  xs: '0.25rem',    // 4px
  sm: '0.5rem',     // 8px
  base: '1rem',     // 16px
  lg: '1.5rem',     // 24px
  xl: '2rem',       // 32px
  '2xl': '3rem',    // 48px
}
```

---

## Component Library

### Data Components

#### MetricCard

Displays financial metrics with trend-based styling:

```tsx
import { MetricCard } from '@/components/ui/metric-card'

<MetricCard
  title="Portfolio Value"
  value={1234567.89}
  change={5.2}
  trend="up"
  size="lg"
  format="currency"
/>
```

**Props:**
- `title: string` - Metric label
- `value: number` - Numeric value
- `change?: number` - Change amount
- `trend?: 'up' | 'down' | 'neutral'` - Visual indicator
- `size?: 'sm' | 'base' | 'lg'` - Component size
- `format?: 'currency' | 'percentage' | 'number'` - Value formatting

#### FinancialAmount

Specialized component for displaying monetary values:

```tsx
import { FinancialAmount } from '@/components/ui/financial-amount'

<FinancialAmount
  amount={-1234.56}
  currency="USD"
  showTrend
  size="lg"
/>
```

**Props:**
- `amount: number` - Monetary amount
- `currency?: string` - Currency code (default: 'USD')
- `showTrend?: boolean` - Display trend indicators
- `size?: 'sm' | 'base' | 'lg'` - Component size
- `precision?: number` - Decimal places

#### DataTable

Sortable table optimized for financial data:

```tsx
import { DataTable } from '@/components/ui/data-table'

const columns = [
  { key: 'symbol', label: 'Symbol', sortable: true },
  { key: 'price', label: 'Price', sortable: true, align: 'right' },
  { key: 'change', label: 'Change', sortable: true, align: 'right' },
]

<DataTable
  data={holdings}
  columns={columns}
  loading={false}
  variant="striped"
/>
```

### Layout Components

#### GridLayout

Responsive grid system for dashboard layouts:

```tsx
import { GridLayout, MetricGrid, ChartGrid } from '@/components/ui/grid-layout'

// Basic grid
<GridLayout columns={3} gap="lg">
  {metrics.map(metric => <MetricCard key={metric.id} {...metric} />)}
</GridLayout>

// Specialized grids
<MetricGrid>
  <MetricCard {...portfolioValue} />
  <MetricCard {...dayChange} />
</MetricGrid>
```

#### Card

Enhanced card component with professional variants:

```tsx
import { Card, CardHeader, CardContent } from '@/components/ui/card'

<Card variant="professional">
  <CardHeader>
    <h3>Holdings Breakdown</h3>
  </CardHeader>
  <CardContent>
    <DataTable data={holdings} columns={columns} />
  </CardContent>
</Card>
```

**Variants:**
- `default` - Basic card styling
- `professional` - Enhanced shadows and borders
- `elevated` - Prominent elevation
- `subtle` - Minimal styling
- `data` - Optimized for data display

### Interactive Components

#### Button

Professional button variants for financial applications:

```tsx
import { Button } from '@/components/ui/button'

<Button variant="professional">
  Generate Report
</Button>

<Button variant="data-action" size="sm">
  Export Data
</Button>
```

**Variants:**
- `default` - Standard button
- `professional` - Enhanced styling for business use
- `data-action` - Optimized for data-related actions
- `ghost` - Minimal styling
- `outline` - Outlined button

#### StatusIndicator

Visual status indicators with financial semantics:

```tsx
import { StatusIndicator } from '@/components/ui/status-indicator'

<StatusIndicator variant="success">
  Live Data
</StatusIndicator>

<StatusIndicator variant="gain" size="sm">
  +2.5%
</StatusIndicator>
```

### Utility Components

#### PercentageChange

Displays percentage changes with automatic trend detection:

```tsx
import { PercentageChange } from '@/components/ui/percentage-change'

<PercentageChange
  value={-2.47}
  showIcon
  animate
/>
```

#### MetricGroup

Compound component for organizing related metrics:

```tsx
import { MetricGroup, PortfolioMetrics } from '@/components/ui/metric-group'

<PortfolioMetrics columns={3}>
  <MetricCard {...totalValue} />
  <MetricCard {...dayChange} />
  <MetricCard {...ytdReturn} />
</PortfolioMetrics>
```

---

## Theme System

### Theme Provider

Wrap your application with the theme provider:

```tsx
import { ThemeProvider } from '@/components/ui/theme-provider'

<ThemeProvider defaultTheme="system" defaultColorScheme="blue">
  <App />
</ThemeProvider>
```

### Theme Switching

Use built-in switcher components:

```tsx
import { ThemeSwitcher, ColorSchemeSwitcher } from '@/components/ui/theme-provider'

// Theme mode switcher
<ThemeSwitcher showLabel size="sm" />

// Color scheme switcher  
<ColorSchemeSwitcher showLabel />
```

### Using Themes in Components

```tsx
import { useTheme } from '@/components/ui/theme-provider'

function MyComponent() {
  const { effectiveTheme, colorScheme } = useTheme()
  
  return (
    <div className={`theme-${effectiveTheme} scheme-${colorScheme}`}>
      Content adapts to theme
    </div>
  )
}
```

---

## Animation System

### Animation Hooks

```tsx
import { useAnimation, useValueTransition } from '@/lib/animations'

function AnimatedMetric({ value }: { value: number }) {
  const { currentValue } = useValueTransition(value)
  const { isAnimating, trigger } = useAnimation()
  
  return (
    <div className={isAnimating ? 'animate-pulse' : ''}>
      {currentValue.toFixed(2)}
    </div>
  )
}
```

### Animation Presets

```tsx
import { animationPresets } from '@/lib/animations'

// Use predefined animation configurations
const animation = useAnimation(animationPresets.financial)
```

---

## Usage Guidelines

### Best Practices

#### Data Display
- Always use tabular numerals for financial data
- Apply semantic colors consistently (green=gains, red=losses)
- Align numerical data to the right
- Use appropriate precision for monetary values

#### Color Usage
```tsx
// Good - Semantic color usage
<PercentageChange value={2.5} /> // Automatically green for positive

// Bad - Manual color assignment
<span className="text-green-500">+2.5%</span>
```

#### Typography
```tsx
// Good - Using design tokens
<div className="text-lg tabular-nums">
  $1,234,567.89
</div>

// Bad - Hardcoded styles
<div style={{ fontSize: '18px' }}>
  $1,234,567.89
</div>
```

#### Spacing
```tsx
// Good - Consistent spacing
<div className="space-y-4">
  <MetricCard />
  <MetricCard />
</div>

// Bad - Arbitrary spacing
<div style={{ marginBottom: '13px' }}>
  <MetricCard />
</div>
```

### Accessibility Guidelines

#### Color Contrast
- All text meets WCAG AA contrast requirements
- Color is never the only means of conveying information
- Focus indicators are clearly visible

#### Keyboard Navigation
- All interactive elements are keyboard accessible
- Tab order follows logical flow
- Focus traps work in modal dialogs

#### Screen Readers
- All images have appropriate alt text
- Form inputs have proper labels
- Status changes are announced

### Performance Considerations

#### Animation Performance
```tsx
// Good - Use animation hooks with reduced motion support
const shouldAnimate = useAnimations()

return (
  <div className={shouldAnimate ? 'animate-fade-in' : ''}>
    Content
  </div>
)
```

#### Large Datasets
```tsx
// Good - Virtualized tables for large datasets
<DataTable
  data={largeDataset}
  virtualized={largeDataset.length > 100}
/>
```

---

## Examples

### Dashboard Layout

```tsx
import { GridLayout, MetricGrid, ChartGrid } from '@/components/ui/grid-layout'
import { MetricCard } from '@/components/ui/metric-card'
import { Card } from '@/components/ui/card'

export function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Portfolio Overview</h2>
        <MetricGrid>
          <MetricCard
            title="Total Value"
            value={1234567.89}
            change={12345.67}
            trend="up"
            format="currency"
            size="lg"
          />
          <MetricCard
            title="Day Change"
            value={2.47}
            trend="up"
            format="percentage"
          />
          <MetricCard
            title="YTD Return"
            value={15.2}
            trend="up"
            format="percentage"
          />
        </MetricGrid>
      </section>

      {/* Charts */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Performance</h2>
        <ChartGrid>
          <Card variant="professional">
            <CardContent>
              <PerformanceChart />
            </CardContent>
          </Card>
        </ChartGrid>
      </section>
    </div>
  )
}
```

### Data Table with Sorting

```tsx
import { DataTable } from '@/components/ui/data-table'
import { FinancialAmount } from '@/components/ui/financial-amount'

const columns = [
  {
    key: 'symbol',
    label: 'Symbol',
    sortable: true,
  },
  {
    key: 'shares',
    label: 'Shares',
    sortable: true,
    align: 'right',
    render: (value: number) => (
      <span className="tabular-nums">{value.toLocaleString()}</span>
    ),
  },
  {
    key: 'price',
    label: 'Price',
    sortable: true,
    align: 'right',
    render: (value: number) => <FinancialAmount amount={value} />,
  },
  {
    key: 'change',
    label: 'Change',
    sortable: true,
    align: 'right',
    render: (value: number) => <PercentageChange value={value} showIcon />,
  },
]

export function HoldingsTable({ holdings }: { holdings: Holding[] }) {
  return (
    <Card variant="data">
      <CardHeader>
        <h3>Holdings</h3>
      </CardHeader>
      <CardContent>
        <DataTable
          data={holdings}
          columns={columns}
          variant="striped"
          hoverable
        />
      </CardContent>
    </Card>
  )
}
```

### Theme-Aware Component

```tsx
import { useTheme } from '@/components/ui/theme-provider'
import { useAnimations } from '@/lib/animations'

export function ThemedComponent() {
  const { effectiveTheme, colorScheme } = useTheme()
  const shouldAnimate = useAnimations()
  
  return (
    <div
      className={`
        ${effectiveTheme === 'dark' ? 'bg-gray-900' : 'bg-white'}
        ${shouldAnimate ? 'transition-colors duration-300' : ''}
      `}
      data-color-scheme={colorScheme}
    >
      <h2>Theme: {effectiveTheme}</h2>
      <p>Color Scheme: {colorScheme}</p>
    </div>
  )
}
```

---

## Migration Guide

### Converting Existing Components

#### From Hardcoded Styles to Design Tokens

```tsx
// Before
<div style={{ color: '#10b981', fontSize: '18px' }}>
  +$1,234.56
</div>

// After
<FinancialAmount
  amount={1234.56}
  showTrend
  size="lg"
/>
```

#### From Basic Cards to Enhanced Cards

```tsx
// Before
<div className="bg-white border rounded-lg p-4">
  <h3>Portfolio Value</h3>
  <p>$1,234,567.89</p>
</div>

// After
<MetricCard
  title="Portfolio Value"
  value={1234567.89}
  format="currency"
  size="lg"
/>
```

### Updating Color Usage

```tsx
// Before - Manual color classes
<span className="text-green-500">+2.5%</span>
<span className="text-red-500">-1.2%</span>

// After - Semantic components
<PercentageChange value={2.5} />
<PercentageChange value={-1.2} />
```

This design system provides a solid foundation for building professional, accessible, and consistent financial applications. For questions or contributions, please refer to the component source files and type definitions.