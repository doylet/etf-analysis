/**
 * useWidgetController - Custom hook for managing widget controllers
 * Provides React integration for SOLID widget architecture
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { useWidgetServices } from './use-widget-services';
import { IWidgetController } from '../lib/interfaces/IWidgetController';
import { WidgetType } from '../lib/interfaces/IWidgetConfiguration';

export interface UseWidgetControllerOptions<TConfig> {
  /** Widget configuration */
  configuration: TConfig;
  
  /** Widget type */
  type: WidgetType;
  
  /** Auto-initialize on mount */
  autoInitialize?: boolean;
  
  /** Auto-dispose on unmount */
  autoDispose?: boolean;
  
  /** Error handler */
  onError?: (error: Error) => void;
  
  /** Success handler for refresh */
  onRefresh?: (data: unknown) => void;
}

export interface UseWidgetControllerResult<TData> {
  /** Current widget data */
  data: TData | null;
  
  /** Loading state */
  isLoading: boolean;
  
  /** Error state */
  error: Error | null;
  
  /** Last update timestamp */
  lastUpdated: Date | null;
  
  /** Manual refresh function */
  refresh: (force?: boolean) => Promise<void>;
  
  /** Update configuration */
  updateConfiguration: (config: Partial<unknown>) => Promise<void>;
  
  /** Controller instance (for advanced usage) */
  controller: IWidgetController<TData> | null;
  
  /** Controller state for debugging */
  getState: () => unknown;
}

export function useWidgetController<TData = unknown, TConfig = unknown>(
  options: UseWidgetControllerOptions<TConfig>
): UseWidgetControllerResult<TData> {
  
  const { factory, eventBus, logger } = useWidgetServices();
  const [controller, setController] = useState<IWidgetController<TData, TConfig> | null>(null);
  const [data, setData] = useState<TData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  // Use refs to avoid stale closures in effect cleanup
  const controllerRef = useRef<IWidgetController<TData, TConfig> | null>(null);
  const unsubscribeRef = useRef<(() => void) | null>(null);

  const {
    configuration,
    type,
    autoInitialize = true,
    autoDispose = true,
    onError,
    onRefresh
  } = options;

  // Initialize controller
  useEffect(() => {
    if (!autoInitialize) return;

    const initializeController = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Create data provider for this widget type
        const dataProvider = factory.createDataProvider(type, {
          baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
          cacheTimeout: 30000
        });

        // Create controller with dependencies
        const dependencies = {
          dataProvider,
          eventBus,
          logger,
          configService: {
            get: (key: string) => undefined,
            set: (key: string, value: unknown) => {},
            subscribe: () => () => {},
            clear: () => {}
          },
          cacheService: {
            get: (key: string) => undefined,
            set: (key: string, value: unknown) => {},
            delete: (key: string) => {},
            clear: () => {},
            getStats: () => ({ size: 0, hitRate: 0, missRate: 0 })
          }
        };

        const newController = factory.createController<TData, TConfig>(
          type,
          configuration,
          dependencies
        );

        // Subscribe to data changes
        const unsubscribe = newController.subscribe((newData) => {
          setData(newData);
          setIsLoading(newController.isLoading);
          setError(newController.error);
          setLastUpdated(newController.lastUpdated);
          
          if (newData && onRefresh) {
            onRefresh(newData);
          }
        });

        // Initialize the controller
        await newController.initialize(configuration);
        
        // Store references
        controllerRef.current = newController;
        unsubscribeRef.current = unsubscribe;
        setController(newController);
        setIsLoading(false);

        logger.info(`Widget controller initialized via hook`, { type, id: newController.id });
        
      } catch (err) {
        const error = err as Error;
        setError(error);
        setIsLoading(false);
        
        if (onError) {
          onError(error);
        } else {
          logger.error('Failed to initialize widget controller via hook', error, { type });
        }
      }
    };

    initializeController();

    return () => {
      // Cleanup on unmount
      if (autoDispose) {
        if (unsubscribeRef.current) {
          unsubscribeRef.current();
          unsubscribeRef.current = null;
        }
        
        if (controllerRef.current) {
          controllerRef.current.dispose().catch((error) => {
            logger.error('Failed to dispose controller in hook cleanup', error);
          });
          controllerRef.current = null;
        }
      }
    };
  }, [type, autoInitialize, autoDispose]); // Note: configuration changes handled separately

  // Handle configuration changes
  useEffect(() => {
    if (controller && configuration) {
      controller.updateConfiguration(configuration).catch((error) => {
        setError(error);
        if (onError) {
          onError(error);
        }
      });
    }
  }, [configuration, controller, onError]);

  // Memoized functions
  const refresh = useCallback(async (force = false) => {
    if (!controller) {
      throw new Error('Controller not initialized');
    }
    
    return controller.refresh(force);
  }, [controller]);

  const updateConfiguration = useCallback(async (config: Partial<TConfig>) => {
    if (!controller) {
      throw new Error('Controller not initialized');
    }
    
    return controller.updateConfiguration(config);
  }, [controller]);

  const getState = useCallback(() => {
    return controller?.getState() || null;
  }, [controller]);

  return {
    data,
    isLoading,
    error,
    lastUpdated,
    refresh,
    updateConfiguration,
    controller,
    getState
  };
}