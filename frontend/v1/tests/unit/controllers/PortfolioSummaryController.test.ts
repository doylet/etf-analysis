/**
 * Unit Tests: PortfolioSummaryController
 * 
 * Purpose: Comprehensive testing of PortfolioSummaryController following SOLID principles
 * Test Coverage: Data transformation, error handling, configuration management, dependency injection
 */

import { PortfolioSummaryController, PortfolioSummaryData, PortfolioSummaryConfig } from '../../../src/lib/controllers/PortfolioSummaryController';
import { MarketDataProvider } from '../../../src/lib/providers/MarketDataProvider';
import { createMockDependencies } from '../../utils/mocks/createMockDependencies';
import { MockDataProvider } from '../../utils/mocks/MockDataProvider';

describe('PortfolioSummaryController', () => {
  let controller: PortfolioSummaryController;
  let mockDataProvider: MockDataProvider<PortfolioSummaryData>;
  let mockDependencies: ReturnType<typeof createMockDependencies>;
  let defaultConfig: PortfolioSummaryConfig;

  const mockPortfolioData: PortfolioSummaryData = {
    total_value: 125000.50,
    total_return: 15000.75,
    total_return_percent: 13.65,
    day_change: 1250.30,
    day_change_percent: 1.01,
    positions: 12,
    allocated_cash: 5000.00,
    last_updated: '2025-12-09T10:30:00Z',
    market_status: 'open'
  };

  beforeEach(() => {
    defaultConfig = {
      type: 'portfolio-summary',
      variant: 'standard',
      title: 'Test Portfolio Summary',
      refreshInterval: 30000,
      cache: true,
      errorRetryAttempts: 3,
      showPercentages: true,
      showCashAllocation: true,
      showMarketStatus: true,
      currencyFormat: 'USD'
    };

    mockDependencies = createMockDependencies();
    mockDataProvider = new MockDataProvider<PortfolioSummaryData>();
    mockDataProvider.setMockData(mockPortfolioData);

    controller = new PortfolioSummaryController(
      mockDataProvider,
      defaultConfig,
      mockDependencies.logger,
      mockDependencies.eventBus,
      mockDependencies.cacheService,
      mockDependencies.configService
    );
  });

  afterEach(() => {
    controller?.dispose();
  });

  describe('SOLID Principles Compliance', () => {
    describe('Single Responsibility Principle', () => {
      it('should only handle portfolio summary presentation logic', () => {
        const controller = new PortfolioSummaryController(
          mockDataProvider,
          defaultConfig,
          mockDependencies.logger
        );

        expect(controller).toBeInstanceOf(PortfolioSummaryController);
        expect(typeof controller.getConfiguration).toBe('function');
        expect(typeof controller.updateConfiguration).toBe('function');
        expect(typeof controller.refreshData).toBe('function');
        
        // Should not have methods for other widget types
        expect((controller as any).getHoldingsData).toBeUndefined();
        expect((controller as any).runMonteCarlo).toBeUndefined();
      });

      it('should delegate data fetching to data provider', async () => {
        await controller.initialize();
        
        expect(mockDataProvider.getCallLog()).toContain('getData');
        expect(mockDataProvider.getCallCount('getData')).toBeGreaterThan(0);
      });
    });

    describe('Open/Closed Principle', () => {
      it('should be open for extension through configuration', () => {
        const extendedConfig = {
          ...defaultConfig,
          showPercentages: false,
          currencyFormat: 'EUR' as const
        };

        const extendedController = new PortfolioSummaryController(
          mockDataProvider,
          extendedConfig,
          mockDependencies.logger
        );

        const config = extendedController.getConfiguration();
        expect(config.showPercentages).toBe(false);
        expect(config.currencyFormat).toBe('EUR');
      });

      it('should be closed for modification of core behavior', async () => {
        await controller.initialize();
        const viewModel = controller.getViewModel();

        // Core data transformation should remain consistent
        expect(viewModel?.totalValue).toMatch(/^\$[\d,]+\.\d{2}$/);
        expect(viewModel?.totalReturnPercent).toMatch(/^[+-]?\d+\.\d{2}%$/);
      });
    });

    describe('Liskov Substitution Principle', () => {
      it('should be substitutable for BaseWidgetController', async () => {
        const baseController = controller as any; // Cast to base interface
        
        await baseController.initialize();
        expect(baseController.getViewModel()).toBeDefined();
        expect(typeof baseController.refreshData).toBe('function');
        expect(typeof baseController.dispose).toBe('function');
      });

      it('should maintain base controller contract', async () => {
        await controller.initialize();
        
        const viewModel = controller.getViewModel();
        expect(viewModel).toHaveProperty('refreshData');
        expect(typeof viewModel?.refreshData).toBe('function');
      });
    });

    describe('Interface Segregation Principle', () => {
      it('should not force clients to depend on unused interfaces', () => {
        // Can be created with minimal dependencies
        const minimalController = new PortfolioSummaryController(
          mockDataProvider,
          defaultConfig
        );
        
        expect(minimalController).toBeInstanceOf(PortfolioSummaryController);
        minimalController.dispose();
      });

      it('should work with optional service dependencies', async () => {
        const controllerWithoutCache = new PortfolioSummaryController(
          mockDataProvider,
          defaultConfig,
          mockDependencies.logger,
          mockDependencies.eventBus,
          undefined, // No cache service
          mockDependencies.configService
        );

        await controllerWithoutCache.initialize();
        expect(controllerWithoutCache.getViewModel()).toBeDefined();
        controllerWithoutCache.dispose();
      });
    });

    describe('Dependency Inversion Principle', () => {
      it('should depend on abstractions not concretions', () => {
        // Uses IDataProvider interface, not concrete MarketDataProvider
        const mockProvider = new MockDataProvider<PortfolioSummaryData>();
        mockProvider.setMockData(mockPortfolioData);

        const testController = new PortfolioSummaryController(
          mockProvider,
          defaultConfig,
          mockDependencies.logger
        );

        expect(testController).toBeInstanceOf(PortfolioSummaryController);
        testController.dispose();
      });

      it('should inject dependencies through constructor', () => {
        const customLogger = mockDependencies.logger;
        const customEventBus = mockDependencies.eventBus;

        const testController = new PortfolioSummaryController(
          mockDataProvider,
          defaultConfig,
          customLogger,
          customEventBus
        );

        expect(testController).toBeInstanceOf(PortfolioSummaryController);
        testController.dispose();
      });
    });
  });

  describe('Data Transformation', () => {
    beforeEach(async () => {
      await controller.initialize();
    });

    it('should transform raw data to formatted view model', () => {
      const viewModel = controller.getViewModel();

      expect(viewModel).toBeDefined();
      expect(viewModel?.totalValue).toBe('$125,000.50');
      expect(viewModel?.totalReturn).toBe('$15,000.75');
      expect(viewModel?.totalReturnPercent).toBe('+13.65%');
      expect(viewModel?.dayChange).toBe('$1,250.30');
      expect(viewModel?.dayChangePercent).toBe('+1.01%');
      expect(viewModel?.positionsCount).toBe('12');
      expect(viewModel?.allocatedCash).toBe('$5,000.00');
    });

    it('should handle negative values correctly', async () => {
      const negativeData: PortfolioSummaryData = {
        ...mockPortfolioData,
        total_return: -2500.00,
        total_return_percent: -2.15,
        day_change: -750.50,
        day_change_percent: -0.65
      };

      mockDataProvider.setMockData(negativeData);
      await controller.refreshData();
      
      const viewModel = controller.getViewModel();
      expect(viewModel?.totalReturn).toBe('-$2,500.00');
      expect(viewModel?.totalReturnPercent).toBe('-2.15%');
      expect(viewModel?.dayChange).toBe('-$750.50');
      expect(viewModel?.dayChangePercent).toBe('-0.65%');
      expect(viewModel?.totalReturnTrend).toBe('negative');
      expect(viewModel?.dayChangeTrend).toBe('negative');
    });

    it('should handle zero values correctly', async () => {
      const zeroData: PortfolioSummaryData = {
        ...mockPortfolioData,
        total_return: 0,
        total_return_percent: 0,
        day_change: 0,
        day_change_percent: 0
      };

      mockDataProvider.setMockData(zeroData);
      await controller.refreshData();
      
      const viewModel = controller.getViewModel();
      expect(viewModel?.totalReturnTrend).toBe('neutral');
      expect(viewModel?.dayChangeTrend).toBe('neutral');
      expect(viewModel?.totalReturnPercent).toBe('+0.00%');
    });

    it('should format currency based on configuration', async () => {
      const eurConfig = { ...defaultConfig, currencyFormat: 'EUR' as const };
      const eurController = new PortfolioSummaryController(
        mockDataProvider,
        eurConfig,
        mockDependencies.logger
      );

      await eurController.initialize();
      const viewModel = eurController.getViewModel();

      expect(viewModel?.totalValue).toMatch(/€[\d,]+\.\d{2}/);
      eurController.dispose();
    });

    it('should format timestamps correctly', () => {
      const viewModel = controller.getViewModel();
      expect(viewModel?.lastUpdated).toBeDefined();
      expect(viewModel?.lastUpdated).not.toBe('Unknown');
      expect(viewModel?.lastUpdated).toMatch(/\w{3} \d{1,2}, \d{1,2}:\d{2} [AP]M/);
    });

    it('should format market status correctly', () => {
      const viewModel = controller.getViewModel();
      expect(viewModel?.marketStatus).toBe('Market Open');
    });
  });

  describe('Configuration Management', () => {
    it('should return current configuration', () => {
      const config = controller.getConfiguration();
      expect(config).toEqual(defaultConfig);
    });

    it('should update configuration and refresh if needed', async () => {
      await controller.initialize();
      
      const updates = {
        showPercentages: false,
        refreshInterval: 60000
      };

      controller.updateConfiguration(updates);
      
      const updatedConfig = controller.getConfiguration();
      expect(updatedConfig.showPercentages).toBe(false);
      expect(updatedConfig.refreshInterval).toBe(60000);
    });

    it('should emit configuration change event', async () => {
      await controller.initialize();
      
      const updates = { showPercentages: false };
      controller.updateConfiguration(updates);
      
      expect(mockDependencies.eventBus.emit).toHaveBeenCalledWith(
        'portfolio-summary-config-updated',
        expect.objectContaining({
          newConfig: expect.objectContaining(updates)
        })
      );
    });

    it('should validate configuration correctly', () => {
      const validConfig = {
        type: 'portfolio-summary' as const,
        variant: 'standard' as const,
        title: 'Test',
        refreshInterval: 30000,
        cache: true,
        errorRetryAttempts: 3
      };

      expect(PortfolioSummaryController.validateConfiguration(validConfig)).toBe(true);

      const invalidConfig = {
        type: 'invalid-type',
        variant: 'standard'
      };

      expect(PortfolioSummaryController.validateConfiguration(invalidConfig)).toBe(false);
    });
  });

  describe('User Interactions', () => {
    beforeEach(async () => {
      await controller.initialize();
    });

    it('should toggle percentage view', () => {
      let viewModel = controller.getViewModel();
      const initialShowPercentages = viewModel?.showPercentages;

      controller.togglePercentageView();
      viewModel = controller.getViewModel();
      
      expect(viewModel?.showPercentages).toBe(!initialShowPercentages);
    });

    it('should refresh data on user request', async () => {
      const initialCallCount = mockDataProvider.getCallCount('getData');
      
      const viewModel = controller.getViewModel();
      viewModel?.refreshData();
      
      await new Promise(resolve => setTimeout(resolve, 10));
      expect(mockDataProvider.getCallCount('getData')).toBeGreaterThan(initialCallCount);
    });

    it('should provide action functions in view model', () => {
      const viewModel = controller.getViewModel();
      
      expect(typeof viewModel?.refreshData).toBe('function');
      expect(typeof viewModel?.togglePercentageView).toBe('function');
    });
  });

  describe('Error Handling', () => {
    it('should handle data provider errors gracefully', async () => {
      mockDataProvider.setErrorMode(true, new Error('API Error'));
      
      await expect(controller.initialize()).rejects.toThrow('API Error');
    });

    it('should emit error events', async () => {
      mockDataProvider.setErrorMode(true, new Error('Test Error'));
      
      try {
        await controller.initialize();
      } catch (error) {
        // Expected error
      }
      
      expect(mockDependencies.eventBus.emit).toHaveBeenCalledWith(
        'portfolio-summary-error',
        expect.objectContaining({
          error: 'Test Error'
        })
      );
    });

    it('should handle invalid data gracefully', async () => {
      const invalidData = {
        ...mockPortfolioData,
        total_value: null,
        total_return: undefined,
        positions: NaN
      } as any;

      mockDataProvider.setMockData(invalidData);
      await controller.initialize();
      
      const viewModel = controller.getViewModel();
      expect(viewModel?.totalValue).toBe('$0.00');
      expect(viewModel?.totalReturn).toBe('$0.00');
      expect(viewModel?.positionsCount).toBe('0');
    });
  });

  describe('Logging', () => {
    it('should log initialization', () => {
      expect(mockDependencies.logger.info).toHaveBeenCalledWith(
        'PortfolioSummaryController initialized',
        expect.objectContaining({
          variant: 'standard'
        })
      );
    });

    it('should log data loading events', async () => {
      await controller.initialize();
      
      expect(mockDependencies.logger.info).toHaveBeenCalledWith(
        'Portfolio summary data loaded successfully',
        expect.objectContaining({
          totalValue: 125000.50,
          positions: 12
        })
      );
    });

    it('should log configuration changes', () => {
      const updates = { showPercentages: false };
      controller.updateConfiguration(updates);
      
      expect(mockDependencies.logger.info).toHaveBeenCalledWith(
        'Portfolio summary configuration updated',
        expect.objectContaining({
          changes: updates
        })
      );
    });
  });

  describe('Event Bus Integration', () => {
    beforeEach(async () => {
      await controller.initialize();
    });

    it('should emit data loaded events', () => {
      expect(mockDependencies.eventBus.emit).toHaveBeenCalledWith(
        'portfolio-summary-data-loaded',
        expect.objectContaining({
          data: expect.objectContaining({
            total_value: 125000.50
          })
        })
      );
    });

    it('should include widget ID in events', () => {
      expect(mockDependencies.eventBus.emit).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          widgetId: expect.any(String)
        })
      );
    });
  });

  describe('Lifecycle Management', () => {
    it('should initialize successfully', async () => {
      await expect(controller.initialize()).resolves.toBeUndefined();
      expect(controller.getViewModel()).toBeDefined();
    });

    it('should dispose resources properly', () => {
      controller.dispose();
      expect(mockDependencies.logger.info).toHaveBeenCalledWith(
        'Disposing PortfolioSummaryController',
        expect.any(Object)
      );
    });

    it('should handle multiple disposal calls', () => {
      controller.dispose();
      expect(() => controller.dispose()).not.toThrow();
    });
  });

  describe('Static Methods', () => {
    it('should return correct type identifier', () => {
      expect(PortfolioSummaryController.getType()).toBe('portfolio-summary');
    });
  });

  describe('Performance Characteristics', () => {
    it('should complete initialization within reasonable time', async () => {
      const startTime = Date.now();
      await controller.initialize();
      const endTime = Date.now();
      
      expect(endTime - startTime).toBeLessThan(100); // Should be very fast with mock data
    });

    it('should not create new view model objects unnecessarily', async () => {
      await controller.initialize();
      
      const viewModel1 = controller.getViewModel();
      const viewModel2 = controller.getViewModel();
      
      // Should return same object reference when data hasn't changed
      expect(viewModel1).toBe(viewModel2);
    });
  });
});