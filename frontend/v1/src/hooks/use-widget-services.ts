/**
 * useWidgetServices - Custom hook to access widget services from context
 * Provides type-safe access to dependency injection container
 */
import { useContext } from 'react';
import { 
  WidgetServicesContext, 
  WidgetServices 
} from '../lib/providers/WidgetServicesProvider';

export function useWidgetServices(): WidgetServices {
  const context = useContext(WidgetServicesContext);
  
  if (!context) {
    throw new Error(
      'useWidgetServices must be used within a WidgetServicesProvider. ' +
      'Make sure to wrap your component with <WidgetServicesProvider>.'
    );
  }
  
  return context;
}

// Re-export types for convenience
export type { WidgetServices } from '../lib/providers/WidgetServicesProvider';