/**
 * MockDataProvider - Test implementation of IDataProvider for unit testing
 * Provides controlled data responses for comprehensive testing scenarios
 */
import { BaseDataProvider } from '../../../src/lib/providers/BaseDataProvider';
import { ILogger, ICacheService } from '../../../src/lib/interfaces/IWidgetFactory';

export interface MockDataResponse {
  data: any;
  delay?: number;
  shouldError?: boolean;
  errorMessage?: string;
}

export interface MockDataOptions {
  /** Name for the mock provider */
  name?: string;
  /** Logger instance */
  logger?: ILogger;
  /** Cache service instance */
  cacheService?: ICacheService;
  /** Predefined responses for specific endpoints */
  mockResponses?: Map<string, MockDataResponse>;
  /** Default delay for all responses (ms) */
  defaultDelay?: number;
  /** Global error simulation */
  simulateNetworkError?: boolean;
}

export class MockDataProvider extends BaseDataProvider {
  private mockResponses: Map<string, MockDataResponse>;
  private defaultDelay: number;
  private simulateNetworkError: boolean;
  private callLog: Array<{ endpoint: string; params: Record<string, any>; timestamp: Date }> = [];

  constructor(options: MockDataOptions = {}) {
    super(
      options.name || 'MockDataProvider',
      options.logger || { info: () => {}, error: () => {}, warn: () => {}, debug: () => {} } as ILogger,
      options.cacheService
    );
    this.mockResponses = options.mockResponses || new Map();
    this.defaultDelay = options.defaultDelay || 0;
    this.simulateNetworkError = options.simulateNetworkError || false;
  }

  /**
   * Mock implementation of fetchData with configurable responses
   */
  public async fetchData(endpoint: string, params: Record<string, any> = {}): Promise<any> {
    // Log the call for testing verification
    this.callLog.push({
      endpoint,
      params: { ...params },
      timestamp: new Date()
    });

    // Simulate network error if configured
    if (this.simulateNetworkError) {
      throw new Error('Network error: Connection failed');
    }

    // Get mock response for this endpoint
    const mockResponse = this.mockResponses.get(endpoint);
    if (!mockResponse) {
      throw new Error(`No mock response configured for endpoint: ${endpoint}`);
    }

    // Simulate error response
    if (mockResponse.shouldError) {
      throw new Error(mockResponse.errorMessage || `Mock error for endpoint: ${endpoint}`);
    }

    // Simulate delay
    const delay = mockResponse.delay ?? this.defaultDelay;
    if (delay > 0) {
      await this.simulateDelay(delay);
    }

    this.logger?.debug('Mock data provider response', { endpoint, params, data: mockResponse.data });
    
    return mockResponse.data;
  }

  /**
   * Configure a mock response for a specific endpoint
   */
  public setMockResponse(endpoint: string, response: MockDataResponse): void {
    this.mockResponses.set(endpoint, response);
  }

  /**
   * Configure multiple mock responses
   */
  public setMockResponses(responses: Record<string, MockDataResponse>): void {
    for (const [endpoint, response] of Object.entries(responses)) {
      this.mockResponses.set(endpoint, response);
    }
  }

  /**
   * Clear all mock responses
   */
  public clearMockResponses(): void {
    this.mockResponses.clear();
  }

  /**
   * Get call log for testing assertions
   */
  public getCallLog(): Array<{ endpoint: string; params: Record<string, any>; timestamp: Date }> {
    return [...this.callLog];
  }

  /**
   * Get calls for a specific endpoint
   */
  public getCallsForEndpoint(endpoint: string): Array<{ endpoint: string; params: Record<string, any>; timestamp: Date }> {
    return this.callLog.filter(call => call.endpoint === endpoint);
  }

  /**
   * Clear call log
   */
  public clearCallLog(): void {
    this.callLog = [];
  }

  /**
   * Check if endpoint was called with specific parameters
   */
  public wasCalledWith(endpoint: string, expectedParams?: Record<string, any>): boolean {
    const calls = this.getCallsForEndpoint(endpoint);
    if (!expectedParams) {
      return calls.length > 0;
    }
    
    return calls.some(call => 
      Object.entries(expectedParams).every(([key, value]) => 
        call.params[key] === value
      )
    );
  }

  /**
   * Get number of calls for an endpoint
   */
  public getCallCount(endpoint: string): number {
    return this.getCallsForEndpoint(endpoint).length;
  }

  /**
   * Simulate network delay
   */
  private async simulateDelay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Enable/disable network error simulation
   */
  public setNetworkErrorSimulation(enable: boolean): void {
    this.simulateNetworkError = enable;
  }

  /**
   * Create mock Holdings data for testing
   */
  public static createMockHoldingsData(count: number = 5): any {
    const mockHoldings = [];
    const assetClasses = ['ETF', 'Stock', 'Bond', 'Commodity', 'REIT'];
    const symbols = ['AAPL', 'GOOGL', 'MSFT', 'SPY', 'QQQ', 'VTI', 'BND', 'GLD', 'VNQ', 'TSLA'];
    
    for (let i = 0; i < count; i++) {
      mockHoldings.push({
        symbol: symbols[i % symbols.length],
        name: `Mock Company ${i + 1} Inc.`,
        asset_class: assetClasses[i % assetClasses.length],
        quantity: Math.floor(Math.random() * 1000) + 10,
        weight: Math.random() * 0.15 + 0.01, // 1% to 16%
        market_value: Math.random() * 50000 + 5000,
        current_price: Math.random() * 300 + 20,
        day_change: (Math.random() - 0.5) * 10,
        day_change_percent: (Math.random() - 0.5) * 5,
        total_return: (Math.random() - 0.3) * 1000,
        total_return_percent: (Math.random() - 0.3) * 20
      });
    }

    return {
      holdings: mockHoldings,
      summary: {
        total_positions: count,
        total_value: mockHoldings.reduce((sum, h) => sum + h.market_value, 0),
        last_updated: new Date().toISOString()
      }
    };
  }

  /**
   * Create mock Portfolio Summary data for testing
   */
  public static createMockPortfolioSummary(): any {
    return {
      total_value: 125000.50,
      total_return: 8750.25,
      total_return_percent: 7.5,
      day_change: -234.50,
      day_change_percent: -0.18,
      positions: 12,
      allocated_cash: 5000.00,
      last_updated: new Date().toISOString()
    };
  }

  /**
   * Create mock Performance data for testing
   */
  public static createMockPerformanceData(period: string = '1M'): any {
    const dataPoints = period === '1Y' ? 365 : period === '3M' ? 90 : 30;
    const returns = [];
    
    for (let i = 0; i < dataPoints; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      returns.push({
        date: date.toISOString().split('T')[0],
        return: (Math.random() - 0.5) * 2, // -1% to 1% daily
        cumulative_return: Math.random() * 10 - 2 // -2% to 8% cumulative
      });
    }
    
    return {
      period,
      returns: returns.reverse(),
      metrics: {
        total_return: 5.2,
        volatility: 12.5,
        sharpe_ratio: 1.1,
        max_drawdown: -3.8
      }
    };
  }

  /**
   * Create common mock responses for Holdings widget testing
   */
  public static createHoldingsMockResponses(): Map<string, MockDataResponse> {
    const responses = new Map<string, MockDataResponse>();
    
    responses.set('holdings', {
      data: MockDataProvider.createMockHoldingsData(8),
      delay: 100
    });
    
    responses.set('summary', {
      data: MockDataProvider.createMockPortfolioSummary(),
      delay: 50
    });
    
    responses.set('performance', {
      data: MockDataProvider.createMockPerformanceData(),
      delay: 150
    });
    
    return responses;
  }

  /**
   * Create error scenarios for testing
   */
  public static createErrorMockResponses(): Map<string, MockDataResponse> {
    const responses = new Map<string, MockDataResponse>();
    
    responses.set('holdings', {
      data: null,
      shouldError: true,
      errorMessage: 'Failed to fetch holdings data',
      delay: 100
    });
    
    responses.set('summary', {
      data: null,
      shouldError: true,
      errorMessage: 'Portfolio not found',
      delay: 50
    });
    
    return responses;
  }

  // Implementation of abstract methods from BaseDataProvider
  protected async doFetchData(query: unknown): Promise<unknown> {
    // Treat query as endpoint string for mock responses
    const endpoint = typeof query === 'string' ? query : JSON.stringify(query);
    
    const mockResponse = this.mockResponses.get(endpoint);
    if (!mockResponse) {
      throw new Error(`No mock response configured for endpoint: ${endpoint}`);
    }

    if (mockResponse.shouldError) {
      throw new Error(mockResponse.errorMessage || `Mock error for endpoint: ${endpoint}`);
    }

    const delay = mockResponse.delay ?? this.defaultDelay;
    if (delay > 0) {
      await this.simulateDelay(delay);
    }

    return mockResponse.data;
  }

  protected async doInitialize(): Promise<void> {
    // Mock provider doesn't need initialization
    this.logger.info('MockDataProvider initialized');
  }

  protected async doDispose(): Promise<void> {
    // Clean up mock responses
    this.mockResponses.clear();
    this.logger.info('MockDataProvider disposed');
  }
}

export default MockDataProvider;