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
  component: ComponentType<{ portfolioId?: string }>;
}

export const AVAILABLE_WIDGETS: WidgetConfig[] = [
  {
    id: 'portfolio-summary',
    name: 'Portfolio Summary',
    component: PortfolioSummaryWidget,
  },
  {
    id: 'holdings',
    name: 'Holdings Breakdown',
    component: HoldingsWidget,
  },
  {
    id: 'benchmark',
    name: 'Benchmark Comparison',
    component: BenchmarkComparisonWidget,
  },
  {
    id: 'dividend',
    name: 'Dividend Analysis',
    component: DividendAnalysisWidget,
  },
  {
    id: 'performance',
    name: 'Performance',
    component: PerformanceWidget,
  },
  {
    id: 'timeseries',
    name: 'Timeseries Analysis',
    component: TimeseriesAnalysisWidget,
  },
  {
    id: 'transition',
    name: 'Portfolio Transition',
    component: PortfolioTransitionWidget,
  },
  {
    id: 'news',
    name: 'News & Event Analysis',
    component: NewsEventAnalysisWidget,
  },
  {
    id: 'optimizer',
    name: 'Portfolio Optimizer',
    component: PortfolioOptimizerWidget,
  },
  {
    id: 'constrained',
    name: 'Constrained Optimization',
    component: ConstrainedOptimizationWidget,
  },
  {
    id: 'correlation-matrix',
    name: 'Correlation Matrix',
    component: CorrelationMatrixWidget,
  },
  {
    id: 'monte-carlo',
    name: 'Monte Carlo Simulation',
    component: MonteCarloWidget,
  },
  {
    id: 'holdings-breakdown',
    name: 'Holdings Breakdown',
    component: HoldingsBreakdownWidget,
  },
];

export function getWidgetComponent(widgetId: string): ComponentType<{ portfolioId?: string }> | null {
  const widget = AVAILABLE_WIDGETS.find((w) => w.id === widgetId);
  return widget?.component || null;
}

export const getWidgetTitle = (widgetId: string): string => {
  const widgetConfig = AVAILABLE_WIDGETS.find(w => w.id === widgetId);
  return widgetConfig?.name || widgetId;
};