# ETF Analysis Dashboard - Frontend (Next.js)

A modern, responsive portfolio analysis and optimization platform built with Next.js 16, shadcn/ui, and Tailwind CSS.

## Features

- 📊 Real-time portfolio summary dashboard
- 🎨 Modern UI with shadcn/ui component library
- 🌓 Dark mode support (built-in)
- ♿ Accessibility-first design
- 📱 Fully responsive layout
- ⚡ Fast build times with Turbopack

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS v4
- **Language**: TypeScript
- **State Management**: React 19 hooks
- **Icons**: Lucide React
- **Charts**: Recharts

## Getting Started

### Prerequisites

- Node.js 20+ 
- npm, yarn, or pnpm

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## Project Structure

```
frontend/v1/
├── src/
│   ├── app/                 # Next.js app router pages
│   │   ├── dashboard/       # Dashboard page
│   │   ├── login/           # Authentication
│   │   └── layout.tsx       # Root layout
│   ├── components/          # React components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── features/        # Feature-specific components
│   │   ├── layout/          # Layout components
│   │   └── README.md        # Component documentation
│   ├── lib/                 # Utility functions
│   │   ├── design-system/   # Design tokens
│   │   └── utils.ts         # Helper utilities
│   ├── hooks/               # Custom React hooks
│   └── contexts/            # React contexts
├── public/                  # Static assets
├── docs/                    # Documentation
│   ├── design-system.md     # Design system guide
│   └── shadcn-migration.md  # Migration notes
├── components.json          # shadcn/ui configuration
└── tailwind.config.js       # Tailwind configuration
```

## Component Library

This project uses [shadcn/ui](https://ui.shadcn.com) - a collection of re-usable components built with Radix UI and Tailwind CSS.

### Available Components

- **Card** - Container component with header/content/footer
- **Alert** - Notification messages (info, success, error)
- **Button** - Interactive buttons with variants
- **Skeleton** - Loading placeholders
- **Popover** - Dropdown menus and popovers

### Adding New Components

Use the shadcn CLI to add components:

```bash
npx shadcn@latest add [component-name]
```

Example:
```bash
npx shadcn@latest add dialog
npx shadcn@latest add table
```

Components are copied to `src/components/ui/` and can be customized as needed.

For more details, see the [Component README](src/components/README.md).

## Design System

The project includes a comprehensive design system built on shadcn/ui foundations:

- **Theme Variables**: Defined in `src/app/globals.css`
- **Design Tokens**: Available in `src/lib/design-system/design-tokens.ts`
- **Custom Variants**: Extendable component patterns
- **Dark Mode**: Built-in theme switching support

See [Design System Documentation](docs/design-system.md) for guidelines.

## Development

### Key Commands

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Code Style

- TypeScript for type safety
- ESLint for code quality
- Tailwind CSS for styling
- Component-first architecture

### Import Aliases

```typescript
// Configured in tsconfig.json
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/use-auth';
```

## Environment Variables

Create a `.env.local` file for environment-specific configuration:

```env
# API endpoints
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

## Testing

```bash
# Run tests (when available)
npm test

# Run tests in watch mode
npm test -- --watch
```

## Deployment

### Vercel (Recommended)

The easiest way to deploy is using [Vercel](https://vercel.com):

1. Push code to GitHub
2. Import project in Vercel
3. Deploy automatically on push

### Other Platforms

Build the production bundle:

```bash
npm run build
```

Then deploy the `.next` folder and `package.json` to your hosting platform.

## Documentation

- [Component Organization](src/components/README.md)
- [Design System Guidelines](docs/design-system.md)
- [shadcn/ui Migration Notes](docs/shadcn-migration.md)
- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)

## Recent Changes

### shadcn/ui Migration (December 2024)

The project was recently migrated from custom base-ui components to shadcn/ui:

- ✓ All components now use shadcn/ui
- ✓ Improved maintainability and customization
- ✓ Better accessibility and performance
- ✓ Enhanced design system foundation

See [Migration Documentation](docs/shadcn-migration.md) for details.

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.

