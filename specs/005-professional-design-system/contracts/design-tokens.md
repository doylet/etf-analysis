# Design Token API Contract

**Version**: 1.0.0  
**Purpose**: Define TypeScript interfaces for design token system  
**Dependencies**: CSS custom properties, Tailwind CSS configuration

## Core Token Interfaces

### DesignTokens

```typescript
export interface DesignTokens {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  border: BorderTokens;
}

export interface ColorTokens {
  financial: {
    positive: string;
    negative: string;
    neutral: string;
    warning: string;
    info: string;
  };
  background: {
    primary: string;
    secondary: string;
    tertiary: string;
    accent: string;
  };
  text: {
    primary: string;
    secondary: string;
    tertiary: string;
    inverse: string;
  };
  interactive: {
    primary: string;
    secondary: string;
    hover: string;
    pressed: string;
    disabled: string;
  };
  border: {
    primary: string;
    secondary: string;
    focus: string;
    error: string;
  };
}

export interface TypographyTokens {
  family: {
    primary: string;
    financial: string;
    monospace: string;
  };
  financial: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
  };
  text: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
  };
  weight: {
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
  lineHeight: {
    tight: string;
    normal: string;
    relaxed: string;
  };
  letterSpacing: {
    tight: string;
    normal: string;
    wide: string;
  };
}

export interface SpacingTokens {
  component: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
  };
  layout: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
  };
  data: {
    table: {
      cellPadding: string;
      rowHeight: string;
      headerHeight: string;
    };
    card: {
      padding: string;
      gap: string;
    };
    metric: {
      gap: string;
      groupGap: string;
    };
  };
}

export interface BorderTokens {
  radius: {
    none: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    full: string;
  };
  width: {
    none: string;
    thin: string;
    medium: string;
    thick: string;
  };
  shadow: {
    none: string;
    sm: string;
    base: string;
    lg: string;
    focus: string;
  };
}
```

## Theme System

### Theme Provider

```typescript
export interface ThemeContextValue {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  resolvedTheme: 'light' | 'dark';
  tokens: DesignTokens;
}

export interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: 'light' | 'dark' | 'system';
  storageKey?: string;
  enableSystem?: boolean;
}
```

## Token Usage Utilities

### CSS Variable Generator

```typescript
export interface CSSVariableConfig {
  prefix?: string;
  scope?: 'global' | 'component';
  transform?: (value: string) => string;
}

export interface CSSVariableOutput {
  variables: Record<string, string>;
  classes: Record<string, string>;
}

export declare function generateCSSVariables(
  tokens: DesignTokens, 
  config?: CSSVariableConfig
): CSSVariableOutput;
```

### Token Access Utilities

```typescript
export declare function useDesignTokens(): DesignTokens;
export declare function getToken(path: string): string | undefined;
export declare function resolveTokenPath(tokens: DesignTokens, path: string): string;

// Examples:
// getToken('colors.financial.positive') → '#15803d'
// getToken('spacing.component.base') → '16px'
```

## Error Handling

### Token Validation

```typescript
export interface TokenValidationError {
  path: string;
  value: string;
  rule: string;
  message: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: TokenValidationError[];
  warnings: TokenValidationError[];
}

export declare function validateTokens(tokens: DesignTokens): ValidationResult;
export declare function validateContrastRatio(foreground: string, background: string): boolean;
```

## Implementation Requirements

### CSS Custom Properties

Design tokens MUST be implemented as CSS custom properties in the format:
```css
:root {
  --dt-color-financial-positive: #15803d;
  --dt-typography-financial-base: 1rem;
  --dt-spacing-component-base: 16px;
}
```

### TypeScript Runtime Access

Tokens MUST be accessible at runtime through React context:
```typescript
const tokens = useDesignTokens();
const positiveColor = tokens.colors.financial.positive;
```

### Tailwind CSS Integration

Tokens MUST extend Tailwind CSS configuration:
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'financial-positive': 'var(--dt-color-financial-positive)',
        'financial-negative': 'var(--dt-color-financial-negative)',
      }
    }
  }
}
```

## Performance Requirements

1. **Token Resolution**: Token access MUST complete in <1ms
2. **Theme Switching**: Theme changes MUST apply in <100ms
3. **Bundle Size**: Token system MUST add <5KB to bundle size
4. **CSS Generation**: CSS variables MUST generate in <10ms

## Accessibility Requirements

1. **Contrast Validation**: All color combinations MUST be validated against WCAG AA standards
2. **Focus Indicators**: Focus styles MUST be clearly visible with 2px minimum thickness
3. **Text Scaling**: Typography MUST support 200% zoom without horizontal scrolling
4. **Color Independence**: Information MUST not rely solely on color

## Breaking Change Policy

### Major Version (X.0.0)
- Removal of token categories
- Renaming of core token properties
- Changes to TypeScript interfaces that break compilation

### Minor Version (X.Y.0)
- Addition of new token categories
- Addition of optional properties to existing interfaces
- New utility functions

### Patch Version (X.Y.Z)
- Token value updates
- Bug fixes in utilities
- Documentation improvements

## Migration Guide

### From Hardcoded Values
```typescript
// Before
const styles = {
  color: '#15803d',
  fontSize: '16px',
  padding: '16px'
};

// After
const tokens = useDesignTokens();
const styles = {
  color: tokens.colors.financial.positive,
  fontSize: tokens.typography.financial.base,
  padding: tokens.spacing.component.base
};
```

### From Tailwind Classes
```typescript
// Before
<div className="text-green-600 text-base p-4">

// After  
<div className="text-financial-positive text-financial-base p-component-base">
```