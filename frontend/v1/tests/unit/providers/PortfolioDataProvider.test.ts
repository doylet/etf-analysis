/**
 * PortfolioDataProvider.test.ts - Comprehensive unit tests for PortfolioDataProvider
 * Tests all aspects of the data provider including API interactions and data transformations
 */
import { PortfolioDataProvider, PortfolioHoldingsData, PortfolioSummaryData } from '../../../src/lib/providers/PortfolioDataProvider';
import { DataProviderOptions } from '../../../src/lib/interfaces/IDataProvider';

// Mock fetch for testing
global.fetch = jest.fn();
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

describe('PortfolioDataProvider', () => {
  let provider: PortfolioDataProvider;
  let mockOptions: DataProviderOptions;

  beforeEach(() => {
    mockOptions = {
      baseUrl: 'http://test-api.com',
      cacheTimeout: 30000,
      name: 'test-portfolio-provider'
    };

    provider = new PortfolioDataProvider(mockOptions);
    
    // Reset fetch mock
    mockFetch.mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Constructor and Configuration', () => {
    it('should initialize with provided options', () => {
      expect(provider.name).toBe('test-portfolio-provider');
      expect(provider.isAvailable).toBe(true);
    });

    it('should use default base URL if not provided', () => {
      const defaultProvider = new PortfolioDataProvider({});
      // Base URL is private, but we can test through API calls
      expect(defaultProvider).toBeDefined();
    });

    it('should handle missing options gracefully', () => {
      const minimalProvider = new PortfolioDataProvider({});
      expect(minimalProvider.isAvailable).toBe(true);
    });
  });

  describe('API Request Handling', () => {
    beforeEach(() => {
      // Mock successful API response
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          widget_name: 'holdings-breakdown',
          success: true,
          data: {
            holdings: [
              {
                symbol: 'AAPL',
                name: 'Apple Inc.',
                asset_class: 'Stock',
                quantity: 100,
                weight: 0.15,
                market_value: 15000,
                current_price: 150,
                day_change: 2.5,
                day_change_percent: 1.8,
                total_return: 500,
                total_return_percent: 3.4
              }
            ],
            summary: {
              total_positions: 1,
              total_value: 15000,
              last_updated: '2024-12-09T10:00:00Z'
            }
          },
          metadata: {
            execution_time: '125ms',
            parameters: { portfolio_id: 'test-123' },
            widget_description: 'Portfolio holdings breakdown',
            cache_hit: false
          }
        })
      } as any);
    });

    it('should make correct API requests', async () => {
      const data = await provider.fetchData('holdings', { 
        portfolio_id: 'test-123',
        include_metadata: true 
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://test-api.com/api/v1/widgets/holdings-breakdown?portfolio_id=test-123&include_metadata=true',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          })
        })
      );

      expect(data).toBeDefined();
    });

    it('should handle query parameters correctly', async () => {
      await provider.fetchData('holdings', { 
        portfolio_id: 'test-123',
        format: 'detailed',
        include_metadata: true
      });

      const expectedUrl = 'http://test-api.com/api/v1/widgets/holdings-breakdown?portfolio_id=test-123&format=detailed&include_metadata=true';
      expect(mockFetch).toHaveBeenCalledWith(
        expectedUrl,
        expect.any(Object)
      );
    });

    it('should handle authentication headers when provided', async () => {
      await provider.fetchData('holdings', { 
        portfolio_id: 'test-123',
        auth_token: 'bearer-token-123'
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer bearer-token-123'
          })
        })
      );
    });

    it('should handle request timeout', async () => {
      // Mock a long-running request that should timeout
      mockFetch.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ ok: true } as any), 35000))
      );

      await expect(provider.fetchData('holdings', { portfolio_id: 'test-123' }))
        .rejects.toThrow();
    });
  });

  describe('Data Transformation', () => {
    it('should transform holdings data correctly', async () => {
      const mockApiResponse = {
        widget_name: 'holdings-breakdown',
        success: true,
        data: {
          holdings: [
            {
              symbol: 'AAPL',
              name: 'Apple Inc.',
              asset_class: 'Stock',
              quantity: 100,
              weight: 0.15,
              market_value: 15000,
              current_price: 150.50,
              day_change: 2.5,
              day_change_percent: 1.8
            },
            {
              symbol: 'GOOGL',
              name: 'Alphabet Inc.',
              asset_class: 'Stock',
              quantity: 50,
              weight: 0.12,
              market_value: 12000,
              current_price: 240.00
            }
          ],
          summary: {
            total_positions: 2,
            total_value: 27000,
            last_updated: '2024-12-09T10:00:00Z'
          }
        },
        metadata: { execution_time: '125ms' }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockApiResponse)
      } as any);

      const data = await provider.fetchData('holdings') as PortfolioHoldingsData;

      expect(data.holdings).toHaveLength(2);
      
      // Check first holding transformation
      const firstHolding = data.holdings[0];
      expect(firstHolding.symbol).toBe('AAPL');
      expect(firstHolding.name).toBe('Apple Inc.');
      expect(firstHolding.asset_class).toBe('Stock');
      expect(firstHolding.quantity).toBe(100);
      expect(firstHolding.weight).toBe(0.15);
      expect(firstHolding.market_value).toBe(15000);
      expect(firstHolding.current_price).toBe(150.50);
      expect(firstHolding.day_change).toBe(2.5);
      expect(firstHolding.day_change_percent).toBe(1.8);
      
      // Check second holding has defaults for missing fields
      const secondHolding = data.holdings[1];
      expect(secondHolding.day_change).toBe(0);
      expect(secondHolding.day_change_percent).toBe(0);
      expect(secondHolding.total_return).toBe(0);
      expect(secondHolding.total_return_percent).toBe(0);

      // Check summary transformation
      expect(data.summary).toBeDefined();
      expect(data.summary!.total_positions).toBe(2);
      expect(data.summary!.total_value).toBe(27000);
      expect(data.summary!.last_updated).toBe('2024-12-09T10:00:00Z');
    });

    it('should handle malformed holdings data', async () => {
      const malformedResponse = {
        widget_name: 'holdings-breakdown',
        success: true,
        data: {
          holdings: null // Invalid - should be array
        },
        metadata: { execution_time: '125ms' }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(malformedResponse)
      } as any);

      await expect(provider.fetchData('holdings'))
        .rejects.toThrow('Invalid holdings data structure');
    });

    it('should transform summary data correctly', async () => {
      const summaryResponse = {
        widget_name: 'portfolio-summary',
        success: true,
        data: {
          total_value: 125000.50,
          total_return: 8750.25,
          total_return_percent: 7.5,
          day_change: -234.50,
          day_change_percent: -0.18,
          positions: 12,
          allocated_cash: 5000.00,
          last_updated: '2024-12-09T10:00:00Z'
        },
        metadata: { execution_time: '75ms' }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(summaryResponse)
      } as any);

      const data = await provider.fetchData('summary') as PortfolioSummaryData;

      expect(data.total_value).toBe(125000.50);
      expect(data.total_return).toBe(8750.25);
      expect(data.total_return_percent).toBe(7.5);
      expect(data.day_change).toBe(-234.50);
      expect(data.day_change_percent).toBe(-0.18);
      expect(data.positions).toBe(12);
      expect(data.allocated_cash).toBe(5000.00);
      expect(data.last_updated).toBe('2024-12-09T10:00:00Z');
    });

    it('should handle type coercion for numeric fields', async () => {
      const responseWithStrings = {
        widget_name: 'holdings-breakdown',
        success: true,
        data: {
          holdings: [
            {
              symbol: 'AAPL',
              name: 'Apple Inc.',
              asset_class: 'Stock',
              quantity: '100',     // String
              weight: '0.15',      // String
              market_value: '15000', // String
              current_price: '150.50' // String
            }
          ]
        },
        metadata: { execution_time: '125ms' }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(responseWithStrings)
      } as any);

      const data = await provider.fetchData('holdings') as PortfolioHoldingsData;
      const holding = data.holdings[0];

      // Should convert strings to numbers
      expect(typeof holding.quantity).toBe('number');
      expect(typeof holding.weight).toBe('number');
      expect(typeof holding.market_value).toBe('number');
      expect(typeof holding.current_price).toBe('number');
      
      expect(holding.quantity).toBe(100);
      expect(holding.weight).toBe(0.15);
    });
  });

  describe('Specific Fetch Methods', () => {
    beforeEach(() => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          widget_name: 'test',
          success: true,
          data: { test: 'data' },
          metadata: { execution_time: '100ms' }
        })
      } as any);
    });

    it('should call fetchHoldings with correct parameters', async () => {
      await provider.fetchHoldings('portfolio-123');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/widgets/holdings-breakdown'),
        expect.any(Object)
      );
    });

    it('should call fetchPortfolioSummary with correct parameters', async () => {
      await provider.fetchPortfolioSummary('portfolio-123');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/widgets/portfolio-summary'),
        expect.any(Object)
      );
    });

    it('should call fetchPerformanceMetrics with correct parameters', async () => {
      await provider.fetchPerformanceMetrics('portfolio-123', '3M');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/widgets/performance-metrics'),
        expect.any(Object)
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle HTTP errors correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      } as any);

      await expect(provider.fetchData('holdings', { portfolio_id: 'invalid' }))
        .rejects.toThrow('API request failed: 404 Not Found');
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(provider.fetchData('holdings'))
        .rejects.toThrow('Network error');
    });

    it('should handle API response errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          widget_name: 'holdings-breakdown',
          success: false,
          data: null,
          error: {
            code: 'PORTFOLIO_NOT_FOUND',
            message: 'Portfolio not found'
          },
          metadata: { execution_time: '25ms' }
        })
      } as any);

      await expect(provider.fetchData('holdings'))
        .rejects.toThrow('API call unsuccessful: Portfolio not found');
    });

    it('should handle invalid JSON responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.reject(new Error('Invalid JSON'))
      } as any);

      await expect(provider.fetchData('holdings'))
        .rejects.toThrow('Invalid JSON');
    });

    it('should handle missing required response structure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          // Missing required fields
          some_field: 'value'
        })
      } as any);

      await expect(provider.fetchData('holdings'))
        .rejects.toThrow('Invalid API response structure for holdings');
    });
  });

  describe('Caching Behavior', () => {
    beforeEach(() => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          widget_name: 'holdings-breakdown',
          success: true,
          data: { holdings: [] },
          metadata: { execution_time: '100ms' }
        })
      } as any);
    });

    it('should cache responses correctly', async () => {
      const params = { portfolio_id: 'test-123' };
      
      // First call
      await provider.fetchData('holdings', params);
      expect(mockFetch).toHaveBeenCalledTimes(1);
      
      // Second call should use cache
      await provider.fetchData('holdings', params);
      expect(mockFetch).toHaveBeenCalledTimes(1); // Still only 1 call
    });

    it('should generate different cache keys for different parameters', async () => {
      await provider.fetchData('holdings', { portfolio_id: 'test-123' });
      await provider.fetchData('holdings', { portfolio_id: 'test-456' });
      
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('should respect cache timeout', async (done) => {
      // Create provider with short cache timeout
      const shortCacheProvider = new PortfolioDataProvider({
        ...mockOptions,
        cacheTimeout: 50 // 50ms
      });

      const params = { portfolio_id: 'test-123' };
      
      await shortCacheProvider.fetchData('holdings', params);
      expect(mockFetch).toHaveBeenCalledTimes(1);
      
      // Wait for cache to expire
      setTimeout(async () => {
        await shortCacheProvider.fetchData('holdings', params);
        expect(mockFetch).toHaveBeenCalledTimes(2);
        done();
      }, 100);
    }, 200);
  });

  describe('URL Building and Parameter Handling', () => {
    it('should build correct URLs for different endpoints', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          widget_name: 'test',
          success: true,
          data: {},
          metadata: { execution_time: '100ms' }
        })
      } as any);

      await provider.fetchData('holdings');
      expect(mockFetch).toHaveBeenLastCalledWith(
        'http://test-api.com/api/v1/widgets/holdings-breakdown',
        expect.any(Object)
      );

      await provider.fetchData('summary');
      expect(mockFetch).toHaveBeenLastCalledWith(
        'http://test-api.com/api/v1/widgets/portfolio-summary',
        expect.any(Object)
      );

      await provider.fetchData('performance');
      expect(mockFetch).toHaveBeenLastCalledWith(
        'http://test-api.com/api/v1/widgets/performance-metrics',
        expect.any(Object)
      );
    });

    it('should handle unknown endpoints', async () => {
      await expect(provider.fetchData('unknown-endpoint'))
        .rejects.toThrow('Unknown endpoint: unknown-endpoint');
    });

    it('should sanitize parameters correctly', async () => {
      const params = {
        portfolio_id: 'test-123',
        include_metadata: true,
        null_value: null,
        undefined_value: undefined,
        empty_string: '',
        zero_value: 0
      };

      await provider.fetchData('holdings', params);

      const lastCall = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
      const url = lastCall[0] as string;
      
      // Should include defined values
      expect(url).toContain('portfolio_id=test-123');
      expect(url).toContain('include_metadata=true');
      expect(url).toContain('empty_string=');
      expect(url).toContain('zero_value=0');
      
      // Should not include null/undefined values
      expect(url).not.toContain('null_value');
      expect(url).not.toContain('undefined_value');
    });
  });
});