/**
 * Widget factory interface following Abstract Factory Pattern
 * Creates widgets with dependency injection and configuration
 */
import { IWidgetController } from './IWidgetController';
import { IDataProvider, DataProviderConfig } from './IDataProvider';
import { WidgetType, WidgetTheme } from './IWidgetConfiguration';

export interface IWidgetFactory {
  /**
   * Create a new widget controller with dependencies injected
   * @param type Widget type identifier
   * @param config Widget configuration
   * @param dependencies Injected dependencies
   */
  createController<TData, TConfig>(
    type: WidgetType,
    config: TConfig,
    dependencies: WidgetDependencies
  ): IWidgetController<TData, TConfig>;

  /**
   * Create a data provider for specific widget type
   * @param type Widget type requiring data provider
   * @param config Data provider configuration
   */
  createDataProvider<TData, TQuery>(
    type: WidgetType,
    config: DataProviderConfig
  ): IDataProvider<TData, TQuery>;

  /**
   * Create default configuration for widget type
   * @param type Widget type
   * @param overrides Configuration overrides
   */
  createDefaultConfiguration<TConfig>(
    type: WidgetType,
    overrides?: Partial<TConfig>
  ): TConfig;

  /**
   * Validate widget configuration
   * @param type Widget type
   * @param config Configuration to validate
   * @returns Validation result with errors if invalid
   */
  validateConfiguration<TConfig>(
    type: WidgetType,
    config: TConfig
  ): ValidationResult;

  /**
   * Get available widget types
   */
  getSupportedTypes(): WidgetType[];

  /**
   * Register a new widget type with factory
   * @param type Widget type identifier
   * @param factory Factory function for creating controllers
   */
  registerWidget<TData, TConfig>(
    type: WidgetType,
    factory: WidgetControllerFactory<TData, TConfig>
  ): void;
}

/**
 * Dependencies injected into widget controllers
 */
export interface WidgetDependencies {
  /** Data provider instance */
  dataProvider: IDataProvider;
  
  /** Event bus for widget communication */
  eventBus: IEventBus;
  
  /** Configuration service */
  configService: IConfigService;
  
  /** Logging service */
  logger: ILogger;
  
  /** Cache service */
  cacheService: ICacheService;
  
  /** Theme service */
  themeService?: IThemeService;
}

/**
 * Factory function for creating widget controllers
 */
export type WidgetControllerFactory<TData, TConfig> = (
  config: TConfig,
  dependencies: WidgetDependencies
) => IWidgetController<TData, TConfig>;

/**
 * Configuration validation result
 */
export interface ValidationResult {
  /** Whether configuration is valid */
  isValid: boolean;
  
  /** Validation errors if invalid */
  errors: ValidationError[];
  
  /** Non-blocking warnings */
  warnings: ValidationWarning[];
}

/**
 * Configuration validation error
 */
export interface ValidationError {
  /** Field path with error */
  field: string;
  
  /** Error message */
  message: string;
  
  /** Error code for programmatic handling */
  code: string;
  
  /** Expected value or format */
  expected?: string;
  
  /** Actual value that failed validation */
  actual?: unknown;
}

/**
 * Configuration validation warning
 */
export interface ValidationWarning {
  /** Field path with warning */
  field: string;
  
  /** Warning message */
  message: string;
  
  /** Warning code */
  code: string;
  
  /** Suggested action */
  suggestion?: string;
}

/**
 * Service interfaces for dependency injection
 */

/**
 * Event bus for inter-widget communication
 */
export interface IEventBus {
  /** Subscribe to events */
  subscribe<T = unknown>(event: string, callback: (data: T) => void): () => void;
  
  /** Publish events */
  publish<T = unknown>(event: string, data: T): void;
  
  /** List active subscriptions */
  getSubscriptions(): Record<string, number>;
}

/**
 * Configuration service interface
 */
export interface IConfigService {
  /** Get configuration value */
  get<T = unknown>(key: string, defaultValue?: T): T | undefined;
  
  /** Set configuration value */
  set<T = unknown>(key: string, value: T): void;
  
  /** Subscribe to configuration changes */
  subscribe(key: string, callback: (value: unknown) => void): () => void;
  
  /** Clear configuration */
  clear(key?: string): void;
}

/**
 * Logging service interface
 */
export interface ILogger {
  /** Log debug message */
  debug(message: string, meta?: Record<string, unknown>): void;
  
  /** Log info message */
  info(message: string, meta?: Record<string, unknown>): void;
  
  /** Log warning message */
  warn(message: string, meta?: Record<string, unknown>): void;
  
  /** Log error message */
  error(message: string, error?: Error, meta?: Record<string, unknown>): void;
}

/**
 * Cache service interface
 */
export interface ICacheService {
  /** Get cached value */
  get<T = unknown>(key: string): T | undefined;
  
  /** Set cached value with optional TTL */
  set<T = unknown>(key: string, value: T, ttlMs?: number): void;
  
  /** Delete cached value */
  delete(key: string): void;
  
  /** Clear all cache */
  clear(): void;
  
  /** Get cache statistics */
  getStats(): {
    size: number;
    hitRate: number;
    missRate: number;
  };
}

/**
 * Theme service interface
 */
export interface IThemeService {
  /** Get current theme */
  getCurrentTheme(): WidgetTheme;
  
  /** Set theme */
  setTheme(theme: WidgetTheme): void;
  
  /** Subscribe to theme changes */
  subscribe(callback: (theme: WidgetTheme) => void): () => void;
  
  /** Get theme for specific widget */
  getWidgetTheme(widgetId: string): WidgetTheme;
}

// Re-export theme type
export type { WidgetTheme } from './IWidgetConfiguration';