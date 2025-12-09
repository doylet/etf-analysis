/**
 * Base Data Provider - Abstract implementation of IDataProvider
 * Provides common functionality for all data providers
 */
import { 
  IDataProvider, 
  ConnectionStatus, 
  DataProviderConfig, 
  FetchOptions, 
  CacheStatus 
} from '../interfaces/IDataProvider';
import { ILogger, ICacheService } from '../interfaces/IWidgetFactory';

export abstract class BaseDataProvider<TData = unknown, TQuery = unknown>
  implements IDataProvider<TData, TQuery> {
  
  public readonly name: string;
  protected _isAvailable = false;
  protected _connectionStatus = ConnectionStatus.DISCONNECTED;
  protected config: DataProviderConfig = {};

  constructor(
    name: string,
    protected logger: ILogger,
    protected cacheService?: ICacheService
  ) {
    this.name = name;
  }

  public get isAvailable(): boolean {
    return this._isAvailable;
  }

  public get connectionStatus(): ConnectionStatus {
    return this._connectionStatus;
  }

  // Abstract methods to be implemented by concrete providers
  protected abstract doFetchData(query: TQuery, options?: FetchOptions): Promise<TData>;
  protected abstract doInitialize(config: DataProviderConfig): Promise<void>;
  protected abstract doDispose(): Promise<void>;

  public async initialize(config: DataProviderConfig): Promise<void> {
    this.config = { ...this.config, ...config };
    this._connectionStatus = ConnectionStatus.CONNECTING;
    
    try {
      await this.doInitialize(this.config);
      this._isAvailable = true;
      this._connectionStatus = ConnectionStatus.CONNECTED;
      
      this.logger.info(`Data provider ${this.name} initialized successfully`, {
        config: this.sanitizeConfig(this.config)
      });
    } catch (error) {
      this._isAvailable = false;
      this._connectionStatus = ConnectionStatus.FAILED;
      this.logger.error(`Failed to initialize data provider ${this.name}`, error as Error);
      throw error;
    }
  }

  public async fetchData(query: TQuery, options?: FetchOptions): Promise<TData> {
    if (!this._isAvailable) {
      throw new Error(`Data provider ${this.name} is not available`);
    }

    const cacheKey = this.generateCacheKey(query);
    
    // Check cache first unless force refresh
    if (!options?.forceRefresh && this.cacheService) {
      const cached = this.cacheService.get<TData>(cacheKey);
      if (cached) {
        this.logger.debug(`Cache hit for ${this.name}`, { cacheKey });
        return cached;
      }
    }

    try {
      const startTime = Date.now();
      const data = await this.doFetchData(query, options);
      const duration = Date.now() - startTime;

      // Cache the result
      if (this.cacheService && data) {
        const ttl = options?.cacheTimeout || this.config.cacheTimeout || 30000; // 30 seconds default
        this.cacheService.set(cacheKey, data, ttl);
      }

      this.logger.debug(`Data fetched from ${this.name}`, { 
        cacheKey, 
        duration,
        cached: !!this.cacheService 
      });

      return data;
    } catch (error) {
      this.logger.error(`Failed to fetch data from ${this.name}`, error as Error, { 
        cacheKey,
        query: this.sanitizeQuery(query)
      });
      throw error;
    }
  }

  public async clearCache(query?: TQuery): Promise<void> {
    if (!this.cacheService) {
      return;
    }

    try {
      if (query) {
        const cacheKey = this.generateCacheKey(query);
        this.cacheService.delete(cacheKey);
        this.logger.debug(`Cache cleared for specific query in ${this.name}`, { cacheKey });
      } else {
        this.cacheService.clear();
        this.logger.debug(`All cache cleared for ${this.name}`);
      }
    } catch (error) {
      this.logger.error(`Failed to clear cache for ${this.name}`, error as Error);
      throw error;
    }
  }

  public getCacheStatus(): CacheStatus {
    if (!this.cacheService) {
      return {
        itemCount: 0,
        sizeBytes: 0,
        hitRatio: 0,
        lastCleanup: null
      };
    }

    const stats = this.cacheService.getStats();
    return {
      itemCount: stats.size,
      sizeBytes: stats.size * 1000, // Rough estimate
      hitRatio: stats.hitRate,
      lastCleanup: new Date() // Simplified
    };
  }

  public async dispose(): Promise<void> {
    try {
      await this.doDispose();
      this._isAvailable = false;
      this._connectionStatus = ConnectionStatus.DISCONNECTED;
      this.logger?.info(`Data provider ${this.name} disposed`);
    } catch (error) {
      this.logger?.error(`Failed to dispose data provider ${this.name}`, error as Error);
      throw error;
    }
  }

  /**
   * Generate cache key from query - override for custom logic
   */
  protected generateCacheKey(query: TQuery): string {
    return `${this.name}:${JSON.stringify(query)}`;
  }

  /**
   * Sanitize configuration for logging (remove sensitive data)
   */
  protected sanitizeConfig(config: DataProviderConfig): Partial<DataProviderConfig> {
    const sanitized = { ...config };
    if (sanitized.apiToken) {
      sanitized.apiToken = '***';
    }
    return sanitized;
  }

  /**
   * Sanitize query for logging - override if query contains sensitive data
   */
  protected sanitizeQuery(query: TQuery): unknown {
    return query;
  }

  /**
   * Handle connection failures with retry logic
   */
  protected async withRetry<T>(
    operation: () => Promise<T>, 
    maxRetries?: number
  ): Promise<T> {
    const retries = maxRetries || this.config.maxRetries || 3;
    let lastError: Error;

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt === retries) {
          this.logger.error(
            `Operation failed after ${retries} attempts in ${this.name}`, 
            lastError
          );
          break;
        }

        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000); // Exponential backoff, max 10s
        this.logger.warn(
          `Operation failed, retrying in ${delay}ms (attempt ${attempt}/${retries}) for ${this.name}`, 
          { error: lastError.message, stack: lastError.stack }
        );
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError!;
  }
}