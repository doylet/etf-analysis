/**
 * Widget Types - SOLID Widget Architecture
 * Centralized type definitions for widget system
 */

// Re-export from data model for consistency
export interface Holding {
  symbol: string;
  name: string;
  assetClass: string;  // Maps from current asset_class field
  quantity: number;
  marketValue: number;  // Maps from current market_value field
  currentPrice: number; // Maps from current current_price field
  weight: number;
  // Performance fields
  dayChange?: number;
  dayChangePercent?: number;
  totalReturn?: number;
  totalReturnPercent?: number;
  // Optional metadata fields
  sector?: string;
  region?: string;
  dividendYield?: number;
  beta?: number;
}

// Widget type enumeration
export enum WidgetType {
  HOLDINGS = 'holdings',
  PORTFOLIO_SUMMARY = 'portfolio-summary',
  CORRELATION_MATRIX = 'correlation-matrix',
  MONTE_CARLO = 'monte-carlo'
}

// Widget configuration types
export interface BaseWidgetConfig {
  id: string;
  type: WidgetType;
  title: string;
  refreshInterval?: number;
}

export interface HoldingsConfiguration extends BaseWidgetConfig {
  type: WidgetType.HOLDINGS;
  portfolioId: string;
  displayMode: 'compact' | 'detailed' | 'table' | 'list' | 'percentage';
  sortBy: 'weight' | 'marketValue' | 'symbol' | 'assetClass';
  sortDirection: 'asc' | 'desc';
  maxItems?: number;
  // Extended options for SOLID architecture
  minWeightThreshold?: number;
  assetClassFilter?: string[];
  showMetrics?: boolean;
  currencyCode?: string;
  precision?: number;
  showSkeleton?: boolean;
}

// Widget data types
export interface HoldingsData {
  holdings: Holding[];
  totalValue: number;
  currency: string;
  lastUpdated: Date;
}

// Legacy field mapping utilities
export interface LegacyHolding {
  symbol?: string;
  name?: string;
  asset_class?: string;
  quantity?: number;
  weight?: number;
  market_value?: number;
  current_price?: number;
}

/**
 * Transforms legacy snake_case holding to new camelCase format
 */
export function transformLegacyHolding(legacy: LegacyHolding): Holding {
  return {
    symbol: legacy.symbol || '',
    name: legacy.name || '',
    assetClass: legacy.asset_class || 'Unknown',
    quantity: legacy.quantity || 0,
    marketValue: legacy.market_value || 0,
    currentPrice: legacy.current_price || 0,
    weight: legacy.weight || 0,
  };
}

// Additional widget-specific configuration types will be added here as needed