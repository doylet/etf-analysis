/**
 * Widget Factory - Main factory implementation for creating widgets
 * Implements Abstract Factory Pattern with dependency injection
 */
import { 
  IWidgetFactory, 
  WidgetDependencies, 
  WidgetControllerFactory,
  ValidationResult,
  ValidationError
} from '../interfaces/IWidgetFactory';
import { IWidgetController } from '../interfaces/IWidgetController';
import { IDataProvider, DataProviderConfig } from '../interfaces/IDataProvider';
import { WidgetType } from '../interfaces/IWidgetConfiguration';
import { HoldingsController, HoldingsData } from '../controllers/HoldingsController';
import { HoldingsConfiguration } from '../../types/widget-types';
import { PortfolioDataProvider } from '../providers/PortfolioDataProvider';
import { PortfolioSummaryController, PortfolioSummaryData } from '../controllers/PortfolioSummaryController';
import { MarketDataProvider } from '../providers/MarketDataProvider';

export class WidgetFactory implements IWidgetFactory {
  private controllerFactories = new Map<WidgetType, WidgetControllerFactory<any, any>>();
  private dataProviderFactories = new Map<WidgetType, (config: DataProviderConfig) => IDataProvider<any, any>>();

  public createController<TData, TConfig>(
    type: WidgetType,
    config: TConfig,
    dependencies: WidgetDependencies
  ): IWidgetController<TData, TConfig> {
    const factory = this.controllerFactories.get(type);
    if (!factory) {
      throw new Error(`No controller factory registered for widget type: ${type}`);
    }

    return factory(config, dependencies);
  }

  public createDataProvider<TData, TQuery>(
    type: WidgetType,
    config: DataProviderConfig
  ): IDataProvider<TData, TQuery> {
    const factory = this.dataProviderFactories.get(type);
    if (!factory) {
      throw new Error(`No data provider factory registered for widget type: ${type}`);
    }

    return factory(config);
  }

  public createDefaultConfiguration<TConfig>(
    type: WidgetType,
    overrides?: Partial<TConfig>
  ): TConfig {
    const defaults = this.getDefaultConfigForType(type);
    return { ...defaults, ...overrides } as TConfig;
  }

  public validateConfiguration<TConfig>(
    type: WidgetType,
    config: TConfig
  ): ValidationResult {
    const errors: ValidationError[] = [];
    
    // Basic validation - extend based on widget type
    if (!config || typeof config !== 'object') {
      errors.push({
        field: 'config',
        message: 'Configuration must be a valid object',
        code: 'INVALID_CONFIG_TYPE',
        expected: 'object',
        actual: typeof config
      });
    }

    // Type-specific validation
    const typeSpecificErrors = this.validateTypeSpecificConfig(type, config);
    errors.push(...typeSpecificErrors);

    return {
      isValid: errors.length === 0,
      errors,
      warnings: [] // Could add warnings for deprecated fields, etc.
    };
  }

  public getSupportedTypes(): WidgetType[] {
    return Array.from(this.controllerFactories.keys());
  }

  public registerWidget<TData, TConfig>(
    type: WidgetType,
    factory: WidgetControllerFactory<TData, TConfig>
  ): void {
    this.controllerFactories.set(type, factory);
  }

  /**
   * Register a data provider factory for a widget type
   */
  public registerDataProvider<TData, TQuery>(
    type: WidgetType,
    factory: (config: DataProviderConfig) => IDataProvider<TData, TQuery>
  ): void {
    this.dataProviderFactories.set(type, factory);
  }

  private getDefaultConfigForType(type: WidgetType): any {
    switch (type) {
      case WidgetType.HOLDINGS:
        return {
          id: `holdings-${Date.now()}`,
          type: WidgetType.HOLDINGS,
          title: 'Holdings',
          portfolioId: '',
          displayMode: 'compact',
          sortBy: 'weight',
          sortDirection: 'desc',
          refreshInterval: 30000
        };
        
      case WidgetType.PORTFOLIO_SUMMARY:
        return {
          id: `portfolio-summary-${Date.now()}`,
          type: WidgetType.PORTFOLIO_SUMMARY,
          title: 'Portfolio Summary',
          portfolioId: '',
          refreshInterval: 30000
        };
        
      case WidgetType.CORRELATION_MATRIX:
        return {
          id: `correlation-matrix-${Date.now()}`,
          type: WidgetType.CORRELATION_MATRIX,
          title: 'Correlation Matrix',
          symbols: [],
          refreshInterval: 300000 // 5 minutes
        };
        
      case WidgetType.MONTE_CARLO:
        return {
          id: `monte-carlo-${Date.now()}`,
          type: WidgetType.MONTE_CARLO,
          title: 'Monte Carlo Simulation',
          portfolioId: '',
          refreshInterval: 0 // Manual refresh only
        };
        
      default:
        return {
          id: `widget-${Date.now()}`,
          type,
          title: 'Widget',
          refreshInterval: 30000
        };
    }
  }

  private validateTypeSpecificConfig<TConfig>(
    type: WidgetType,
    config: TConfig
  ): ValidationError[] {
    const errors: ValidationError[] = [];
    const configObj = config as any;

    switch (type) {
      case WidgetType.HOLDINGS:
        if (!configObj.portfolioId || typeof configObj.portfolioId !== 'string') {
          errors.push({
            field: 'portfolioId',
            message: 'Portfolio ID is required for Holdings widget',
            code: 'MISSING_PORTFOLIO_ID',
            expected: 'string',
            actual: configObj.portfolioId
          });
        }
        break;
        
      case WidgetType.CORRELATION_MATRIX:
        if (!Array.isArray(configObj.symbols) || configObj.symbols.length === 0) {
          errors.push({
            field: 'symbols',
            message: 'Symbols array is required for Correlation Matrix widget',
            code: 'MISSING_SYMBOLS',
            expected: 'string[]',
            actual: configObj.symbols
          });
        }
        break;
    }

    return errors;
  }

  /**
   * Initialize with default widget registrations
   */
  public static createWithDefaults(): WidgetFactory {
    const factory = new WidgetFactory();
    
    // Register Holdings widget
    factory.registerWidget(
      WidgetType.HOLDINGS, 
      (config: HoldingsConfiguration, dependencies) => {
        return new HoldingsController(
          `holdings-${Date.now()}`, // id
          'holdings', // type
          config, // configuration
          dependencies.dataProvider as IDataProvider<HoldingsData>, // dataProvider
          dependencies.logger, // logger
          dependencies.eventBus // eventBus
        );
      }
    );
    
    factory.registerDataProvider(
      WidgetType.HOLDINGS,
      (config: DataProviderConfig) => new PortfolioDataProvider(
        'holdings-data-provider',
        {} as any, // logger - would need to be injected properly
        undefined, // cacheService
        config.baseUrl
      )
    );
    
    // Register Portfolio Summary widget
    factory.registerWidget(
      WidgetType.PORTFOLIO_SUMMARY,
      (config: any, dependencies) => {
        return new PortfolioSummaryController(
          dependencies.dataProvider as IDataProvider<PortfolioSummaryData>,
          config,
          dependencies.logger,
          dependencies.eventBus,
          dependencies.cacheService,
          dependencies.configService
        );
      }
    );
    
    factory.registerDataProvider(
      WidgetType.PORTFOLIO_SUMMARY,
      (config: DataProviderConfig) => new MarketDataProvider(
        'market-data-provider',
        {} as any, // logger - would need to be injected properly
        undefined, // cacheService
        undefined  // configService - could derive from config
      )
    );
    
    return factory;
  }
}