/**
 * createMockDependencies - Factory for creating mock widget dependencies
 * Provides comprehensive mocking for all widget dependencies for unit testing
 */
import { WidgetDependencies } from '../../../src/lib/interfaces/IWidgetFactory';
import { MockDataProvider, MockDataOptions } from './MockDataProvider';
import { IEventBus, ILogger } from '../../../src/lib/providers/WidgetServicesProvider';

export interface MockEventBusOptions {
  /** Enable logging of all events for testing verification */
  enableLogging?: boolean;
  /** Maximum number of events to store in memory */
  maxEventLog?: number;
}

export interface MockLoggerOptions {
  /** Enable console output for mock logger */
  enableConsole?: boolean;
  /** Log levels to capture */
  captureLevel?: 'debug' | 'info' | 'warn' | 'error';
}

export interface MockDependenciesOptions {
  /** Options for mock data provider */
  dataProvider?: MockDataOptions;
  /** Options for mock event bus */
  eventBus?: MockEventBusOptions;
  /** Options for mock logger */
  logger?: MockLoggerOptions;
  /** Override with custom data provider */
  customDataProvider?: MockDataProvider;
}

/**
 * Mock Event Bus for testing
 */
export class MockEventBus implements IEventBus {
  private listeners = new Map<string, Set<(data: any) => void>>();
  private eventLog: Array<{ event: string; data: any; timestamp: Date }> = [];
  private enableLogging: boolean;
  private maxEventLog: number;

  constructor(options: MockEventBusOptions = {}) {
    this.enableLogging = options.enableLogging ?? true;
    this.maxEventLog = options.maxEventLog ?? 1000;
  }

  subscribe<T = unknown>(event: string, callback: (data: T) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    
    this.listeners.get(event)!.add(callback);
    
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  publish<T = unknown>(event: string, data: T): void {
    if (this.enableLogging) {
      this.eventLog.push({
        event,
        data,
        timestamp: new Date()
      });
      
      // Maintain max log size
      if (this.eventLog.length > this.maxEventLog) {
        this.eventLog = this.eventLog.slice(-this.maxEventLog);
      }
    }

    this.listeners.get(event)?.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in mock event listener for ${event}:`, error);
      }
    });
  }

  // Test utilities
  getEventLog(): Array<{ event: string; data: any; timestamp: Date }> {
    return [...this.eventLog];
  }

  getEventsForType(eventType: string): Array<{ event: string; data: any; timestamp: Date }> {
    return this.eventLog.filter(log => log.event === eventType);
  }

  clearEventLog(): void {
    this.eventLog = [];
  }

  wasEventPublished(event: string, data?: any): boolean {
    const events = this.getEventsForType(event);
    if (!data) {
      return events.length > 0;
    }
    
    return events.some(log => JSON.stringify(log.data) === JSON.stringify(data));
  }

  getEventCount(event: string): number {
    return this.getEventsForType(event).length;
  }

  clearListeners(): void {
    this.listeners.clear();
  }

  getSubscriptions(): Record<string, number> {
    const subscriptions: Record<string, number> = {};
    this.listeners.forEach((listeners, event) => {
      subscriptions[event] = listeners.size;
    });
    return subscriptions;
  }
}

/**
 * Mock Logger for testing
 */
export class MockLogger implements ILogger {
  private logs: Array<{
    level: 'debug' | 'info' | 'warn' | 'error';
    message: string;
    meta?: Record<string, unknown>;
    error?: Error;
    timestamp: Date;
  }> = [];
  
  private enableConsole: boolean;
  private captureLevel: 'debug' | 'info' | 'warn' | 'error';

  constructor(options: MockLoggerOptions = {}) {
    this.enableConsole = options.enableConsole ?? false;
    this.captureLevel = options.captureLevel ?? 'debug';
  }

  debug(message: string, meta?: Record<string, unknown>): void {
    this.log('debug', message, meta);
    if (this.enableConsole) {
      console.debug(`[MOCK DEBUG] ${message}`, meta);
    }
  }

  info(message: string, meta?: Record<string, unknown>): void {
    this.log('info', message, meta);
    if (this.enableConsole) {
      console.info(`[MOCK INFO] ${message}`, meta);
    }
  }

  warn(message: string, meta?: Record<string, unknown>): void {
    this.log('warn', message, meta);
    if (this.enableConsole) {
      console.warn(`[MOCK WARN] ${message}`, meta);
    }
  }

  error(message: string, error?: Error, meta?: Record<string, unknown>): void {
    this.log('error', message, meta, error);
    if (this.enableConsole) {
      console.error(`[MOCK ERROR] ${message}`, error, meta);
    }
  }

  private log(
    level: 'debug' | 'info' | 'warn' | 'error',
    message: string,
    meta?: Record<string, unknown>,
    error?: Error
  ): void {
    const levelOrder = ['debug', 'info', 'warn', 'error'];
    if (levelOrder.indexOf(level) >= levelOrder.indexOf(this.captureLevel)) {
      this.logs.push({
        level,
        message,
        meta,
        error,
        timestamp: new Date()
      });
    }
  }

  // Test utilities
  getLogs(): Array<{
    level: 'debug' | 'info' | 'warn' | 'error';
    message: string;
    meta?: Record<string, unknown>;
    error?: Error;
    timestamp: Date;
  }> {
    return [...this.logs];
  }

  getLogsByLevel(level: 'debug' | 'info' | 'warn' | 'error'): Array<{
    level: 'debug' | 'info' | 'warn' | 'error';
    message: string;
    meta?: Record<string, unknown>;
    error?: Error;
    timestamp: Date;
  }> {
    return this.logs.filter(log => log.level === level);
  }

  clearLogs(): void {
    this.logs = [];
  }

  wasMessageLogged(message: string, level?: 'debug' | 'info' | 'warn' | 'error'): boolean {
    const logs = level ? this.getLogsByLevel(level) : this.logs;
    return logs.some(log => log.message.includes(message));
  }

  getLogCount(level?: 'debug' | 'info' | 'warn' | 'error'): number {
    return level ? this.getLogsByLevel(level).length : this.logs.length;
  }
}

/**
 * Mock Config Service for testing
 */
export class MockConfigService {
  private config = new Map<string, any>();
  private changeListeners = new Map<string, Set<(value: unknown) => void>>();

  get<T = unknown>(key: string, defaultValue?: T): T | undefined {
    return this.config.has(key) ? this.config.get(key) : defaultValue;
  }

  set<T = unknown>(key: string, value: T): void {
    this.config.set(key, value);
    this.notifyListeners(key, value);
  }

  subscribe(key: string, callback: (value: unknown) => void): () => void {
    if (!this.changeListeners.has(key)) {
      this.changeListeners.set(key, new Set());
    }
    this.changeListeners.get(key)!.add(callback);
    return () => {
      this.changeListeners.get(key)?.delete(callback);
    };
  }

  clear(key?: string): void {
    if (key) {
      this.config.delete(key);
      this.notifyListeners(key, undefined);
    } else {
      this.config.clear();
      this.changeListeners.forEach((_, configKey) => {
        this.notifyListeners(configKey, undefined);
      });
    }
  }

  private notifyListeners(key: string, value: unknown): void {
    this.changeListeners.get(key)?.forEach(listener => {
      try {
        listener(value);
      } catch (error) {
        console.error(`Error in config change listener for ${key}:`, error);
      }
    });
  }

  // Test utilities
  getConfig(): Map<string, any> {
    return new Map(this.config);
  }

  hasKey(key: string): boolean {
    return this.config.has(key);
  }

  getKeys(): string[] {
    return Array.from(this.config.keys());
  }
}

/**
 * Mock Cache Service for testing
 */
export class MockCacheService {
  private cache = new Map<string, any>();
  private stats = { hits: 0, misses: 0 };

  get(key: string): any {
    const hasKey = this.cache.has(key);
    if (hasKey) {
      this.stats.hits++;
    } else {
      this.stats.misses++;
    }
    return hasKey ? this.cache.get(key) : undefined;
  }

  set(key: string, value: any): void {
    this.cache.set(key, value);
  }

  delete(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
    this.stats = { hits: 0, misses: 0 };
  }

  getStats(): { size: number; hitRate: number; missRate: number } {
    const total = this.stats.hits + this.stats.misses;
    return {
      size: this.cache.size,
      hitRate: total > 0 ? this.stats.hits / total : 0,
      missRate: total > 0 ? this.stats.misses / total : 0
    };
  }

  // Test utilities
  getCacheContents(): Map<string, any> {
    return new Map(this.cache);
  }

  hasKey(key: string): boolean {
    return this.cache.has(key);
  }

  getKeys(): string[] {
    return Array.from(this.cache.keys());
  }

  resetStats(): void {
    this.stats = { hits: 0, misses: 0 };
  }
}

/**
 * Main factory function for creating mock dependencies
 */
export function createMockDependencies(options: MockDependenciesOptions = {}): {
  dependencies: WidgetDependencies;
  mocks: {
    dataProvider: MockDataProvider;
    eventBus: MockEventBus;
    logger: MockLogger;
    configService: MockConfigService;
    cacheService: MockCacheService;
  };
} {
  // Create mock services
  const mockDataProvider = options.customDataProvider || new MockDataProvider(options.dataProvider);
  const mockEventBus = new MockEventBus(options.eventBus);
  const mockLogger = new MockLogger(options.logger);
  const mockConfigService = new MockConfigService();
  const mockCacheService = new MockCacheService();

  const dependencies: WidgetDependencies = {
    dataProvider: mockDataProvider,
    eventBus: mockEventBus,
    logger: mockLogger,
    configService: mockConfigService,
    cacheService: mockCacheService
  };

  return {
    dependencies,
    mocks: {
      dataProvider: mockDataProvider,
      eventBus: mockEventBus,
      logger: mockLogger,
      configService: mockConfigService,
      cacheService: mockCacheService
    }
  };
}

/**
 * Create mock dependencies specifically configured for Holdings widget testing
 */
export function createHoldingsMockDependencies(): {
  dependencies: WidgetDependencies;
  mocks: {
    dataProvider: MockDataProvider;
    eventBus: MockEventBus;
    logger: MockLogger;
    configService: MockConfigService;
    cacheService: MockCacheService;
  };
} {
  const mockDataProvider = new MockDataProvider({
    mockResponses: MockDataProvider.createHoldingsMockResponses(),
    defaultDelay: 10 // Fast responses for tests
  });

  return createMockDependencies({
    customDataProvider: mockDataProvider,
    logger: { enableConsole: false, captureLevel: 'debug' },
    eventBus: { enableLogging: true, maxEventLog: 100 }
  });
}

/**
 * Create mock dependencies for error scenario testing
 */
export function createErrorMockDependencies(): {
  dependencies: WidgetDependencies;
  mocks: {
    dataProvider: MockDataProvider;
    eventBus: MockEventBus;
    logger: MockLogger;
    configService: MockConfigService;
    cacheService: MockCacheService;
  };
} {
  const mockDataProvider = new MockDataProvider({
    mockResponses: MockDataProvider.createErrorMockResponses(),
    defaultDelay: 10
  });

  return createMockDependencies({
    customDataProvider: mockDataProvider,
    logger: { enableConsole: false, captureLevel: 'error' },
    eventBus: { enableLogging: true }
  });
}

export default createMockDependencies;