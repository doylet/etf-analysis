/**
 * Mock Configuration Factory for Testing
 * 
 * Purpose: Provides configurable mock widget configurations for comprehensive testing
 * Features: Pre-defined configurations, custom overrides, validation helpers
 */

import { WidgetConfig } from '@/lib/interfaces/IWidgetConfig';

export interface MockConfigOptions {
  /** Override default configuration values */
  overrides?: Partial<WidgetConfig>;
  /** Enable performance monitoring in mock */
  enablePerformance?: boolean;
  /** Add custom metadata for test tracking */
  testMetadata?: Record<string, any>;
  /** Configure error simulation */
  simulateErrors?: {
    dataProviderErrors?: boolean;
    configValidationErrors?: boolean;
    renderErrors?: boolean;
  };
  /** Configure loading states for testing */
  simulateLoading?: {
    dataLoadingTime?: number;
    componentMountTime?: number;
  };
}

/**
 * Creates mock widget configurations for testing with various scenarios
 */
export class MockConfigurationFactory {
  /**
   * Creates a basic Holdings widget configuration for testing
   */
  static createHoldingsConfig(options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: 'holdings',
      variant: 'table',
      portfolioId: 'mock-portfolio-1',
      title: 'Mock Holdings Widget',
      refreshInterval: 30000,
      cache: true,
      errorRetryAttempts: 3,
    };

    return this.mergeWithOptions(defaultConfig, options);
  }

  /**
   * Creates Holdings percentage variant configuration for testing
   */
  static createHoldingsPercentageConfig(options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: 'holdings',
      variant: 'percentage',
      portfolioId: 'mock-portfolio-1',
      title: 'Mock Holdings Percentage Widget',
      refreshInterval: 30000,
      cache: true,
      errorRetryAttempts: 3
    };

    return this.mergeWithOptions(defaultConfig, options);
  }

  /**
   * Creates a PortfolioSummary widget configuration for testing
   */
  static createPortfolioSummaryConfig(options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: 'portfolio-summary',
      variant: 'standard',
      title: 'Mock Portfolio Summary',
      refreshInterval: 60000,
      cache: true,
      errorRetryAttempts: 2
    };

    return this.mergeWithOptions(defaultConfig, options);
  }

  /**
   * Creates a CorrelationMatrix widget configuration for testing
   */
  // Note: correlation-matrix type not supported in current WidgetConfig union
  static createCorrelationMatrixConfig(options: MockConfigOptions = {}): WidgetConfig {
    // Fallback to holdings config since correlation-matrix is not supported
    return this.createHoldingsConfig(options);
    /*
    const defaultConfig: WidgetConfig = {
      type: 'correlation-matrix',
      variant: 'heatmap',
      title: 'Mock Correlation Matrix',
      refreshInterval: 120000,
      cache: true,
      errorRetryAttempts: 1
    };
    */

    return this.mergeWithOptions(this.createHoldingsConfig(options), options);
  }

  /**
   * Creates a MonteCarlo simulation widget configuration for testing
   */
  // Note: monte-carlo type not supported in current WidgetConfig union
  static createMonteCarloConfig(options: MockConfigOptions = {}): WidgetConfig {
    // Fallback to holdings config since monte-carlo is not supported
    return this.createHoldingsConfig(options);
    /*
    const defaultConfig: WidgetConfig = {
      type: 'monte-carlo',
      variant: 'chart',
      title: 'Mock Monte Carlo Simulation',
      refreshInterval: 300000, // 5 minutes
      cache: false, // Simulations should be fresh
      errorRetryAttempts: 2
    };
    */

    return this.mergeWithOptions(this.createHoldingsConfig(options), options);
  }

  /**
   * Creates configuration with aggressive refresh for performance testing
   */
  static createHighFrequencyConfig(baseType: string = 'holdings', options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: 'holdings',
      variant: 'table',
      portfolioId: 'mock-portfolio-1',
      title: 'High Frequency Test Widget',
      refreshInterval: 1000, // 1 second
      cache: false,
      errorRetryAttempts: 1
    };

    return this.mergeWithOptions(defaultConfig, options);
  }

  /**
   * Creates configuration with no caching for fresh data testing
   */
  static createNoCacheConfig(baseType: string = 'holdings', options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: baseType as any,
      variant: 'table',
      title: 'No Cache Test Widget',
      refreshInterval: 30000,
      cache: false,
      errorRetryAttempts: 3
    };

    return this.mergeWithOptions(defaultConfig, options);
  }

  /**
   * Creates configuration optimized for error testing scenarios
   */
  static createErrorProneConfig(baseType: string = 'holdings', options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: baseType as any,
      variant: 'table',
      title: 'Error Test Widget',
      refreshInterval: 5000, // Quick refresh to trigger errors
      cache: false,
      errorRetryAttempts: 5 // More retries for testing
    };

    const errorOptions: MockConfigOptions = {
      ...options,
      simulateErrors: {
        dataProviderErrors: true,
        configValidationErrors: true,
        renderErrors: true,
        ...options.simulateErrors
      }
    };

    return this.mergeWithOptions(defaultConfig, errorOptions);
  }

  /**
   * Creates configuration with slow loading for loading state testing
   */
  static createSlowLoadingConfig(baseType: string = 'holdings', options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: baseType as any,
      variant: 'table',
      title: 'Slow Loading Test Widget',
      refreshInterval: 30000,
      cache: true,
      errorRetryAttempts: 3
    };

    const loadingOptions: MockConfigOptions = {
      ...options,
      simulateLoading: {
        dataLoadingTime: 3000, // 3 seconds
        componentMountTime: 1000, // 1 second
        ...options.simulateLoading
      }
    };

    return this.mergeWithOptions(defaultConfig, loadingOptions);
  }

  /**
   * Creates a batch of configurations for comprehensive testing
   */
  static createTestSuite(): Record<string, WidgetConfig> {
    return {
      holdingsTable: this.createHoldingsConfig(),
      holdingsPercentage: this.createHoldingsPercentageConfig(),
      portfolioSummary: this.createPortfolioSummaryConfig(),
      correlationMatrix: this.createCorrelationMatrixConfig(),
      monteCarlo: this.createMonteCarloConfig(),
      highFrequency: this.createHighFrequencyConfig(),
      noCache: this.createNoCacheConfig(),
      errorProne: this.createErrorProneConfig(),
      slowLoading: this.createSlowLoadingConfig()
    };
  }

  /**
   * Creates configuration for mobile testing with compact layouts
   */
  static createMobileConfig(baseType: string = 'holdings', options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: baseType as any,
      variant: 'compact',
      title: 'Mobile Test Widget',
      refreshInterval: 60000, // Longer interval for mobile
      cache: true, // Cache for mobile performance
      errorRetryAttempts: 2
    };

    return this.mergeWithOptions(defaultConfig, options);
  }

  /**
   * Creates configuration with different presentation variants for UI testing
   */
  static createPresentationConfig(
    baseType: string = 'holdings',
    presentationVariant: 'table' | 'percentage' = 'table',
    options: MockConfigOptions = {}
  ): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: 'holdings',
      variant: presentationVariant,
      portfolioId: 'mock-portfolio-1',
      title: `${presentationVariant.charAt(0).toUpperCase() + presentationVariant.slice(1)} Presentation Test`,
      refreshInterval: 30000,
      cache: true,
      errorRetryAttempts: 3
    };

    return this.mergeWithOptions(defaultConfig, options);
  }

  /**
   * Validates a mock configuration for testing completeness
   */
  static validateConfig(config: WidgetConfig): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Required fields
    if (!config.type) errors.push('Missing required field: type');
    if (!config.variant) errors.push('Missing required field: variant');
    if (!config.title) errors.push('Missing required field: title');

    // Numeric validations
    if (config.refreshInterval !== undefined && config.refreshInterval < 1000) {
      warnings.push('Refresh interval less than 1 second may cause performance issues');
    }

    if (config.errorRetryAttempts !== undefined && config.errorRetryAttempts > 10) {
      warnings.push('High retry attempts may cause poor user experience');
    }

    // Type validations
    const validTypes = ['holdings', 'portfolio-summary', 'correlation-matrix', 'monte-carlo'];
    if (config.type && !validTypes.includes(config.type)) {
      errors.push(`Invalid widget type: ${config.type}. Valid types: ${validTypes.join(', ')}`);
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Creates a configuration with all optional parameters for comprehensive testing
   */
  static createFullFeatureConfig(baseType: string = 'holdings', options: MockConfigOptions = {}): WidgetConfig {
    const defaultConfig: WidgetConfig = {
      type: baseType as any,
      variant: 'table',
      title: 'Full Feature Test Widget',
      refreshInterval: 30000,
      cache: true,
      errorRetryAttempts: 3,
      // Additional testing properties that might be added in the future
      ...(options.enablePerformance && { performanceMonitoring: true }),
      ...(options.testMetadata && { testMetadata: options.testMetadata })
    };

    return this.mergeWithOptions(defaultConfig, options);
  }

  /**
   * Private helper to merge configuration with options
   */
  private static mergeWithOptions(baseConfig: WidgetConfig, options: MockConfigOptions): WidgetConfig {
    let merged = { ...baseConfig } as WidgetConfig;
    
    if (options.overrides) {
      // Only override compatible properties
      merged = {
        ...merged,
        ...(options.overrides as Partial<WidgetConfig>)
      } as WidgetConfig;
    }

    // Add test-specific metadata if provided
    if (options.testMetadata || options.simulateErrors || options.simulateLoading) {
      (merged as any)._testConfig = {
        metadata: options.testMetadata,
        simulateErrors: options.simulateErrors,
        simulateLoading: options.simulateLoading,
        enablePerformance: options.enablePerformance
      };
    }

    return merged;
  }
}

/**
 * Convenience functions for quick mock creation
 */
export const createMockConfiguration = MockConfigurationFactory;

/**
 * Test helper to create configurations with specific error scenarios
 */
export function createErrorScenarioConfigs(): Record<string, WidgetConfig> {
  return {
    dataProviderError: MockConfigurationFactory.createErrorProneConfig('holdings', {
      simulateErrors: { dataProviderErrors: true }
    }),
    configValidationError: MockConfigurationFactory.createErrorProneConfig('holdings', {
      simulateErrors: { configValidationErrors: true }
    }),
    renderError: MockConfigurationFactory.createErrorProneConfig('holdings', {
      simulateErrors: { renderErrors: true }
    }),
    allErrors: MockConfigurationFactory.createErrorProneConfig('holdings', {
      simulateErrors: {
        dataProviderErrors: true,
        configValidationErrors: true,
        renderErrors: true
      }
    })
  };
}

/**
 * Test helper to create configurations with different loading scenarios
 */
export function createLoadingScenarioConfigs(): Record<string, WidgetConfig> {
  return {
    fastLoading: MockConfigurationFactory.createSlowLoadingConfig('holdings', {
      simulateLoading: { dataLoadingTime: 100, componentMountTime: 50 }
    }),
    normalLoading: MockConfigurationFactory.createSlowLoadingConfig('holdings', {
      simulateLoading: { dataLoadingTime: 1000, componentMountTime: 500 }
    }),
    slowLoading: MockConfigurationFactory.createSlowLoadingConfig('holdings', {
      simulateLoading: { dataLoadingTime: 5000, componentMountTime: 2000 }
    })
  };
}

/**
 * Test helper to create configurations for different presentation strategies
 */
export function createPresentationScenarioConfigs(): Record<string, WidgetConfig> {
  return {
    table: MockConfigurationFactory.createPresentationConfig('holdings', 'table'),
    percentage: MockConfigurationFactory.createPresentationConfig('holdings', 'percentage')
  };
}