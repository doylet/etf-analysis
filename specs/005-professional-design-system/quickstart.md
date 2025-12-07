# Professional Design System - Implementation Quickstart

**Target Audience**: Frontend developers implementing the design system  
**Prerequisites**: Next.js 16+, TypeScript, Tailwind CSS 4, shadcn/ui foundation  
**Estimated Time**: 2-3 days for full implementation

## Overview

This guide walks through implementing a professional design system optimized for financial data display. The system enhances the existing shadcn/ui foundation with specialized components and design tokens.

## Phase 1: Design Token Foundation (Day 1)

### 1. Install Dependencies

```bash
# Already installed in project:
# @radix-ui/react-slot, class-variance-authority, clsx, tailwind-merge

# Additional type utilities (if needed)
npm install --save-dev @types/react
```

### 2. Create Design Token Structure

```bash
mkdir -p frontend/v1/src/lib/design-tokens
```

**File: `frontend/v1/src/lib/design-tokens/colors.ts`**
```typescript
export const colors = {
  financial: {
    positive: '#15803d',      // Forest green for gains
    negative: '#dc2626',      // Professional red for losses
    neutral: '#374151',       // Charcoal gray for unchanged
    warning: '#d97706',       // Amber for warnings
    info: '#2563eb',         // Blue for information
  },
  background: {
    primary: 'oklch(1 0 0)',           // White
    secondary: 'oklch(0.985 0 0)',     // Light gray
    tertiary: 'oklch(0.97 0 0)',      // Subtle gray
    accent: 'oklch(0.985 0.02 240)',   // Light blue
  },
  text: {
    primary: 'oklch(0.145 0 0)',      // Near black
    secondary: 'oklch(0.4 0 0)',      // Dark gray
    tertiary: 'oklch(0.55 0 0)',      // Medium gray
    inverse: 'oklch(0.985 0 0)',      // White
  },
  interactive: {
    primary: 'oklch(0.4 0.2 240)',    // Blue
    secondary: 'oklch(0.55 0 0)',     // Gray
    hover: 'oklch(0.35 0.2 240)',     // Darker blue
    pressed: 'oklch(0.3 0.2 240)',    // Darkest blue
    disabled: 'oklch(0.85 0 0)',      // Light gray
  },
  border: {
    primary: 'oklch(0.92 0 0)',       // Light gray
    secondary: 'oklch(0.95 0 0)',     // Lighter gray
    focus: 'oklch(0.4 0.2 240)',      // Blue
    error: 'oklch(0.5 0.2 15)',       // Red
  },
} as const;

export const darkColors = {
  financial: {
    positive: '#22c55e',      // Bright green
    negative: '#ef4444',      // Bright red
    neutral: '#d1d5db',       // Light gray
    warning: '#f59e0b',       // Bright amber
    info: '#3b82f6',         // Bright blue
  },
  background: {
    primary: 'oklch(0.145 0 0)',      // Dark gray
    secondary: 'oklch(0.18 0 0)',     // Lighter dark
    tertiary: 'oklch(0.22 0 0)',      // Medium dark
    accent: 'oklch(0.16 0.02 240)',   // Dark blue
  },
  text: {
    primary: 'oklch(0.985 0 0)',      // Near white
    secondary: 'oklch(0.8 0 0)',      // Light gray
    tertiary: 'oklch(0.65 0 0)',      // Medium gray
    inverse: 'oklch(0.145 0 0)',      // Dark gray
  },
  interactive: {
    primary: 'oklch(0.6 0.2 240)',    // Bright blue
    secondary: 'oklch(0.65 0 0)',     // Gray
    hover: 'oklch(0.65 0.2 240)',     // Brighter blue
    pressed: 'oklch(0.7 0.2 240)',    // Brightest blue
    disabled: 'oklch(0.35 0 0)',      // Dark gray
  },
  border: {
    primary: 'oklch(0.3 0 0)',        // Medium dark
    secondary: 'oklch(0.25 0 0)',     // Darker
    focus: 'oklch(0.6 0.2 240)',      // Bright blue
    error: 'oklch(0.6 0.2 15)',       // Bright red
  },
} as const;

export type ColorTokens = typeof colors;
```

**File: `frontend/v1/src/lib/design-tokens/typography.ts`**
```typescript
export const typography = {
  family: {
    primary: 'Inter, system-ui, sans-serif',
    financial: 'Inter, system-ui, sans-serif', // With tabular-nums
    monospace: 'JetBrains Mono, Consolas, monospace',
  },
  financial: {
    xs: '0.75rem',    // 12px - Small table data
    sm: '0.875rem',   // 14px - Regular metrics
    base: '1rem',     // 16px - Standard financial data
    lg: '1.125rem',   // 18px - Important numbers
    xl: '1.5rem',     // 24px - Large metrics
    '2xl': '2rem',    // 32px - Hero numbers
  },
  text: {
    xs: '0.75rem',    // 12px - Captions
    sm: '0.875rem',   // 14px - Small text
    base: '1rem',     // 16px - Body text
    lg: '1.125rem',   // 18px - Headings
    xl: '1.25rem',    // 20px - Large headings
    '2xl': '1.5rem',  // 24px - Page titles
  },
  weight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: '1.2',
    normal: '1.4',
    relaxed: '1.6',
  },
  letterSpacing: {
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
  },
} as const;

export type TypographyTokens = typeof typography;
```

**File: `frontend/v1/src/lib/design-tokens/spacing.ts`**
```typescript
export const spacing = {
  component: {
    xs: '4px',
    sm: '8px',
    base: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
  },
  layout: {
    xs: '8px',
    sm: '16px',
    base: '24px',
    lg: '48px',
    xl: '64px',
    '2xl': '96px',
  },
  data: {
    table: {
      cellPadding: '12px',
      rowHeight: '48px',
      headerHeight: '56px',
    },
    card: {
      padding: '20px',
      gap: '16px',
    },
    metric: {
      gap: '8px',
      groupGap: '24px',
    },
  },
} as const;

export type SpacingTokens = typeof spacing;
```

**File: `frontend/v1/src/lib/design-tokens/index.ts`**
```typescript
export { colors, darkColors, type ColorTokens } from './colors';
export { typography, type TypographyTokens } from './typography';
export { spacing, type SpacingTokens } from './spacing';

export interface DesignTokens {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
}

export const lightTokens: DesignTokens = {
  colors,
  typography,
  spacing,
};

export const darkTokens: DesignTokens = {
  colors: darkColors,
  typography,
  spacing,
};
```

### 3. Update Global CSS

**File: `frontend/v1/src/app/globals.css`**
```css
@import "tailwindcss";

@layer base {
  :root {
    /* Existing variables... */
    
    /* Financial Colors */
    --financial-positive: #15803d;
    --financial-negative: #dc2626;
    --financial-neutral: #374151;
    --financial-warning: #d97706;
    --financial-info: #2563eb;
    
    /* Typography Features */
    --font-financial: Inter, system-ui, sans-serif;
    --font-feature-tabular: "tnum" 1;
  }

  .dark {
    /* Dark theme financial colors */
    --financial-positive: #22c55e;
    --financial-negative: #ef4444;
    --financial-neutral: #d1d5db;
    --financial-warning: #f59e0b;
    --financial-info: #3b82f6;
  }
  
  /* Financial typography utilities */
  .font-financial {
    font-family: var(--font-financial);
    font-variant-numeric: tabular-nums;
    font-feature-settings: var(--font-feature-tabular);
  }
  
  .text-financial-positive { color: var(--financial-positive); }
  .text-financial-negative { color: var(--financial-negative); }
  .text-financial-neutral { color: var(--financial-neutral); }
  .text-financial-warning { color: var(--financial-warning); }
  .text-financial-info { color: var(--financial-info); }
}
```

### 4. Extend Tailwind Configuration

**File: `frontend/v1/tailwind.config.js`**
```javascript
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'financial-positive': 'var(--financial-positive)',
        'financial-negative': 'var(--financial-negative)', 
        'financial-neutral': 'var(--financial-neutral)',
        'financial-warning': 'var(--financial-warning)',
        'financial-info': 'var(--financial-info)',
      },
      fontFamily: {
        'financial': ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'financial-xs': ['0.75rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-sm': ['0.875rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-base': ['1rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-lg': ['1.125rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-xl': ['1.5rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-2xl': ['2rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
      },
      spacing: {
        'component-xs': '4px',
        'component-sm': '8px', 
        'component-base': '16px',
        'component-lg': '24px',
        'component-xl': '32px',
        'component-2xl': '48px',
      }
    },
  },
  plugins: [],
}
```

## Phase 2: Core Components (Day 2)

### 1. Create MetricCard Component

**File: `frontend/v1/src/components/ui/metric-card.tsx`**
```typescript
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { Card, CardHeader, CardContent } from "./card"

const metricCardVariants = cva(
  "transition-colors",
  {
    variants: {
      variant: {
        default: "bg-card",
        highlighted: "bg-accent",
        compact: "bg-card",
        minimal: "bg-transparent border-none shadow-none",
      },
      size: {
        sm: "p-4",
        base: "p-6", 
        lg: "p-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "base",
    },
  }
)

interface TrendProps {
  direction: 'up' | 'down' | 'neutral';
  value: string;
  label?: string;
}

export interface MetricCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof metricCardVariants> {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: TrendProps;
  icon?: React.ComponentType<{ className?: string }>;
  formatValue?: (value: string | number) => string;
}

const MetricCard = React.forwardRef<HTMLDivElement, MetricCardProps>(
  ({ 
    className, 
    variant, 
    size, 
    title, 
    value, 
    subtitle, 
    trend, 
    icon: Icon,
    formatValue,
    ...props 
  }, ref) => {
    const formattedValue = formatValue ? formatValue(value) : value.toString();
    
    const trendColor = trend?.direction === 'up' 
      ? 'text-financial-positive' 
      : trend?.direction === 'down' 
      ? 'text-financial-negative' 
      : 'text-financial-neutral';

    return (
      <Card
        ref={ref}
        className={cn(metricCardVariants({ variant, size, className }))}
        {...props}
      >
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
          {Icon && (
            <Icon className="h-4 w-4 text-muted-foreground" />
          )}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold font-financial tracking-tight">
            {formattedValue}
          </div>
          {subtitle && (
            <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
          )}
          {trend && (
            <p className={cn("text-xs mt-2", trendColor)}>
              {trend.value} {trend.label}
            </p>
          )}
        </CardContent>
      </Card>
    )
  }
)
MetricCard.displayName = "MetricCard"

export { MetricCard, metricCardVariants }
```

### 2. Create FinancialAmount Component

**File: `frontend/v1/src/components/ui/financial-amount.tsx`**
```typescript
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const financialAmountVariants = cva(
  "font-financial tabular-nums",
  {
    variants: {
      size: {
        xs: "text-financial-xs",
        sm: "text-financial-sm",
        base: "text-financial-base",
        lg: "text-financial-lg",
        xl: "text-financial-xl",
        "2xl": "text-financial-2xl",
      },
      weight: {
        normal: "font-normal",
        medium: "font-medium", 
        semibold: "font-semibold",
        bold: "font-bold",
      },
      color: {
        auto: "", // Will be set based on value
        positive: "text-financial-positive",
        negative: "text-financial-negative",
        neutral: "text-financial-neutral",
        inherit: "",
      },
    },
    defaultVariants: {
      size: "base",
      weight: "medium",
      color: "auto",
    },
  }
)

export interface FinancialAmountProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof financialAmountVariants> {
  value: number;
  currency?: string;
  showSign?: boolean;
  precision?: number;
  abbreviated?: boolean;
}

const formatCurrency = (
  value: number, 
  currency: string = 'USD', 
  precision: number = 2,
  showSign: boolean = false,
  abbreviated: boolean = false
): string => {
  const absValue = Math.abs(value);
  let formattedValue = value;
  let suffix = '';

  if (abbreviated) {
    if (absValue >= 1e9) {
      formattedValue = value / 1e9;
      suffix = 'B';
    } else if (absValue >= 1e6) {
      formattedValue = value / 1e6; 
      suffix = 'M';
    } else if (absValue >= 1e3) {
      formattedValue = value / 1e3;
      suffix = 'K';
    }
  }

  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
    signDisplay: showSign ? 'always' : 'auto',
  }).format(formattedValue);

  return formatted + suffix;
};

const FinancialAmount = React.forwardRef<HTMLSpanElement, FinancialAmountProps>(
  ({ 
    className,
    value,
    currency = 'USD',
    showSign = false,
    precision = 2,
    abbreviated = false,
    size,
    weight,
    color = 'auto',
    ...props 
  }, ref) => {
    // Auto color determination
    const resolvedColor = color === 'auto' 
      ? value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral'
      : color;

    const formattedAmount = formatCurrency(value, currency, precision, showSign, abbreviated);

    return (
      <span
        ref={ref}
        className={cn(
          financialAmountVariants({ 
            size, 
            weight, 
            color: resolvedColor, 
            className 
          })
        )}
        {...props}
      >
        {formattedAmount}
      </span>
    )
  }
)
FinancialAmount.displayName = "FinancialAmount"

export { FinancialAmount, financialAmountVariants }
```

### 3. Update Existing Portfolio Components

**Update: `frontend/v1/src/components/PortfolioSummary.tsx`**
```typescript
// Replace the existing metric rendering with:
import { MetricCard } from '@/components/ui/metric-card';
import { FinancialAmount } from '@/components/ui/financial-amount';

// In the render section:
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <MetricCard 
    title="Total Value"
    value={summary.total_value}
    formatValue={(val) => 
      <FinancialAmount value={Number(val)} size="lg" />
    }
    icon={DollarSign}
  />
  <MetricCard 
    title="Total Return"
    value={summary.total_return}
    formatValue={(val) => 
      <FinancialAmount value={Number(val)} showSign color="auto" />
    }
    trend={{
      direction: summary.total_return >= 0 ? 'up' : 'down',
      value: `${summary.total_return_percent?.toFixed(2)}%`,
    }}
    icon={isPositiveChange(summary.total_return) ? TrendingUp : TrendingDown}
  />
  {/* Similar updates for other metrics */}
</div>
```

## Phase 3: Integration & Testing (Day 3)

### 1. Create Design Token Hook

**File: `frontend/v1/src/hooks/use-design-tokens.tsx`**
```typescript
import React, { createContext, useContext } from 'react';
import { DesignTokens, lightTokens, darkTokens } from '@/lib/design-tokens';
import { useTheme } from 'next-themes';

const DesignTokensContext = createContext<DesignTokens>(lightTokens);

export function DesignTokensProvider({ children }: { children: React.ReactNode }) {
  const { resolvedTheme } = useTheme();
  const tokens = resolvedTheme === 'dark' ? darkTokens : lightTokens;

  return (
    <DesignTokensContext.Provider value={tokens}>
      {children}
    </DesignTokensContext.Provider>
  );
}

export function useDesignTokens(): DesignTokens {
  const context = useContext(DesignTokensContext);
  if (!context) {
    throw new Error('useDesignTokens must be used within a DesignTokensProvider');
  }
  return context;
}
```

### 2. Add Theme Provider to App

**Update: `frontend/v1/src/app/layout.tsx`**
```typescript
import { ThemeProvider } from 'next-themes';
import { DesignTokensProvider } from '@/hooks/use-design-tokens';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <DesignTokensProvider>
            {children}
          </DesignTokensProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### 3. Test Implementation

Create a test page to verify all components:

**File: `frontend/v1/src/app/design-system/page.tsx`**
```typescript
import { MetricCard } from '@/components/ui/metric-card';
import { FinancialAmount } from '@/components/ui/financial-amount';
import { DollarSign, TrendingUp, TrendingDown } from 'lucide-react';

export default function DesignSystemTestPage() {
  return (
    <div className="container mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold">Design System Test</h1>
      
      <section>
        <h2 className="text-xl font-semibold mb-4">MetricCard Components</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard 
            title="Portfolio Value"
            value={121297.49}
            formatValue={(val) => 
              <FinancialAmount value={Number(val)} currency="USD" />
            }
            icon={DollarSign}
          />
          <MetricCard 
            title="Daily Change"
            value={2847.32}
            formatValue={(val) => 
              <FinancialAmount value={Number(val)} showSign color="auto" />
            }
            trend={{
              direction: 'up',
              value: '+2.34%',
              label: 'vs yesterday'
            }}
            icon={TrendingUp}
            variant="highlighted"
          />
          <MetricCard 
            title="Total Return"
            value={-1250.50}
            formatValue={(val) => 
              <FinancialAmount value={Number(val)} showSign color="auto" />
            }
            trend={{
              direction: 'down',
              value: '-1.02%',
              label: 'YTD'
            }}
            icon={TrendingDown}
          />
        </div>
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-4">Financial Amount Formatting</h2>
        <div className="space-y-2">
          <div>Small: <FinancialAmount value={1234.56} size="sm" /></div>
          <div>Base: <FinancialAmount value={12345.67} /></div>
          <div>Large: <FinancialAmount value={123456.78} size="lg" /></div>
          <div>Abbreviated: <FinancialAmount value={1234567} abbreviated /></div>
          <div>With Sign: <FinancialAmount value={1234.56} showSign /></div>
        </div>
      </section>
    </div>
  );
}
```

### 4. Accessibility Testing

Test with keyboard navigation:
```bash
# Install axe for accessibility testing
npm install --save-dev @axe-core/react
```

Add to your test setup:
```typescript
// In jest setup or test file
import { configureAxe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);
```

## Verification Checklist

- [ ] **Typography**: Financial numbers display with tabular numerals
- [ ] **Colors**: Semantic colors apply correctly (green for gains, red for losses)
- [ ] **Spacing**: Consistent spacing using design tokens
- [ ] **Accessibility**: 4.5:1 contrast ratio on all text
- [ ] **Responsive**: Components adapt to mobile screens
- [ ] **Theme Switching**: Light/dark themes work correctly
- [ ] **Performance**: No layout shifts or rendering delays

## Next Steps

1. **Add DataTable Component**: Implement sortable tables for holdings data
2. **Create Chart Themes**: Apply design system to Recharts components  
3. **Add Animation**: Implement subtle animations for value changes
4. **Documentation**: Create component library documentation
5. **Testing**: Add comprehensive unit and integration tests

## Common Issues & Solutions

**Issue**: Numbers not aligning in tables  
**Solution**: Ensure `font-financial` class is applied with `tabular-nums`

**Issue**: Colors not updating with theme  
**Solution**: Use CSS custom properties, not hardcoded values

**Issue**: Poor mobile performance  
**Solution**: Implement virtual scrolling for large data sets

**Issue**: Accessibility warnings  
**Solution**: Add proper ARIA labels and semantic HTML

This implementation provides a solid foundation for a professional financial design system that emphasizes data legibility and accessibility.