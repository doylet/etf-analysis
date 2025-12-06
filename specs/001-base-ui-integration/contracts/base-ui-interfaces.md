# Base UI Component Interfaces

**Feature**: 001-base-ui-integration  
**Created**: December 5, 2025

## Component Wrapper Interface

### BaseUIComponentProps
Standardized interface for all Base UI component wrappers in the ETF analysis dashboard:

```typescript
interface BaseUIComponentProps {
  /** Custom CSS classes to apply to the component */
  className?: string;
  /** Accessibility label for screen readers */
  'aria-label'?: string;
  /** Test ID for automated testing */
  'data-testid'?: string;
  /** Whether the component is disabled */
  disabled?: boolean;
  /** Theme variant to apply */
  variant?: 'default' | 'accent' | 'danger' | 'success';
}
```

### PopoverComponentInterface
Interface for Popover component implementation:

```typescript
interface PopoverComponentInterface extends BaseUIComponentProps {
  /** Content to display in the popover */
  content: React.ReactNode;
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
```

## Style Customization API

### ComponentStyleConfig
Interface for configuring component styles within the design system:

```typescript
interface ComponentStyleConfig {
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
```

## Accessibility Helper Functions

### AccessibilityHelpers
Utility functions for consistent accessibility implementation:

```typescript
interface AccessibilityHelpers {
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
```

## Portal Configuration API

### PortalConfigInterface
Interface for configuring portal behavior:

```typescript
interface PortalConfigInterface {
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
```

## Component Registration

### ComponentRegistry
Interface for registering and retrieving Base UI component configurations:

```typescript
interface ComponentRegistry {
  /** Register a new component configuration */
  register<T extends BaseUIComponentProps>(
    name: string, 
    component: React.ComponentType<T>,
    config: ComponentStyleConfig
  ): void;
  
  /** Get a registered component by name */
  get(name: string): {
    component: React.ComponentType<any>;
    config: ComponentStyleConfig;
  } | undefined;
  
  /** List all registered component names */
  list(): string[];
}
```

## Usage Examples

### Basic Popover Implementation
```typescript
import { Popover } from '@base-ui-components/react/popover';
import type { PopoverComponentInterface } from './contracts/base-ui-interfaces';

export function NotificationPopover({ 
  content, 
  title = "Notifications",
  sideOffset = 8,
  ...props 
}: PopoverComponentInterface) {
  return (
    <Popover.Root>
      <Popover.Trigger 
        className="flex size-10 items-center justify-center rounded-md border"
        {...props}
      >
        <BellIcon aria-label="Notifications" />
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Positioner sideOffset={sideOffset}>
          <Popover.Popup className="rounded-lg bg-white px-6 py-4 shadow-lg">
            {title && <Popover.Title>{title}</Popover.Title>}
            <Popover.Description>{content}</Popover.Description>
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
```

### Style Configuration Example
```typescript
const popoverStyles: ComponentStyleConfig = {
  base: "rounded-lg shadow-lg transition-opacity",
  variants: {
    default: "bg-white text-gray-900 border border-gray-200",
    accent: "bg-blue-50 text-blue-900 border border-blue-200",
    danger: "bg-red-50 text-red-900 border border-red-200"
  },
  sizes: {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-3 text-base", 
    lg: "px-6 py-4 text-lg"
  }
};
```