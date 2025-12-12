/**
 * Widget Metadata Registry
 * Defines content characteristics, priorities, and layout requirements for dynamic layout algorithm
 * Size configurations are imported from widget components for better co-location
 */

import { ResponsiveSize } from '../services/layout-algorithm';
import { WIDGET_SIZE_CONFIG as PORTFOLIO_SUMMARY_CONFIG } from './PortfolioSummaryWidget';
import { WIDGET_SIZE_CONFIG as HOLDINGS_CONFIG } from './HoldingsWidget';
import { WIDGET_SIZE_CONFIG as BENCHMARK_CONFIG } from './BenchmarkComparisonWidget';
import { WIDGET_SIZE_CONFIG as DIVIDEND_CONFIG } from './DividendAnalysisWidget';
import { WIDGET_SIZE_CONFIG as PERFORMANCE_CONFIG } from './PerformanceWidget';
import { WIDGET_SIZE_CONFIG as TIMESERIES_CONFIG } from './TimeseriesAnalysisWidget';
import { WIDGET_SIZE_CONFIG as TRANSITION_CONFIG } from './PortfolioTransitionWidget';
import { WIDGET_SIZE_CONFIG as NEWS_CONFIG } from './NewsEventAnalysisWidget';
import { WIDGET_SIZE_CONFIG as OPTIMIZER_CONFIG } from './PortfolioOptimizerWidget';
import { WIDGET_SIZE_CONFIG as CONSTRAINED_CONFIG } from './ConstrainedOptimizationWidget';
import { WIDGET_SIZE_CONFIG as CORRELATION_CONFIG } from './CorrelationMatrixWidget';
import { WIDGET_SIZE_CONFIG as MONTE_CARLO_CONFIG } from './MonteCarloWidget';
import { WIDGET_SIZE_CONFIG as HOLDINGS_BREAKDOWN_CONFIG } from './HoldingsBreakdownWidget';

export type ContentType = 'compact' | 'width-heavy' | 'height-heavy' | 'square' | 'full-width' | 'balanced';

export interface WidgetMetadata {
  contentType: ContentType;
  priority: number; // 0-100, higher = more important
  minSize: ResponsiveSize;
  aspectRatioPreference: number; // width/height ratio
  isScrollable: boolean;
  requiresFullWidth: boolean;
}

/**
 * Widget metadata defining content requirements and priorities
 * Used by dynamic layout algorithm to optimize placement
 * Priority is centralized here, size configs come from widget components
 */
export const WIDGET_METADATA: Record<string, WidgetMetadata> = {
  'portfolio-summary': {
    ...PORTFOLIO_SUMMARY_CONFIG,
    priority: 100,
  },
  'holdings': {
    ...HOLDINGS_CONFIG,
    priority: 90,
  },
  'benchmark': {
    ...BENCHMARK_CONFIG,
    priority: 75,
  },
  'dividend': {
    ...DIVIDEND_CONFIG,
    priority: 60,
  },
  'performance': {
    ...PERFORMANCE_CONFIG,
    priority: 80,
  },
  'timeseries': {
    ...TIMESERIES_CONFIG,
    priority: 95,
  },
  'transition': {
    ...TRANSITION_CONFIG,
    priority: 50,
  },
  'news': {
    ...NEWS_CONFIG,
    priority: 55,
  },
  'optimizer': {
    ...OPTIMIZER_CONFIG,
    priority: 60,
  },
  'constrained': {
    ...CONSTRAINED_CONFIG,
    priority: 55,
  },
  'correlation-matrix': {
    ...CORRELATION_CONFIG,
    priority: 85,
  },
  'monte-carlo': {
    ...MONTE_CARLO_CONFIG,
    priority: 65,
  },
  'holdings-breakdown': {
    ...HOLDINGS_BREAKDOWN_CONFIG,
    priority: 75,
  },
};

export function getWidgetMetadata(widgetId: string): WidgetMetadata {
  return WIDGET_METADATA[widgetId] || {
    contentType: 'balanced',
    priority: 50,
    minSize: { w: 4, h: 4 },
    aspectRatioPreference: 1.0,
    isScrollable: true,
    requiresFullWidth: false,
  };
}
