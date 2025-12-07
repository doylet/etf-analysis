/**
 * Typography Token Definitions
 * Professional Data-Focused Design System for ETF Analysis
 * 
 * Optimized for financial data legibility with tabular numerals and proper spacing
 */

import type { TypographyTokens } from './index';

// =============================================================================
// TYPOGRAPHY SYSTEM
// =============================================================================

export const typography: TypographyTokens = {
  // Font families - prioritizing system fonts with OpenType features
  family: {
    primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    financial: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
    monospace: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  },
  
  // Financial data size scale - optimized for numerical readability
  financial: {
    xs: '0.75rem',      // 12px - Small numbers, table data
    sm: '0.875rem',     // 14px - Regular metric values
    base: '1rem',       // 16px - Primary financial data
    lg: '1.125rem',     // 18px - Important totals
    xl: '1.25rem',      // 20px - Hero numbers
    '2xl': '1.5rem',    // 24px - Major portfolio values
  },
  
  // Interface text scale - standard hierarchy for UI elements
  text: {
    xs: '0.75rem',      // 12px - Captions, labels
    sm: '0.875rem',     // 14px - Body text
    base: '1rem',       // 16px - Default text
    lg: '1.125rem',     // 18px - Section headings
    xl: '1.25rem',      // 20px - Page titles
    '2xl': '1.5rem',    // 24px - Hero headings
  },
  
  // Font weights - professional hierarchy
  weight: {
    normal: 400,        // Regular text
    medium: 500,        // Emphasized text
    semibold: 600,      // Headings
    bold: 700,          // Important numbers
  },
  
  // Line heights optimized for data scanning
  lineHeight: {
    tight: '1.2',       // Large numbers - minimal line spacing
    normal: '1.4',      // Regular text - comfortable reading
    relaxed: '1.6',     // Body paragraphs - easy reading
  },
  
  // Letter spacing for enhanced data readability
  letterSpacing: {
    tight: '-0.025em',  // Large headings - tighter spacing
    normal: '0',        // Regular text - default spacing
    wide: '0.025em',    // Financial numbers - enhanced separation
  },
};

// =============================================================================
// TYPOGRAPHY UTILITIES
// =============================================================================

/**
 * Generate CSS classes for financial typography
 */
export function generateFinancialTypographyClasses(): Record<string, object> {
  const classes: Record<string, object> = {};
  
  // Financial text size classes with optimized properties
  Object.entries(typography.financial).forEach(([size, fontSize]) => {
    classes[`.text-financial-${size}`] = {
      fontSize,
      fontFamily: typography.family.primary,
      fontWeight: typography.weight.medium,
      lineHeight: typography.lineHeight.tight,
      letterSpacing: typography.letterSpacing.wide,
      fontFeatureSettings: '"tnum"',  // Enable tabular numerals
      fontVariantNumeric: 'tabular-nums',
    };
  });
  
  // Utility classes for common patterns
  classes['.font-tabular'] = {
    fontFeatureSettings: '"tnum"',
    fontVariantNumeric: 'tabular-nums',
  };
  
  classes['.font-financial'] = {
    fontFamily: typography.family.primary,
    fontFeatureSettings: '"tnum"',
    fontVariantNumeric: 'tabular-nums',
    letterSpacing: typography.letterSpacing.wide,
  };
  
  return classes;
}

/**
 * Get typography styles for a specific financial data type
 */
export function getFinancialTypography(
  size: keyof typeof typography.financial,
  weight?: keyof typeof typography.weight
): object {
  return {
    fontSize: typography.financial[size],
    fontFamily: typography.family.primary,
    fontWeight: typography.weight[weight || 'medium'],
    lineHeight: typography.lineHeight.tight,
    letterSpacing: typography.letterSpacing.wide,
    fontFeatureSettings: '"tnum"',
    fontVariantNumeric: 'tabular-nums',
  };
}

/**
 * Get typography styles for interface text
 */
export function getInterfaceTypography(
  size: keyof typeof typography.text,
  weight?: keyof typeof typography.weight
): object {
  return {
    fontSize: typography.text[size],
    fontFamily: typography.family.primary,
    fontWeight: typography.weight[weight || 'normal'],
    lineHeight: typography.lineHeight.normal,
    letterSpacing: typography.letterSpacing.normal,
  };
}

// =============================================================================
// RESPONSIVE TYPOGRAPHY SCALES
// =============================================================================

/**
 * Responsive financial data typography for different screen sizes
 */
export const responsiveFinancialTypography = {
  // Mobile-first responsive scale
  mobile: {
    xs: '0.625rem',     // 10px
    sm: '0.75rem',      // 12px
    base: '0.875rem',   // 14px
    lg: '1rem',         // 16px
    xl: '1.125rem',     // 18px
    '2xl': '1.25rem',   // 20px
  },
  
  // Tablet breakpoint adjustments
  tablet: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px
  },
  
  // Desktop and up (default scale)
  desktop: typography.financial,
};

// =============================================================================
// ACCESSIBILITY HELPERS
// =============================================================================

/**
 * Get minimum font size for accessibility compliance
 */
export function getMinimumFontSize(context: 'interface' | 'financial'): string {
  // WCAG guidelines suggest minimum 16px for body text
  // Financial data can be slightly smaller if well-contrasted
  return context === 'interface' ? '1rem' : '0.875rem';
}

/**
 * Validate typography for readability
 */
export function validateTypographyReadability(
  fontSize: string,
  lineHeight: string,
  context: 'interface' | 'financial' | 'heading'
): { isValid: boolean; suggestions: string[] } {
  const suggestions: string[] = [];
  let isValid = true;
  
  const size = parseFloat(fontSize);
  const height = parseFloat(lineHeight);
  
  // Check minimum sizes
  if (context === 'interface' && size < 16) {
    suggestions.push('Consider increasing font size to at least 16px for better readability');
    isValid = false;
  }
  
  if (context === 'financial' && size < 14) {
    suggestions.push('Financial data should be at least 14px for clear number recognition');
    isValid = false;
  }
  
  // Check line height ratios
  if (height < 1.2) {
    suggestions.push('Line height should be at least 1.2 for comfortable reading');
    isValid = false;
  }
  
  if (context === 'interface' && height < 1.4) {
    suggestions.push('Interface text benefits from line height of 1.4 or greater');
  }
  
  return { isValid, suggestions };
}

export type { TypographyTokens } from './index';