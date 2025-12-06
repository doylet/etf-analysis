# Component Organization

This directory contains all React components for the ETF Analysis frontend, organized following shadcn/ui best practices.

## Directory Structure

```
src/components/
├── ui/              # shadcn/ui components (installed via CLI)
├── features/        # Feature-specific components
├── layout/          # Layout components (Header, Footer, etc.)
└── [root files]     # Page-level components
```

## Component Categories

### UI Components (`ui/`)

Canonical shadcn/ui components installed and managed via the shadcn CLI.

**Installation**: Use `npx shadcn@latest add [component]` to add new components.

**Current Components**:
- `alert.tsx` - Alert/notification messages
- `button.tsx` - Button component with variants
- `card.tsx` - Card container with header/content/footer
- `skeleton.tsx` - Loading skeleton placeholders
- `popover.tsx` - Popover/dropdown menus

**Customization**: Modify these components directly if needed. They're copied into your project, not imported from a package.

### Feature Components (`features/`)

Components specific to application features that don't belong in the generic UI library.

**Examples**:
- `notifications.tsx` - Notification bell and popover

**Guidelines**:
- Use shadcn/ui components as building blocks
- Keep feature-specific logic self-contained
- Export components individually (no barrel exports unless needed)

### Layout Components (`layout/`)

Components that define the application layout and structure.

**Examples**:
- `header.tsx` - Application header with navigation
- `footer.tsx` - Application footer
- `page-header.tsx` - Page-level header component

**Guidelines**:
- Should be reusable across different pages
- Handle responsive layouts
- Integrate with theme and design system

### Root Components

Page-level or cross-cutting components that don't fit into other categories.

**Examples**:
- `PortfolioSummary.tsx` - Main portfolio dashboard component
- `ProtectedRoute.tsx` - Authentication wrapper component

## Import Paths

All components use the `@/components` alias configured in `tsconfig.json`:

```typescript
// UI components
import { Card, Button } from '@/components/ui/card';

// Feature components
import { Notifications } from '@/components/features/notifications';

// Layout components
import { Header } from '@/components/layout/header';
```

## Adding New Components

### shadcn/ui Components

Use the CLI to add new shadcn/ui components:

```bash
npx shadcn@latest add [component-name]
```

This will:
1. Download the component to `src/components/ui/`
2. Install any required dependencies
3. Update `components.json` configuration

### Custom Components

1. Choose the appropriate directory (`features/`, `layout/`, or root)
2. Create a new `.tsx` file with the component
3. Use shadcn/ui components as building blocks
4. Export the component for use elsewhere

## Styling Guidelines

- Use Tailwind CSS classes for styling
- Leverage shadcn/ui design tokens (defined in `globals.css`)
- Use the `cn()` utility from `@/lib/utils` for conditional classes
- Follow the component patterns established by shadcn/ui

## Testing

- Write tests alongside components when appropriate
- Test component behavior, not implementation details
- Use React Testing Library conventions

## Design System

The design system is built on shadcn/ui foundations with custom theming:

- **Colors**: Defined in `tailwind.config.js` and `globals.css`
- **Typography**: System fonts with fallbacks
- **Spacing**: Tailwind's default spacing scale
- **Border Radius**: Customizable via `--radius` CSS variable

For more details, see the [Design System Documentation](../../docs/design-system.md).
