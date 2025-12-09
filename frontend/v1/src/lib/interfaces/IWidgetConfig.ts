/**
 * Widget Configuration Interface
 * 
 * Purpose: Define the configuration structure for all widget types
 * Ensures type safety for widget configuration across the SOLID architecture
 */

export interface BaseWidgetConfig {
  type: string;
  variant?: string;
  title: string;
  refreshInterval?: number;
  cache?: boolean;
  errorRetryAttempts?: number;
}

export interface HoldingsWidgetConfig extends BaseWidgetConfig {
  type: 'holdings';
  variant: 'table' | 'percentage';
  portfolioId: string;
  showQuantity?: boolean;
  showWeight?: boolean;
  sortBy?: 'symbol' | 'value' | 'weight';
  sortOrder?: 'asc' | 'desc';
}

export interface PortfolioSummaryWidgetConfig extends BaseWidgetConfig {
  type: 'portfolio-summary';
  variant: 'standard' | 'compact' | 'detailed';
  showPercentages?: boolean;
  showCashAllocation?: boolean;
  showMarketStatus?: boolean;
  currencyFormat?: 'USD' | 'EUR' | 'GBP';
}

// Add more widget config types as they're implemented
export interface PerformanceWidgetConfig extends BaseWidgetConfig {
  type: 'performance';
  variant: 'chart' | 'table';
  timeRange?: '1D' | '1W' | '1M' | '3M' | '1Y' | 'YTD';
}

export interface NewsWidgetConfig extends BaseWidgetConfig {
  type: 'news';
  variant: 'headlines' | 'detailed';
  sources?: string[];
  maxItems?: number;
}

// Union type for all possible widget configurations
export type WidgetConfig = 
  | HoldingsWidgetConfig 
  | PortfolioSummaryWidgetConfig
  | PerformanceWidgetConfig
  | NewsWidgetConfig;

// Type guards for configuration validation
export function isHoldingsConfig(config: WidgetConfig): config is HoldingsWidgetConfig {
  return config.type === 'holdings';
}

export function isPortfolioSummaryConfig(config: WidgetConfig): config is PortfolioSummaryWidgetConfig {
  return config.type === 'portfolio-summary';
}

export function isPerformanceConfig(config: WidgetConfig): config is PerformanceWidgetConfig {
  return config.type === 'performance';
}

export function isNewsConfig(config: WidgetConfig): config is NewsWidgetConfig {
  return config.type === 'news';
}