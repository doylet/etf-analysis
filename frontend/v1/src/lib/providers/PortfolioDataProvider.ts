/**
 * PortfolioDataProvider - Specific implementation for portfolio-related data fetching
 * Implements the Strategy pattern for different data sources
 */
import { BaseDataProvider } from './BaseDataProvider';
import { ILogger, ICacheService } from '../interfaces/IWidgetFactory';

export interface PortfolioApiResponse {
  widget_name: string;
  success: boolean;
  data: any;
  metadata: {
    execution_time: string;
    parameters: Record<string, any>;
    widget_description: string;
    cache_hit?: boolean;
    cached_at?: string;
  };
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

export interface PortfolioHoldingsData {
  holdings: Array<{
    symbol: string;
    name: string;
    asset_class: string;
    quantity: number;
    weight: number;
    market_value: number;
    current_price: number;
    day_change?: number;
    day_change_percent?: number;
    total_return?: number;
    total_return_percent?: number;
  }>;
  summary?: {
    total_positions: number;
    total_value: number;
    last_updated: string;
  };
}

export interface PortfolioSummaryData {
  total_value: number;
  total_return: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
  positions: number;
  allocated_cash: number;
  last_updated: string;
}

export class PortfolioDataProvider extends BaseDataProvider {
  
  private readonly apiBaseUrl: string;
  private readonly cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly cacheTimeout: number = 30000; // 30 seconds default
  
  constructor(
    name: string,
    logger: ILogger,
    cacheService?: ICacheService,
    apiBaseUrl?: string
  ) {
    super(name, logger, cacheService);
    this.apiBaseUrl = apiBaseUrl || 'http://localhost:8000';
  }

  /**
   * Fetch portfolio data based on endpoint and parameters
   */
  public async fetchData(endpoint: string, params: Record<string, any> = {}): Promise<any> {
    const cacheKey = this.getCacheKey(endpoint, params);
    
    // Check cache first
    const cachedData = this.getFromCache(cacheKey);
    if (cachedData && this.isCacheValid(cacheKey)) {
      this.logger?.debug('Portfolio data served from cache', { endpoint, cacheKey });
      return cachedData;
    }

    try {
      const response = await this.makeApiRequest(endpoint, params);
      
      // Validate API response structure
      if (!this.isValidApiResponse(response)) {
        throw new Error(`Invalid API response structure for ${endpoint}`);
      }

      // Extract and transform data based on endpoint
      const transformedData = this.transformApiData(endpoint, response);
      
      // Cache the result
      this.setCache(cacheKey, transformedData);
      
      this.logger?.info('Portfolio data fetched successfully', {
        endpoint,
        success: response.success,
        executionTime: response.metadata?.execution_time,
        cacheHit: response.metadata?.cache_hit
      });

      return transformedData;
      
    } catch (error) {
      this.logger?.error('Portfolio data fetch failed', error instanceof Error ? error : new Error(String(error)), { endpoint, params });
      throw error;
    }
  }

  /**
   * Specific method for fetching holdings data
   */
  public async fetchHoldings(portfolioId: string): Promise<PortfolioHoldingsData> {
    return this.fetchData('portfolio/holdings', { 
      portfolio_id: portfolioId,
      breakdown_type: 'asset_class' // Add breakdown_type as expected by API
    });
  }

  /**
   * Specific method for fetching portfolio summary
   */
  public async fetchPortfolioSummary(portfolioId: string): Promise<PortfolioSummaryData> {
    return this.fetchData('portfolio/summary', {
      portfolio_id: portfolioId
    });
  }

  /**
   * Specific method for fetching performance metrics
   */
  public async fetchPerformanceMetrics(portfolioId: string, period: string = '1M'): Promise<any> {
    return this.fetchData('performance', {
      portfolio_id: portfolioId,
      period,
      include_benchmarks: true
    });
  }

  /**
   * Make HTTP request to portfolio API
   */
  private async makeApiRequest(endpoint: string, params: Record<string, any>): Promise<PortfolioApiResponse> {
    const url = this.buildApiUrl(endpoint);
    const queryParams = new URLSearchParams(this.sanitizeParams(params)).toString();
    const fullUrl = queryParams ? `${url}?${queryParams}` : url;

    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        // Add authentication headers if needed
        ...(params.auth_token && { 'Authorization': `Bearer ${params.auth_token}` })
      },
      // Add request timeout
      signal: AbortSignal.timeout(30000)
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Build API URL for specific endpoint
   */
  private buildApiUrl(endpoint: string): string {
    const endpointMap: Record<string, string> = {
      'portfolio/holdings': '/api/widgets/portfolio/holdings', // Updated to match working API
      'portfolio/summary': '/api/widgets/portfolio/summary',   // Updated to match working API
      performance: '/api/widgets/performance',
      correlation: '/api/widgets/portfolio/correlation',
      optimization: '/api/widgets/portfolio/optimization'
    };

    const apiPath = endpointMap[endpoint];
    if (!apiPath) {
      throw new Error(`Unknown endpoint: ${endpoint}`);
    }

    return `${this.apiBaseUrl}${apiPath}`;
  }

  /**
   * Validate API response has expected structure
   */
  private isValidApiResponse(response: any): response is PortfolioApiResponse {
    return (
      response &&
      typeof response === 'object' &&
      typeof response.widget_name === 'string' &&
      typeof response.success === 'boolean' &&
      response.metadata &&
      typeof response.metadata === 'object'
    );
  }

  /**
   * Transform API data based on endpoint type
   */
  private transformApiData(endpoint: string, response: PortfolioApiResponse): any {
    if (!response.success || !response.data) {
      throw new Error(`API call unsuccessful: ${response.error?.message || 'Unknown error'}`);
    }

    switch (endpoint) {
      case 'holdings':
        return this.transformHoldingsData(response.data);
      case 'summary':
        return this.transformSummaryData(response.data);
      case 'performance':
        return this.transformPerformanceData(response.data);
      default:
        // Return raw data for unknown endpoints
        return response.data;
    }
  }

  /**
   * Transform holdings data with validation
   */
  private transformHoldingsData(data: any): PortfolioHoldingsData {
    if (!data || !Array.isArray(data.holdings)) {
      throw new Error('Invalid holdings data structure');
    }

    return {
      holdings: data.holdings.map((holding: any) => ({
        symbol: String(holding.symbol || ''),
        name: String(holding.name || ''),
        asset_class: String(holding.asset_class || 'Unknown'),
        quantity: Number(holding.quantity || 0),
        weight: Number(holding.weight || 0),
        market_value: Number(holding.market_value || 0),
        current_price: Number(holding.current_price || 0),
        day_change: Number(holding.day_change || 0),
        day_change_percent: Number(holding.day_change_percent || 0),
        total_return: Number(holding.total_return || 0),
        total_return_percent: Number(holding.total_return_percent || 0)
      })),
      summary: data.summary ? {
        total_positions: Number(data.summary.total_positions || 0),
        total_value: Number(data.summary.total_value || 0),
        last_updated: String(data.summary.last_updated || new Date().toISOString())
      } : undefined
    };
  }

  /**
   * Transform summary data with validation
   */
  private transformSummaryData(data: any): PortfolioSummaryData {
    return {
      total_value: Number(data.total_value || 0),
      total_return: Number(data.total_return || 0),
      total_return_percent: Number(data.total_return_percent || 0),
      day_change: Number(data.day_change || 0),
      day_change_percent: Number(data.day_change_percent || 0),
      positions: Number(data.positions || 0),
      allocated_cash: Number(data.allocated_cash || 0),
      last_updated: String(data.last_updated || new Date().toISOString())
    };
  }

  /**
   * Transform performance data with validation
   */
  private transformPerformanceData(data: any): any {
    // Add performance-specific transformations here
    return data;
  }

  /**
   * Sanitize parameters for API request
   */
  private sanitizeParams(params: Record<string, any>): Record<string, string> {
    const sanitized: Record<string, string> = {};
    
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined) {
        sanitized[key] = String(value);
      }
    }
    
    return sanitized;
  }

  /**
   * Generate cache key from endpoint and parameters
   */
  private getCacheKey(endpoint: string, params: Record<string, any>): string {
    const paramString = Object.entries(params)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => `${key}:${value}`)
      .join('|');
    
    return `portfolio:${endpoint}:${paramString}`;
  }

  /**
   * Check if cached data is still valid
   */
  private isCacheValid(cacheKey: string): boolean {
    const cached = this.cache.get(cacheKey);
    if (!cached) return false;
    
    const age = Date.now() - cached.timestamp;
    return age < this.cacheTimeout;
  }

  /**
   * Get data from cache
   */
  private getFromCache(cacheKey: string): any | null {
    const cached = this.cache.get(cacheKey);
    return cached ? cached.data : null;
  }

  /**
   * Set data in cache
   */
  private setCache(cacheKey: string, data: any): void {
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    });
  }

  // Implementation of abstract methods from BaseDataProvider
  protected async doFetchData(query: unknown): Promise<unknown> {
    // For portfolio data provider, assume query is an endpoint string or has endpoint property
    if (typeof query === 'string') {
      return this.fetchData(query);
    } else if (query && typeof query === 'object' && 'endpoint' in query) {
      const { endpoint, params } = query as { endpoint: string; params?: Record<string, any> };
      return this.fetchData(endpoint, params);
    } else {
      // Default to holdings endpoint if query is not recognized
      return this.fetchData('/portfolio/holdings');
    }
  }

  protected async doInitialize(): Promise<void> {
    // Initialize any connections or setup needed
    this.logger?.info(`PortfolioDataProvider initialized successfully`);
  }

  protected async doDispose(): Promise<void> {
    // Clean up resources, clear cache
    this.cache.clear();
    this.logger?.info(`PortfolioDataProvider disposed successfully`);
  }
}