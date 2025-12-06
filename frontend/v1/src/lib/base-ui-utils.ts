/**
 * Base UI Utility Functions
 * Helper functions for Base UI component integration in ETF Analysis Dashboard
 */

import type { 
  AccessibilityHelpers, 
  ComponentStyleConfig, 
  PortalConfigInterface,
  AriaAttributes, 
  BaseUIComponentProps
} from './base-ui-types';

// Generate unique IDs for accessibility
let idCounter = 0;
export const generateId = (prefix: string): string => {
  return `${prefix}-${++idCounter}`;
};

// Create ARIA attributes for popup components
export const createPopupAria = (triggerId: string, popupId: string) => {
  return {
    trigger: {
      'aria-expanded': false,
      'aria-controls': popupId,
      'aria-describedby': popupId,
    } as AriaAttributes,
    popup: {
      'aria-labelledby': triggerId,
      role: 'dialog',
    } as AriaAttributes,
  };
};

// Focus trap management for modal components
export const manageFocusTrap = (container: HTMLElement) => {
  const focusableElements = container.querySelectorAll(
    'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
  );
  const firstElement = focusableElements[0] as HTMLElement;
  const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

  let isActive = false;

  const handleTabKeyPress = (e: KeyboardEvent) => {
    if (!isActive) return;
    
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    }

    if (e.key === 'Escape') {
      deactivate();
    }
  };

  const activate = () => {
    isActive = true;
    firstElement?.focus();
    document.addEventListener('keydown', handleTabKeyPress);
  };

  const deactivate = () => {
    isActive = false;
    document.removeEventListener('keydown', handleTabKeyPress);
  };

  return { activate, deactivate };
};

// Announce content changes to screen readers
export const announceToScreenReader = (
  message: string, 
  priority: 'polite' | 'assertive' = 'polite'
) => {
  const announcer = document.createElement('div');
  announcer.setAttribute('aria-live', priority);
  announcer.setAttribute('aria-atomic', 'true');
  announcer.setAttribute('class', 'sr-only');
  announcer.style.position = 'absolute';
  announcer.style.left = '-9999px';
  announcer.style.width = '1px';
  announcer.style.height = '1px';
  announcer.style.overflow = 'hidden';
  
  document.body.appendChild(announcer);
  announcer.textContent = message;
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcer);
  }, 1000);
};

// Style utilities for consistent component styling
export const mergeClasses = (...classes: (string | undefined)[]): string => {
  return classes.filter(Boolean).join(' ');
};

export const applyVariant = (
  config: ComponentStyleConfig,
  variant: string = 'default',
  size?: string
): string => {
  const baseClasses = config.base;
  const variantClasses = config.variants[variant] || config.variants.default || '';
  const sizeClasses = size && config.sizes ? (config.sizes as Record<string, string>)[size] || '' : '';
  
  return mergeClasses(baseClasses, variantClasses, sizeClasses);
};

// Portal configuration helpers
export const getPortalContainer = (config?: PortalConfigInterface): HTMLElement => {
  if (config?.container) return config.container;
  
  // Create or get default portal container
  let portalRoot = document.getElementById('base-ui-portal-root');
  if (!portalRoot) {
    portalRoot = document.createElement('div');
    portalRoot.id = 'base-ui-portal-root';
    portalRoot.style.position = 'relative';
    portalRoot.style.zIndex = '9999';
    document.body.appendChild(portalRoot);
  }
  
  return portalRoot;
};

// Component registry implementation
class BaseUIComponentRegistry {
  private registry = new Map<string, { component: React.ComponentType<BaseUIComponentProps>; config: ComponentStyleConfig }>();

  register<T extends BaseUIComponentProps>(
    name: string, 
    component: React.ComponentType<T>,
    config: ComponentStyleConfig
  ): void {
    this.registry.set(name, { component: component as React.ComponentType<BaseUIComponentProps>, config });
  }

  get(name: string) {
    return this.registry.get(name);
  }

  list(): string[] {
    return Array.from(this.registry.keys());
  }
}

// Export singleton registry instance
export const componentRegistry = new BaseUIComponentRegistry();

// Pre-defined style configurations
export const defaultPopoverStyles: ComponentStyleConfig = {
  base: "rounded-lg shadow-lg transition-opacity",
  variants: {
    default: "bg-white text-gray-900 border border-gray-200",
    accent: "bg-blue-50 text-blue-900 border border-blue-200",
    danger: "bg-red-50 text-red-900 border border-red-200",
    success: "bg-green-50 text-green-900 border border-green-200"
  },
  sizes: {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-3 text-base", 
    lg: "px-6 py-4 text-lg"
  },
  states: {
    hover: "hover:shadow-xl",
    focus: "focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-600",
    disabled: "opacity-50 cursor-not-allowed"
  }
};

// Accessibility helpers object
export const accessibilityHelpers: AccessibilityHelpers = {
  generateId,
  createPopupAria,
  manageFocusTrap,
  announceToScreenReader
};