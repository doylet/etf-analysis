/**
 * Core widget controller interface following Single Responsibility Principle
 * Separates presentation logic from data fetching and business rules
 */
export interface IWidgetController<TData = unknown, TConfig = unknown> {
  /** Unique identifier for the widget controller */
  readonly id: string;
  
  /** Widget type identifier */
  readonly type: string;
  
  /** Current widget configuration */
  readonly configuration: TConfig;
  
  /** Current data state */
  readonly data: TData | null;
  
  /** Loading state indicator */
  readonly isLoading: boolean;
  
  /** Error state with optional error details */
  readonly error: Error | null;
  
  /** Last successful data update timestamp */
  readonly lastUpdated: Date | null;

  /**
   * Initialize the widget controller with configuration
   * @param config Widget-specific configuration
   */
  initialize(config: TConfig): Promise<void>;

  /**
   * Refresh widget data from data provider
   * @param force Force refresh ignoring cache
   */
  refresh(force?: boolean): Promise<void>;

  /**
   * Update widget configuration and refresh if needed
   * @param config Updated configuration
   */
  updateConfiguration(config: Partial<TConfig>): Promise<void>;

  /**
   * Clean up resources and subscriptions
   */
  dispose(): Promise<void>;

  /**
   * Subscribe to data changes
   * @param callback Function called when data changes
   * @returns Unsubscribe function
   */
  subscribe(callback: (data: TData | null) => void): () => void;

  /**
   * Get current widget state summary for debugging
   */
  getState(): WidgetState<TData, TConfig>;
}

/**
 * Widget state interface for debugging and monitoring
 */
export interface WidgetState<TData, TConfig> {
  id: string;
  type: string;
  configuration: TConfig;
  data: TData | null;
  isLoading: boolean;
  error: Error | null;
  lastUpdated: Date | null;
  subscriptionCount: number;
}