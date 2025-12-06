# Design System Guidelines

## Overview

The ETF Analysis design system is built on top of shadcn/ui components with custom theming and brand-specific styling. This document outlines the guidelines for using and extending the design system.

## Architecture

```
Design System Foundation
├── shadcn/ui Base Components (src/components/ui/)
├── Custom Theme (globals.css + tailwind.config.js)
├── Design Tokens (src/lib/design-system/design-tokens.ts)
└── Custom Component Variants (extending shadcn/ui)
```

## Color System

### Primary Colors

The design system uses HSL color space for flexibility and theme support:

```css
--primary: 0 0% 9%           /* Dark primary for light mode */
--primary-foreground: 0 0% 98% /* Light text on primary */
```

### Semantic Colors

- **Destructive/Error**: Red tones for errors and destructive actions
- **Muted**: Gray tones for secondary content
- **Accent**: Highlighted content and interactive elements
- **Border**: Consistent border colors across components

### Using Colors

```tsx
// Using theme colors in components
<div className="bg-primary text-primary-foreground">
  Primary content
</div>

<div className="bg-destructive text-destructive-foreground">
  Error message
</div>
```

## Typography

### Font Families

- **Sans**: System default sans-serif stack
- **Mono**: Monospace for code (disabled temporarily due to network)

### Font Sizes

Use Tailwind's text utilities:
- `text-xs` - 12px (labels, captions)
- `text-sm` - 14px (secondary text)
- `text-base` - 16px (body text)
- `text-lg` - 18px (large body)
- `text-xl` through `text-6xl` - Headings

### Usage Example

```tsx
<h1 className="text-2xl font-semibold">Page Title</h1>
<p className="text-sm text-muted-foreground">Description text</p>
```

## Spacing

Follow the 4px grid system using Tailwind spacing utilities:

- `p-4` - 16px padding
- `m-6` - 24px margin
- `gap-4` - 16px gap in flex/grid

## Component Variants

### Using shadcn/ui Variants

Most shadcn/ui components support variant props:

```tsx
// Button variants
<Button variant="default">Default</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Secondary</Button>
<Button variant="ghost">Tertiary</Button>

// Alert variants
<Alert variant="default">Info</Alert>
<Alert variant="destructive">Error</Alert>
```

### Sizes

Components support size variants:

```tsx
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
```

## Custom Components

### Creating Custom Variants

When extending shadcn/ui components, use `class-variance-authority`:

```tsx
import { cva } from "class-variance-authority";

const customVariants = cva(
  "base-classes",
  {
    variants: {
      variant: {
        custom: "custom-classes",
      },
    },
  }
);
```

### Wrapper Components

Create wrapper components for brand-specific patterns:

```tsx
// src/components/shared/brand-card.tsx
import { Card } from '@/components/ui/card';

export function BrandCard({ children, ...props }) {
  return (
    <Card className="border-2 border-primary" {...props}>
      {children}
    </Card>
  );
}
```

## Theming

### CSS Variables

All theme values are defined as CSS variables in `globals.css`:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 0 0% 3.9%;
  /* ... more variables */
}

.dark {
  --background: 0 0% 3.9%;
  --foreground: 0 0% 98%;
  /* ... dark mode overrides */
}
```

### Dark Mode

Dark mode support is built-in:

```tsx
// Toggle dark mode by adding 'dark' class to html element
<html className="dark">
```

### Custom Theme Extension

To customize the theme:

1. Update CSS variables in `globals.css`
2. Extend Tailwind config in `tailwind.config.js`
3. Components automatically inherit new values

Example:

```css
/* globals.css */
:root {
  --primary: 221 83% 53%; /* Custom blue */
}
```

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: '#3b82f6', // Custom brand color
      },
    },
  },
};
```

## Best Practices

### DO ✓

- Use shadcn/ui components as building blocks
- Leverage the `cn()` utility for conditional classes
- Follow Tailwind conventions for consistency
- Use semantic color names (primary, destructive) over literal colors
- Test components in both light and dark modes
- Document custom variants and wrapper components

### DON'T ✗

- Hardcode colors - use theme variables
- Create new components when shadcn/ui variants exist
- Override component internals - use composition instead
- Mix different design systems
- Skip accessibility considerations
- Forget to update documentation when adding custom patterns

## Accessibility

All shadcn/ui components follow accessibility best practices:

- Proper ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader support

When creating custom components:

```tsx
<button
  role="button"
  aria-label="Descriptive label"
  className="..."
>
  Content
</button>
```

## Resources

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Radix UI Documentation](https://radix-ui.com) (component primitives)
- [Component README](../components/README.md)

## Migration Notes

This design system was migrated from a custom base-ui implementation to shadcn/ui while maintaining visual consistency and functionality. Key changes:

- Component API updated to match shadcn/ui patterns
- Props simplified (removed custom size/variant props where possible)
- Styling moved from inline styles to Tailwind classes
- Theme now uses CSS variables for better customization

For migration details, see [shadcn-migration.md](./shadcn-migration.md).
