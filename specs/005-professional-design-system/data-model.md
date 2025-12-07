# Phase 1: Design Token Data Model

**Feature**: Professional Data-Focused Design System  
**Phase**: 1 (Design & Architecture)  
**Date**: December 6, 2025  
**Dependencies**: Phase 0 Research Complete

## Design Token Structure

### Core Token Categories

#### Colors

```typescript
interface ColorTokens {
  // Financial semantic colors
  financial: {
    positive: string;        // Forest green for gains
    negative: string;        // Professional red for losses
    neutral: string;         // Charcoal gray for unchanged
    warning: string;         // Amber for alerts
    info: string;           // Blue for informational states
  };
  
  // Professional background palette
  background: {
    primary: string;         // Main background (white/dark)
    secondary: string;       // Card backgrounds
    tertiary: string;        // Subtle backgrounds
    accent: string;          // Highlight backgrounds
  };
  
  // Text hierarchy
  text: {
    primary: string;         // Main headings and labels
    secondary: string;       // Descriptive text
    tertiary: string;        // Subtle text and captions
    inverse: string;         // Text on dark backgrounds
  };
  
  // Interactive states
  interactive: {
    primary: string;         // Primary buttons and links
    secondary: string;       // Secondary actions
    hover: string;          // Hover state color
    pressed: string;        // Active/pressed state
    disabled: string;       // Disabled state
  };
  
  // Border and divider colors
  border: {
    primary: string;         // Main borders
    secondary: string;       // Subtle dividers
    focus: string;          // Focus indicators
    error: string;          // Error state borders
  };
}
```

#### Typography

```typescript
interface TypographyTokens {
  // Font families
  family: {
    primary: string;         // Main interface font (Inter)
    financial: string;       // Tabular numbers font
    monospace: string;       // Code and fixed-width data
  };
  
  // Financial data size scale
  financial: {
    xs: string;             // Small numbers, table data
    sm: string;             // Regular metric values  
    base: string;           // Primary financial data
    lg: string;             // Important totals
    xl: string;             // Hero numbers
    '2xl': string;          // Major portfolio values
  };
  
  // Interface text scale
  text: {
    xs: string;             // Captions, labels
    sm: string;             // Body text
    base: string;           // Default text
    lg: string;             // Section headings
    xl: string;             // Page titles
    '2xl': string;          // Hero headings
  };
  
  // Font weights
  weight: {
    normal: number;         // 400 - Regular text
    medium: number;         // 500 - Emphasized text
    semibold: number;       // 600 - Headings
    bold: number;           // 700 - Important numbers
  };
  
  // Line heights optimized for data
  lineHeight: {
    tight: string;          // 1.2 - Large numbers
    normal: string;         // 1.4 - Regular text
    relaxed: string;        // 1.6 - Body paragraphs
  };
  
  // Letter spacing for data readability
  letterSpacing: {
    tight: string;          // -0.025em - Large headings
    normal: string;         // 0 - Regular text
    wide: string;           // 0.025em - Financial numbers
  };
}
```

#### Spacing

```typescript
interface SpacingTokens {
  // Component spacing
  component: {
    xs: string;             // 4px - Tight spacing
    sm: string;             // 8px - Small gaps
    base: string;           // 16px - Default spacing
    lg: string;             // 24px - Section spacing
    xl: string;             // 32px - Large gaps
    '2xl': string;          // 48px - Major sections
  };
  
  // Layout spacing
  layout: {
    xs: string;             // 8px - Micro layouts
    sm: string;             // 16px - Small containers
    base: string;           // 24px - Default containers
    lg: string;             // 48px - Large containers
    xl: string;             // 64px - Major layout gaps
    '2xl': string;          // 96px - Page sections
  };
  
  // Data-specific spacing
  data: {
    table: {
      cellPadding: string;  // 12px - Table cell padding
      rowHeight: string;    // 48px - Minimum row height
      headerHeight: string; // 56px - Header row height
    };
    card: {
      padding: string;      // 20px - Card internal spacing
      gap: string;          // 16px - Between card elements
    };
    metric: {
      gap: string;          // 8px - Between number and label
      groupGap: string;     // 24px - Between metric groups
    };
  };
}
```

#### Border & Shadow

```typescript
interface BorderTokens {
  // Border radius
  radius: {
    none: string;           // 0 - Sharp corners
    sm: string;             // 4px - Small radius
    base: string;           // 6px - Default radius
    lg: string;             // 8px - Large radius
    xl: string;             // 12px - Extra large
    full: string;           // 9999px - Pill shape
  };
  
  // Border widths
  width: {
    none: string;           // 0
    thin: string;           // 1px - Default borders
    medium: string;         // 2px - Emphasized borders
    thick: string;          // 4px - Focus indicators
  };
  
  // Shadow system
  shadow: {
    none: string;           // No shadow
    sm: string;             // Subtle card shadow
    base: string;           // Default card shadow
    lg: string;             // Elevated card shadow
    focus: string;          // Focus ring shadow
  };
}
```

## Component Data Models

### MetricCard Component

```typescript
interface MetricCardProps {
  // Content
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: string;
    label?: string;
  };
  
  // Styling
  variant?: 'default' | 'highlighted' | 'compact';
  size?: 'sm' | 'base' | 'lg';
  
  // Icon
  icon?: React.ComponentType<{ className?: string }>;
  iconColor?: 'primary' | 'positive' | 'negative' | 'neutral';
  
  // Accessibility
  'aria-label'?: string;
  'data-testid'?: string;
}
```

### DataTable Component

```typescript
interface DataTableProps<T> {
  // Data
  data: T[];
  columns: ColumnDef<T>[];
  
  // Features
  sortable?: boolean;
  defaultSort?: {
    column: string;
    direction: 'asc' | 'desc';
  };
  
  // Styling
  variant?: 'default' | 'compact' | 'spacious';
  striped?: boolean;
  bordered?: boolean;
  
  // Loading states
  loading?: boolean;
  loadingRows?: number;
  
  // Accessibility
  'aria-label'?: string;
  caption?: string;
}

interface ColumnDef<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  width?: string;
  formatter?: (value: any) => string;
  cellClassName?: string;
}
```

### Typography Components

```typescript
interface FinancialAmountProps {
  // Value
  value: number;
  currency?: string;
  locale?: string;
  
  // Formatting
  precision?: number;
  showSign?: boolean;
  abbreviated?: boolean;
  
  // Styling
  size?: keyof TypographyTokens['financial'];
  weight?: keyof TypographyTokens['weight'];
  color?: 'auto' | 'positive' | 'negative' | 'neutral';
  
  // Accessibility
  'aria-label'?: string;
}

interface PercentageChangeProps {
  // Value
  value: number;
  baseline?: number;
  
  // Display
  showSign?: boolean;
  showIcon?: boolean;
  precision?: number;
  
  // Styling
  size?: keyof TypographyTokens['financial'];
  variant?: 'inline' | 'badge' | 'minimal';
  
  // Accessibility
  'aria-label'?: string;
}
```

## Theme Structure

### Light Theme Values

```typescript
const lightTheme: DesignTokens = {
  colors: {
    financial: {
      positive: '#15803d',      // Forest green
      negative: '#dc2626',      // Professional red
      neutral: '#374151',       // Charcoal gray
      warning: '#d97706',       // Amber
      info: '#2563eb',         // Blue
    },
    background: {
      primary: '#ffffff',       // White
      secondary: '#f9fafb',     // Light gray
      tertiary: '#f3f4f6',     // Subtle gray
      accent: '#eff6ff',       // Light blue
    },
    text: {
      primary: '#111827',       // Near black
      secondary: '#374151',     // Dark gray
      tertiary: '#6b7280',     // Medium gray
      inverse: '#ffffff',      // White
    },
    interactive: {
      primary: '#2563eb',       // Blue
      secondary: '#6b7280',     // Gray
      hover: '#1d4ed8',        // Darker blue
      pressed: '#1e40af',      // Even darker blue
      disabled: '#d1d5db',     // Light gray
    },
    border: {
      primary: '#d1d5db',       // Light gray
      secondary: '#e5e7eb',     // Lighter gray
      focus: '#2563eb',        // Blue
      error: '#dc2626',        // Red
    },
  },
  // ... typography, spacing, etc.
};
```

### Dark Theme Values

```typescript
const darkTheme: DesignTokens = {
  colors: {
    financial: {
      positive: '#22c55e',      // Bright green
      negative: '#ef4444',      // Bright red
      neutral: '#d1d5db',       // Light gray
      warning: '#f59e0b',       // Bright amber
      info: '#3b82f6',         // Bright blue
    },
    background: {
      primary: '#111827',       // Dark gray
      secondary: '#1f2937',     // Lighter dark
      tertiary: '#374151',      // Medium dark
      accent: '#1e3a8a',       // Dark blue
    },
    text: {
      primary: '#f9fafb',       // Near white
      secondary: '#d1d5db',     // Light gray
      tertiary: '#9ca3af',     // Medium gray
      inverse: '#111827',      // Dark gray
    },
    // ... continued
  },
  // ... typography, spacing, etc.
};
```

## Validation Rules

### Design Token Constraints

1. **Color Accessibility**: All text/background combinations must meet WCAG AA 4.5:1 contrast ratio
2. **Typography Scale**: Each size must be at least 1.125x the previous size for clear hierarchy
3. **Spacing Consistency**: All spacing values must use 4px base unit (4, 8, 12, 16, 20, 24, etc.)
4. **Border Radius Logic**: Radius values should not exceed element height/width
5. **Shadow Consistency**: Shadows must follow consistent blur and offset patterns

### Component Validation

1. **MetricCard**: Value must be formatted consistently with locale-appropriate number formatting
2. **DataTable**: Column alignment must follow data type conventions (numbers right, text left)
3. **Typography**: Financial amounts must use tabular numerals for proper alignment
4. **Themes**: All token values must exist in both light and dark theme variants

## Migration Strategy

### Phase 1: Foundation
1. Implement design token system with CSS custom properties
2. Create TypeScript interfaces for type safety
3. Update globals.css with new theme variables

### Phase 2: Components
1. Enhance existing shadcn/ui components with new variants
2. Create new financial-specific components
3. Update existing components to use design tokens

### Phase 3: Integration
1. Replace hardcoded values with design tokens throughout application
2. Implement theme switching functionality
3. Add comprehensive component documentation

This data model provides the foundation for a systematic, maintainable design system that prioritizes financial data legibility while maintaining professional appearance standards.