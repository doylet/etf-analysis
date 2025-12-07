/**
 * Design Token System - TypeScript Interfaces
 * Professional Data-Focused Design System for ETF Analysis
 */

// =============================================================================
// CORE TOKEN INTERFACES
// =============================================================================

export interface ColorTokens {
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

export interface TypographyTokens {
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

export interface SpacingTokens {
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
      gap: string;          // 8px - Between metric elements
      padding: string;      // 16px - Metric container padding
    };
  };
}

export interface BorderRadiusTokens {
  xs: string;               // 2px - Small elements
  sm: string;               // 4px - Buttons, inputs
  base: string;             // 6px - Cards, containers
  lg: string;               // 8px - Large cards
  xl: string;               // 12px - Modal dialogs
  full: string;             // 50% - Pills, avatars
}

export interface ShadowTokens {
  xs: string;               // Subtle card shadow
  sm: string;               // Default card shadow
  base: string;             // Elevated card shadow
  lg: string;               // Modal shadow
  xl: string;               // Overlay shadow
  inner: string;            // Inset shadow for inputs
}

export interface AnimationTokens {
  duration: {
    fast: string;           // 150ms - Hover states
    normal: string;         // 200ms - Standard transitions
    slow: string;           // 300ms - Complex animations
  };
  
  easing: {
    linear: string;         // Linear timing
    easeOut: string;        // Ease out (most UI)
    easeIn: string;         // Ease in (exits)
    bounce: string;         // Subtle bounce
  };
}

// =============================================================================
// COMPONENT INTERFACES
// =============================================================================

export interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ComponentType<{ className?: string }>;
  change?: {
    value: number;
    type: 'percentage' | 'absolute';
  };
  trend?: 'positive' | 'negative' | 'neutral';
  size?: 'sm' | 'base' | 'lg';
  variant?: 'default' | 'highlighted' | 'subtle';
  loading?: boolean;
  className?: string;
}

export interface FinancialAmountProps {
  amount: number;
  currency?: string | null | undefined;
  precision?: number;
  suffix?: string;
  showTrend?: boolean;
  size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | 'md';
  variant?: 'default' | 'positive' | 'negative' | 'neutral';
  showSign?: boolean;
  showCurrency?: boolean;
  className?: string;
}

export interface StatusIndicatorProps {
  status: 'positive' | 'negative' | 'neutral' | 'warning' | 'info';
  size?: 'sm' | 'base' | 'lg';
  variant?: 'dot' | 'badge' | 'text';
  label?: string;
  className?: string;
}

export interface GridLayoutProps {
  columns?: 1 | 2 | 3 | 4 | 6 | 12 | 'auto' | 'auto-sm' | 'auto-lg' | null;
  gap?: keyof SpacingTokens['component'];
  responsive?: boolean;
  children: React.ReactNode;
  className?: string;
}

export interface PercentageChangeProps {
  value: number;
  precision?: number;
  size?: keyof TypographyTokens['financial'];
  showSign?: boolean;
  variant?: 'default' | 'bold' | 'subtle';
  className?: string;
}

// =============================================================================
// DESIGN SYSTEM CONFIGURATION
// =============================================================================

export interface DesignSystemConfig {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  borderRadius: BorderRadiusTokens;
  shadows: ShadowTokens;
  animations: AnimationTokens;
}

export interface ThemeConfig {
  light: DesignSystemConfig;
  dark: DesignSystemConfig;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

export type ColorKeys = keyof ColorTokens;
export type TypographyKeys = keyof TypographyTokens;
export type SpacingKeys = keyof SpacingTokens;

export type FinancialTrend = 'positive' | 'negative' | 'neutral';
export type ComponentSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl';
export type ComponentVariant = 'default' | 'primary' | 'secondary' | 'subtle';

// =============================================================================
// CONTEXT INTERFACES
// =============================================================================

export interface DesignSystemContextValue {
  theme: 'light' | 'dark';
  tokens: DesignSystemConfig;
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

// =============================================================================
// VALIDATION INTERFACES
// =============================================================================

export interface TokenValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface AccessibilityValidation {
  contrastRatio: number;
  meetsWCAG: boolean;
  level: 'AA' | 'AAA' | 'fail';
}

// =============================================================================
// TOKEN EXPORTS
// =============================================================================

// Re-export all token implementations
export { lightColors, darkColors } from './colors';
export { typography } from './typography';
export { spacing } from './spacing';

// Create complete design system configs
export const borderRadius: BorderRadiusTokens = {
  xs: '0.125rem',   // 2px
  sm: '0.25rem',    // 4px
  base: '0.375rem', // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  full: '50%',
};

export const shadows: ShadowTokens = {
  xs: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  sm: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  base: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  lg: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  xl: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
};

export const animations: AnimationTokens = {
  duration: {
    fast: '150ms',
    normal: '200ms',
    slow: '300ms',
  },
  easing: {
    linear: 'linear',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },
};