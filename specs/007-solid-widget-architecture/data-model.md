# Data Model - SOLID Widget Architecture

**Phase**: 1 - Design  
**Target**: ETF Analysis Dashboard Widget Data Models  
**Date**: December 9, 2025

## Core Entities

### Widget Configuration
```typescript
interface WidgetConfiguration {
  id: string;
  type: WidgetType;
  title: string;
  size: WidgetSize;
  refreshInterval?: number;
  dataSource: DataSourceConfig;
  displayOptions: DisplayOptions;
}

enum WidgetType {
  HOLDINGS = 'holdings',
  PORTFOLIO_SUMMARY = 'portfolio-summary',
  CORRELATION_MATRIX = 'correlation-matrix',
  MONTE_CARLO = 'monte-carlo'
}

interface DataSourceConfig {
  endpoint: string;
  cacheTimeout: number;
  errorRetryCount: number;
  mockMode?: boolean;
}
```

### Portfolio Data
```typescript
interface Portfolio {
  id: string;
  name: string;
  totalValue: number;
  currency: string;
  holdings: Holding[];
  lastUpdated: Date;
  metadata: PortfolioMetadata;
}

interface Holding {
  symbol: string;
  name: string;
  assetClass: string;  // Maps from current asset_class field
  quantity: number;
  marketValue: number;  // Maps from current market_value field
  currentPrice: number; // Maps from current current_price field
  weight: number;
  sector?: string;
  region?: string;
  dividendYield?: number;
  beta?: number;
}

interface PortfolioMetadata {
  totalReturn: number;
  totalReturnPercentage: number;
  dayChange: number;
  dayChangePercentage: number;
  volatility: number;
  sharpeRatio: number;
}
```

### Market Data
```typescript
interface MarketData {
  correlationMatrix: CorrelationMatrix;
  historicalPrices: PriceHistory[];
  marketIndicators: MarketIndicator[];
  lastUpdated: Date;
}

interface CorrelationMatrix {
  symbols: string[];
  correlations: number[][];
  timeframe: string;
  confidence: number;
}

interface PriceHistory {
  symbol: string;
  date: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface MarketIndicator {
  name: string;
  value: number;
  change: number;
  changePercentage: number;
}
```

### Simulation Data
```typescript
interface SimulationResult {
  id: string;
  parameters: SimulationParameters;
  outcomes: SimulationOutcome[];
  statistics: SimulationStatistics;
  createdAt: Date;
}

interface SimulationParameters {
  timeHorizon: number;
  iterations: number;
  confidenceLevel: number;
  volatilityModel: string;
  rebalancingFrequency: string;
}

interface SimulationOutcome {
  iteration: number;
  finalValue: number;
  maxDrawdown: number;
  volatility: number;
  returns: number[];
}

interface SimulationStatistics {
  meanReturn: number;
  medianReturn: number;
  standardDeviation: number;
  valueAtRisk: number;
  conditionalVaR: number;
  probabilityOfLoss: number;
}
```

## Data Relationships

### Portfolio → Holdings (One-to-Many)
- Each Portfolio contains multiple Holdings
- Holdings aggregate to Portfolio total value and metadata
- Holdings weight must sum to 1.0 (100%)

### Portfolio → MarketData (Many-to-Many)
- Multiple Portfolios can reference same MarketData
- MarketData provides correlation and price history for Portfolio analysis
- Cached at market data level for efficiency

### Portfolio → SimulationResult (One-to-Many)
- Each Portfolio can have multiple simulation scenarios
- SimulationResults are specific to Portfolio composition
- Historical simulations retained for comparison

## Validation Rules

### Portfolio Validation
- `totalValue` must equal sum of holding market values
- `holdings[].weight` must sum to 1.0 ± 0.001
- `currency` must be valid ISO currency code
- `lastUpdated` cannot be future date

### Holding Validation
- `quantity` must be positive number
- `marketValue` must equal `quantity * currentPrice`
- `weight` must be between 0 and 1
- `symbol` must match market data availability
- `assetClass` must be non-empty string

### Legacy Field Mapping (for Holdings.tsx migration)
- `asset_class` → `assetClass`
- `market_value` → `marketValue` 
- `current_price` → `currentPrice`
- All other fields remain the same (symbol, name, quantity, weight)

### Market Data Validation
- Correlation matrix must be symmetric
- Correlation values between -1 and 1
- Price history dates must be chronological
- No gaps in trading day price history

### Simulation Validation
- `iterations` must be ≥ 1000 for statistical significance
- `timeHorizon` must be positive
- `confidenceLevel` between 0.01 and 0.99
- Outcome arrays must match iteration count

## State Transitions

### Widget Lifecycle States
```typescript
enum WidgetState {
  INITIALIZING = 'initializing',
  LOADING = 'loading', 
  READY = 'ready',
  ERROR = 'error',
  REFRESHING = 'refreshing'
}

// State transitions
INITIALIZING → LOADING → READY
READY → REFRESHING → READY  
ANY_STATE → ERROR → LOADING (retry)
```

### Data Refresh States
```typescript
enum DataState {
  STALE = 'stale',
  FRESH = 'fresh',
  UPDATING = 'updating',
  FAILED = 'failed'
}

// Automatic transitions based on cache timeout
FRESH → STALE (after cache timeout)
STALE → UPDATING (on access)
UPDATING → FRESH (success) | FAILED (error)
```

## Performance Considerations

### Performance Targets
- Widget render time: <100ms initial load
- Re-render on data updates: <50ms
- Smooth interactions: 60fps maintained
- Cache hit ratio: >80% for repeated data access

### Caching Strategy
- Portfolio data cached for 30 seconds
- Market data cached for 5 minutes  
- Simulation results cached until portfolio changes
- Widget configurations cached in localStorage

### Data Loading
- Lazy loading for non-visible widgets
- Incremental loading for large datasets
- Background refresh with optimistic updates
- Error boundaries for widget isolation

## Migration Path

### Existing Data Compatibility
- Current data structures mapped to new interfaces
- Gradual migration using adapter pattern
- Fallback to legacy data sources during transition
- Validation layers ensure data integrity

### Breaking Changes
- Widget configuration format updated
- API response structure standardized
- Error handling consolidated
- Cache keys reorganized