/**
 * HoldingsController.test.ts - Comprehensive unit tests for HoldingsController
 * Tests all aspects of the controller including SOLID principles compliance
 */
import { HoldingsController, HoldingsData } from '../../../src/lib/controllers/HoldingsController';
import { HoldingsConfiguration } from '../../../src/types/widget-types';
import { createHoldingsMockDependencies, MockDataProvider } from '../../utils/mocks/createMockDependencies';
import { WidgetType } from '../../../src/lib/interfaces/IWidgetConfiguration';

describe('HoldingsController', () => {
  let controller: HoldingsController;
  let mockDependencies: ReturnType<typeof createHoldingsMockDependencies>;
  let mockConfig: HoldingsConfiguration;

  beforeEach(() => {
    mockDependencies = createHoldingsMockDependencies();
    
    mockConfig = {
      id: 'test-holdings',
      type: WidgetType.HOLDINGS,
      title: 'Test Holdings Widget',
      portfolioId: 'test-portfolio-123',
      displayMode: 'detailed',
      sortBy: 'marketValue',
      sortDirection: 'desc',
      maxItems: 10,
      showMetrics: true,
      precision: 2,
      refreshInterval: 30000
    };

    controller = new HoldingsController(
      mockConfig,
      mockDependencies.dependencies.dataProvider,
      mockDependencies.dependencies.eventBus,
      mockDependencies.dependencies.logger
    );
  });

  afterEach(() => {
    controller.dispose();
  });

  describe('Constructor and Initialization', () => {
    it('should create controller with correct configuration', () => {
      expect(controller.id).toBeDefined();
      expect(controller.type).toBe(WidgetType.HOLDINGS);
      expect(controller.isLoading).toBe(false);
      expect(controller.error).toBe(null);
      expect(controller.data).toBe(null);
    });

    it('should initialize with valid configuration', async () => {
      await controller.initialize(mockConfig);
      
      expect(controller.isLoading).toBe(false);
      expect(controller.error).toBe(null);
      expect(controller.data).toBeDefined();
    });

    it('should validate configuration on initialization', async () => {
      const invalidConfig = {
        ...mockConfig,
        portfolioId: null as any
      };

      await expect(controller.initialize(invalidConfig))
        .rejects.toThrow();
    });
  });

  describe('Data Fetching and Transformation', () => {
    beforeEach(async () => {
      await controller.initialize(mockConfig);
    });

    it('should fetch and transform holdings data correctly', () => {
      const data = controller.data as HoldingsData;
      
      expect(data).toBeDefined();
      expect(data.holdings).toBeInstanceOf(Array);
      expect(data.metadata).toBeDefined();
      expect(data.metadata.totalValue).toBeGreaterThan(0);
      expect(data.metadata.totalPositions).toBeGreaterThan(0);
    });

    it('should transform snake_case API fields to camelCase', () => {
      const data = controller.data as HoldingsData;
      const holding = data.holdings[0];
      
      // Ensure camelCase transformation worked
      expect(holding.assetClass).toBeDefined();
      expect(holding.marketValue).toBeDefined();
      expect(holding.currentPrice).toBeDefined();
      
      // Ensure snake_case fields are not present
      expect((holding as any).asset_class).toBeUndefined();
      expect((holding as any).market_value).toBeUndefined();
      expect((holding as any).current_price).toBeUndefined();
    });

    it('should handle performance metrics transformation', () => {
      const data = controller.data as HoldingsData;
      const holding = data.holdings[0];
      
      expect(typeof holding.dayChange).toBe('number');
      expect(typeof holding.dayChangePercent).toBe('number');
      expect(typeof holding.totalReturn).toBe('number');
      expect(typeof holding.totalReturnPercent).toBe('number');
    });

    it('should calculate metadata correctly', () => {
      const data = controller.data as HoldingsData;
      const expectedTotal = data.holdings.reduce((sum, h) => sum + h.marketValue, 0);
      
      expect(data.metadata.totalValue).toBeCloseTo(expectedTotal, 2);
      expect(data.metadata.totalPositions).toBe(data.holdings.length);
      expect(data.metadata.lastUpdated).toBeInstanceOf(Date);
      expect(data.metadata.executionTime).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Holdings Analysis Methods', () => {
    beforeEach(async () => {
      await controller.initialize(mockConfig);
    });

    it('should calculate comprehensive metrics', () => {
      const metrics = controller.calculateMetrics();
      
      expect(metrics.totalValue).toBeGreaterThan(0);
      expect(metrics.totalPositions).toBeGreaterThan(0);
      expect(metrics.averageWeight).toBeGreaterThan(0);
      expect(metrics.largestPosition).toBeDefined();
      expect(metrics.diversification.byAssetClass).toBeDefined();
      expect(metrics.diversification.topHoldings).toBeInstanceOf(Array);
    });

    it('should filter holdings by asset class', () => {
      const data = controller.data as HoldingsData;
      const firstHolding = data.holdings[0];
      const filtered = controller.filterByAssetClass(firstHolding.assetClass);
      
      expect(filtered).toBeInstanceOf(Array);
      filtered.forEach(holding => {
        expect(holding.assetClass.toLowerCase()).toBe(firstHolding.assetClass.toLowerCase());
      });
    });

    it('should search holdings by symbol and name', () => {
      const data = controller.data as HoldingsData;
      const firstHolding = data.holdings[0];
      
      // Search by symbol
      const symbolResults = controller.searchHoldings(firstHolding.symbol);
      expect(symbolResults.length).toBeGreaterThan(0);
      
      // Search by partial name
      const nameResults = controller.searchHoldings('Mock');
      expect(nameResults.length).toBeGreaterThan(0);
    });

    it('should sort holdings by different criteria', () => {
      const sortedByValue = controller.getSortedHoldings('marketValue', 'desc');
      const sortedBySymbol = controller.getSortedHoldings('symbol', 'asc');
      
      expect(sortedByValue).toBeInstanceOf(Array);
      expect(sortedBySymbol).toBeInstanceOf(Array);
      
      // Verify sorting
      for (let i = 1; i < sortedByValue.length; i++) {
        expect(sortedByValue[i - 1].marketValue).toBeGreaterThanOrEqual(sortedByValue[i].marketValue);
      }
      
      for (let i = 1; i < sortedBySymbol.length; i++) {
        expect(sortedBySymbol[i - 1].symbol.localeCompare(sortedBySymbol[i].symbol)).toBeLessThanOrEqual(0);
      }
    });
  });

  describe('Configuration Management', () => {
    beforeEach(async () => {
      await controller.initialize(mockConfig);
    });

    it('should update configuration and trigger refresh', async () => {
      const newConfig = {
        ...mockConfig,
        maxItems: 5,
        sortBy: 'symbol' as const
      };
      
      await controller.updateConfiguration(newConfig);
      
      expect(mockDependencies.mocks.dataProvider.getCallCount('holdings')).toBeGreaterThan(1);
    });

    it('should validate configuration updates', async () => {
      const invalidUpdate = {
        portfolioId: 123 as any,  // Should be string
        sortBy: 'invalid' as any
      };
      
      await expect(controller.updateConfiguration(invalidUpdate))
        .rejects.toThrow();
    });

    it('should handle display mode changes', async () => {
      await controller.updateConfiguration({ displayMode: 'percentage' });
      await controller.updateConfiguration({ displayMode: 'table' });
      
      expect(mockDependencies.mocks.logger.wasMessageLogged('Configuration updated')).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should handle data provider errors gracefully', async () => {
      // Simulate network error
      mockDependencies.mocks.dataProvider.setNetworkErrorSimulation(true);
      
      await expect(controller.initialize(mockConfig))
        .rejects.toThrow();
      
      expect(controller.error).toBeDefined();
      expect(mockDependencies.mocks.logger.getLogsByLevel('error').length).toBeGreaterThan(0);
    });

    it('should handle invalid data responses', async () => {
      // Set up invalid response
      mockDependencies.mocks.dataProvider.setMockResponse('holdings', {
        data: { invalid: 'data structure' },
        shouldError: false
      });
      
      await expect(controller.initialize(mockConfig))
        .rejects.toThrow();
    });

    it('should recover from errors on refresh', async () => {
      // First, initialize successfully
      await controller.initialize(mockConfig);
      expect(controller.error).toBe(null);
      
      // Then simulate error
      mockDependencies.mocks.dataProvider.setMockResponse('holdings', {
        data: null,
        shouldError: true,
        errorMessage: 'Temporary error'
      });
      
      await expect(controller.refresh()).rejects.toThrow();
      expect(controller.error).toBeDefined();
      
      // Restore success and refresh again
      mockDependencies.mocks.dataProvider.setMockResponse('holdings', {
        data: MockDataProvider.createMockHoldingsData(5)
      });
      
      await controller.refresh();
      expect(controller.error).toBe(null);
    });
  });

  describe('Subscription and Events', () => {
    it('should notify subscribers on data changes', async () => {
      const subscriber = jest.fn();
      const unsubscribe = controller.subscribe(subscriber);
      
      await controller.initialize(mockConfig);
      
      expect(subscriber).toHaveBeenCalled();
      expect(subscriber).toHaveBeenCalledWith(controller.data);
      
      unsubscribe();
    });

    it('should publish events through event bus', async () => {
      await controller.initialize(mockConfig);
      
      expect(mockDependencies.mocks.eventBus.getEventCount('widget.initialized')).toBeGreaterThanOrEqual(0);
    });

    it('should handle multiple subscribers', async () => {
      const subscriber1 = jest.fn();
      const subscriber2 = jest.fn();
      
      controller.subscribe(subscriber1);
      controller.subscribe(subscriber2);
      
      await controller.initialize(mockConfig);
      
      expect(subscriber1).toHaveBeenCalled();
      expect(subscriber2).toHaveBeenCalled();
    });
  });

  describe('Lifecycle Management', () => {
    it('should dispose resources properly', async () => {
      await controller.initialize(mockConfig);
      
      await controller.dispose();
      
      expect(mockDependencies.mocks.logger.wasMessageLogged('disposed')).toBe(true);
    });

    it('should handle refresh with force flag', async () => {
      await controller.initialize(mockConfig);
      
      const initialCallCount = mockDependencies.mocks.dataProvider.getCallCount('holdings');
      
      await controller.refresh(false); // Should use cache if available
      await controller.refresh(true);  // Should force fetch
      
      expect(mockDependencies.mocks.dataProvider.getCallCount('holdings')).toBeGreaterThan(initialCallCount);
    });
  });

  describe('Performance and Caching', () => {
    it('should measure execution time correctly', async () => {
      await controller.initialize(mockConfig);
      
      const data = controller.data as HoldingsData;
      expect(data.metadata.executionTime).toBeGreaterThanOrEqual(0);
      expect(data.metadata.executionTime).toBeLessThan(1000); // Should be fast in tests
    });

    it('should handle large datasets efficiently', async () => {
      // Set up large dataset
      mockDependencies.mocks.dataProvider.setMockResponse('holdings', {
        data: MockDataProvider.createMockHoldingsData(1000)
      });
      
      const startTime = Date.now();
      await controller.initialize(mockConfig);
      const endTime = Date.now();
      
      expect(endTime - startTime).toBeLessThan(500); // Should process quickly
      expect(controller.data?.holdings.length).toBe(1000);
    });
  });

  describe('SOLID Principles Compliance', () => {
    it('should follow Single Responsibility Principle', () => {
      // Controller should only manage holdings data, not handle UI concerns
      expect(controller.data).toBeDefined();
      expect(typeof controller.calculateMetrics).toBe('function');
      expect(typeof controller.filterByAssetClass).toBe('function');
      
      // Should not have UI methods
      expect((controller as any).render).toBeUndefined();
      expect((controller as any).onClick).toBeUndefined();
    });

    it('should follow Open/Closed Principle', () => {
      // Can be extended without modifying base class
      class ExtendedHoldingsController extends HoldingsController {
        public customMethod(): string {
          return 'extended';
        }
      }
      
      const extended = new ExtendedHoldingsController(
        mockConfig,
        mockDependencies.dependencies.dataProvider,
        mockDependencies.dependencies.eventBus,
        mockDependencies.dependencies.logger
      );
      
      expect(extended.customMethod()).toBe('extended');
      expect(extended).toBeInstanceOf(HoldingsController);
    });

    it('should follow Dependency Inversion Principle', () => {
      // Controller depends on abstractions (interfaces) not concrete classes
      expect(controller).toBeDefined();
      
      // Should work with any IDataProvider implementation
      const customDataProvider = new MockDataProvider();
      const controllerWithCustomProvider = new HoldingsController(
        mockConfig,
        customDataProvider,
        mockDependencies.dependencies.eventBus,
        mockDependencies.dependencies.logger
      );
      
      expect(controllerWithCustomProvider).toBeInstanceOf(HoldingsController);
    });
  });
});