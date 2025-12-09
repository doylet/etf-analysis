import React, { useState } from 'react';
import { usePortfolioTransition } from '@/hooks/use-portfolio-widgets';

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
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
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
    <div className="p-4 space-y-3">
      <div className="flex gap-2">
        <select 
          value={transitionMethod} 
          onChange={(e) => setTransitionMethod(e.target.value)}
          className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
        >
          {transitionMethods.map(t => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
        <select 
          value={optimizationPriority} 
          onChange={(e) => setOptimizationPriority(e.target.value)}
          className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
        >
          {optimizationPriorities.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>
      
      {hasFullData ? (
        <>
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
                    <div className="text-xs text-muted-foreground">${trade.value?.toLocaleString()}</div>
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
        </>
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
