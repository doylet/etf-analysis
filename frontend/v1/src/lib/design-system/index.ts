// Design System - Main Export File
// Central export for all design system utilities, tokens, and configurations

// Core Design Tokens
export * from './design-tokens';

// Design System Configuration & Themes
export * from './design-system';

// Design Utilities & Helper Functions
export * from './design-utils';

// Re-export commonly used utilities for convenience
export { 
  createVariantStyles,
  responsive,
  focus,
  layout,
  animations
} from './design-utils';

export {
  theme,
  componentThemes,
  type ThemeConfig,
  type ComponentThemes
} from './design-system';