# SOLID Widget Architecture - Developer Quickstart

**Target**: ETF Analysis Dashboard Widgets  
**Framework**: React + TypeScript + SOLID Principles  
**Date**: December 9, 2025

## Getting Started

This guide helps developers create and work with widgets using the new SOLID architecture. The architecture separates concerns using dependency injection, making widgets more testable, maintainable, and extensible.

## Architecture Overview

### Core Principles
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification  
- **Liskov Substitution**: Implementations are interchangeable
- **Interface Segregation**: Clients depend only on interfaces they use
- **Dependency Inversion**: Depend on abstractions, not concretions

### Key Components
```
Widget Component (React) → Widget Controller → Data Provider → API
                       ↗ Configuration Service
                       ↗ Event Bus
                       ↗ Cache Service
```

## Creating a New Widget

### 1. Define Widget Configuration

```typescript
// types/MyWidgetConfig.ts
export interface MyWidgetConfiguration extends IWidgetConfiguration {
  data: MyWidgetConfigData;
}

export interface MyWidgetConfigData {
  type: WidgetType.MY_WIDGET;
  customProperty: string;
  displayOptions: {
    showHeader: boolean;
    maxItems: number;
  };
}
```

### 2. Create Widget Controller

```typescript
// controllers/MyWidgetController.ts
import { IWidgetController, IDataProvider, WidgetDependencies } from '@/lib/interfaces';

export class MyWidgetController implements IWidgetController<MyWidgetData, MyWidgetConfiguration> {
  public readonly id: string;
  public readonly type = WidgetType.MY_WIDGET;
  
  private _data: MyWidgetData | null = null;
  private _isLoading = false;
  private _error: Error | null = null;
  private _lastUpdated: Date | null = null;
  private subscribers: Set<(data: MyWidgetData | null) => void> = new Set();

  constructor(
    id: string,
    private config: MyWidgetConfiguration,
    private dependencies: WidgetDependencies
  ) {
    this.id = id;
  }

  public get configuration() { return this.config; }
  public get data() { return this._data; }
  public get isLoading() { return this._isLoading; }
  public get error() { return this._error; }
  public get lastUpdated() { return this._lastUpdated; }

  public async initialize(config: MyWidgetConfiguration): Promise<void> {
    this.config = config;
    await this.refresh();
  }

  public async refresh(force = false): Promise<void> {
    if (this._isLoading) return;
    
    this._isLoading = true;
    this._error = null;
    this.notifySubscribers();

    try {
      const query = this.buildQuery();
      this._data = await this.dependencies.dataProvider.fetchData(query, { forceRefresh: force });
      this._lastUpdated = new Date();
      this.dependencies.logger.info(`Widget ${this.id} refreshed successfully`);
    } catch (error) {
      this._error = error as Error;
      this.dependencies.logger.error(`Widget ${this.id} refresh failed`, error as Error);
    } finally {
      this._isLoading = false;
      this.notifySubscribers();
    }
  }

  public subscribe(callback: (data: MyWidgetData | null) => void): () => void {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  public async dispose(): Promise<void> {
    this.subscribers.clear();
    // Clean up any other resources
  }

  private buildQuery(): MyWidgetQuery {
    return {
      customProperty: this.config.data.customProperty,
      // Build query from configuration
    };
  }

  private notifySubscribers(): void {
    this.subscribers.forEach(callback => callback(this._data));
  }
}
```

### 3. Create Data Provider

```typescript
// providers/MyWidgetDataProvider.ts
import { IDataProvider, ConnectionStatus } from '@/lib/interfaces';

export class MyWidgetDataProvider implements IDataProvider<MyWidgetData, MyWidgetQuery> {
  public readonly name = 'MyWidgetDataProvider';
  private _isAvailable = false;
  private _connectionStatus = ConnectionStatus.DISCONNECTED;

  public get isAvailable() { return this._isAvailable; }
  public get connectionStatus() { return this._connectionStatus; }

  public async initialize(config: DataProviderConfig): Promise<void> {
    // Initialize data source connection
    this._connectionStatus = ConnectionStatus.CONNECTING;
    try {
      // Setup REST client, WebSocket, etc.
      this._isAvailable = true;
      this._connectionStatus = ConnectionStatus.CONNECTED;
    } catch (error) {
      this._connectionStatus = ConnectionStatus.FAILED;
      throw error;
    }
  }

  public async fetchData(query: MyWidgetQuery, options?: FetchOptions): Promise<MyWidgetData> {
    if (!this._isAvailable) {
      throw new Error('Data provider not available');
    }

    // Check cache first unless force refresh
    if (!options?.forceRefresh) {
      const cached = this.getFromCache(query);
      if (cached) return cached;
    }

    // Fetch from API
    const response = await this.makeRequest(query, options);
    const data = this.transformResponse(response);
    
    // Cache the result
    this.setCache(query, data);
    
    return data;
  }

  private async makeRequest(query: MyWidgetQuery, options?: FetchOptions): Promise<any> {
    // Implementation specific to data source
    // REST API call, WebSocket message, etc.
  }

  private transformResponse(response: any): MyWidgetData {
    // Transform API response to widget data format
  }

  // Implement other IDataProvider methods...
}
```

### 4. Create React Component

```typescript
// components/MyWidget.tsx
import React from 'react';
import { useWidgetController } from '@/hooks/use-widget-controller';
import { MyWidgetConfiguration, MyWidgetData } from '@/types';

interface MyWidgetProps {
  configuration: MyWidgetConfiguration;
}

export function MyWidget({ configuration }: MyWidgetProps) {
  const { data, isLoading, error, refresh } = useWidgetController<MyWidgetData, MyWidgetConfiguration>(
    configuration
  );

  if (error) {
    return (
      <div className="widget-error">
        <h3>Error loading widget</h3>
        <p>{error.message}</p>
        <button onClick={() => refresh(true)}>Retry</button>
      </div>
    );
  }

  if (isLoading) {
    return <div className="widget-loading">Loading...</div>;
  }

  return (
    <div className="widget-container">
      <div className="widget-header">
        <h3>{configuration.title}</h3>
        <button onClick={() => refresh()}>Refresh</button>
      </div>
      
      <div className="widget-content">
        {data ? (
          // Render widget content
          <div>{/* Widget content based on data */}</div>
        ) : (
          <div>No data available</div>
        )}
      </div>
    </div>
  );
}
```

### 5. Register Widget with Factory

```typescript
// lib/factories/WidgetFactory.ts
import { MyWidgetController } from '@/controllers/MyWidgetController';
import { MyWidgetConfiguration, MyWidgetData } from '@/types';

export class WidgetFactory implements IWidgetFactory {
  constructor() {
    this.registerWidget(
      WidgetType.MY_WIDGET,
      (config, dependencies) => new MyWidgetController(
        crypto.randomUUID(),
        config as MyWidgetConfiguration,
        dependencies
      )
    );
  }

  // Implement IWidgetFactory methods...
}
```

## Using Widgets in Dashboard

### Widget Provider Setup

```typescript
// app/dashboard/page.tsx
import { WidgetServicesProvider } from '@/lib/providers/WidgetServicesProvider';
import { createWidgetServices } from '@/lib/factories/createWidgetServices';

export default function DashboardPage() {
  const services = createWidgetServices();

  return (
    <WidgetServicesProvider services={services}>
      <Dashboard />
    </WidgetServicesProvider>
  );
}
```

### Custom Hook for Widget Controllers

```typescript
// hooks/use-widget-controller.ts
import { useState, useEffect } from 'react';
import { useWidgetServices } from './use-widget-services';
import { IWidgetController, IWidgetConfiguration } from '@/lib/interfaces';

export function useWidgetController<TData, TConfig extends IWidgetConfiguration>(
  configuration: TConfig
) {
  const { factory } = useWidgetServices();
  const [controller, setController] = useState<IWidgetController<TData, TConfig> | null>(null);
  const [data, setData] = useState<TData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const dependencies = createWidgetDependencies();
    const newController = factory.createController<TData, TConfig>(
      configuration.type,
      configuration,
      dependencies
    );

    const unsubscribe = newController.subscribe(setData);
    
    newController.initialize(configuration).then(() => {
      setController(newController);
      setIsLoading(false);
    }).catch(setError);

    return () => {
      unsubscribe();
      newController.dispose();
    };
  }, [configuration, factory]);

  const refresh = (force = false) => {
    if (controller) {
      return controller.refresh(force);
    }
  };

  return {
    data,
    isLoading: isLoading || controller?.isLoading || false,
    error: error || controller?.error,
    refresh,
    controller
  };
}
```

## Testing Widgets

### Unit Testing Controllers

```typescript
// tests/controllers/MyWidgetController.test.ts
import { MyWidgetController } from '@/controllers/MyWidgetController';
import { createMockDependencies, createMockConfiguration } from '../utils/mocks';

describe('MyWidgetController', () => {
  let controller: MyWidgetController;
  let mockDependencies: WidgetDependencies;
  let mockConfig: MyWidgetConfiguration;

  beforeEach(() => {
    mockDependencies = createMockDependencies();
    mockConfig = createMockConfiguration();
    controller = new MyWidgetController('test-id', mockConfig, mockDependencies);
  });

  it('should initialize with configuration', async () => {
    await controller.initialize(mockConfig);
    expect(controller.configuration).toEqual(mockConfig);
  });

  it('should fetch data on refresh', async () => {
    const mockData = { value: 'test' };
    mockDependencies.dataProvider.fetchData = jest.fn().mockResolvedValue(mockData);

    await controller.refresh();

    expect(controller.data).toEqual(mockData);
    expect(controller.isLoading).toBe(false);
    expect(controller.error).toBeNull();
  });

  it('should handle errors gracefully', async () => {
    const mockError = new Error('Test error');
    mockDependencies.dataProvider.fetchData = jest.fn().mockRejectedValue(mockError);

    await controller.refresh();

    expect(controller.data).toBeNull();
    expect(controller.error).toEqual(mockError);
  });
});
```

### Integration Testing Components

```typescript
// tests/integration/widget-integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { MyWidget } from '@/components/MyWidget';
import { WidgetServicesProvider } from '@/lib/providers/WidgetServicesProvider';
import { createMockServices } from '../utils/mocks';

describe('MyWidget Integration', () => {
  it('should render widget with data', async () => {
    const mockServices = createMockServices();
    const mockConfig = createMockConfiguration();

    render(
      <WidgetServicesProvider services={mockServices}>
        <MyWidget configuration={mockConfig} />
      </WidgetServicesProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Widget content')).toBeInTheDocument();
    });
  });
});
```

## Development Workflow

### 1. Development Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests in watch mode
npm run test:watch
```

### 2. Creating New Widget Type
1. Add widget type to `WidgetType` enum
2. Create configuration interfaces
3. Implement controller and data provider
4. Create React component
5. Register with factory
6. Add tests
7. Update documentation

### 3. Debugging
- Use browser dev tools to inspect widget state
- Check controller state with `controller.getState()`
- Monitor data provider cache with `provider.getCacheStatus()`
- Use logger service for structured logging

## Migration from Legacy Widgets

### Gradual Migration Strategy

1. **Phase 1**: Wrap existing widgets with new controller interface
2. **Phase 2**: Extract data fetching to providers
3. **Phase 3**: Implement full SOLID architecture
4. **Phase 4**: Remove legacy code

### Compatibility Layer

```typescript
// adapters/LegacyWidgetAdapter.ts
export class LegacyWidgetAdapter implements IWidgetController {
  constructor(private legacyWidget: LegacyWidget) {}
  
  // Implement interface by delegating to legacy widget
  public async refresh(): Promise<void> {
    return this.legacyWidget.loadData();
  }
  
  // Other adapter methods...
}
```

## Performance Considerations

### Optimization Tips

1. **Lazy Loading**: Only create controllers when widgets are visible
2. **Data Caching**: Use cache service to avoid redundant API calls
3. **Memoization**: Use React.memo for component optimization
4. **Batch Updates**: Group multiple data updates using event batching

### Monitoring

```typescript
// lib/monitoring/WidgetPerformanceMonitor.ts
export class WidgetPerformanceMonitor {
  trackWidgetRender(widgetId: string, renderTime: number) {
    console.log(`Widget ${widgetId} rendered in ${renderTime}ms`);
    // Send to analytics service
  }
}
```

## Best Practices

1. **Keep controllers lightweight**: Delegate complex logic to services
2. **Use interfaces consistently**: Never depend on concrete implementations
3. **Handle errors gracefully**: Always provide fallback UI states
4. **Cache intelligently**: Balance performance with data freshness
5. **Test thoroughly**: Unit test controllers, integration test components
6. **Document widgets**: Include configuration examples and usage notes

## Troubleshooting

### Common Issues

1. **Widget not loading**: Check data provider initialization and configuration
2. **Stale data**: Verify cache settings and refresh intervals
3. **Memory leaks**: Ensure proper subscription cleanup in dispose methods
4. **Type errors**: Verify interface implementations match contracts

### Debug Tools

```typescript
// Debug hook for development
export function useWidgetDebug(controller: IWidgetController) {
  useEffect(() => {
    console.log('Widget State:', controller.getState());
  }, [controller]);
}
```