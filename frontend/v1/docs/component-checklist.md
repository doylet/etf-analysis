# Base UI Component Implementation Checklist

This checklist ensures consistent, accessible, and high-quality implementation of Base UI components in the ETF Analysis Dashboard.

## Pre-Implementation

### Planning & Research
- [ ] **Component Requirements Defined**: Clear understanding of component functionality and use cases
- [ ] **Base UI Component Selected**: Appropriate Base UI primitive chosen from available options
- [ ] **Design System Alignment**: Component fits within established design patterns and color schemes
- [ ] **Accessibility Requirements**: WCAG 2.1 AA compliance requirements understood
- [ ] **API Design**: Component props and interface designed with TypeScript

### Dependencies & Setup
- [ ] **Base UI Package**: Correct @base-ui-components/react version installed
- [ ] **Type Definitions**: Custom TypeScript interfaces defined in `@/lib/base-ui-types.ts`
- [ ] **Utility Functions**: Helper functions added to `@/lib/base-ui-utils.ts` if needed
- [ ] **Import Structure**: Proper import paths and tree-shaking considerations

## Component Development

### File Structure & Organization
- [ ] **Component File**: Created in appropriate `src/components/ui/` directory
- [ ] **Naming Convention**: Uses consistent naming (PascalCase for components, kebab-case for files)
- [ ] **File Exports**: Proper named and default exports defined
- [ ] **Import Organization**: Imports grouped logically (React, Base UI, internal, types)

### TypeScript Implementation
- [ ] **Interface Definition**: Component props interface extends `BaseUIComponentProps`
- [ ] **Type Safety**: All props properly typed with appropriate unions and optionals
- [ ] **Generic Types**: Generic types used where appropriate for flexibility
- [ ] **Default Values**: Sensible defaults provided for optional props
- [ ] **Props Forwarding**: Remaining props forwarded with `...props` spread

### Styling Implementation
- [ ] **Style Configuration**: `ComponentStyleConfig` object defined with base, variants, sizes
- [ ] **Variant System**: Consistent variant names (default, primary, secondary, etc.)
- [ ] **Size System**: Standard sizes (sm, md, lg) with appropriate scaling
- [ ] **applyVariant Usage**: `applyVariant` utility function used for consistent styling
- [ ] **className Merging**: `cn` utility used for proper class name merging
- [ ] **Responsive Design**: Mobile-first responsive utilities included

### Base UI Integration
- [ ] **Correct Import**: Base UI component imported from correct path (lowercase)
- [ ] **Proper Composition**: Base UI primitives composed correctly (Root, Trigger, Portal, etc.)
- [ ] **Event Handling**: Base UI events handled appropriately (onOpenChange, etc.)
- [ ] **Ref Forwarding**: Refs forwarded to appropriate elements when needed
- [ ] **Portal Usage**: Portal components used correctly for overlays

## Accessibility Implementation

### Semantic HTML & ARIA
- [ ] **Semantic Elements**: Appropriate HTML elements used (button, nav, main, etc.)
- [ ] **ARIA Labels**: `aria-label`, `aria-labelledby`, `aria-describedby` used appropriately
- [ ] **ARIA States**: `aria-expanded`, `aria-pressed`, `aria-current` implemented correctly
- [ ] **ARIA Properties**: `aria-hidden`, `aria-live`, `role` attributes used properly
- [ ] **Screen Reader Support**: Screen reader only content added with `.sr-only` class

### Keyboard Navigation
- [ ] **Tab Order**: Logical tab order through component
- [ ] **Keyboard Events**: Arrow keys, Enter, Space, Escape handled appropriately
- [ ] **Focus Management**: Focus moves correctly between component parts
- [ ] **Focus Trapping**: Focus trapped within modals/popovers when open
- [ ] **Focus Indicators**: Clear, visible focus indicators for all interactive elements

### Color & Contrast
- [ ] **Contrast Ratios**: All text meets WCAG AA contrast requirements (4.5:1 normal, 3:1 large)
- [ ] **Color Independence**: Information not conveyed by color alone
- [ ] **Dark Mode Support**: Proper dark mode color variants implemented
- [ ] **High Contrast**: Works with high contrast mode preferences

## Testing & Quality Assurance

### Unit Testing
- [ ] **Component Rendering**: Component renders without errors
- [ ] **Props Testing**: All props work correctly and handle edge cases
- [ ] **Event Testing**: User interactions trigger correct events
- [ ] **Keyboard Testing**: Keyboard navigation works as expected
- [ ] **Accessibility Tests**: axe-core tests pass without violations

### Manual Testing
- [ ] **Visual Testing**: Component looks correct in all variants and sizes
- [ ] **Responsive Testing**: Works correctly across different screen sizes
- [ ] **Browser Testing**: Tested in Chrome, Firefox, Safari, and Edge
- [ ] **Screen Reader Testing**: Tested with NVDA, JAWS, or VoiceOver
- [ ] **Keyboard Only**: Fully functional using only keyboard navigation

### Integration Testing
- [ ] **Build Success**: Component builds without TypeScript or linting errors
- [ ] **Bundle Size**: No significant impact on bundle size (tree-shaking working)
- [ ] **Performance**: No performance regressions in rendering or interactions
- [ ] **Existing Components**: Doesn't break existing component functionality

## Documentation & Examples

### Code Documentation
- [ ] **JSDoc Comments**: Component and props documented with clear descriptions
- [ ] **Usage Examples**: Basic usage example provided in component file
- [ ] **Type Documentation**: Complex types documented with examples
- [ ] **Accessibility Notes**: Accessibility features documented in component

### Usage Documentation
- [ ] **README**: Component usage documented in README or docs
- [ ] **Examples**: Working examples created in `src/components/ui/examples/`
- [ ] **Storybook/Demo**: Interactive demos created if applicable
- [ ] **Integration Guide**: How to integrate with existing components documented

## Performance & Optimization

### Bundle Optimization
- [ ] **Tree Shaking**: Only used Base UI components included in bundle
- [ ] **Import Optimization**: Imports use specific paths for better tree-shaking
- [ ] **Lazy Loading**: Large components use lazy loading when appropriate
- [ ] **Bundle Analysis**: Bundle size impact measured and documented

### Runtime Performance
- [ ] **Re-render Optimization**: Unnecessary re-renders minimized
- [ ] **Event Handler Stability**: Event handlers stable across renders (useCallback)
- [ ] **Memory Leaks**: No memory leaks from event listeners or subscriptions
- [ ] **Large Lists**: Virtualization used for large data sets when needed

## Security Considerations

### XSS Prevention
- [ ] **Input Sanitization**: User content properly sanitized before rendering
- [ ] **dangerouslySetInnerHTML**: Avoided or used safely with sanitization
- [ ] **URL Handling**: External URLs validated and secured
- [ ] **Content Security**: No inline styles or scripts that violate CSP

## Deployment Checklist

### Pre-Deployment
- [ ] **Code Review**: Code reviewed by team member
- [ ] **Tests Passing**: All automated tests pass
- [ ] **Linting**: ESLint and Prettier checks pass
- [ ] **TypeScript**: No TypeScript errors
- [ ] **Accessibility Audit**: Accessibility review completed

### Production Readiness
- [ ] **Error Boundaries**: Component handles errors gracefully
- [ ] **Loading States**: Appropriate loading states implemented
- [ ] **Error States**: Error handling and user feedback implemented
- [ ] **Fallback UI**: Graceful degradation for unsupported features
- [ ] **Mobile Optimization**: Optimized for mobile devices and touch interactions

## Post-Implementation

### Monitoring & Maintenance
- [ ] **Usage Tracking**: Component usage monitored in production
- [ ] **Performance Monitoring**: Performance metrics tracked
- [ ] **User Feedback**: User feedback collected and addressed
- [ ] **Accessibility Monitoring**: Ongoing accessibility compliance verified
- [ ] **Updates**: Base UI updates evaluated and integrated when beneficial

### Documentation Updates
- [ ] **Changelog**: Changes documented in project changelog
- [ ] **API Documentation**: Component API documentation updated
- [ ] **Design System**: Design system documentation updated
- [ ] **Team Knowledge**: Team training completed for new component patterns

## Quick Reference

### Essential Files to Create/Update
```
src/
├── components/ui/
│   └── your-component.tsx          # Main component file
├── lib/
│   ├── base-ui-types.ts           # Add interface if needed
│   └── base-ui-utils.ts           # Add utilities if needed
└── components/ui/examples/
    └── your-component-examples.tsx # Usage examples
```

### Essential Imports
```tsx
import React from 'react';
import { ComponentName } from '@base-ui-components/react/component-name';
import { cn } from '@/lib/utils';
import { applyVariant } from '@/lib/base-ui-utils';
import type { ComponentStyleConfig, BaseUIComponentProps } from '@/lib/base-ui-types';
```

### Essential Code Pattern
```tsx
export interface YourComponentProps extends BaseUIComponentProps {
  // Your specific props
}

const componentStyles: ComponentStyleConfig = {
  base: "base-styles",
  variants: { /* variants */ },
  sizes: { /* sizes */ }
};

export const YourComponent: React.FC<YourComponentProps> = ({
  variant = 'default',
  size = 'md',
  className,
  ...props
}) => {
  const classes = applyVariant(componentStyles, variant, size);
  
  return (
    <ComponentName
      className={cn(classes, className)}
      {...props}
    />
  );
};
```

## Common Pitfalls to Avoid

- **Missing accessibility attributes**: Always include proper ARIA labels
- **Inconsistent naming**: Follow established naming conventions
- **Poor TypeScript types**: Use specific types instead of `any`
- **Missing responsive design**: Always consider mobile-first design
- **Inadequate testing**: Test accessibility and keyboard navigation
- **Bundle size impact**: Verify tree-shaking is working correctly
- **Color-only communication**: Always provide non-color indicators

## Resources

- [Base UI Documentation](https://base-ui.netlify.app/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [TypeScript Best Practices](https://typescript-eslint.io/rules/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro)

---

**Remember**: This checklist ensures quality and consistency. Take time to review each item carefully - it's better to implement correctly once than to refactor later.