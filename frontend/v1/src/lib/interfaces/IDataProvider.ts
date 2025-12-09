/**
 * Data provider interface following Open/Closed and Dependency Inversion Principles
 * Abstracts data sources to support multiple implementations (REST, WebSocket, Mock)
 */
export interface IDataProvider<TData = unknown, TQuery = unknown> {
  /** Provider identifier for debugging and logging */
  readonly name: string;
  
  /** Indicates if provider is currently available/connected */
  readonly isAvailable: boolean;
  
  /** Connection status for real-time providers */
  readonly connectionStatus: ConnectionStatus;

  /**
   * Initialize the data provider with configuration
   * @param config Provider-specific configuration
   */
  initialize(config: DataProviderConfig): Promise<void>;

  /**
   * Fetch data based on query parameters
   * @param query Query parameters specific to data type
   * @param options Request options (cache, timeout, etc.)
   */
  fetchData(query: TQuery, options?: FetchOptions): Promise<TData>;

  /**
   * Subscribe to real-time data updates (for WebSocket providers)
   * @param query Query parameters for subscription
   * @param callback Function called when data updates
   * @returns Unsubscribe function
   */
  subscribe?(query: TQuery, callback: (data: TData) => void): () => void;

  /**
   * Clear cached data for specific query
   * @param query Query to clear cache for, or undefined for all cache
   */
  clearCache(query?: TQuery): Promise<void>;

  /**
   * Get cache status for debugging
   */
  getCacheStatus(): CacheStatus;

  /**
   * Clean up provider resources
   */
  dispose(): Promise<void>;
}

/**
 * Connection status for real-time data providers
 */
export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  FAILED = 'failed'
}

/**
 * Configuration interface for data providers
 */
export interface DataProviderConfig {
  /** Base URL for REST providers */
  baseUrl?: string;
  
  /** WebSocket URL for real-time providers */
  websocketUrl?: string;
  
  /** API authentication token */
  apiToken?: string;
  
  /** Default cache timeout in milliseconds */
  cacheTimeout?: number;
  
  /** Request timeout in milliseconds */
  requestTimeout?: number;
  
  /** Maximum retry attempts */
  maxRetries?: number;
  
  /** Mock data mode for testing */
  mockMode?: boolean;
  
  /** Custom headers for requests */
  headers?: Record<string, string>;
}

/**
 * Options for data fetching requests
 */
export interface FetchOptions {
  /** Force refresh ignoring cache */
  forceRefresh?: boolean;
  
  /** Custom cache timeout for this request */
  cacheTimeout?: number;
  
  /** Request timeout override */
  timeout?: number;
  
  /** Abort signal for cancellation */
  abortSignal?: AbortSignal;
  
  /** Additional request headers */
  headers?: Record<string, string>;
}

/**
 * Cache status information
 */
export interface CacheStatus {
  /** Number of cached items */
  itemCount: number;
  
  /** Total cache size in bytes (estimated) */
  sizeBytes: number;
  
  /** Cache hit ratio (0-1) */
  hitRatio: number;
  
  /** Last cache cleanup timestamp */
  lastCleanup: Date | null;
}