import React, { useState } from 'react';
import { usePortfolioTransition } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { WidgetSelect } from '@/components/ui/widget/widget-controls';
import { formatCurrency } from '@/lib/formatters';
import { XCircle } from 'lucide-react';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 4 },
  contentType: 'balanced' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.5,
  isScrollable: false,
} as const;

interface PortfolioTransitionWidgetProps {
  portfolioId?: string;
}

const PortfolioTransitionWidget: React.FC<PortfolioTransitionWidgetProps> = ({ portfolioId }) => {
  const [transitionMethod, setTransitionMethod] = useState('Gradual');
  const [optimizationPriority, setOptimizationPriority] = useState('Balance');
  
  const { data, loading, error } = usePortfolioTransition({ 
    currentPortfolioId: portfolioId, 
    transitionMethod, 
    optimizationPriority 
  });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Transition Data Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.required_trades !== undefined && Array.isArray(data.required_trades);

  const transitionMethods = [
    { value: 'Immediate', label: 'Immediate' },
    { value: 'Gradual', label: 'Gradual' },
    { value: 'Tax Optimized', label: 'Tax Optimized' },
    { value: 'Cost Minimized', label: 'Cost Minimized' },
  ];

  const optimizationPriorities = [
    { value: 'Cost', label: 'Cost' },
    { value: 'Speed', label: 'Speed' },
    { value: 'Tax Efficiency', label: 'Tax Efficiency' },
    { value: 'Balance', label: 'Balance' },
  ];

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex gap-2 flex-shrink-0">
        <WidgetSelect
          value={transitionMethod}
          onChange={setTransitionMethod}
          options={transitionMethods}
          className="flex-1"
        />
        <WidgetSelect
          value={optimizationPriority}
          onChange={setOptimizationPriority}
          options={optimizationPriorities}
          className="flex-1"
        />
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3">
          <div className="text-sm font-medium text-foreground mb-2">Required Trades</div>
          {data.required_trades.length > 0 ? (
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
                    <div className="text-xs text-muted-foreground">{formatCurrency(trade.value || 0)}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground text-center py-4">No trades required</div>
          )}
          <div className="flex flex-wrap justify-center gap-3 mt-3 pt-3 border-t border-border">
            <div className="text-center p-2 bg-muted rounded-md">
              <div className="text-sm font-bold text-foreground">{formatCurrency(data.transition_cost || 0)}</div>
              <div className="text-xs text-muted-foreground">Cost</div>
            </div>
            <div className="text-center p-2 bg-muted rounded-md">
              <div className="text-sm font-bold text-foreground">
                {(data.expected_impact?.risk_change || 0).toFixed(2)}%
              </div>
              <div className="text-xs text-muted-foreground">Risk Change</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Portfolio transition data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

PortfolioTransitionWidget.displayName = 'PortfolioTransitionWidget';

export default React.memo(PortfolioTransitionWidget);
