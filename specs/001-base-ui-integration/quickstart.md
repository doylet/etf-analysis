# Quick Start: Base UI Library Integration

**Feature**: 001-base-ui-integration  
**Created**: December 5, 2025

## Overview

This guide helps developers integrate and use Base UI components in the ETF Analysis Dashboard. Base UI provides modern, accessible, and unstyled components that integrate seamlessly with our existing Tailwind CSS design system.

## Installation & Setup

### 1. Install Base UI Library

```bash
cd frontend/v1
npm install @base-ui-components/react
```

### 2. Configure Portal Support

Update `frontend/v1/src/app/layout.tsx`:

```tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning={true}
      >
        <div className="root">
          <AuthProvider>
            {children}
          </AuthProvider>
        </div>
      </body>
    </html>
  );
}
```

### 3. Add Required CSS

Add to `frontend/v1/src/app/globals.css`:

```css
/* Portal isolation for popup components */
.root {
  isolation: isolate;
}

/* iOS 26+ Safari compatibility */
body {
  position: relative;
}
```

## Basic Component Implementation

### Example: Notification Popover

Create a new file `frontend/v1/src/components/ui/notification-popover.tsx`:

```tsx
'use client';

import { Popover } from '@base-ui-components/react/popover';
import { BellIcon } from 'lucide-react';

interface NotificationPopoverProps {
  notifications: string[];
  className?: string;
}

export function NotificationPopover({ 
  notifications, 
  className = "" 
}: NotificationPopoverProps) {
  return (
    <Popover.Root>
      <Popover.Trigger 
        className={`flex size-10 items-center justify-center rounded-md border border-gray-200 bg-gray-50 text-gray-900 hover:bg-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-1 focus-visible:outline-blue-800 ${className}`}
      >
        <BellIcon aria-label="Notifications" className="h-5 w-5" />
      </Popover.Trigger>
      
      <Popover.Portal>
        <Popover.Positioner sideOffset={8}>
          <Popover.Popup className="origin-[var(--transform-origin)] rounded-lg bg-white px-6 py-4 text-gray-900 shadow-lg shadow-gray-200 outline outline-1 outline-gray-200 transition-[transform,scale,opacity] data-[ending-style]:scale-90 data-[ending-style]:opacity-0 data-[starting-style]:scale-90 data-[starting-style]:opacity-0">
            
            <Popover.Arrow className="data-[side=bottom]:top-[-8px] data-[side=top]:bottom-[-8px] data-[side=top]:rotate-180">
              <ArrowIcon />
            </Popover.Arrow>
            
            <Popover.Title className="text-base font-medium mb-2">
              Notifications
            </Popover.Title>
            
            <Popover.Description className="text-base text-gray-600">
              {notifications.length === 0 ? (
                "You're all caught up. Good job!"
              ) : (
                <ul className="space-y-1">
                  {notifications.map((notification, index) => (
                    <li key={index} className="text-sm">{notification}</li>
                  ))}
                </ul>
              )}
            </Popover.Description>
            
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}

// Arrow component for popover
function ArrowIcon() {
  return (
    <svg width="20" height="10" viewBox="0 0 20 10" fill="none">
      <path
        d="M9.66437 2.60207L4.80758 6.97318C4.07308 7.63423 3.11989 8 2.13172 8H0V10H20V8H18.5349C17.5468 8 16.5936 7.63423 15.8591 6.97318L11.0023 2.60207C10.622 2.2598 10.0447 2.25979 9.66437 2.60207Z"
        fill="white"
      />
      <path
        d="M8.99542 1.85876C9.75604 1.17425 10.9106 1.17422 11.6713 1.85878L16.5281 6.22989C17.0789 6.72568 17.7938 7.00001 18.5349 7.00001L15.89 7L11.0023 2.60207C10.622 2.2598 10.0447 2.2598 9.66436 2.60207L4.77734 7L2.13171 7.00001C2.87284 7.00001 3.58774 6.72568 4.13861 6.22989L8.99542 1.85876Z"
        fill="#e5e7eb"
      />
    </svg>
  );
}
```

### Usage in Dashboard

Add to any dashboard page:

```tsx
import { NotificationPopover } from '@/components/ui/notification-popover';

export default function DashboardPage() {
  const notifications = ["Portfolio updated", "New market data available"];
  
  return (
    <div className="dashboard">
      <header className="flex justify-between items-center p-4">
        <h1>ETF Analysis Dashboard</h1>
        <NotificationPopover notifications={notifications} />
      </header>
      {/* Rest of dashboard content */}
    </div>
  );
}
```

## Development Patterns

### 1. Component Structure

Follow this pattern for all Base UI components:

```tsx
'use client'; // Required for interactive components

import { ComponentName } from '@base-ui-components/react/component-name';

interface YourComponentProps {
  // Define your props with proper TypeScript types
}

export function YourComponent({ ...props }: YourComponentProps) {
  return (
    <ComponentName.Root>
      <ComponentName.Trigger className="tailwind-classes">
        {/* Trigger content */}
      </ComponentName.Trigger>
      
      <ComponentName.Portal>
        <ComponentName.Positioner>
          <ComponentName.Content className="tailwind-classes">
            {/* Component content */}
          </ComponentName.Content>
        </ComponentName.Positioner>
      </ComponentName.Portal>
    </ComponentName.Root>
  );
}
```

### 2. Styling Guidelines

- **Use Tailwind classes directly** on Base UI components
- **Maintain consistent spacing** with existing design system
- **Include hover and focus states** for interactive elements
- **Add data attributes** for testing: `data-testid="component-name"`

### 3. Accessibility Checklist

For every Base UI component implementation:

- ✅ Include `aria-label` on trigger elements
- ✅ Ensure keyboard navigation works (Tab, Enter, Escape)
- ✅ Test with screen reader (VoiceOver on macOS)
- ✅ Verify focus management (focus trap for modals)
- ✅ Check color contrast meets WCAG 2.1 AA standards

## Available Components

Base UI provides these components ready for integration:

- **Popover**: Floating content attached to an element
- **Dialog**: Modal overlays for important actions
- **Tooltip**: Brief descriptions on hover/focus
- **Collapsible**: Expandable content sections
- **Checkbox**: Enhanced checkbox inputs
- **Radio Group**: Enhanced radio button groups
- **Slider**: Range input controls
- **Switch**: Toggle switches

## Best Practices

### Performance

- **Tree-shake imports**: Import specific components, not the entire library
- **Lazy load components**: Use React.lazy() for non-critical components
- **Optimize animations**: Keep transitions under 300ms for responsiveness

### Styling

- **Consistent with design system**: Use existing Tailwind utilities
- **Mobile-first approach**: Design for mobile, enhance for desktop
- **Dark mode ready**: Use CSS variables for theme-aware styling

### Accessibility

- **Semantic HTML**: Let Base UI handle accessibility automatically
- **Custom labels**: Provide meaningful aria-labels for unique contexts
- **Test regularly**: Include accessibility testing in development workflow

## Troubleshooting

### Common Issues

**Issue**: Popover doesn't appear above other content  
**Solution**: Verify portal configuration and `.root { isolation: isolate }` style

**Issue**: Styling conflicts with existing components  
**Solution**: Base UI is unstyled - conflicts usually indicate Tailwind class specificity issues

**Issue**: iOS Safari backdrop not covering full viewport  
**Solution**: Ensure `body { position: relative }` is applied

### Bundle Size Monitoring

Monitor bundle size after adding Base UI components:

```bash
npm run build
npm run analyze # If you have bundle analyzer configured
```

Target: <50KB increase from Base UI integration

## Support

- **Base UI Documentation**: https://base-ui.com/docs
- **ETF Dashboard patterns**: Check existing components in `frontend/v1/src/components/`
- **Accessibility resources**: WCAG 2.1 guidelines and testing tools