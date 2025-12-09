/**
 * Dashboard Page with Working Widgets
 */

'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { Responsive, WidthProvider, Layout, Layouts } from 'react-grid-layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

// Import working hooks
import { 
  usePortfolioSummary, 
  useHoldingsBreakdown,
  useBenchmarkComparison,
  useDividendAnalysis,
  usePerformanceAnalysis,
  useTimeseriesAnalysis,
  usePortfolioTransition,
  useNewsEventAnalysis,
  usePortfolioOptimizer,
  useConstrainedOptimization
} from '@/hooks/use-portfolio-widgets';

// Import legacy components
import CorrelationMatrix from '@/components/CorrelationMatrix';
import MonteCarloSimulation from '@/components/MonteCarloSimulation';

import { Plus, X } from 'lucide-react';

// Import CSS for react-grid-layout
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface WidgetInstance {
  id: string;
  type: string;
  name: string;
  component: React.ComponentType<{ portfolioId?: string }>;
  position: {
    i: string;
    x: number;
    y: number;
    w: number;
    h: number;
  };
}

// Simple working widget components
function PortfolioSummaryWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = usePortfolioSummary({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-xl font-bold text-foreground">${data.total_value.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Total Value</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className={`text-xl font-bold ${data.total_return >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            ${data.total_return.toLocaleString()}
          </div>
          <div className="text-xs text-muted-foreground">Total Return</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-xl font-bold text-foreground">{data.positions}</div>
          <div className="text-xs text-muted-foreground">Positions</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-xl font-bold text-foreground">${data.allocated_cash.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Cash</div>
        </div>
      </div>
    </div>
  );
}

function HoldingsWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = useHoldingsBreakdown({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-2 overflow-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left p-2 text-muted-foreground font-medium">Symbol</th>
            <th className="text-right p-2 text-muted-foreground font-medium">Value</th>
            <th className="text-right p-2 text-muted-foreground font-medium">Weight</th>
            <th className="text-right p-2 text-muted-foreground font-medium">Return</th>
          </tr>
        </thead>
        <tbody>
          {data.holdings.map((holding) => (
            <tr key={holding.symbol} className="border-b border-border hover:bg-muted/50">
              <td className="p-2 font-medium text-foreground">{holding.symbol}</td>
              <td className="text-right p-2 text-foreground">${holding.current_value.toLocaleString()}</td>
              <td className="text-right p-2 text-foreground">{(holding.weight_percent * 100).toFixed(1)}%</td>
              <td className={`text-right p-2 ${holding.total_return >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {holding.total_return >= 0 ? '+' : ''}{holding.total_return_percent.toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BenchmarkComparisonWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = useBenchmarkComparison({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.portfolio_return.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Portfolio Return</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.benchmark_return.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Benchmark Return</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.alpha.toFixed(2)}</div>
          <div className="text-xs text-muted-foreground">Alpha</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.sharpe_ratio.toFixed(2)}</div>
          <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
        </div>
      </div>
    </div>
  );
}

function DividendAnalysisWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = useDividendAnalysis({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">${data.total_dividends.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Total Dividends</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.dividend_yield.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Yield</div>
        </div>
      </div>
      {data.top_dividend_holdings && data.top_dividend_holdings.length > 0 && (
        <div className="mt-3">
          <div className="text-xs font-medium text-muted-foreground mb-2">Top Dividend Holdings</div>
          <div className="space-y-1">
            {data.top_dividend_holdings.slice(0, 3).map((holding) => (
              <div key={holding.symbol} className="flex justify-between text-xs">
                <span className="text-foreground">{holding.symbol}</span>
                <span className="text-muted-foreground">{holding.yield.toFixed(2)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function PerformanceWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = usePerformanceAnalysis({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.total_return.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Total Return</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.annualized_return.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Annualized</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.volatility.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Volatility</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.sharpe_ratio.toFixed(2)}</div>
          <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
        </div>
      </div>
    </div>
  );
}

function TimeseriesAnalysisWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = useTimeseriesAnalysis({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.statistics.total_return.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Total Return</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.statistics.volatility.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Volatility</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.statistics.sharpe_ratio.toFixed(2)}</div>
          <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-destructive">{data.statistics.max_drawdown.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Max Drawdown</div>
        </div>
      </div>
      {data.price_data && data.price_data.length > 0 && (
        <div className="mt-2 text-xs text-muted-foreground text-center">
          {data.price_data.length} data points
        </div>
      )}
    </div>
  );
}

function PortfolioTransitionWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = usePortfolioTransition({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="text-sm font-medium text-foreground mb-2">Required Trades</div>
      {data.required_trades && data.required_trades.length > 0 ? (
        <div className="space-y-2 max-h-40 overflow-auto">
          {data.required_trades.slice(0, 5).map((trade, idx) => (
            <div key={idx} className="flex items-center justify-between p-2 bg-muted rounded-md">
              <div className="flex items-center gap-2">
                <span className={`text-xs font-medium px-2 py-1 rounded ${
                  trade.action === 'buy' ? 'bg-green-600/20 text-green-600 dark:text-green-400' : 'bg-red-600/20 text-red-600 dark:text-red-400'
                }`}>
                  {trade.action.toUpperCase()}
                </span>
                <span className="text-sm text-foreground">{trade.symbol}</span>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-foreground">{trade.shares} shares</div>
                <div className="text-xs text-muted-foreground">${trade.value.toLocaleString()}</div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-sm text-muted-foreground text-center py-4">No trades required</div>
      )}
      <div className="grid grid-cols-2 gap-3 mt-3 pt-3 border-t border-border">
        <div className="text-center p-2 bg-muted rounded-md">
          <div className="text-sm font-bold text-foreground">${data.transition_cost?.toLocaleString() || 0}</div>
          <div className="text-xs text-muted-foreground">Cost</div>
        </div>
        <div className="text-center p-2 bg-muted rounded-md">
          <div className="text-sm font-bold text-foreground">
            {data.expected_impact?.risk_change?.toFixed(2) || 0}%
          </div>
          <div className="text-xs text-muted-foreground">Risk Change</div>
        </div>
      </div>
    </div>
  );
}

function NewsEventAnalysisWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = useNewsEventAnalysis({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">
            {data.sentiment_analysis?.overall_sentiment?.toFixed(2) || 0}
          </div>
          <div className="text-xs text-muted-foreground">Overall Sentiment</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">
            {data.market_impact?.price_correlation?.toFixed(2) || 0}
          </div>
          <div className="text-xs text-muted-foreground">Price Correlation</div>
        </div>
      </div>
      {data.events && data.events.length > 0 && (
        <div className="mt-3">
          <div className="text-xs font-medium text-muted-foreground mb-2">Recent Events</div>
          <div className="space-y-2 max-h-40 overflow-auto">
            {data.events.slice(0, 3).map((event, idx) => (
              <div key={idx} className="p-2 bg-muted rounded-md">
                <div className="text-xs font-medium text-foreground mb-1">{event.title}</div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    {new Date(event.date).toLocaleDateString()}
                  </span>
                  <span className={`text-xs ${
                    event.sentiment >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  }`}>
                    Sentiment: {event.sentiment.toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function PortfolioOptimizerWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = usePortfolioOptimizer({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.expected_return.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Expected Return</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.expected_risk.toFixed(2)}%</div>
          <div className="text-xs text-muted-foreground">Expected Risk</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">{data.sharpe_ratio.toFixed(2)}</div>
          <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
        </div>
      </div>
      {data.improvement_metrics && (
        <div className="mt-3 p-3 bg-muted rounded-md">
          <div className="text-xs font-medium text-muted-foreground mb-2">Improvements</div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <div className="text-sm font-bold text-green-600 dark:text-green-400">
                +{data.improvement_metrics.return_improvement.toFixed(2)}%
              </div>
              <div className="text-xs text-muted-foreground">Return</div>
            </div>
            <div>
              <div className="text-sm font-bold text-green-600 dark:text-green-400">
                {data.improvement_metrics.risk_reduction.toFixed(2)}%
              </div>
              <div className="text-xs text-muted-foreground">Risk</div>
            </div>
            <div>
              <div className="text-sm font-bold text-green-600 dark:text-green-400">
                +{data.improvement_metrics.sharpe_improvement.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">Sharpe</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ConstrainedOptimizationWidget({ portfolioId }: { portfolioId?: string }) {
  const { data, loading, error } = useConstrainedOptimization({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">
            {data.optimization_result.return.toFixed(2)}%
          </div>
          <div className="text-xs text-muted-foreground">Return</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">
            {data.optimization_result.risk.toFixed(2)}%
          </div>
          <div className="text-xs text-muted-foreground">Risk</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-lg font-bold text-foreground">
            {data.optimization_result.sharpe_ratio.toFixed(2)}
          </div>
          <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className={`text-lg font-bold ${
            data.constraints_satisfied ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            {data.constraints_satisfied ? 'YES' : 'NO'}
          </div>
          <div className="text-xs text-muted-foreground">Constraints Met</div>
        </div>
      </div>
      {data.constraint_violations && data.constraint_violations.length > 0 && (
        <div className="mt-3 p-2 bg-destructive/10 rounded-md">
          <div className="text-xs font-medium text-destructive mb-1">Violations</div>
          {data.constraint_violations.slice(0, 3).map((violation, idx) => (
            <div key={idx} className="text-xs text-muted-foreground">
              {violation.constraint}: {violation.violation.toFixed(2)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const AVAILABLE_WIDGETS = [
  {
    type: 'portfolio-summary',
    name: 'Portfolio Summary',
    component: PortfolioSummaryWidget,
    defaultSize: { w: 6, h: 4 }
  },
  {
    type: 'holdings',
    name: 'Holdings',
    component: HoldingsWidget,
    defaultSize: { w: 6, h: 5 }
  },
  {
    type: 'benchmark-comparison',
    name: 'Benchmark Comparison',
    component: BenchmarkComparisonWidget,
    defaultSize: { w: 6, h: 4 }
  },
  {
    type: 'dividend-analysis',
    name: 'Dividend Analysis',
    component: DividendAnalysisWidget,
    defaultSize: { w: 6, h: 5 }
  },
  {
    type: 'performance',
    name: 'Performance',
    component: PerformanceWidget,
    defaultSize: { w: 6, h: 4 }
  },
  {
    type: 'timeseries-analysis',
    name: 'Timeseries Analysis',
    component: TimeseriesAnalysisWidget,
    defaultSize: { w: 6, h: 4 }
  },
  {
    type: 'portfolio-transition',
    name: 'Portfolio Transition',
    component: PortfolioTransitionWidget,
    defaultSize: { w: 6, h: 6 }
  },
  {
    type: 'news-events',
    name: 'News & Events',
    component: NewsEventAnalysisWidget,
    defaultSize: { w: 6, h: 6 }
  },
  {
    type: 'portfolio-optimizer',
    name: 'Portfolio Optimizer',
    component: PortfolioOptimizerWidget,
    defaultSize: { w: 6, h: 5 }
  },
  {
    type: 'constrained-optimization',
    name: 'Constrained Optimization',
    component: ConstrainedOptimizationWidget,
    defaultSize: { w: 6, h: 5 }
  },
  {
    type: 'correlation-matrix',
    name: 'Correlation Matrix',
    component: CorrelationMatrix,
    defaultSize: { w: 12, h: 6 }
  },
  {
    type: 'monte-carlo',
    name: 'Monte Carlo Simulation',
    component: MonteCarloSimulation,
    defaultSize: { w: 6, h: 6 }
  }
];

export default function DashboardPage() {
  const [portfolioId] = useState<string | undefined>();
  const [showWidgetPalette, setShowWidgetPalette] = useState(false);
  
  // Initialize with default widgets
  const [widgets, setWidgets] = useState<WidgetInstance[]>([
    {
      id: 'portfolio-summary-1',
      type: 'portfolio-summary',
      name: 'Portfolio Summary',
      component: PortfolioSummaryWidget,
      position: { i: 'portfolio-summary-1', x: 0, y: 0, w: 6, h: 4 }
    },
    {
      id: 'holdings-1',
      type: 'holdings',
      name: 'Holdings',
      component: HoldingsWidget,
      position: { i: 'holdings-1', x: 6, y: 0, w: 6, h: 5 }
    },
    {
      id: 'correlation-matrix-1',
      type: 'correlation-matrix',
      name: 'Correlation Matrix',
      component: CorrelationMatrix,
      position: { i: 'correlation-matrix-1', x: 0, y: 5, w: 12, h: 6 }
    },
    {
      id: 'monte-carlo-1',
      type: 'monte-carlo',
      name: 'Monte Carlo Simulation',
      component: MonteCarloSimulation,
      position: { i: 'monte-carlo-1', x: 0, y: 11, w: 6, h: 6 }
    }
  ]);

  // Convert widgets to grid layout format
  const layouts = useMemo((): Layouts => {
    const layout: Layout[] = widgets.map(widget => ({
      ...widget.position,
      isDraggable: true,
      isResizable: true
    }));

    return {
      lg: layout,
      md: layout,
      sm: layout,
      xs: layout.map(item => ({ ...item, w: Math.min(item.w, 4) })),
      xxs: layout.map(item => ({ ...item, w: 2 }))
    };
  }, [widgets]);

  // Handle layout changes from drag/resize
  const handleLayoutChange = useCallback((layout: Layout[]) => {
    setWidgets(prev => prev.map(widget => {
      const layoutItem = layout.find(item => item.i === widget.id);
      return layoutItem ? {
        ...widget,
        position: {
          i: widget.id,
          x: layoutItem.x,
          y: layoutItem.y,
          w: layoutItem.w,
          h: layoutItem.h
        }
      } : widget;
    }));
  }, []);

  const addWidget = useCallback((type: string) => {
    const widgetDef = AVAILABLE_WIDGETS.find(w => w.type === type);
    if (!widgetDef) return;

    const timestamp = Date.now();
    const newWidget: WidgetInstance = {
      id: `${type}-${timestamp}`,
      type,
      name: widgetDef.name,
      position: {
        i: `${type}-${timestamp}`,
        x: 0,
        y: 0,
        w: widgetDef.defaultSize.w,
        h: widgetDef.defaultSize.h
      }
    };

    // Add component
    newWidget.component = widgetDef.component;

    setWidgets(prev => [...prev, newWidget]);
    setShowWidgetPalette(false);
  }, []);

  const removeWidget = (widgetId: string) => {
    setWidgets(prev => prev.filter(w => w.id !== widgetId));
  };

  const handleRefreshAll = () => {
    // Trigger re-renders by updating widget keys
    setWidgets(prev => [...prev]);
  };

  // Simple widget renderer
  function WidgetRenderer({ widget }: { widget: WidgetInstance }) {
    const Component = widget.component;
    return <Component portfolioId={portfolioId} />;
  }

  // Render individual widget with remove button
  const renderWidget = (widget: WidgetInstance) => (
    <Card key={widget.id} className="h-full relative overflow-hidden cursor-move">
      <CardHeader className="py-2 px-3 border-b">
        <CardTitle className="text-sm font-medium flex items-center justify-between">
          <span className="truncate">{widget.name}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              removeWidget(widget.id);
            }}
            className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <X className="h-3 w-3" />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 h-full overflow-auto">
        <WidgetRenderer widget={widget} />
      </CardContent>
    </Card>
  );

  const availableToAdd = AVAILABLE_WIDGETS.filter(
    available => !widgets.some(widget => widget.type === available.type)
  );

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 border-b bg-background">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="font-semibold text-lg">Portfolio Dashboard</h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>{widgets.length} widgets</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              onClick={() => setShowWidgetPalette(!showWidgetPalette)}
              className="gap-2"
              disabled={availableToAdd.length === 0}
            >
              <Plus className="h-4 w-4" />
              Add Widget
            </Button>
            
            <Button variant="outline" onClick={handleRefreshAll} className="gap-2">
              Refresh
            </Button>
          </div>
        </div>

      {/* Widget Palette */}
      {showWidgetPalette && (
          <div className="p-3 border-b bg-muted/30">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-sm font-medium">Add Widget:</span>
              {availableToAdd.map(widget => (
                <Button
                  key={widget.type}
                  variant="outline"
                  size="sm"
                  onClick={() => addWidget(widget.type)}
                  className="gap-2"
                >
                  <Plus className="h-3 w-3" />
                  {widget.name}
                </Button>
              ))}
              {availableToAdd.length === 0 && (
                <span className="text-sm text-muted-foreground">All widgets already added</span>
              )}
            </div>
          </div>
      )}

      {/* Main Dashboard Grid */}
      <div className="flex-1 overflow-auto">
          <ResponsiveGridLayout
            layouts={layouts}
            onLayoutChange={handleLayoutChange}
            breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
            cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
            rowHeight={60}
            margin={[12, 12]}
            isDraggable={true}
            isResizable={true}
            compactType="vertical"
            preventCollision={false}
            useCSSTransforms={true}
          >
            {widgets.map(widget => (
              <div key={widget.id} className="group">
                {renderWidget(widget)}
              </div>
            ))}
        </ResponsiveGridLayout>
        
        {widgets.length === 0 && (
            <div className="flex items-center justify-center h-96 border-2 border-dashed border-border rounded-lg">
              <div className="text-center">
                <h3 className="text-lg font-medium mb-2">No widgets added yet</h3>
                <p className="text-muted-foreground mb-4">
                  Click &ldquo;Add Widget&rdquo; to start building your dashboard
                </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}