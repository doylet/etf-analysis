import { ComponentType } from 'react';
import {
  PortfolioSummaryWidget,
  HoldingsWidget,
  BenchmarkComparisonWidget,
  DividendAnalysisWidget,
  PerformanceWidget,
  TimeseriesAnalysisWidget,
  PortfolioTransitionWidget,
  NewsEventAnalysisWidget,
  PortfolioOptimizerWidget,
  ConstrainedOptimizationWidget,
  CorrelationMatrixWidget,
  MonteCarloWidget,
  HoldingsBreakdownWidget,
} from './index';

export interface WidgetConfig {
  id: string;
  name: string;
  defaultSize: { w: number; h: number };
  component: ComponentType<{ portfolioId?: string }>;
}

export const AVAILABLE_WIDGETS: WidgetConfig[] = [
  {
    id: 'portfolio-summary',
    name: 'Portfolio Summary',
    defaultSize: { w: 4, h: 2 },
    component: PortfolioSummaryWidget,
  },
  {
    id: 'holdings',
    name: 'Holdings Breakdown',
    defaultSize: { w: 6, h: 3 },
    component: HoldingsWidget,
  },
  {
    id: 'benchmark',
    name: 'Benchmark Comparison',
    defaultSize: { w: 6, h: 3 },
    component: BenchmarkComparisonWidget,
  },
  {
    id: 'dividend',
    name: 'Dividend Analysis',
    defaultSize: { w: 6, h: 3 },
    component: DividendAnalysisWidget,
  },
  {
    id: 'performance',
    name: 'Performance',
    defaultSize: { w: 6, h: 3 },
    component: PerformanceWidget,
  },
  {
    id: 'timeseries',
    name: 'Timeseries Analysis',
    defaultSize: { w: 12, h: 4 },
    component: TimeseriesAnalysisWidget,
  },
  {
    id: 'transition',
    name: 'Portfolio Transition',
    defaultSize: { w: 6, h: 3 },
    component: PortfolioTransitionWidget,
  },
  {
    id: 'news',
    name: 'News & Event Analysis',
    defaultSize: { w: 6, h: 3 },
    component: NewsEventAnalysisWidget,
  },
  {
    id: 'optimizer',
    name: 'Portfolio Optimizer',
    defaultSize: { w: 6, h: 4 },
    component: PortfolioOptimizerWidget,
  },
  {
    id: 'constrained',
    name: 'Constrained Optimization',
    defaultSize: { w: 6, h: 4 },
    component: ConstrainedOptimizationWidget,
  },
  {
    id: 'correlation-matrix',
    name: 'Correlation Matrix',
    defaultSize: { w: 12, h: 6 },
    component: CorrelationMatrixWidget,
  },
  {
    id: 'monte-carlo',
    name: 'Monte Carlo Simulation',
    defaultSize: { w: 6, h: 6 },
    component: MonteCarloWidget,
  },
  {
    id: 'holdings-breakdown',
    name: 'Holdings Breakdown',
    defaultSize: { w: 6, h: 4 },
    component: HoldingsBreakdownWidget,
  },
];

export function getWidgetComponent(widgetId: string): ComponentType<{ portfolioId?: string }> | null {
  const widget = AVAILABLE_WIDGETS.find((w) => w.id === widgetId);
  return widget?.component || null;
}
