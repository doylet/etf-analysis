/**
 * Base Widget Controller - Abstract implementation of IWidgetController
 * Provides common functionality for all widget controllers
 */
import { IWidgetController, WidgetState } from '../interfaces/IWidgetController';
import { IDataProvider } from '../interfaces/IDataProvider';
import { ILogger, IEventBus } from '../interfaces/IWidgetFactory';

export abstract class BaseWidgetController<TData = unknown, TConfig = unknown> 
  implements IWidgetController<TData, TConfig> {
  
  protected _data: TData | null = null;
  protected _isLoading = false;
  protected _error: Error | null = null;
  protected _lastUpdated: Date | null = null;
  protected _configuration: TConfig;
  protected subscribers = new Set<(data: TData | null) => void>();

  public readonly id: string;
  public readonly type: string;

  constructor(
    id: string,
    type: string,
    configuration: TConfig,
    protected dataProvider: IDataProvider<TData>,
    protected logger?: ILogger,
    protected eventBus?: IEventBus
  ) {
    this.id = id;
    this.type = type;
    this._configuration = configuration;
  }

  // Getters
  public get configuration(): TConfig {
    return this._configuration;
  }

  public get data(): TData | null {
    return this._data;
  }

  public get isLoading(): boolean {
    return this._isLoading;
  }

  public get error(): Error | null {
    return this._error;
  }

  public get lastUpdated(): Date | null {
    return this._lastUpdated;
  }

  // Abstract methods to be implemented by concrete controllers
  protected abstract buildQuery(config: TConfig): unknown;
  
  /**
   * Base validation for widget configuration
   * Override in concrete implementations for specific validation
   */
  protected validateConfiguration(config: TConfig): boolean {
    if (!config) {
      this.logger?.error('Configuration is required');
      return false;
    }
    return true;
  }

  public async initialize(config: TConfig): Promise<void> {
    try {
      if (!this.validateConfiguration(config)) {
        throw new Error('Invalid configuration provided');
      }
      this._configuration = config;
      await this.refresh();
      this.logger?.info(`Widget controller ${this.id} initialized`, { type: this.type });
    } catch (error) {
      this.logger?.error(`Failed to initialize widget controller ${this.id}`, error as Error);
      throw error;
    }
  }

  public async refresh(force = false): Promise<void> {
    if (this._isLoading && !force) {
      return;
    }

    this._isLoading = true;
    this._error = null;
    this.notifySubscribers();

    try {
      const query = this.buildQuery(this._configuration);
      this._data = await this.dataProvider.fetchData(query, { forceRefresh: force });
      this._lastUpdated = new Date();
      this._isLoading = false;
      
      this.logger?.debug(`Widget ${this.id} data refreshed`, { 
        type: this.type,
        lastUpdated: this._lastUpdated 
      });

      // Publish refresh event
      if (this.eventBus) {
        this.eventBus.publish(`widget.${this.id}.refreshed`, {
          widgetId: this.id,
          type: this.type,
          data: this._data
        });
      }

      this.notifySubscribers();
    } catch (error) {
      this._error = error as Error;
      this._isLoading = false;
      this.logger?.error(`Widget ${this.id} refresh failed`, error as Error);
      this.notifySubscribers();
      throw error;
    }
  }

  public async updateConfiguration(config: Partial<TConfig>): Promise<void> {
    try {
      const newConfig = { ...this._configuration, ...config };
      if (!this.validateConfiguration(newConfig)) {
        throw new Error('Invalid configuration provided');
      }
      
      const hasDataImpact = this.hasDataImpact(config);
      this._configuration = newConfig;
      
      if (hasDataImpact) {
        await this.refresh(true);
      }

      this.logger?.info(`Widget ${this.id} configuration updated`, { 
        type: this.type,
        hasDataImpact 
      });
    } catch (error) {
      this.logger?.error(`Failed to update configuration for widget ${this.id}`, error as Error);
      throw error;
    }
  }

  public subscribe(callback: (data: TData | null) => void): () => void {
    this.subscribers.add(callback);
    
    // Immediately call with current data
    callback(this._data);

    return () => {
      this.subscribers.delete(callback);
    };
  }

  public async dispose(): Promise<void> {
    try {
      this.subscribers.clear();
      await this.dataProvider.dispose();
      
      if (this.eventBus) {
        this.eventBus.publish(`widget.${this.id}.disposed`, {
          widgetId: this.id,
          type: this.type
        });
      }

      this.logger?.info(`Widget controller ${this.id} disposed`, { type: this.type });
    } catch (error) {
      this.logger?.error(`Failed to dispose widget controller ${this.id}`, error as Error);
      throw error;
    }
  }

  public getState(): WidgetState<TData, TConfig> {
    return {
      id: this.id,
      type: this.type,
      configuration: this._configuration,
      data: this._data,
      isLoading: this._isLoading,
      error: this._error,
      lastUpdated: this._lastUpdated,
      subscriptionCount: this.subscribers.size
    };
  }

  protected notifySubscribers(): void {
    this.subscribers.forEach(callback => {
      try {
        callback(this._data);
      } catch (error) {
        this.logger?.error(`Subscriber callback failed for widget ${this.id}`, error as Error);
      }
    });
  }

  /**
   * Determine if configuration changes require data refresh
   * Override in concrete implementations for specific logic
   */
  protected hasDataImpact(config: Partial<TConfig>): boolean {
    return true; // Conservative default - refresh on any config change
  }
}