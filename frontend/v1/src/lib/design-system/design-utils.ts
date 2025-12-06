/**
 * Design System Utilities
 * Helper functions to generate styles from design tokens
 */

import { theme, componentThemes, type ThemeConfig } from './design-system';
import { cn } from '../utils';

// Component variant style interfaces
interface BaseVariantStyle {
  readonly backgroundColor?: string;
  readonly color?: string;
  readonly borderColor?: string;
  readonly borderWidth?: string;
  readonly shadow?: string;
}

interface StatefulVariantStyle extends BaseVariantStyle {
  readonly hover?: BaseVariantStyle;
  readonly active?: BaseVariantStyle;
  readonly disabled?: BaseVariantStyle;
}

type ComponentVariants = Record<string, StatefulVariantStyle>;

// Type helpers
type DeepKeyOf<T> = T extends object 
  ? { [K in keyof T]: K extends string ? `${K}` | `${K}.${DeepKeyOf<T[K]>}` : never }[keyof T]
  : never;

type ColorPath = DeepKeyOf<ThemeConfig['colors']>;
type SpacingPath = keyof ThemeConfig['spacing'];
type TypographyPath = DeepKeyOf<ThemeConfig['typography']>;

// Utility to get nested object values by path
function getNestedValue<T>(obj: T, path: string): unknown {
  return path.split('.').reduce((acc: unknown, key) => (acc as Record<string, unknown>)?.[key], obj);
}

// Color utilities
export const getColor = (path: ColorPath): string => {
  const color = getNestedValue(theme.colors, path);
  if (!color || typeof color !== 'string') {
    console.warn(`Color not found for path: ${path}`);
    return theme.colors.text.primary; // fallback
  }
  return color as string;
};

// Spacing utilities
export const getSpacing = (size: SpacingPath): string => {
  const spacing = theme.spacing[size];
  if (typeof spacing === 'string') {
    return spacing;
  }
  // If it's an object, return a fallback string
  console.warn(`Spacing for ${String(size)} is not a string value`);
  return '1rem'; // fallback
};

// Typography utilities
export const getTypography = (path: TypographyPath): unknown => {
  return getNestedValue(theme.typography, path);
};

// Generate CSS variables from theme
export const generateCSSVariables = (themeConfig: ThemeConfig) => {
  const vars: Record<string, string> = {};
  
  // Convert nested objects to CSS custom properties
  const flattenObject = (obj: any, prefix: string = '') => {
    Object.keys(obj).forEach(key => {
      const value = obj[key];
      const cssVar = prefix ? `${prefix}-${key}` : key;
      
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        flattenObject(value, cssVar);
      } else {
        vars[`--${cssVar}`] = Array.isArray(value) ? value[0] : value;
      }
    });
  };
  
  flattenObject(themeConfig.colors, 'color');
  flattenObject(themeConfig.spacing, 'spacing');
  flattenObject(themeConfig.radius, 'radius');
  flattenObject(themeConfig.shadows, 'shadow');
  
  return vars;
};

// Component style builders
export const buildButtonStyles = (
  variant: keyof typeof componentThemes.button.variants = 'primary',
  size: keyof typeof componentThemes.button.sizes = 'md'
) => {
  const variantStyles = componentThemes.button.variants[variant];
  const sizeStyles = componentThemes.button.sizes[size];
  
  return {
    base: cn(
      // Base styles
      'inline-flex items-center justify-center font-medium transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
      'disabled:pointer-events-none disabled:opacity-50',
      `rounded-[${theme.radius.button}]`
    ),
    variant: {
      backgroundColor: variantStyles.backgroundColor,
      color: variantStyles.color,
      borderColor: variantStyles.borderColor,
      borderWidth: variantStyles.borderColor !== 'transparent' ? '1px' : '0',
      height: sizeStyles.height,
      padding: sizeStyles.padding,
      fontSize: sizeStyles.fontSize
    },
    hover: 'hover' in variantStyles ? variantStyles.hover : undefined,
    active: 'active' in variantStyles ? variantStyles.active : undefined,
    disabled: 'disabled' in variantStyles ? variantStyles.disabled : undefined
  };
};

export const buildCardStyles = (
  variant: keyof typeof componentThemes.card.variants = 'default'
) => {
  const variantStyles = componentThemes.card.variants[variant] as StatefulVariantStyle;
  
  return {
    base: cn(
      'transition-shadow',
      `rounded-[${theme.radius.card}]`
    ),
    variant: {
      backgroundColor: variantStyles.backgroundColor,
      borderColor: variantStyles.borderColor,
      borderWidth: variantStyles.borderWidth || '1px',
      boxShadow: variantStyles.shadow
    },
    hover: 'hover' in variantStyles ? variantStyles.hover : undefined
  };
};

export const buildAlertStyles = (
  variant: keyof typeof componentThemes.alert.variants = 'info'
) => {
  const variantStyles = componentThemes.alert.variants[variant];
  
  return {
    base: cn(
      'border p-4 transition-all',
      `rounded-[${theme.radius.card}]`
    ),
    variant: {
      backgroundColor: variantStyles.backgroundColor,
      borderColor: variantStyles.borderColor,
      color: variantStyles.color
    },
    icon: {
      color: variantStyles.iconColor
    }
  };
};

// Style composition utilities
export const createVariantStyles = <T extends Record<string, unknown>>(
  config: T,
  variant: keyof T,
  size?: string
) => {
  const baseStyles = (config as Record<string, unknown>).base as string || '';
  const variants = (config as Record<string, unknown>).variants as Record<string, string>;
  const sizes = (config as Record<string, unknown>).sizes as Record<string, string>;
  
  const variantStyles = variants?.[variant as string] || '';
  const sizeStyles = size && sizes ? sizes[size] || '' : '';
  
  return cn(baseStyles, variantStyles, sizeStyles);
};

// Responsive utilities
export const responsive = {
  sm: (styles: string) => `sm:${styles}`,
  md: (styles: string) => `md:${styles}`,
  lg: (styles: string) => `lg:${styles}`,
  xl: (styles: string) => `xl:${styles}`,
  '2xl': (styles: string) => `2xl:${styles}`
};

// Dark mode utilities (for future use)
export const darkMode = (styles: string) => `dark:${styles}`;

// Animation utilities
export const animations = {
  fadeIn: 'animate-in fade-in-0',
  fadeOut: 'animate-out fade-out-0',
  slideInFromBottom: 'animate-in slide-in-from-bottom-2',
  slideInFromTop: 'animate-in slide-in-from-top-2',
  slideInFromLeft: 'animate-in slide-in-from-left-2',
  slideInFromRight: 'animate-in slide-in-from-right-2',
  scaleIn: 'animate-in zoom-in-95',
  scaleOut: 'animate-out zoom-out-95'
};

// Layout utilities
export const layout = {
  container: cn(
    'mx-auto max-w-7xl',
    `px-[${theme.spacing.layout.container}]`,
    responsive.sm(`px-[${theme.spacing.layout.sidebar}]`),
    responsive.lg(`px-[${theme.spacing[8]}]`)
  ),
  section: cn(
    `py-[${theme.spacing.layout.section}]`
  ),
  grid: {
    auto: 'grid grid-cols-1',
    cols2: 'grid grid-cols-1 md:grid-cols-2',
    cols3: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    cols4: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  }
};

// Focus management
export const focus = {
  ring: cn(
    'focus-visible:outline-none focus-visible:ring-2',
    `focus-visible:ring-[${theme.colors.border.focus}]`,
    'focus-visible:ring-offset-2'
  ),
  within: 'focus-within:ring-2 focus-within:ring-offset-2',
  visible: 'focus-visible:outline-none'
};

export { theme, componentThemes };