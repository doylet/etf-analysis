/**
 * Portfolio Summary Controller
 * 
 * Purpose: SOLID implementation for Portfolio Summary widget following Single Responsibility Principle
 * Responsibilities: Presentation logic, state management, user interactions for portfolio summary
 * Dependencies: Injected via constructor (IDataProvider, configuration, logger, etc.)
 */

import { BaseWidgetController } from './BaseWidgetController';
import { IDataProvider } from '../interfaces/IDataProvider';
import { ILogger, IEventBus, ICacheService, IConfigService } from '../interfaces/IWidgetFactory';

// Portfolio Summary specific types
export interface PortfolioSummaryData {
  total_value: number;
  total_return: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
  positions: number;
  allocated_cash: number;
  last_updated: string;
  market_status: 'open' | 'closed' | 'pre_market' | 'after_hours';
}

export interface PortfolioSummaryConfig {
  type: 'portfolio-summary';
  variant: 'standard' | 'compact' | 'detailed';
  title: string;
  refreshInterval: number;
  cache: boolean;
  errorRetryAttempts: number;
  showPercentages?: boolean;
  showCashAllocation?: boolean;
  showMarketStatus?: boolean;
  currencyFormat?: 'USD' | 'EUR' | 'GBP';
}

export interface PortfolioSummaryViewModel {
  // Formatted display data
  totalValue: string;
  totalReturn: string;
  totalReturnPercent: string;
  dayChange: string;
  dayChangePercent: string;
  positionsCount: string;
  allocatedCash: string;
  lastUpdated: string;
  marketStatus: string;
  
  // UI state
  showPercentages: boolean;
  showCashAllocation: boolean;
  showMarketStatus: boolean;
  
  // Trend indicators
  totalReturnTrend: 'positive' | 'negative' | 'neutral';
  dayChangeTrend: 'positive' | 'negative' | 'neutral';
  
  // Actions
  refreshData: () => void;
  togglePercentageView: () => void;
}

/**
 * Controller for Portfolio Summary widget implementing SOLID principles
 */
export class PortfolioSummaryController extends BaseWidgetController<PortfolioSummaryData, PortfolioSummaryConfig> {
  private config: PortfolioSummaryConfig;
  private marketDataProvider: IDataProvider<PortfolioSummaryData>;
  private showPercentages: boolean = true;
  private cacheService?: ICacheService;
  private configService?: IConfigService;

  constructor(
    marketDataProvider: IDataProvider<PortfolioSummaryData>,
    config: PortfolioSummaryConfig,
    logger?: ILogger,
    eventBus?: IEventBus,
    cacheService?: ICacheService,
    configService?: IConfigService
  ) {
    super(
      `portfolio-summary-${Date.now()}`, // id
      'portfolio-summary', // type 
      config, // configuration
      marketDataProvider, // dataProvider
      logger, // logger
      eventBus // eventBus
    );
    
    this.marketDataProvider = marketDataProvider;
    this.config = config;
    this.showPercentages = config.showPercentages ?? true;
    this.cacheService = cacheService;
    this.configService = configService;
    
    this.logger?.info('PortfolioSummaryController initialized', { 
      widgetId: this.id,
      variant: config.variant 
    });
  }

  /**
   * Build query parameters from widget configuration
   */
  protected buildQuery(config: PortfolioSummaryConfig): Record<string, any> {
    return {
      variant: config.variant,
      show_percentages: config.showPercentages,
      show_cash_allocation: config.showCashAllocation,
      show_market_status: config.showMarketStatus,
      currency_format: config.currencyFormat,
      refresh_interval: config.refreshInterval
    };
  }

  /**
   * Load portfolio summary data from the data provider
   */
  protected async fetchData(): Promise<PortfolioSummaryData> {
    try {
      this.logger?.debug('Fetching portfolio summary data', { widgetId: this.id });
      
      const data = await this.marketDataProvider.fetchData('portfolio-summary', {});
      
      this.logger?.info('Portfolio summary data loaded successfully', { 
        widgetId: this.id,
        totalValue: data.total_value,
        positions: data.positions 
      });
      
      // Emit data loaded event
      this.eventBus?.publish('portfolio-summary-data-loaded', {
        widgetId: this.id,
        data,
        timestamp: new Date().toISOString()
      });
      
      return data;
    } catch (error) {
      this.logger?.error('Failed to load portfolio summary data', error instanceof Error ? error : undefined, { 
        widgetId: this.id,
        error: error instanceof Error ? error.message : String(error) 
      });
      throw error;
    }
  }

  /**
   * Transform raw data into view model for presentation
   */
  protected transformToViewModel(data: PortfolioSummaryData): PortfolioSummaryViewModel {
    const currencyFormat = this.config.currencyFormat || 'USD';
    
    return {
      // Formatted display values
      totalValue: this.formatCurrency(data.total_value, currencyFormat),
      totalReturn: this.formatCurrency(data.total_return, currencyFormat),
      totalReturnPercent: this.formatPercent(data.total_return_percent),
      dayChange: this.formatCurrency(data.day_change, currencyFormat),
      dayChangePercent: this.formatPercent(data.day_change_percent),
      positionsCount: data.positions.toString(),
      allocatedCash: this.formatCurrency(data.allocated_cash, currencyFormat),
      lastUpdated: this.formatTimestamp(data.last_updated),
      marketStatus: this.formatMarketStatus(data.market_status),
      
      // UI state
      showPercentages: this.showPercentages && (this.config.showPercentages ?? true),
      showCashAllocation: this.config.showCashAllocation ?? true,
      showMarketStatus: this.config.showMarketStatus ?? true,
      
      // Trend indicators
      totalReturnTrend: this.determineTrend(data.total_return),
      dayChangeTrend: this.determineTrend(data.day_change),
      
      // Actions
      refreshData: () => this.refresh(),
      togglePercentageView: () => this.togglePercentageView()
    };
  }

  /**
   * Get widget configuration
   */
  public getConfiguration(): PortfolioSummaryConfig {
    return { ...this.config };
  }

  /**
   * Update configuration and refresh if needed
   */
  public async updateConfiguration(updates: Partial<PortfolioSummaryConfig>): Promise<void> {
    const oldConfig = { ...this.config };
    this.config = { ...this.config, ...updates };
    
    this.logger?.info('Portfolio summary configuration updated', { 
      widgetId: this.id,
      changes: updates 
    });
    
    // Emit configuration change event
    this.eventBus?.publish('portfolio-summary-config-updated', {
      widgetId: this.id,
      oldConfig,
      newConfig: this.config,
      timestamp: new Date().toISOString()
    });
    
    // Refresh data if cache settings changed
    if ('cache' in updates || 'refreshInterval' in updates) {
      this.refresh();
    }
  }

  /**
   * Toggle percentage display mode
   */
  public togglePercentageView(): void {
    this.showPercentages = !this.showPercentages;
    
    this.logger?.debug('Percentage view toggled', { 
      widgetId: this.id,
      showPercentages: this.showPercentages 
    });
    
    // Trigger re-render with updated view model
    if (this._data) {
      this.notifySubscribers();
    }
  }

  /**
   * Format currency with proper locale and currency symbol
   */
  private formatCurrency(amount: number, currency: string = 'USD'): string {
    if (amount === undefined || amount === null || isNaN(amount)) {
      return '$0.00';
    }
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  }

  /**
   * Format percentage with sign indicator
   */
  private formatPercent(value: number): string {
    if (value === undefined || value === null || isNaN(value)) {
      return '0.00%';
    }
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  }

  /**
   * Format timestamp for display
   */
  private formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch (error) {
      return 'Unknown';
    }
  }

  /**
   * Format market status for display
   */
  private formatMarketStatus(status: string): string {
    const statusMap: Record<string, string> = {
      open: 'Market Open',
      closed: 'Market Closed',
      pre_market: 'Pre-Market',
      after_hours: 'After Hours'
    };
    
    return statusMap[status] || 'Unknown';
  }

  /**
   * Determine trend direction for visual indicators
   */
  private determineTrend(value: number): 'positive' | 'negative' | 'neutral' {
    if (value === undefined || value === null || isNaN(value)) {
      return 'neutral';
    }
    return value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';
  }

  /**
   * Handle errors specific to portfolio summary operations
   */
  protected handleError(error: Error, context: string): void {
    this.logger?.error(`Portfolio summary error in ${context}`, error, { widgetId: this.id });
    
    // Emit portfolio summary specific error event
    this.eventBus?.publish('portfolio-summary-error', {
      widgetId: this.id,
      error: error.message,
      context,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Cleanup controller resources
   */
  public async dispose(): Promise<void> {
    this.logger?.info('Disposing PortfolioSummaryController', { widgetId: this.id });
    await super.dispose();
  }

  /**
   * Get controller type for factory registration
   */
  public static getType(): string {
    return 'portfolio-summary';
  }

  /**
   * Validate configuration for portfolio summary
   */
  public static validateConfiguration(config: any): config is PortfolioSummaryConfig {
    return (
      config &&
      config.type === 'portfolio-summary' &&
      typeof config.variant === 'string' &&
      ['standard', 'compact', 'detailed'].includes(config.variant) &&
      typeof config.title === 'string' &&
      typeof config.refreshInterval === 'number' &&
      typeof config.cache === 'boolean' &&
      typeof config.errorRetryAttempts === 'number'
    );
  }
}