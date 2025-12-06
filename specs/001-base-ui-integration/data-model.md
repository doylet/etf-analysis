# Data Model: Base UI Library Integration

**Feature**: 001-base-ui-integration  
**Created**: December 5, 2025

## UI Component Configuration Entities

### Base UI Component Configuration
Represents the configuration structure for any Base UI component instance:

- **Component Type**: Identifier for the specific Base UI component (e.g., 'Popover', 'Dialog', 'Tooltip')
- **Props Configuration**: Key-value pairs defining component behavior and appearance
- **Style Classes**: Tailwind CSS class strings for component styling
- **Accessibility Attributes**: ARIA labels, roles, and descriptions for screen reader compatibility
- **Portal Settings**: Configuration for popup components that require portal rendering

### Portal Configuration
Represents the setup that enables popup components to render outside their parent containers:

- **Container Element**: Target DOM element for portal rendering (typically body or dedicated portal root)
- **Isolation Context**: CSS isolation settings to create proper stacking context
- **Position Strategy**: Positioning approach (fixed vs absolute) with iOS Safari compatibility
- **Z-Index Management**: Layer ordering configuration for proper popup display

### Style Integration Mapping
Represents the relationship between Base UI components and existing design system:

- **Component Variants**: Named style variants for consistent component appearance
- **Tailwind Class Sets**: Predefined combinations of Tailwind classes for common patterns
- **Theme Tokens**: Design system values (colors, spacing, typography) mapped to component properties
- **Responsive Breakpoints**: Mobile-first styling configurations for different screen sizes

### Accessibility Configuration
Represents accessibility settings and requirements for Base UI components:

- **ARIA Attributes**: Required accessibility attributes for screen reader support
- **Keyboard Navigation**: Tab order and keyboard interaction patterns
- **Focus Management**: Focus trap and restoration behaviors for modal components
- **Screen Reader Announcements**: Live region configurations for dynamic content updates

## Relationships

- **Component Configuration** uses **Style Integration Mapping** for consistent appearance
- **Portal Configuration** enables **Component Configuration** for popup components
- **Accessibility Configuration** is required by all **Component Configuration** instances
- **Style Integration Mapping** references existing Tailwind CSS design tokens and classes

## Configuration Examples

### Popover Component Configuration
```typescript
{
  componentType: 'Popover',
  props: {
    sideOffset: 8,
    align: 'start'
  },
  styleClasses: {
    trigger: 'flex size-10 items-center justify-center rounded-md border',
    popup: 'rounded-lg bg-white px-6 py-4 shadow-lg',
    arrow: 'fill-white'
  },
  accessibility: {
    triggerLabel: 'Open notifications',
    popupRole: 'dialog',
    closeLabel: 'Close notifications'
  },
  portalEnabled: true
}
```

### Style Integration Example
```typescript
{
  variant: 'notification-popover',
  tailwindClasses: {
    base: 'rounded-lg shadow-lg transition-opacity',
    variants: {
      light: 'bg-white text-gray-900 border border-gray-200',
      dark: 'bg-gray-800 text-white border border-gray-600'
    }
  }
}
```