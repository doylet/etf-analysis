/**
 * Widget Configuration and Management Types
 * Defines the structure for dynamic widget management
 */

export interface WidgetConfig {
  id: string;
  type: WidgetType;
  title: string;
  description?: string;
  position: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
  options?: Record<string, any>;
  isVisible: boolean;
  isMinimized: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export type WidgetType = 
  | 'portfolio-summary'
  | 'holdings-breakdown'
  | 'correlation-matrix'
  | 'monte-carlo'
  | 'benchmark-comparison'
  | 'dividend-analysis'
  | 'performance-analysis'
  | 'timeseries-analysis'
  | 'portfolio-transition'
  | 'news-event-analysis'
  | 'portfolio-optimizer'
  | 'constrained-optimization';

export interface WidgetDefinition {
  type: WidgetType;
  name: string;
  description: string;
  category: WidgetCategory;
  defaultSize: {
    w: number;
    h: number;
  };
  minSize: {
    w: number;
    h: number;
  };
  maxSize?: {
    w: number;
    h: number;
  };
  configurable: boolean;
  requiresPortfolio: boolean;
  refreshInterval?: number;
  icon?: string;
  tags?: string[];
}

export type WidgetCategory = 
  | 'overview'
  | 'analysis'
  | 'optimization'
  | 'performance'
  | 'risk'
  | 'market';

export interface DashboardLayout {
  id: string;
  name: string;
  description?: string;
  widgets: WidgetConfig[];
  createdAt: Date;
  updatedAt: Date;
  isDefault: boolean;
}

export interface WidgetAction {
  type: 'add' | 'remove' | 'update' | 'move' | 'resize' | 'minimize' | 'maximize' | 'configure';
  payload: {
    widgetId?: string;
    widgetType?: WidgetType;
    position?: WidgetConfig['position'];
    options?: Record<string, any>;
    config?: Partial<WidgetConfig>;
  };
}

export interface WidgetRegistry {
  [key in WidgetType]: WidgetDefinition;
}

export const WIDGET_REGISTRY: WidgetRegistry = {
  'portfolio-summary': {
    type: 'portfolio-summary',
    name: 'Portfolio Summary',
    description: 'Overview of portfolio performance and key metrics',
    category: 'overview',
    defaultSize: { w: 6, h: 4 },
    minSize: { w: 4, h: 3 },
    configurable: false,
    requiresPortfolio: true,
    refreshInterval: 900000, // 15 minutes
    icon: 'chart-line',
    tags: ['overview', 'performance', 'summary']
  },
  'holdings-breakdown': {
    type: 'holdings-breakdown',
    name: 'Holdings Breakdown',
    description: 'Detailed breakdown of portfolio holdings and allocations',
    category: 'overview',
    defaultSize: { w: 6, h: 5 },
    minSize: { w: 4, h: 4 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 1800000, // 30 minutes
    icon: 'pie-chart',
    tags: ['holdings', 'allocation', 'breakdown']
  },
  'correlation-matrix': {
    type: 'correlation-matrix',
    name: 'Correlation Matrix',
    description: 'Asset correlation analysis and risk assessment',
    category: 'risk',
    defaultSize: { w: 8, h: 6 },
    minSize: { w: 6, h: 5 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 3600000, // 1 hour
    icon: 'grid',
    tags: ['correlation', 'risk', 'analysis']
  },
  'monte-carlo': {
    type: 'monte-carlo',
    name: 'Monte Carlo Simulation',
    description: 'Portfolio performance simulation and projections',
    category: 'risk',
    defaultSize: { w: 8, h: 6 },
    minSize: { w: 6, h: 5 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 7200000, // 2 hours
    icon: 'trending-up',
    tags: ['simulation', 'projection', 'risk']
  },
  'benchmark-comparison': {
    type: 'benchmark-comparison',
    name: 'Benchmark Comparison',
    description: 'Compare portfolio performance against market benchmarks',
    category: 'performance',
    defaultSize: { w: 8, h: 5 },
    minSize: { w: 6, h: 4 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 900000, // 15 minutes
    icon: 'bar-chart',
    tags: ['benchmark', 'comparison', 'performance']
  },
  'dividend-analysis': {
    type: 'dividend-analysis',
    name: 'Dividend Analysis',
    description: 'Dividend income tracking and yield analysis',
    category: 'analysis',
    defaultSize: { w: 6, h: 5 },
    minSize: { w: 4, h: 4 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 3600000, // 1 hour
    icon: 'dollar-sign',
    tags: ['dividends', 'income', 'yield']
  },
  'performance-analysis': {
    type: 'performance-analysis',
    name: 'Performance Analysis',
    description: 'Comprehensive performance metrics and analytics',
    category: 'performance',
    defaultSize: { w: 8, h: 6 },
    minSize: { w: 6, h: 5 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 900000, // 15 minutes
    icon: 'activity',
    tags: ['performance', 'metrics', 'analytics']
  },
  'timeseries-analysis': {
    type: 'timeseries-analysis',
    name: 'Timeseries Analysis',
    description: 'Historical price and performance trend analysis',
    category: 'analysis',
    defaultSize: { w: 12, h: 6 },
    minSize: { w: 8, h: 5 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 1800000, // 30 minutes
    icon: 'timeline',
    tags: ['timeseries', 'trends', 'history']
  },
  'portfolio-transition': {
    type: 'portfolio-transition',
    name: 'Portfolio Transition',
    description: 'Analyze transitions between different portfolio allocations',
    category: 'optimization',
    defaultSize: { w: 8, h: 5 },
    minSize: { w: 6, h: 4 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 3600000, // 1 hour
    icon: 'shuffle',
    tags: ['transition', 'rebalancing', 'optimization']
  },
  'news-event-analysis': {
    type: 'news-event-analysis',
    name: 'News & Events',
    description: 'Market news and events affecting portfolio holdings',
    category: 'market',
    defaultSize: { w: 6, h: 6 },
    minSize: { w: 4, h: 5 },
    configurable: true,
    requiresPortfolio: false,
    refreshInterval: 300000, // 5 minutes
    icon: 'newspaper',
    tags: ['news', 'events', 'market']
  },
  'portfolio-optimizer': {
    type: 'portfolio-optimizer',
    name: 'Portfolio Optimizer',
    description: 'Optimize portfolio allocation using modern portfolio theory',
    category: 'optimization',
    defaultSize: { w: 8, h: 7 },
    minSize: { w: 6, h: 6 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 7200000, // 2 hours
    icon: 'target',
    tags: ['optimization', 'allocation', 'efficiency']
  },
  'constrained-optimization': {
    type: 'constrained-optimization',
    name: 'Constrained Optimization',
    description: 'Portfolio optimization with custom constraints and limits',
    category: 'optimization',
    defaultSize: { w: 8, h: 7 },
    minSize: { w: 6, h: 6 },
    configurable: true,
    requiresPortfolio: true,
    refreshInterval: 7200000, // 2 hours
    icon: 'settings',
    tags: ['optimization', 'constraints', 'custom']
  }
};

export const WIDGET_CATEGORIES = [
  { id: 'overview', name: 'Overview', color: '#3B82F6' },
  { id: 'analysis', name: 'Analysis', color: '#8B5CF6' },
  { id: 'optimization', name: 'Optimization', color: '#10B981' },
  { id: 'performance', name: 'Performance', color: '#F59E0B' },
  { id: 'risk', name: 'Risk Management', color: '#EF4444' },
  { id: 'market', name: 'Market Data', color: '#6B7280' }
] as const;