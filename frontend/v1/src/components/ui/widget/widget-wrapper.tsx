/**
 * WidgetWrapper Component
 * Standardized container for dashboard widgets with consistent spacing
 * Applied at the render layer to ensure all widgets have consistent styling
 */

import * as React from 'react';
import { cn } from '@/lib/utils';

export type WidgetSpacing = 'tight' | 'compact' | 'normal';

interface WidgetWrapperProps extends React.HTMLAttributes<HTMLDivElement> {
  spacing?: WidgetSpacing;
}

const spacingMap: Record<WidgetSpacing, string> = {
  tight: 'p-1.5',
  compact: 'p-2',
  normal: 'p-3',
};

export const WidgetWrapper = React.forwardRef<HTMLDivElement, WidgetWrapperProps>(
  ({ spacing = 'compact', className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn(spacingMap[spacing], className)} {...props}>
        {children}
      </div>
    );
  }
);

WidgetWrapper.displayName = 'WidgetWrapper';

interface WidgetSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  spacing?: WidgetSpacing;
}

const sectionSpacingMap: Record<WidgetSpacing, string> = {
  tight: 'space-y-1.5',
  compact: 'space-y-2',
  normal: 'space-y-3',
};

export const WidgetSection = React.forwardRef<HTMLDivElement, WidgetSectionProps>(
  ({ spacing = 'compact', className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn(sectionSpacingMap[spacing], className)} {...props}>
        {children}
      </div>
    );
  }
);

WidgetSection.displayName = 'WidgetSection';

// Hook for managing widget spacing globally
interface UseWidgetSpacingReturn {
  spacing: WidgetSpacing;
  setSpacing: (spacing: WidgetSpacing) => void;
}

const WidgetSpacingContext = React.createContext<UseWidgetSpacingReturn | undefined>(undefined);

export function WidgetSpacingProvider({ 
  children, 
  defaultSpacing = 'compact' 
}: { 
  children: React.ReactNode;
  defaultSpacing?: WidgetSpacing;
}) {
  const [spacing, setSpacing] = React.useState<WidgetSpacing>(defaultSpacing);

  return (
    <WidgetSpacingContext.Provider value={{ spacing, setSpacing }}>
      {children}
    </WidgetSpacingContext.Provider>
  );
}

export function useWidgetSpacing(): UseWidgetSpacingReturn {
  const context = React.useContext(WidgetSpacingContext);
  if (!context) {
    // Return default if not in provider
    return {
      spacing: 'compact',
      setSpacing: () => {},
    };
  }
  return context;
}
