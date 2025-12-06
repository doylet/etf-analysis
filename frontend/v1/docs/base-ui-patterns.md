# Base UI Styling Patterns

This document outlines the styling patterns and conventions for implementing Base UI components in the ETF Analysis Dashboard.

## Table of Contents

1. [Overview](#overview)
2. [Design System](#design-system)
3. [Component Architecture](#component-architecture)
4. [Styling Patterns](#styling-patterns)
5. [Variant System](#variant-system)
6. [Responsive Design](#responsive-design)
7. [Dark Mode Support](#dark-mode-support)
8. [Best Practices](#best-practices)

## Overview

Base UI provides unstyled, accessible components that we enhance with our design system using Tailwind CSS. This approach ensures consistency, accessibility, and flexibility across our application.

### Philosophy

- **Unstyled by default**: Base UI components provide behavior and accessibility without imposing visual design
- **Styled with purpose**: We apply consistent styling patterns using our design tokens
- **Flexible and composable**: Components can be easily customized while maintaining consistency
- **Accessible first**: All styling maintains WCAG 2.1 AA compliance

## Design System

### Color Palette

Our color system is built around semantic meaning and provides good contrast ratios:

#### Primary Colors
```css
/* Blue - Primary brand color */
--color-blue-50: #eff6ff
--color-blue-500: #3b82f6
--color-blue-600: #2563eb
--color-blue-700: #1d4ed8

/* Gray - Neutral colors */
--color-gray-50: #f9fafb
--color-gray-100: #f3f4f6
--color-gray-200: #e5e7eb
--color-gray-500: #6b7280
--color-gray-900: #111827
```

#### Semantic Colors
```css
/* Success */
--color-green-500: #10b981
--color-green-600: #059669

/* Warning */  
--color-yellow-500: #f59e0b
--color-yellow-600: #d97706

/* Danger */
--color-red-500: #ef4444
--color-red-600: #dc2626

/* Info */
--color-blue-500: #3b82f6
--color-blue-600: #2563eb
```

### Typography Scale

```css
/* Text sizes */
.text-xs    { font-size: 0.75rem }    /* 12px */
.text-sm    { font-size: 0.875rem }   /* 14px */
.text-base  { font-size: 1rem }       /* 16px */
.text-lg    { font-size: 1.125rem }   /* 18px */
.text-xl    { font-size: 1.25rem }    /* 20px */

/* Font weights */
.font-normal   { font-weight: 400 }
.font-medium   { font-weight: 500 }
.font-semibold { font-weight: 600 }
.font-bold     { font-weight: 700 }
```

### Spacing Scale

```css
/* Spacing scale (padding, margin, gaps) */
.spacing-1  { 0.25rem }  /* 4px */
.spacing-2  { 0.5rem }   /* 8px */
.spacing-3  { 0.75rem }  /* 12px */
.spacing-4  { 1rem }     /* 16px */
.spacing-6  { 1.5rem }   /* 24px */
.spacing-8  { 2rem }     /* 32px */
```

## Component Architecture

### Base Structure

All Base UI components follow this pattern:

```tsx
import { BaseUIComponent } from '@base-ui-components/react/component-name';
import { cn } from '@/lib/utils';
import { applyVariant } from '@/lib/base-ui-utils';
import type { ComponentStyleConfig, BaseUIComponentProps } from '@/lib/base-ui-types';

export interface CustomComponentProps extends BaseUIComponentProps {
  // Component-specific props
  customProp?: string;
}

const componentStyles: ComponentStyleConfig = {
  base: "shared-styles-for-all-variants",
  variants: {
    default: "default-variant-styles",
    primary: "primary-variant-styles"
  },
  sizes: {
    sm: "small-size-styles",
    md: "medium-size-styles",
    lg: "large-size-styles"
  }
};

export const CustomComponent: React.FC<CustomComponentProps> = ({
  variant = 'default',
  size = 'md',
  className,
  ...props
}) => {
  const classes = applyVariant(componentStyles, variant, size);
  
  return (
    <BaseUIComponent
      className={cn(classes, className)}
      {...props}
    />
  );
};
```

### File Organization

```
src/
├── components/
│   └── ui/
│       ├── notification-popover.tsx    # Main component file
│       ├── examples/                   # Usage examples
│       │   ├── base-ui-examples.tsx
│       │   ├── index.ts
│       │   └── README.md
│       └── index.ts                    # Component exports
├── lib/
│   ├── base-ui-types.ts               # TypeScript interfaces
│   ├── base-ui-utils.ts               # Utility functions
│   └── utils.ts                       # General utilities (cn function)
└── docs/
    ├── base-ui-patterns.md            # This file
    ├── accessibility.md               # Accessibility guidelines
    └── component-checklist.md         # Implementation checklist
```

## Styling Patterns

### 1. Base Styles

Base styles are applied to all variants and provide the foundation:

```css
.base-component {
  @apply relative inline-flex items-center justify-center;
  @apply rounded-md font-medium transition-colors;
  @apply focus-visible:outline-none focus-visible:ring-2;
  @apply disabled:pointer-events-none disabled:opacity-50;
}
```

### 2. Interactive States

Standard interactive states for all components:

```css
/* Hover states */
.hover\:bg-blue-700:hover { background-color: #1d4ed8 }

/* Focus states */
.focus-visible\:ring-2:focus-visible { 
  box-shadow: 0 0 0 2px var(--ring-color);
}

/* Active states */
.active\:scale-95:active { transform: scale(0.95) }

/* Disabled states */
.disabled\:opacity-50:disabled { opacity: 0.5 }
.disabled\:pointer-events-none:disabled { pointer-events: none }
```

### 3. Component Composition

Components are composed using multiple Base UI primitives:

```tsx
// Example: Modal component composition
<BaseModal.Root>
  <BaseModal.Trigger />
  <BaseModal.Portal>
    <BaseModal.Backdrop />
    <BaseModal.Positioner>
      <BaseModal.Popup>
        <BaseModal.Title />
        <BaseModal.Description />
        <BaseModal.Close />
      </BaseModal.Popup>
    </BaseModal.Positioner>
  </BaseModal.Portal>
</BaseModal.Root>
```

## Variant System

### Standard Variants

Most components support these standard variants:

#### Primary Variant
```css
.variant-primary {
  @apply bg-blue-600 text-white border-transparent;
  @apply hover:bg-blue-700 focus:ring-blue-500;
  @apply dark:bg-blue-500 dark:hover:bg-blue-600;
}
```

#### Secondary Variant
```css
.variant-secondary {
  @apply bg-gray-100 text-gray-900 border-gray-300;
  @apply hover:bg-gray-200 focus:ring-gray-500;
  @apply dark:bg-gray-800 dark:text-gray-100 dark:border-gray-600;
}
```

#### Danger Variant
```css
.variant-danger {
  @apply bg-red-600 text-white border-transparent;
  @apply hover:bg-red-700 focus:ring-red-500;
  @apply dark:bg-red-500 dark:hover:bg-red-600;
}
```

### Component-Specific Variants

Some components define their own variants:

```tsx
// NotificationPopover variants
const popoverStyles = {
  variants: {
    default: "border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900",
    elevated: "shadow-xl border-gray-100 bg-white dark:border-gray-700 dark:bg-gray-800"
  }
};
```

## Size System

### Standard Sizes

Components support consistent sizing:

#### Small (sm)
```css
.size-sm {
  @apply h-8 px-3 text-xs;
}
```

#### Medium (md) - Default
```css
.size-md {
  @apply h-10 px-4 text-sm;
}
```

#### Large (lg)
```css
.size-lg {
  @apply h-12 px-6 text-base;
}
```

### Responsive Sizing

Use responsive prefixes for adaptive sizing:

```tsx
className="w-full sm:w-80 md:w-96 lg:w-auto"
```

## Responsive Design

### Breakpoint System

```css
/* Tailwind CSS breakpoints */
sm: 640px    /* Small devices (landscape phones) */
md: 768px    /* Medium devices (tablets) */
lg: 1024px   /* Large devices (desktops) */
xl: 1280px   /* Extra large devices */
2xl: 1536px  /* 2X large devices */
```

### Mobile-First Approach

Always design for mobile first, then enhance for larger screens:

```tsx
className={cn(
  "p-2 sm:p-3",           // Smaller padding on mobile
  "text-xs sm:text-sm",   // Smaller text on mobile
  "w-full sm:w-80",       // Full width on mobile, fixed on larger screens
  "max-h-64 sm:max-h-80"  // Constrained height with responsive limits
)}
```

### Common Responsive Patterns

```tsx
// Stack on mobile, horizontal on desktop
"flex flex-col sm:flex-row"

// Hide on mobile, show on desktop
"hidden sm:block"

// Show on mobile, hide on desktop  
"block sm:hidden"

// Responsive grid
"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"

// Responsive spacing
"space-y-2 sm:space-y-0 sm:space-x-4"
```

## Dark Mode Support

### Color Strategy

Use semantic color classes that automatically adapt:

```css
/* Light and dark mode colors */
.text-primary { @apply text-gray-900 dark:text-gray-100; }
.bg-surface { @apply bg-white dark:bg-gray-900; }
.border-subtle { @apply border-gray-200 dark:border-gray-800; }
```

### Dark Mode Patterns

```tsx
// Background colors
"bg-white dark:bg-gray-900"

// Text colors
"text-gray-900 dark:text-gray-100"

// Border colors
"border-gray-200 dark:border-gray-800"

// Hover states
"hover:bg-gray-50 dark:hover:bg-gray-800"

// Focus rings
"focus:ring-blue-500 dark:focus:ring-blue-400"
```

### Testing Dark Mode

Test all components in both light and dark modes:

```tsx
// Force dark mode for testing
<div className="dark">
  <YourComponent />
</div>
```

## Best Practices

### 1. Consistency

- Use the `applyVariant` utility for all styled components
- Follow the established variant and size naming conventions
- Maintain consistent spacing and typography scales

### 2. Performance

- Use the `cn` utility to merge classes efficiently
- Leverage Tailwind's purge/tree-shaking for optimal bundle size
- Avoid inline styles; use Tailwind classes

### 3. Accessibility

- Include proper ARIA attributes in component interfaces
- Ensure sufficient color contrast (4.5:1 minimum)
- Test with keyboard navigation
- Verify screen reader compatibility

### 4. Maintainability

- Document component variants and their use cases
- Use TypeScript interfaces for all props
- Keep component logic separate from styling logic
- Write clear prop descriptions and examples

### 5. Testing

```tsx
// Test all variants and sizes
const variants = ['default', 'primary', 'secondary', 'danger'];
const sizes = ['sm', 'md', 'lg'];

variants.forEach(variant => {
  sizes.forEach(size => {
    // Test component with variant and size
    render(<Component variant={variant} size={size} />);
  });
});
```

### 6. Documentation

- Include usage examples for all variants
- Document responsive behavior
- Provide accessibility notes
- Show integration patterns

## Common Gotchas

### 1. Portal Components

Some Base UI components render in portals. Ensure proper styling:

```tsx
// Ensure portal styling inherits correctly
<BaseModal.Portal>
  <BaseModal.Backdrop className="fixed inset-0 bg-black/50" />
</BaseModal.Portal>
```

### 2. Z-Index Management

Use consistent z-index values:

```css
.z-dropdown { z-index: 1000; }
.z-modal { z-index: 1100; }
.z-tooltip { z-index: 1200; }
```

### 3. Animation Conflicts

Be careful with competing animations:

```tsx
// Use specific animation classes
className="animate-in fade-in-0 zoom-in-95 duration-200"
```

### 4. SSR Considerations

Some styling may need hydration handling:

```tsx
// Use client-only styling when needed
const [mounted, setMounted] = useState(false);
useEffect(() => setMounted(true), []);

if (!mounted) return null;
```

## Examples

See the `/src/components/ui/examples/` directory for complete working examples of all patterns described in this document.

## Resources

- [Base UI Documentation](https://base-ui.netlify.app/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)