# Migration Guide: Professional Design System

This guide helps developers migrate existing hardcoded styles to the professional design system components and tokens.

## Table of Contents

1. [Migration Overview](#migration-overview)
2. [Color Migration](#color-migration)
3. [Typography Migration](#typography-migration)
4. [Component Migration](#component-migration)
5. [Layout Migration](#layout-migration)
6. [Theme Migration](#theme-migration)
7. [Testing & Validation](#testing--validation)
8. [Checklist](#checklist)

---

## Migration Overview

### Why Migrate?

- **Consistency**: Unified visual language across the application
- **Accessibility**: WCAG AA compliance built-in
- **Maintainability**: Centralized design tokens for easy updates
- **Performance**: Optimized components with proper hover states
- **Professional**: Industry-standard financial application appearance

### Migration Strategy

1. **Audit**: Identify hardcoded styles and custom components
2. **Replace**: Convert to design system components
3. **Validate**: Test accessibility and functionality
4. **Clean**: Remove old CSS and unused code

---

## Color Migration

### Before: Hardcoded Colors

```tsx
// ❌ Old approach - hardcoded colors
<div className="text-green-500">+2.5%</div>
<div className="text-red-500">-1.2%</div>
<div style={{ color: '#10b981' }}>$1,234.56</div>
<span className="bg-blue-600 text-white">Live</span>
```

### After: Semantic Design Tokens

```tsx
// ✅ New approach - semantic components
<PercentageChange value={2.5} showIcon />
<PercentageChange value={-1.2} showIcon />
<FinancialAmount amount={1234.56} showTrend />
<StatusIndicator variant="success">Live</StatusIndicator>
```

### Color Mapping Reference

| Old Hardcoded | New Semantic | Component |
|---------------|--------------|-----------|
| `text-green-500` | `text-financial-positive` | `PercentageChange` |
| `text-red-500` | `text-financial-negative` | `PercentageChange` |
| `text-gray-600` | `text-financial-neutral` | `FinancialAmount` |
| `bg-blue-600` | `StatusIndicator` variant | `StatusIndicator` |
| `bg-green-100` | Auto-applied | `MetricCard` with trend |

### CSS Variable Migration

```css
/* ❌ Old CSS */
.custom-positive { color: #10b981; }
.custom-negative { color: #dc2626; }
.custom-neutral { color: #6b7280; }

/* ✅ New CSS using design tokens */
.positive { color: hsl(var(--financial-positive)); }
.negative { color: hsl(var(--financial-negative)); }
.neutral { color: hsl(var(--financial-neutral)); }
```

---

## Typography Migration

### Financial Numbers

```tsx
// ❌ Old approach
<span style={{ fontSize: '24px', fontWeight: 'bold' }}>
  $1,234,567.89
</span>

// ✅ New approach
<FinancialAmount 
  amount={1234567.89} 
  size="lg" 
  currency="USD" 
/>
```

### Tabular Numerals

```tsx
// ❌ Old approach
<div className="font-mono">
  $1,000,000.00
</div>

// ✅ New approach - automatic tabular numerals
<div className="tabular-nums">
  $1,000,000.00
</div>
```

### Typography Scale Migration

| Old Class | New Class | Use Case |
|-----------|-----------|----------|
| `text-2xl font-bold` | `text-financial-2xl` | Large metric values |
| `text-xl font-semibold` | `text-financial-xl` | Standard metric values |
| `text-lg font-medium` | `text-financial-lg` | Small metric values |
| `text-sm text-gray-600` | `text-text-secondary` | Labels and descriptions |

---

## Component Migration

### Button Migration

```tsx
// ❌ Old buttons
<button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
  Export Data
</button>

<button className="bg-gray-900 text-white px-6 py-3 rounded shadow-lg">
  Generate Report
</button>

// ✅ New Button component
<Button variant="data-action" size="default">
  Export Data
</Button>

<Button variant="professional" size="lg">
  Generate Report
</Button>
```

### Card Migration

```tsx
// ❌ Old card structure
<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
  <h3 className="text-lg font-semibold mb-2">Portfolio Value</h3>
  <div className="text-2xl font-bold text-gray-900">$1,234,567.89</div>
  <div className="text-sm text-green-600">+$12,345.67 (+1.2%)</div>
</div>

// ✅ New MetricCard component
<MetricCard
  title="Portfolio Value"
  value={1234567.89}
  change={12345.67}
  trend="up"
  format="currency"
  size="lg"
/>
```

### Table Migration

```tsx
// ❌ Old table
<table className="w-full">
  <thead>
    <tr className="border-b border-gray-200">
      <th className="text-left py-3 px-4">Symbol</th>
      <th className="text-right py-3 px-4">Price</th>
      <th className="text-right py-3 px-4">Change</th>
    </tr>
  </thead>
  <tbody>
    {data.map((row, index) => (
      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
        <td className="py-3 px-4">{row.symbol}</td>
        <td className="py-3 px-4 text-right tabular-nums">${row.price}</td>
        <td className="py-3 px-4 text-right">
          <span className={row.change >= 0 ? 'text-green-600' : 'text-red-600'}>
            {row.change >= 0 ? '+' : ''}{row.change}%
          </span>
        </td>
      </tr>
    ))}
  </tbody>
</table>

// ✅ New DataTable component
<DataTable
  data={data}
  columns={[
    { key: 'symbol', label: 'Symbol', sortable: true },
    { key: 'price', label: 'Price', sortable: true, align: 'right' },
    { key: 'change', label: 'Change', sortable: true, align: 'right' },
  ]}
  variant="hoverable"
/>
```

---

## Layout Migration

### Grid Systems

```tsx
// ❌ Old grid approach
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {metrics.map((metric) => (
    <div key={metric.id} className="bg-white p-6 rounded-lg border">
      {/* metric content */}
    </div>
  ))}
</div>

// ✅ New GridLayout system
<MetricGrid>
  {metrics.map((metric) => (
    <MetricCard key={metric.id} {...metric} />
  ))}
</MetricGrid>
```

### Dashboard Layout

```tsx
// ❌ Old dashboard structure
<div className="max-w-7xl mx-auto px-4 py-8">
  <div className="mb-8">
    <h1 className="text-3xl font-bold">Dashboard</h1>
  </div>
  
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
    {/* metric cards */}
  </div>
  
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    {/* charts */}
  </div>
</div>

// ✅ New professional layout
<div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
  <Section title="Portfolio Overview">
    <MetricGrid>
      {metrics.map((metric) => <MetricCard key={metric.id} {...metric} />)}
    </MetricGrid>
  </Section>
  
  <Section title="Performance Analysis">
    <ChartGrid>
      {charts.map((chart) => (
        <Card key={chart.id} variant="professional">
          <CardContent>{chart.component}</CardContent>
        </Card>
      ))}
    </ChartGrid>
  </Section>
</div>
```

---

## Theme Migration

### Dark Mode Support

```tsx
// ❌ Old theme implementation
const [isDark, setIsDark] = useState(false)

<div className={`${isDark ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
  Content
</div>

// ✅ New theme system
import { ThemeProvider, useTheme } from '@/components/ui/theme-provider'

// Wrap app with provider
<ThemeProvider defaultTheme="system">
  <App />
</ThemeProvider>

// Use in components
function MyComponent() {
  const { effectiveTheme } = useTheme()
  return (
    <div className="bg-background text-foreground">
      Content automatically adapts to theme
    </div>
  )
}
```

### Theme Controls

```tsx
// ❌ Old theme toggle
<button onClick={() => setIsDark(!isDark)}>
  {isDark ? '☀️' : '🌙'}
</button>

// ✅ New theme switcher
<ThemeSwitcher showLabel />
<ColorSchemeSwitcher showLabel />
```

---

## Testing & Validation

### Accessibility Testing

```tsx
// Add to your test file
import { AccessibilityTestPanel } from '@/lib/accessibility-utils'

// Test component accessibility
function TestComponent() {
  const [elementRef, setElementRef] = React.useState<HTMLElement | null>(null)
  
  return (
    <div>
      <div ref={setElementRef}>
        <MetricCard title="Test" value={100} />
      </div>
      <AccessibilityTestPanel targetElement={elementRef} />
    </div>
  )
}
```

### Visual Regression Testing

```typescript
// Add visual tests for migrated components
describe('Design System Migration', () => {
  it('matches expected design for MetricCard', () => {
    cy.visit('/design-system')
    cy.get('[data-testid="metric-card"]').should('be.visible')
    cy.matchImageSnapshot('metric-card')
  })
})
```

### Color Contrast Validation

```typescript
import { checkWCAGCompliance } from '@/lib/accessibility-utils'

// Validate color combinations
const result = checkWCAGCompliance('#ffffff', '#2563eb', false)
expect(result.level).toBe('AA') // or 'AAA'
expect(result.passes).toBe(true)
```

---

## Step-by-Step Migration Process

### Phase 1: Audit & Inventory

1. **Identify components to migrate**:
   ```bash
   # Search for hardcoded colors
   grep -r "text-green-" src/
   grep -r "text-red-" src/
   grep -r "bg-blue-" src/
   
   # Search for hardcoded styles
   grep -r "style={{" src/
   grep -r "className.*text-" src/
   ```

2. **Create migration tracking sheet**:
   ```markdown
   - [ ] Portfolio value display → MetricCard
   - [ ] Percentage changes → PercentageChange  
   - [ ] Data tables → DataTable
   - [ ] Status indicators → StatusIndicator
   - [ ] Custom buttons → Button variants
   ```

### Phase 2: Install Dependencies

```bash
# Install any missing dependencies
npm install class-variance-authority
npm install lucide-react
npm install @radix-ui/react-slot
```

### Phase 3: Gradual Migration

1. **Start with leaf components** (no dependencies)
2. **Migrate common patterns** (buttons, cards)
3. **Update layout components** (grids, containers)
4. **Integrate theme system**

### Phase 4: Testing & Cleanup

1. **Run accessibility audits**
2. **Test responsive behavior**  
3. **Validate dark mode**
4. **Remove unused CSS**

---

## Migration Checklist

### Pre-Migration
- [ ] Audit existing components and styles
- [ ] Install design system dependencies
- [ ] Set up theme provider in app root
- [ ] Create migration tracking document

### Component Migration
- [ ] Replace hardcoded colors with semantic variants
- [ ] Convert custom cards to MetricCard components
- [ ] Update buttons to use professional variants
- [ ] Migrate tables to DataTable component
- [ ] Replace status displays with StatusIndicator
- [ ] Convert percentage displays to PercentageChange
- [ ] Update financial amounts to FinancialAmount

### Layout Migration
- [ ] Replace custom grids with GridLayout system
- [ ] Use MetricGrid for metric collections
- [ ] Implement ChartGrid for chart layouts
- [ ] Add Section components for organization
- [ ] Update responsive breakpoints

### Theme Integration
- [ ] Wrap app with ThemeProvider
- [ ] Add theme switcher to header/settings
- [ ] Test dark mode functionality
- [ ] Validate color scheme switching
- [ ] Check reduced motion preferences

### Testing & Validation
- [ ] Run accessibility audit on all pages
- [ ] Test keyboard navigation
- [ ] Validate WCAG AA compliance
- [ ] Check responsive behavior across devices
- [ ] Test theme switching functionality
- [ ] Verify hover and animation effects

### Cleanup
- [ ] Remove unused CSS files
- [ ] Clean up hardcoded style attributes
- [ ] Remove old color variables
- [ ] Update documentation
- [ ] Archive old component files

### Performance Validation
- [ ] Test sub-3-second data identification
- [ ] Verify 60fps interactions
- [ ] Check animation performance
- [ ] Validate bundle size impact

---

## Common Migration Patterns

### Pattern 1: Metric Display

```tsx
// Before
<div className="bg-white p-4 rounded border">
  <div className="text-sm text-gray-600">Portfolio Value</div>
  <div className="text-2xl font-bold">$1,234,567</div>
  <div className="text-green-600">+$12,345 (+1.2%)</div>
</div>

// After
<MetricCard
  title="Portfolio Value"
  value={1234567}
  change={12345}
  trend="up"
  format="currency"
/>
```

### Pattern 2: Status Display

```tsx
// Before
<span className={`px-2 py-1 rounded text-sm ${
  status === 'live' ? 'bg-green-100 text-green-800' :
  status === 'delayed' ? 'bg-yellow-100 text-yellow-800' :
  'bg-red-100 text-red-800'
}`}>
  {status}
</span>

// After
<StatusIndicator variant={
  status === 'live' ? 'success' :
  status === 'delayed' ? 'warning' :
  'danger'
}>
  {status}
</StatusIndicator>
```

### Pattern 3: Interactive Elements

```tsx
// Before
<button 
  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
  onClick={exportData}
>
  Export Data
</button>

// After
<Button variant="data-action" onClick={exportData}>
  Export Data
</Button>
```

This migration guide ensures a systematic approach to adopting the professional design system while maintaining functionality and improving accessibility.