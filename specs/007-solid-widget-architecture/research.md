# SOLID Widget Architecture - Research Report

**Research Phase**: Phase 0  
**Target**: React/TypeScript Widget Architecture  
**Date**: December 9, 2025  
**Context**: ETF Analysis Dashboard Widgets (Holdings, PortfolioSummary, CorrelationMatrix, MonteCarloSimulation)

## Executive Summary

This research addresses five critical areas for implementing SOLID principles in React widget architecture: dependency injection patterns, controller-view separation, data provider abstraction, testing strategies, and migration approaches. The goal is to refactor existing dashboard widgets to follow SOLID principles while maintaining backward compatibility and improving maintainability.

## 1. Dependency Injection Patterns in React

### Decision: React Context + Custom Hook Pattern

**Rationale**: React Context provides the most natural dependency injection mechanism for React applications without introducing external libraries. It aligns with React's component tree structure and provides type safety through TypeScript.

**Implementation Approach**:
```typescript
// Service Provider Context
interface WidgetServicesContext {
  dataProvider: IDataProvider;
  configService: IConfigService;
  eventBus: IEventBus;
}

const WidgetServicesContext = createContext<WidgetServicesContext | null>(null);

// Custom hook for dependency access
function useWidgetServices(): WidgetServicesContext {
  const context = useContext(WidgetServicesContext);
  if (!context) {
    throw new Error('useWidgetServices must be used within WidgetServicesProvider');
  }
  return context;
}

// Provider component
function WidgetServicesProvider({ children, services }: {
  children: ReactNode;
  services: WidgetServicesContext;
}) {
  return (
    <WidgetServicesContext.Provider value={services}>
      {children}
    </WidgetServicesContext.Provider>
  );
}
```

**Alternatives Considered**:

1. **Prop Drilling**: Simple but creates tight coupling and maintenance burden
2. **Third-party DI Libraries** (InversifyJS, TSyringe): Add complexity and bundle size
3. **Module-level Singletons**: Difficult to test and lack flexibility
4. **Higher-Order Components (HOC)**: More verbose than hooks and harder to compose

**Implementation Considerations**:
- Use multiple focused contexts instead of one monolithic context for better performance
- Implement context splitting by concern (data, configuration, events)
- Provide default implementations for testing and development
- Use TypeScript strict mode for compile-time dependency validation

## 2. Widget Controller Architecture

### Decision: Controller-as-Hook Pattern with Presentation Component Separation

**Rationale**: React hooks provide a natural way to separate business logic from presentation while maintaining React's declarative paradigm. This approach keeps controllers close to React's lifecycle while enabling easy testing and reuse.

**Implementation Approach**:
```typescript
// Widget Controller Interface
interface IWidgetController<TData, TConfig> {
  data: TData | null;
  loading: boolean;
  error: string | null;
  config: TConfig;
  refetch: () => Promise<void>;
  updateConfig: (config: Partial<TConfig>) => void;
}

// Controller Hook Implementation
function useHoldingsController(
  config: HoldingsConfig,
  dependencies: WidgetDependencies
): IWidgetController<HoldingsData, HoldingsConfig> {
  const [data, setData] = useState<HoldingsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [widgetConfig, setWidgetConfig] = useState(config);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await dependencies.dataProvider.getHoldings(widgetConfig);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [dependencies.dataProvider, widgetConfig]);

  return {
    data,
    loading,
    error,
    config: widgetConfig,
    refetch: fetchData,
    updateConfig: (newConfig) => setWidgetConfig(prev => ({ ...prev, ...newConfig }))
  };
}

// Presentation Component
function HoldingsView({ controller }: { controller: IWidgetController<HoldingsData, HoldingsConfig> }) {
  const { data, loading, error } = controller;
  
  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorDisplay message={error} />;
  if (!data) return <EmptyState />;
  
  return <HoldingsTable holdings={data.holdings} />;
}
```

**Alternatives Considered**:

1. **Class-based Controllers**: More traditional but don't integrate well with React hooks
2. **Reducer Pattern**: Overly complex for simple widget state management
3. **State Machines (XState)**: Powerful but adds learning curve and complexity
4. **Custom Event System**: Creates indirection that's harder to debug

**Implementation Considerations**:
- Keep controllers focused on a single widget type
- Use composition for shared controller logic
- Implement controller factories for different widget variants
- Provide mock controllers for testing and development

## 3. Data Provider Abstraction

### Decision: Repository Pattern with Async Interface + Caching Strategy

**Rationale**: The Repository pattern provides a clean abstraction over data sources while supporting multiple implementations (REST API, WebSocket, mock data). Combined with React Query or SWR for caching, it provides optimal performance and developer experience.

**Implementation Approach**:
```typescript
// Data Provider Interface
interface IDataProvider {
  getPortfolioSummary(config: PortfolioConfig): Promise<PortfolioSummaryData>;
  getHoldings(config: HoldingsConfig): Promise<HoldingsData>;
  getCorrelationMatrix(config: CorrelationConfig): Promise<CorrelationData>;
  getMonteCarloSimulation(config: MonteCarloConfig): Promise<MonteCarloData>;
}

// Cache-aware Implementation
class CachedDataProvider implements IDataProvider {
  constructor(
    private apiClient: ApiClient,
    private cache: QueryClient
  ) {}

  async getPortfolioSummary(config: PortfolioConfig): Promise<PortfolioSummaryData> {
    const cacheKey = ['portfolio-summary', config];
    
    return this.cache.fetchQuery({
      queryKey: cacheKey,
      queryFn: () => this.apiClient.get('/api/widgets/portfolio/summary', { params: config }),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
    });
  }
}

// Mock Implementation for Testing
class MockDataProvider implements IDataProvider {
  async getPortfolioSummary(config: PortfolioConfig): Promise<PortfolioSummaryData> {
    await new Promise(resolve => setTimeout(resolve, 100)); // Simulate network delay
    return mockPortfolioSummaryData;
  }
}
```

**Alternatives Considered**:

1. **Direct API Calls in Hooks**: Simple but creates tight coupling and poor testability
2. **GraphQL with Apollo**: Powerful but overkill for current REST API architecture
3. **Redux/Zustand with RTK Query**: Adds state management complexity
4. **Custom Fetch Abstraction**: Reinvents existing solutions

**Implementation Considerations**:
- Use React Query or SWR for automatic caching and background updates
- Implement retry logic with exponential backoff
- Support optimistic updates for user interactions
- Provide offline/degraded mode capabilities
- Use TypeScript generics for type-safe data contracts

## 4. Testing Strategies

### Decision: Layered Testing with Mock Injection + React Testing Library

**Rationale**: A layered approach enables testing at appropriate levels of abstraction. Mock injection through dependency injection allows isolated unit testing, while integration tests verify complete widget functionality.

**Implementation Approach**:

**Unit Testing - Controller Logic**:
```typescript
describe('HoldingsController', () => {
  let mockDataProvider: jest.Mocked<IDataProvider>;
  let mockEventBus: jest.Mocked<IEventBus>;
  
  beforeEach(() => {
    mockDataProvider = createMockDataProvider();
    mockEventBus = createMockEventBus();
  });

  it('should load holdings data on initialization', async () => {
    const mockData = createMockHoldingsData();
    mockDataProvider.getHoldings.mockResolvedValue(mockData);
    
    const { result } = renderHook(() => 
      useHoldingsController(defaultConfig, { dataProvider: mockDataProvider, eventBus: mockEventBus })
    );
    
    await waitFor(() => {
      expect(result.current.data).toEqual(mockData);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should handle errors gracefully', async () => {
    const errorMessage = 'API Error';
    mockDataProvider.getHoldings.mockRejectedValue(new Error(errorMessage));
    
    const { result } = renderHook(() => 
      useHoldingsController(defaultConfig, { dataProvider: mockDataProvider, eventBus: mockEventBus })
    );
    
    await waitFor(() => {
      expect(result.current.error).toBe(errorMessage);
      expect(result.current.data).toBeNull();
    });
  });
});
```

**Integration Testing - Complete Widget**:
```typescript
describe('Holdings Widget Integration', () => {
  it('should display holdings data correctly', async () => {
    const mockServices = {
      dataProvider: new MockDataProvider(),
      configService: new MockConfigService(),
      eventBus: new MockEventBus()
    };

    render(
      <WidgetServicesProvider services={mockServices}>
        <Holdings />
      </WidgetServicesProvider>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('$150.00')).toBeInTheDocument();
    });
  });

  it('should handle configuration updates', async () => {
    const mockServices = createMockServices();
    
    render(
      <WidgetServicesProvider services={mockServices}>
        <Holdings />
      </WidgetServicesProvider>
    );

    fireEvent.click(screen.getByText('Group by Sector'));
    
    await waitFor(() => {
      expect(mockServices.dataProvider.getHoldings).toHaveBeenCalledWith(
        expect.objectContaining({ groupBy: 'sector' })
      );
    });
  });
});
```

**Alternatives Considered**:

1. **End-to-End Testing Only**: Slow and brittle, poor debugging experience
2. **Snapshot Testing**: Fragile with UI changes, doesn't test behavior
3. **Manual Testing**: Not sustainable for regression testing
4. **Storybook Component Testing**: Good for UI states, poor for business logic

**Implementation Considerations**:
- Use MSW (Mock Service Worker) for realistic API mocking in tests
- Implement test utilities for common widget test scenarios
- Create reusable mock factories for data providers and services
- Use React Testing Library best practices (query by role, not implementation)
- Implement visual regression testing for complex widgets like correlation matrix

## 5. Migration Approach

### Decision: Incremental Refactoring with Feature Flags + Adapter Pattern

**Rationale**: Gradual migration minimizes risk and allows for validation at each step. Feature flags enable safe deployment and rollback, while adapter patterns allow old and new architectures to coexist during transition.

**Implementation Approach**:

**Phase 1 - Infrastructure Setup**:
```typescript
// Feature Flag for SOLID Architecture
const useSolidArchitecture = useFeatureFlag('SOLID_WIDGET_ARCHITECTURE');

// Legacy Widget Adapter
function LegacyWidgetAdapter({ children, widgetType }: {
  children: (services: WidgetServices) => ReactNode;
  widgetType: string;
}) {
  const legacyHook = useLegacyWidgetHooks(widgetType);
  
  // Adapt legacy hook data to new service interface
  const adaptedServices = useMemo(() => ({
    dataProvider: new LegacyHookDataProvider(legacyHook),
    configService: new DefaultConfigService(),
    eventBus: new NoOpEventBus(),
  }), [legacyHook]);

  return <>{children(adaptedServices)}</>;
}

// Progressive Widget Component
function Holdings() {
  const useSolid = useFeatureFlag('SOLID_ARCHITECTURE_HOLDINGS');
  
  if (useSolid) {
    return <SolidHoldingsWidget />;
  } else {
    return <LegacyHoldingsWidget />;
  }
}
```

**Phase 2 - Widget-by-Widget Migration**:
```typescript
// Migration utility
function createMigratedWidget<TProps>(
  legacyComponent: ComponentType<TProps>,
  solidComponent: ComponentType<TProps>,
  featureFlag: string
) {
  return (props: TProps) => {
    const useSolid = useFeatureFlag(featureFlag);
    return useSolid ? 
      createElement(solidComponent, props) : 
      createElement(legacyComponent, props);
  };
}

// Apply to each widget
export const Holdings = createMigratedWidget(
  LegacyHoldings,
  SolidHoldings,
  'SOLID_HOLDINGS'
);
```

**Phase 3 - Validation and Cleanup**:
```typescript
// A/B Testing Component for Validation
function ValidatedWidget({ children }: { children: ReactNode }) {
  const trackingService = useWidgetTracking();
  
  useEffect(() => {
    trackingService.track('widget_architecture_comparison', {
      architecture: 'solid',
      renderTime: performance.now(),
    });
  }, []);

  return <>{children}</>;
}
```

**Alternatives Considered**:

1. **Big Bang Rewrite**: High risk, difficult to validate, long feedback cycles
2. **Branch-based Development**: Merge conflicts, difficult to maintain parallel versions
3. **Duplicate Components**: Code duplication, maintenance overhead
4. **Runtime Feature Detection**: More complex than feature flags, harder to control

**Implementation Considerations**:
- Implement comprehensive monitoring to compare old vs new architecture performance
- Use TypeScript strict mode to catch interface mismatches during migration
- Create migration scripts for automated testing of both architectures
- Plan rollback strategy for each migration phase
- Document migration progress and lessons learned for team knowledge sharing

## Research Conclusions and Next Steps

### Key Technical Decisions Summary

1. **Dependency Injection**: React Context + Custom Hooks pattern
2. **Controller Architecture**: Controller-as-Hook with separated presentation components  
3. **Data Abstraction**: Repository pattern with React Query caching
4. **Testing Strategy**: Layered testing with mock injection via DI
5. **Migration Approach**: Incremental refactoring with feature flags and adapters

### Critical Implementation Requirements

1. **Type Safety**: All interfaces must be strictly typed with TypeScript
2. **Performance**: No degradation in widget rendering (<100ms target)
3. **Backward Compatibility**: Existing widget APIs must continue working
4. **Developer Experience**: Clear patterns and comprehensive documentation
5. **Testing Coverage**: 95% coverage target for business logic

### Phase 1 Design Phase Inputs

The research resolves these technical unknowns for Phase 1:
- **Dependency Injection Mechanism**: React Context with typed providers
- **Controller Pattern**: Custom hooks implementing controller interfaces
- **Data Layer Architecture**: Repository pattern with cache-aware implementations
- **Testing Infrastructure**: Mock injection through DI container
- **Migration Strategy**: Feature flags with adapter pattern for coexistence

### Risk Mitigation Strategies

1. **Performance Risk**: Implement React.memo and careful dependency arrays
2. **Complexity Risk**: Start with simplest widget (PortfolioSummary) for validation
3. **Adoption Risk**: Provide comprehensive examples and documentation
4. **Regression Risk**: Maintain legacy tests during migration period
5. **Integration Risk**: Use adapter pattern for gradual interface migration

This research provides the technical foundation for implementing SOLID principles in React widget architecture while maintaining the performance and usability requirements of the ETF Analysis dashboard.