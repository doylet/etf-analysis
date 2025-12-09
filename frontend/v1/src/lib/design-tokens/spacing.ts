/**
 * Spacing Token Definitions
 * Professional Data-Focused Design System for ETF Analysis
 * 
 * Consistent spacing system optimized for financial data layouts
 */

import type { SpacingTokens } from './index';

// =============================================================================
// SPACING SYSTEM
// =============================================================================

export const spacing: SpacingTokens = {
  // Component spacing - for elements within components
  component: {
    xs: '0.25rem',      // 4px - Tight spacing between related elements
    sm: '0.5rem',       // 8px - Small gaps within cards or forms
    base: '1rem',       // 16px - Default spacing between elements
    lg: '1.5rem',       // 24px - Section spacing within components
    xl: '2rem',         // 32px - Large gaps for visual separation
    '2xl': '3rem',      // 48px - Major section breaks
  },
  
  // Layout spacing - for page and section organization
  layout: {
    xs: '0.5rem',       // 8px - Micro layouts, button groups
    sm: '1rem',         // 16px - Small containers, sidebars
    base: '1.5rem',     // 24px - Default container spacing
    lg: '3rem',         // 48px - Large containers, page sections
    xl: '4rem',         // 64px - Major layout separations
    '2xl': '6rem',      // 96px - Page-level spacing
  },
  
  // Data-specific spacing - optimized for financial interfaces
  data: {
    table: {
      cellPadding: '0.75rem',     // 12px - Table cell internal padding
      rowHeight: '3rem',          // 48px - Minimum row height for touch
      headerHeight: '3.5rem',     // 56px - Header row for emphasis
    },
    card: {
      padding: '1.25rem',         // 20px - Card internal spacing
      gap: '1rem',                // 16px - Between card elements
    },
    metric: {
      gap: '0.5rem',              // 8px - Between metric number and label
      padding: '1rem',            // 16px - Metric container padding
    },
  },
};

// =============================================================================
// SPACING UTILITIES
// =============================================================================

/**
 * Generate responsive spacing values
 */
export const responsiveSpacing = {
  // Mobile-first responsive spacing
  mobile: {
    component: {
      xs: '0.25rem',
      sm: '0.5rem',
      base: '0.75rem',    // Reduced for mobile
      lg: '1rem',
      xl: '1.5rem',
      '2xl': '2rem',
    },
    layout: {
      xs: '0.5rem',
      sm: '0.75rem',
      base: '1rem',       // Reduced for mobile
      lg: '2rem',
      xl: '3rem',
      '2xl': '4rem',
    },
  },
  
  // Tablet breakpoint
  tablet: {
    component: {
      xs: '0.25rem',
      sm: '0.5rem',
      base: '0.875rem',   // Slightly reduced
      lg: '1.25rem',
      xl: '1.75rem',
      '2xl': '2.5rem',
    },
    layout: {
      xs: '0.5rem',
      sm: '0.875rem',
      base: '1.25rem',    // Slightly reduced
      lg: '2.5rem',
      xl: '3.5rem',
      '2xl': '5rem',
    },
  },
  
  // Desktop (default scale)
  desktop: spacing,
};

/**
 * Get spacing value by key path
 */
export function getSpacing(path: string): string {
  const keys = path.split('.');
  let value: unknown = spacing;
  
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = (value as Record<string, unknown>)[key];
    } else {
      return spacing.component.base; // Fallback
    }
  }
  
  return typeof value === 'string' ? value : spacing.component.base;
}

/**
 * Generate CSS custom properties for spacing
 */
export function generateSpacingVariables(prefix = ''): Record<string, string> {
  const vars: Record<string, string> = {};
  
  // Component spacing variables
  Object.entries(spacing.component).forEach(([key, value]) => {
    vars[`--${prefix}spacing-component-${key}`] = value;
  });
  
  // Layout spacing variables
  Object.entries(spacing.layout).forEach(([key, value]) => {
    vars[`--${prefix}spacing-layout-${key}`] = value;
  });
  
  // Data spacing variables
  vars[`--${prefix}spacing-table-cell-padding`] = spacing.data.table.cellPadding;
  vars[`--${prefix}spacing-table-row-height`] = spacing.data.table.rowHeight;
  vars[`--${prefix}spacing-table-header-height`] = spacing.data.table.headerHeight;
  vars[`--${prefix}spacing-card-padding`] = spacing.data.card.padding;
  vars[`--${prefix}spacing-card-gap`] = spacing.data.card.gap;
  vars[`--${prefix}spacing-metric-gap`] = spacing.data.metric.gap;
  vars[`--${prefix}spacing-metric-padding`] = spacing.data.metric.padding;
  
  return vars;
}

// =============================================================================
// LAYOUT HELPERS
// =============================================================================

/**
 * Get appropriate spacing for different layout contexts
 */
export function getLayoutSpacing(
  context: 'container' | 'section' | 'component' | 'element',
  size: 'sm' | 'base' | 'lg' = 'base'
): string {
  switch (context) {
    case 'container':
      return spacing.layout[size];
    case 'section':
      return spacing.layout[size === 'sm' ? 'base' : size === 'base' ? 'lg' : 'xl'];
    case 'component':
      return spacing.component[size];
    case 'element':
      return spacing.component[size === 'lg' ? 'base' : size === 'base' ? 'sm' : 'xs'];
    default:
      return spacing.component.base;
  }
}

/**
 * Get financial data specific spacing
 */
export function getDataSpacing(
  type: 'table' | 'card' | 'metric',
  property?: 'padding' | 'gap' | 'height'
): string {
  if (type === 'table') {
    switch (property) {
      case 'padding': return spacing.data.table.cellPadding;
      case 'height': return spacing.data.table.rowHeight;
      default: return spacing.data.table.cellPadding;
    }
  }
  
  if (type === 'card') {
    switch (property) {
      case 'padding': return spacing.data.card.padding;
      case 'gap': return spacing.data.card.gap;
      default: return spacing.data.card.padding;
    }
  }
  
  if (type === 'metric') {
    switch (property) {
      case 'padding': return spacing.data.metric.padding;
      case 'gap': return spacing.data.metric.gap;
      default: return spacing.data.metric.gap;
    }
  }
  
  return spacing.component.base;
}

// =============================================================================
// GRID AND FLEXBOX UTILITIES
// =============================================================================

/**
 * Common spacing patterns for CSS Grid layouts
 */
export const gridSpacing = {
  // Financial dashboard grids
  dashboard: {
    gap: spacing.layout.base,
    padding: spacing.layout.sm,
    columnGap: spacing.component.lg,
    rowGap: spacing.component.base,
  },
  
  // Data table grids
  table: {
    gap: '0',  // Tables handle their own spacing
    cellPadding: spacing.data.table.cellPadding,
    rowGap: '1px',  // For border spacing
  },
  
  // Card grids
  cardGrid: {
    gap: spacing.component.lg,
    padding: spacing.layout.sm,
    minCardWidth: '280px',  // Minimum for metric cards
  },
  
  // Metric grids
  metrics: {
    gap: spacing.component.base,
    padding: spacing.data.metric.padding,
    itemGap: spacing.data.metric.gap,
  },
};

/**
 * Common spacing patterns for Flexbox layouts
 */
export const flexSpacing = {
  // Horizontal layouts
  horizontal: {
    gap: spacing.component.base,
    itemSpacing: spacing.component.sm,
  },
  
  // Vertical layouts
  vertical: {
    gap: spacing.component.lg,
    itemSpacing: spacing.component.base,
  },
  
  // Form layouts
  form: {
    gap: spacing.component.lg,
    fieldGap: spacing.component.sm,
    labelGap: spacing.component.xs,
  },
  
  // Button groups
  buttonGroup: {
    gap: spacing.component.sm,
    padding: spacing.component.xs,
  },
};

export type { SpacingTokens } from './index';