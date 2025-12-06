# Accessibility Guidelines for Base UI Components

This document provides comprehensive accessibility guidelines for implementing and using Base UI components in the ETF Analysis Dashboard to ensure WCAG 2.1 AA compliance.

## Table of Contents

1. [Overview](#overview)
2. [WCAG 2.1 Principles](#wcag-21-principles)
3. [Component Accessibility](#component-accessibility)
4. [Keyboard Navigation](#keyboard-navigation)
5. [Screen Reader Support](#screen-reader-support)
6. [Color and Contrast](#color-and-contrast)
7. [Focus Management](#focus-management)
8. [ARIA Best Practices](#aria-best-practices)
9. [Testing Guidelines](#testing-guidelines)
10. [Common Patterns](#common-patterns)

## Overview

Accessibility is a core requirement for all Base UI components. This ensures our ETF analysis dashboard is usable by everyone, including users with disabilities.

### Accessibility Goals

- **WCAG 2.1 AA Compliance**: Meet or exceed Level AA standards
- **Universal Design**: Components work for all users regardless of ability
- **Progressive Enhancement**: Functionality degrades gracefully
- **Semantic HTML**: Proper use of HTML elements and ARIA attributes

## WCAG 2.1 Principles

Our components adhere to the four WCAG principles:

### 1. Perceivable
Information and UI components must be presentable to users in ways they can perceive.

- **Color Contrast**: Minimum 4.5:1 ratio for normal text, 3:1 for large text
- **Text Alternatives**: All non-text content has text alternatives
- **Adaptable**: Content can be presented without losing meaning
- **Distinguishable**: Make it easier for users to see and hear content

### 2. Operable
UI components and navigation must be operable by all users.

- **Keyboard Accessible**: All functionality available from keyboard
- **No Seizures**: Content doesn't cause seizures or physical reactions
- **Enough Time**: Users have enough time to read and use content
- **Navigable**: Help users navigate and find content

### 3. Understandable
Information and operation of UI must be understandable.

- **Readable**: Text is readable and understandable
- **Predictable**: Web pages appear and operate predictably
- **Input Assistance**: Help users avoid and correct mistakes

### 4. Robust
Content must be robust enough for interpretation by assistive technologies.

- **Compatible**: Maximize compatibility with assistive technologies
- **Valid Code**: Use clean, semantic markup

## Component Accessibility

### Base UI Component Features

Base UI components come with built-in accessibility features:

- **Semantic HTML**: Proper element types and structure
- **ARIA Attributes**: Comprehensive ARIA support
- **Keyboard Navigation**: Full keyboard accessibility
- **Focus Management**: Proper focus handling
- **Screen Reader Support**: Optimized for assistive technologies

### NotificationPopover Accessibility

Our NotificationPopover component implements these accessibility features:

```tsx
// Proper ARIA labeling
<button
  aria-label={`Notifications ${unreadCount > 0 ? `(${unreadCount} unread)` : ''}`}
  aria-expanded={open}
  aria-haspopup="dialog"
>
  <BellIcon />
  {unreadCount > 0 && (
    <span className="sr-only">
      {unreadCount} unread notifications
    </span>
  )}
</button>

// Accessible popover content
<div
  role="dialog"
  aria-labelledby="notifications-title"
  aria-describedby="notifications-description"
>
  <h3 id="notifications-title">Notifications</h3>
  <div id="notifications-description" className="sr-only">
    List of {notifications.length} notifications
  </div>
</div>
```

## Keyboard Navigation

### Universal Keyboard Standards

All components must support these keyboard interactions:

| Key | Action |
|-----|--------|
| `Tab` | Move focus to next focusable element |
| `Shift + Tab` | Move focus to previous focusable element |
| `Enter` | Activate buttons and links |
| `Space` | Activate buttons, toggle checkboxes |
| `Escape` | Close modals, popovers, dropdowns |
| `Arrow Keys` | Navigate within component collections |
| `Home` | Move to first item in a collection |
| `End` | Move to last item in a collection |

### Component-Specific Navigation

#### Popover/Dropdown Components
```tsx
// Keyboard event handling
const handleKeyDown = (event: React.KeyboardEvent) => {
  switch (event.key) {
    case 'Escape':
      setOpen(false);
      triggerRef.current?.focus();
      break;
    case 'ArrowDown':
      if (!open) setOpen(true);
      else focusNextItem();
      break;
    case 'ArrowUp':
      if (open) focusPreviousItem();
      break;
    case 'Enter':
    case ' ':
      if (!open) setOpen(true);
      break;
  }
};
```

#### Button Components
```tsx
// Proper button semantics
<button
  type="button"
  disabled={disabled}
  aria-pressed={pressed} // For toggle buttons
  aria-describedby={helpTextId} // Link to help text
  onKeyDown={handleKeyDown}
>
  {children}
</button>
```

## Screen Reader Support

### Content Structuring

Use proper heading hierarchy and landmarks:

```tsx
// Proper heading structure
<main aria-labelledby="main-title">
  <h1 id="main-title">ETF Analysis Dashboard</h1>
  
  <section aria-labelledby="portfolio-section">
    <h2 id="portfolio-section">Portfolio Overview</h2>
    
    <div role="region" aria-labelledby="notifications">
      <h3 id="notifications">Notifications</h3>
      <NotificationPopover />
    </div>
  </section>
</main>
```

### Screen Reader Only Content

Use `.sr-only` class for screen reader only information:

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

```tsx
// Example usage
<button>
  <TrashIcon aria-hidden="true" />
  <span className="sr-only">Delete notification</span>
</button>
```

### Live Regions

Use ARIA live regions for dynamic content updates:

```tsx
// Announce notification changes
<div
  aria-live="polite"
  aria-atomic="true"
  className="sr-only"
>
  {announceText}
</div>

// Update announcement when notifications change
useEffect(() => {
  if (unreadCount > 0) {
    setAnnounceText(`${unreadCount} new notifications received`);
  }
}, [unreadCount]);
```

## Color and Contrast

### Contrast Requirements

Ensure proper color contrast ratios:

- **Normal text**: 4.5:1 minimum contrast ratio
- **Large text**: 3:1 minimum contrast ratio
- **Non-text elements**: 3:1 minimum for UI components and graphics

### Color Implementation

```css
/* High contrast color combinations */
.text-high-contrast {
  @apply text-gray-900 dark:text-gray-100; /* ~15:1 ratio */
}

.text-medium-contrast {
  @apply text-gray-700 dark:text-gray-300; /* ~7:1 ratio */
}

.text-subtle {
  @apply text-gray-600 dark:text-gray-400; /* ~4.5:1 ratio */
}

/* Ensure interactive elements meet contrast requirements */
.btn-primary {
  @apply bg-blue-600 text-white; /* 4.5:1 ratio */
  @apply hover:bg-blue-700; /* Maintain contrast on hover */
}

.btn-secondary {
  @apply bg-gray-100 text-gray-900 border-gray-300; /* 4.5:1 ratio */
  @apply hover:bg-gray-200; /* Maintain contrast on hover */
}
```

### Color Independence

Never rely on color alone to convey information:

```tsx
// Bad - relies only on color
<div className="text-red-500">Error occurred</div>

// Good - uses color AND icon/text
<div className="text-red-500 flex items-center space-x-2">
  <ErrorIcon aria-hidden="true" />
  <span>Error: Unable to load data</span>
</div>
```

## Focus Management

### Focus Indicators

Ensure all interactive elements have clear focus indicators:

```css
/* Custom focus styles */
.focus-visible\:ring-2:focus-visible {
  outline: 2px solid transparent;
  box-shadow: 0 0 0 2px var(--ring-color);
}

.focus-visible\:ring-blue-500:focus-visible {
  --ring-color: #3b82f6;
}

/* High contrast focus for better visibility */
@media (prefers-contrast: high) {
  .focus-visible\:ring-2:focus-visible {
    outline: 3px solid;
    outline-offset: 2px;
  }
}
```

### Focus Trapping

Trap focus within modals and popovers:

```tsx
const useFocusTrap = (isActive: boolean) => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!isActive || !containerRef.current) return;
    
    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
    
    const handleTabKey = (e: KeyboardEvent) => {
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
    };
    
    container.addEventListener('keydown', handleTabKey);
    firstElement?.focus();
    
    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }, [isActive]);
  
  return containerRef;
};
```

## ARIA Best Practices

### Common ARIA Attributes

#### Labels and Descriptions

```tsx
// aria-label: Accessible name when text content isn't sufficient
<button aria-label="Close notification popover">
  <XIcon />
</button>

// aria-labelledby: Reference to element that labels this one
<div role="dialog" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Action</h2>
</div>

// aria-describedby: Reference to element that describes this one
<input
  type="password"
  aria-describedby="password-help"
/>
<div id="password-help">
  Password must be at least 8 characters
</div>
```

#### States and Properties

```tsx
// aria-expanded: For collapsible content
<button aria-expanded={isOpen} aria-controls="menu-items">
  Menu
</button>

// aria-pressed: For toggle buttons
<button aria-pressed={isActive}>
  {isActive ? 'Enabled' : 'Disabled'}
</button>

// aria-current: For current item in a set
<nav>
  <a href="/dashboard" aria-current="page">Dashboard</a>
  <a href="/portfolio">Portfolio</a>
</nav>

// aria-hidden: Hide decorative elements from screen readers
<span aria-hidden="true">👍</span>
<span>Great job!</span>
```

### Custom Roles

```tsx
// Use appropriate roles for custom components
<div role="tablist">
  <button role="tab" aria-selected={selected} aria-controls="panel-1">
    Tab 1
  </button>
</div>

<div role="tabpanel" id="panel-1">
  Tab content
</div>
```

## Testing Guidelines

### Manual Testing

#### Keyboard Testing
1. Navigate using only the keyboard
2. Ensure all interactive elements are reachable
3. Verify logical tab order
4. Test all keyboard shortcuts
5. Confirm focus indicators are visible

#### Screen Reader Testing
1. Test with NVDA (Windows), VoiceOver (Mac), or JAWS
2. Verify all content is announced properly
3. Check navigation shortcuts work
4. Ensure dynamic content updates are announced

### Automated Testing

```tsx
// Example accessibility tests with jest-axe
import { axe, toHaveNoViolations } from 'jest-axe';
import { render } from '@testing-library/react';

expect.extend(toHaveNoViolations);

test('NotificationPopover should not have accessibility violations', async () => {
  const { container } = render(
    <NotificationPopover
      notifications={mockNotifications}
      unreadCount={2}
    />
  );
  
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

// Test keyboard navigation
test('should handle keyboard navigation correctly', () => {
  render(<NotificationPopover />);
  
  const trigger = screen.getByRole('button');
  
  // Test Enter key opens popover
  fireEvent.keyDown(trigger, { key: 'Enter' });
  expect(screen.getByRole('dialog')).toBeVisible();
  
  // Test Escape key closes popover
  fireEvent.keyDown(document, { key: 'Escape' });
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});
```

### Tools for Testing

- **axe-core**: Automated accessibility testing
- **WAVE**: Web accessibility evaluation tool
- **Lighthouse**: Accessibility auditing
- **Colour Contrast Analyser**: Color contrast checking
- **Screen readers**: NVDA, JAWS, VoiceOver for real-world testing

## Common Patterns

### Loading States

```tsx
// Accessible loading state
<div role="status" aria-live="polite">
  {loading ? (
    <>
      <span className="sr-only">Loading notifications...</span>
      <LoadingSpinner aria-hidden="true" />
    </>
  ) : (
    <NotificationList notifications={notifications} />
  )}
</div>
```

### Error States

```tsx
// Accessible error handling
<div role="alert" aria-live="assertive">
  {error && (
    <div className="flex items-center space-x-2">
      <ErrorIcon aria-hidden="true" />
      <span>Error: {error.message}</span>
    </div>
  )}
</div>
```

### Form Validation

```tsx
// Accessible form validation
<div>
  <label htmlFor="email" className="block text-sm font-medium">
    Email Address
  </label>
  <input
    id="email"
    type="email"
    aria-invalid={!!emailError}
    aria-describedby={emailError ? "email-error" : undefined}
    className={cn(
      "block w-full rounded-md border",
      emailError ? "border-red-500" : "border-gray-300"
    )}
  />
  {emailError && (
    <div id="email-error" role="alert" className="text-red-600 text-sm">
      {emailError}
    </div>
  )}
</div>
```

### Data Tables

```tsx
// Accessible data table
<table role="table">
  <caption className="sr-only">
    Portfolio holdings with performance data
  </caption>
  <thead>
    <tr>
      <th scope="col">Symbol</th>
      <th scope="col">Holdings</th>
      <th scope="col">Performance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">VTI</th>
      <td>$10,000</td>
      <td>+5.2%</td>
    </tr>
  </tbody>
</table>
```

## Component Checklist

For each new component, verify:

- [ ] Proper semantic HTML structure
- [ ] Keyboard navigation implemented
- [ ] ARIA attributes added appropriately
- [ ] Color contrast meets WCAG AA standards
- [ ] Focus management implemented correctly
- [ ] Screen reader testing completed
- [ ] Automated accessibility tests pass
- [ ] Documentation includes accessibility notes

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Resources](https://webaim.org/resources/)
- [Base UI Accessibility Documentation](https://base-ui.netlify.app/guides/accessibility)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [axe-core Rules](https://dequeuniversity.com/rules/axe/)

## Getting Help

For accessibility questions or concerns:

1. Review this documentation
2. Check WCAG 2.1 guidelines
3. Test with screen readers
4. Use automated testing tools
5. Consult accessibility experts when needed

Remember: Accessibility is not a one-time task but an ongoing commitment to inclusive design.