/**
 * Base UI TypeScript Interfaces
 * Standardized types for Base UI component integration in ETF Analysis Dashboard
 */

import type { ReactNode } from 'react';

// Base interface for all Base UI component wrappers
export interface BaseUIComponentProps {
  /** Custom CSS classes to apply to the component */
  className?: string;
  /** Accessibility label for screen readers */
  'aria-label'?: string;
  /** Test ID for automated testing */
  'data-testid'?: string;
  /** Whether the component is disabled */
  disabled?: boolean;
  /** Theme variant to apply */
//   variant?: 'default' | 'accent' | 'danger' | 'success';
}

// Popover component interface
export interface PopoverComponentInterface extends BaseUIComponentProps {
  /** Content to display in the popover */
  content: ReactNode;
  /** Title for the popover header */
  title?: string;
  /** Side offset from the trigger element */
  sideOffset?: number;
  /** Alignment relative to trigger */
  align?: 'start' | 'center' | 'end';
  /** Whether to show an arrow pointing to trigger */
  showArrow?: boolean;
  /** Callback when popover opens/closes */
  onOpenChange?: (open: boolean) => void;
}

// Style configuration interface
export interface ComponentStyleConfig {
  /** Base styles applied to all variants */
  base: string;
  /** Variant-specific style overrides */
  variants: {
    [variant: string]: string;
  };
  /** Size-specific styles */
  sizes?: {
    sm: string;
    md: string;
    lg: string;
  };
  /** State-specific styles (hover, focus, disabled) */
  states?: {
    hover?: string;
    focus?: string;
    disabled?: string;
  };
}

// Portal configuration interface
export interface PortalConfigInterface {
  /** Target container for portal rendering */
  container?: HTMLElement | null;
  /** Whether to use iOS Safari compatible positioning */
  iosCompatible?: boolean;
  /** Custom z-index for portal content */
  zIndex?: number;
  /** Portal mount/unmount callbacks */
  onMount?: (element: HTMLElement) => void;
  onUnmount?: () => void;
}

// Accessibility helper types
export interface AriaAttributes {
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-controls'?: string;
  role?: string;
}

export interface AccessibilityHelpers {
  /** Generate unique ID for ARIA relationships */
  generateId(prefix: string): string;
  
  /** Create ARIA attributes for popup components */
  createPopupAria(triggerId: string, popupId: string): {
    trigger: AriaAttributes;
    popup: AriaAttributes;
  };
  
  /** Manage focus trap for modal components */
  manageFocusTrap(container: HTMLElement): {
    activate: () => void;
    deactivate: () => void;
  };
  
  /** Announce dynamic content changes to screen readers */
  announceToScreenReader(message: string, priority?: 'polite' | 'assertive'): void;
}

// Component registry interface
export interface ComponentRegistry {
  /** Register a new component configuration */
  register<T extends BaseUIComponentProps>(
    name: string, 
    component: React.ComponentType<T>,
    config: ComponentStyleConfig
  ): void;
  
  /** Get a registered component by name */
  get(name: string): {
    component: React.ComponentType<BaseUIComponentProps>;
    config: ComponentStyleConfig;
  } | undefined;
  
  /** List all registered component names */
  list(): string[];
}