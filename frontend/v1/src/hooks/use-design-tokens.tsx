'use client';

import { createContext, useContext, ReactNode } from 'react';
import { colors } from '@/lib/design-tokens/colors';
import { typography } from '@/lib/design-tokens/typography';
import { spacing } from '@/lib/design-tokens/spacing';
import type { ColorTokens, TypographyTokens, SpacingTokens } from '@/lib/design-tokens';

/**
 * Design tokens context interface
 * Provides access to all design system tokens in a type-safe manner
 */
interface DesignTokensContext {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  theme: 'light' | 'dark';
}

/**
 * Design tokens context
 * Centralizes access to design system tokens across the application
 */
const DesignTokensContext = createContext<DesignTokensContext | undefined>(undefined);

/**
 * Props for the DesignTokensProvider component
 */
interface DesignTokensProviderProps {
  children: ReactNode;
  theme?: 'light' | 'dark';
}

/**
 * Design tokens provider component
 * 
 * Provides design system tokens to all child components.
 * This enables consistent access to colors, typography, and spacing
 * throughout the application while maintaining type safety.
 * 
 * @param children - React children components
 * @param theme - Current theme ('light' | 'dark')
 */
export function DesignTokensProvider({ 
  children, 
  theme = 'light' 
}: DesignTokensProviderProps) {
  const contextValue: DesignTokensContext = {
    colors: colors,
    typography: typography,
    spacing: spacing,
    theme
  };

  return (
    <DesignTokensContext.Provider value={contextValue}>
      {children}
    </DesignTokensContext.Provider>
  );
}

/**
 * Hook to access design tokens
 * 
 * Provides type-safe access to the design system tokens.
 * Must be used within a DesignTokensProvider.
 * 
 * @returns Design tokens context with colors, typography, spacing, and theme
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { colors, typography, spacing } = useDesignTokens();
 *   
 *   return (
 *     <div 
 *       style={{
 *         color: colors.semantic.success,
 *         fontSize: typography.scale.body.md.fontSize,
 *         padding: spacing.component.padding.md
 *       }}
 *     >
 *       Financial data with proper styling
 *     </div>
 *   );
 * }
 * ```
 */
export function useDesignTokens(): DesignTokensContext {
  const context = useContext(DesignTokensContext);
  
  if (context === undefined) {
    throw new Error(
      'useDesignTokens must be used within a DesignTokensProvider. ' +
      'Please wrap your component tree with <DesignTokensProvider>.'
    );
  }
  
  return context;
}

/**
 * Hook to access color tokens specifically
 * 
 * Convenience hook for components that primarily need color values.
 * 
 * @returns Color tokens object
 */
export function useColorTokens(): ColorTokens {
  const { colors } = useDesignTokens();
  return colors;
}

/**
 * Hook to access typography tokens specifically
 * 
 * Convenience hook for components that primarily need typography values.
 * 
 * @returns Typography tokens object
 */
export function useTypographyTokens(): TypographyTokens {
  const { typography } = useDesignTokens();
  return typography;
}

/**
 * Hook to access spacing tokens specifically
 * 
 * Convenience hook for components that primarily need spacing values.
 * 
 * @returns Spacing tokens object
 */
export function useSpacingTokens(): SpacingTokens {
  const { spacing } = useDesignTokens();
  return spacing;
}

/**
 * Hook to access current theme
 * 
 * Provides access to the current theme state for conditional styling.
 * 
 * @returns Current theme ('light' | 'dark')
 */
export function useTheme(): 'light' | 'dark' {
  const { theme } = useDesignTokens();
  return theme;
}