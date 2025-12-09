/**
 * Market Data Provider
 * 
 * Purpose: SOLID implementation for fetching market and portfolio data following Interface Segregation Principle
 * Responsibilities: API communication, data transformation, caching for market data
 * Supports: Portfolio summary, market status, pricing data
 */

import { BaseDataProvider } from './BaseDataProvider';
import { ILogger, ICacheService, IConfigService } from '../interfaces/IWidgetFactory';

// Market data response interfaces
interface MarketDataResponse {
  portfolio_summary: {
    total_value: number;
    total_return: number;
    total_return_percent: number;
    day_change: number;
    day_change_percent: number;
    positions: number;
    allocated_cash: number;
    last_updated: string;
    market_status: 'open' | 'closed' | 'pre_market' | 'after_hours';
  };
  market_status: {
    is_open: boolean;
    next_open: string;
    next_close: string;
    timezone: string;
  };
  pricing_data: {
    symbols: Record<string, {
      price: number;
      change: number;
      change_percent: number;
      volume: number;
      last_updated: string;
    }>;
  };
}

// Portfolio summary data (what controllers expect)
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

// Market status data
export interface MarketStatusData {
  is_open: boolean;
  next_open: string;
  next_close: string;
  timezone: string;
  current_time: string;
}

// Pricing data
export interface PricingData {
  symbols: Record<string, {
    price: number;
    change: number;
    change_percent: number;
    volume: number;
    last_updated: string;
  }>;
}

/**
 * Provider for market data including portfolio summaries, market status, and pricing
 */
export class MarketDataProvider extends BaseDataProvider<PortfolioSummaryData> {
  private readonly baseUrl: string;
  private readonly apiKey?: string;
  private readonly timeout: number;
  private readonly configService?: IConfigService;

  constructor(
    name: string = 'MarketDataProvider',
    logger?: ILogger,
    cacheService?: ICacheService,
    configService?: IConfigService
  ) {
    super(name, logger || {} as ILogger, cacheService);
    
    this.configService = configService;
    this.baseUrl = configService?.get('API_BASE_URL') || 'http://localhost:8000';
    this.apiKey = configService?.get('API_KEY');
    this.timeout = configService?.get('API_TIMEOUT') || 10000;
    
    this.logger?.info('MarketDataProvider initialized', { 
      baseUrl: this.baseUrl,
      hasApiKey: !!this.apiKey 
    });
  }

  /**
   * Fetch portfolio summary data
   */
  public async getData(): Promise<PortfolioSummaryData> {
    const cacheKey = 'market-data-portfolio-summary';
    
    // Try cache first
    const cached = this.cacheService?.get<PortfolioSummaryData>(cacheKey);
    if (cached) {
      this.logger?.debug('Portfolio summary data retrieved from cache');
      return cached;
    }
    
    try {
      this.logger?.debug('Fetching portfolio summary from API');
      
      const url = `${this.baseUrl}/api/widgets/portfolio/summary`;
      const response = await this.fetchWithTimeout(url, {
        headers: this.buildHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      const rawData: MarketDataResponse = await response.json();
      const portfolioData = this.transformPortfolioSummary(rawData.portfolio_summary);
      
      // Cache the transformed data
      if (this.cacheService) {
        this.cacheService.set(cacheKey, portfolioData, 30000); // 30 second cache
      }
      
      this.logger?.info('Portfolio summary data fetched successfully', { 
        totalValue: portfolioData.total_value,
        positions: portfolioData.positions 
      });
      
      return portfolioData;
    } catch (error) {
      this.logger?.error('Failed to fetch portfolio summary data', error instanceof Error ? error : new Error(String(error)));
      throw new Error(`Failed to load portfolio summary: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Fetch market status data
   */
  public async getMarketStatus(): Promise<MarketStatusData> {
    const cacheKey = 'market-data-market-status';
    
    // Try cache first
    const cached = this.cacheService?.get<MarketStatusData>(cacheKey);
    if (cached) {
      this.logger?.debug('Market status retrieved from cache');
      return cached;
    }
    
    try {
      this.logger?.debug('Fetching market status from API');
      
      const url = `${this.baseUrl}/api/market/status`;
      const response = await this.fetchWithTimeout(url, {
        headers: this.buildHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      const rawData: MarketDataResponse = await response.json();
      const marketStatus: MarketStatusData = {
        ...rawData.market_status,
        current_time: new Date().toISOString()
      };
      
      // Cache for 5 minutes
      if (this.cacheService) {
        this.cacheService.set(cacheKey, marketStatus, 300000);
      }
      
      this.logger?.info('Market status fetched successfully', { 
        isOpen: marketStatus.is_open 
      });
      
      return marketStatus;
    } catch (error) {
      this.logger?.error('Failed to fetch pricing data', error instanceof Error ? error : new Error(String(error)));
      throw new Error(`Failed to load pricing data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Fetch pricing data for specific symbols
   */
  public async getPricingData(symbols: string[]): Promise<PricingData> {
    const cacheKey = `market-data-pricing-${symbols.sort().join(',')}`;
    
    // Try cache first
    const cached = this.cacheService?.get<PricingData>(cacheKey);
    if (cached) {
      this.logger?.debug('Pricing data retrieved from cache', { symbols });
      return cached;
    }
    
    try {
      this.logger?.debug('Fetching pricing data from API', { symbols });
      
      const symbolsParam = symbols.join(',');
      const url = `${this.baseUrl}/api/market/pricing?symbols=${encodeURIComponent(symbolsParam)}`;
      const response = await this.fetchWithTimeout(url, {
        headers: this.buildHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      const rawData: MarketDataResponse = await response.json();
      const pricingData = rawData.pricing_data;
      
      // Cache for 1 minute (pricing data changes frequently)
      if (this.cacheService) {
        this.cacheService.set(cacheKey, pricingData, 60000);
      }
      
      this.logger?.info('Pricing data fetched successfully', { 
        symbolCount: Object.keys(pricingData.symbols).length 
      });
      
      return pricingData;
    } catch (error) {
      this.logger?.error('Failed to fetch pricing data', error instanceof Error ? error : new Error(String(error)), { 
        symbols 
      });
      throw new Error(`Failed to load pricing data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Fetch comprehensive market data (portfolio + market status + pricing for portfolio symbols)
   */
  public async getComprehensiveMarketData(): Promise<{
    portfolio: PortfolioSummaryData;
    marketStatus: MarketStatusData;
    pricing: PricingData;
  }> {
    try {
      this.logger?.debug('Fetching comprehensive market data');
      
      // Fetch all data in parallel for better performance
      const [portfolio, marketStatus] = await Promise.all([
        this.getData(),
        this.getMarketStatus()
      ]);
      
      // Get symbols from portfolio for pricing data (if available)
      // For now, use common symbols as we don't have portfolio holdings detail in this provider
      const commonSymbols = ['SPY', 'QQQ', 'VTI', 'AAPL', 'MSFT', 'GOOGL'];
      const pricing = await this.getPricingData(commonSymbols);
      
      this.logger?.info('Comprehensive market data fetched successfully');
      
      return {
        portfolio,
        marketStatus,
        pricing
      };
    } catch (error) {
      this.logger?.error('Failed to fetch comprehensive market data', error instanceof Error ? error : new Error(String(error)));
      throw new Error(`Failed to load comprehensive market data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Transform raw portfolio summary data to expected format
   */
  private transformPortfolioSummary(data: any): PortfolioSummaryData {
    return {
      total_value: this.safeNumber(data.total_value, 0),
      total_return: this.safeNumber(data.total_return, 0),
      total_return_percent: this.safeNumber(data.total_return_percent, 0),
      day_change: this.safeNumber(data.day_change, 0),
      day_change_percent: this.safeNumber(data.day_change_percent, 0),
      positions: this.safeNumber(data.positions, 0),
      allocated_cash: this.safeNumber(data.allocated_cash, 0),
      last_updated: data.last_updated || new Date().toISOString(),
      market_status: this.validateMarketStatus(data.market_status)
    };
  }

  /**
   * Safely convert to number with fallback
   */
  private safeNumber(value: any, fallback: number = 0): number {
    const num = Number(value);
    return isNaN(num) ? fallback : num;
  }

  /**
   * Validate market status value
   */
  private validateMarketStatus(status: any): 'open' | 'closed' | 'pre_market' | 'after_hours' {
    const validStatuses = ['open', 'closed', 'pre_market', 'after_hours'];
    return validStatuses.includes(status) ? status : 'closed';
  }

  /**
   * Build request headers
   */
  private buildHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    
    return headers;
  }

  /**
   * Fetch with timeout support
   */
  private async fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Request timeout after ${this.timeout}ms`);
      }
      throw error;
    }
  }

  /**
   * Invalidate all market data cache
   */
  public async invalidateCache(): Promise<void> {
    if (this.cacheService) {
      const cacheKeys = [
        'market-data-portfolio-summary',
        'market-data-market-status'
      ];
      
      for (const key of cacheKeys) {
        await this.cacheService.delete(key);
      }
      
      // Also invalidate pricing data cache (pattern-based)
      // This would depend on cache service implementation
      this.logger?.info('Market data cache invalidated');
    }
  }

  /**
   * Get provider type identifier
   */
  public static getType(): string {
    return 'market-data';
  }

  /**
   * Health check for the market data provider
   */
  public async healthCheck(): Promise<{
    healthy: boolean;
    responseTime: number;
    error?: string;
  }> {
    const startTime = Date.now();
    
    try {
      const url = `${this.baseUrl}/api/health`;
      const response = await this.fetchWithTimeout(url, {
        method: 'GET',
        headers: this.buildHeaders(),
      });
      
      const responseTime = Date.now() - startTime;
      const healthy = response.ok;
      
      this.logger?.debug('Health check completed', { healthy, responseTime });
      
      return {
        healthy,
        responseTime,
        error: healthy ? undefined : `HTTP ${response.status}: ${response.statusText}`
      };
    } catch (error) {
      const responseTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      this.logger?.warn('Health check failed', { responseTime, error: errorMessage });
      
      return {
        healthy: false,
        responseTime,
        error: errorMessage
      };
    }
  }

  // Implementation of abstract methods from BaseDataProvider
  protected async doFetchData(query: unknown): Promise<PortfolioSummaryData> {
    // Use the existing getData method for portfolio summary
    return this.getData();
  }

  protected async doInitialize(): Promise<void> {
    // Initialize connection by performing a health check
    const health = await this.healthCheck();
    if (!health.healthy) {
      throw new Error(`MarketDataProvider initialization failed: ${health.error}`);
    }
    this.logger?.info(`MarketDataProvider initialized successfully`);
  }

  protected async doDispose(): Promise<void> {
    // Clean up resources if any (none needed for this implementation)
    this.logger?.info(`MarketDataProvider disposed successfully`);
  }
}