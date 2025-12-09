import React, { useState } from 'react';
import { usePortfolioOptimizer } from '@/hooks/use-portfolio-widgets';

interface PortfolioOptimizerWidgetProps {
  portfolioId?: string;
}

const PortfolioOptimizerWidget: React.FC<PortfolioOptimizerWidgetProps> = ({ portfolioId }) => {
  const [mode, setMode] = useState('Max Sharpe');
  const [timePeriod, setTimePeriod] = useState('1Y');
  const [includeDividends, setIncludeDividends] = useState(true);
  
  const { data, loading, error } = usePortfolioOptimizer({ portfolioId, mode, timePeriod, includeDividends });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.expected_return !== undefined && data.expected_risk !== undefined;

  const modes = [
    { value: 'Max Sharpe', label: 'Max Sharpe' },
    { value: 'Min Volatility', label: 'Min Volatility' },
    { value: 'Efficient Frontier', label: 'Efficient Frontier' },
    { value: 'Max Return', label: 'Max Return' },
    { value: 'Target Return', label: 'Target Return' },
  ];

  const periods = [
    { value: '1M', label: '1 Month' },
    { value: '3M', label: '3 Months' },
    { value: '6M', label: '6 Months' },
    { value: '1Y', label: '1 Year' },
    { value: '2Y', label: '2 Years' },
    { value: '5Y', label: '5 Years' },
  ];

  return (
    <div className="p-4 space-y-3">
      <div className="flex flex-col gap-2">
        <div className="flex gap-2">
          <select 
            value={mode} 
            onChange={(e) => setMode(e.target.value)}
            className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
          >
            {modes.map(m => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
          <select 
            value={timePeriod} 
            onChange={(e) => setTimePeriod(e.target.value)}
            className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
          >
            {periods.map(p => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        </div>
        <label className="flex items-center gap-2 text-sm text-foreground">
          <input 
            type="checkbox" 
            checked={includeDividends} 
            onChange={(e) => setIncludeDividends(e.target.checked)}
            className="rounded"
          />
          Include Dividends
        </label>
      </div>
      
      {hasFullData ? (
        <>
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">{data.expected_return?.toFixed(2)}%</div>
              <div className="text-xs text-muted-foreground">Expected Return</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">{data.expected_risk?.toFixed(2)}%</div>
              <div className="text-xs text-muted-foreground">Expected Risk</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">{data.sharpe_ratio?.toFixed(2)}</div>
              <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
            </div>
          </div>
          {data.improvement_metrics && (
            <div className="mt-3 p-3 bg-muted rounded-md">
              <div className="text-xs font-medium text-muted-foreground mb-2">Improvements</div>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div>
                  <div className="text-sm font-bold text-green-600 dark:text-green-400">
                    +{data.improvement_metrics.return_improvement?.toFixed(2)}%
                  </div>
                  <div className="text-xs text-muted-foreground">Return</div>
                </div>
                <div>
                  <div className="text-sm font-bold text-green-600 dark:text-green-400">
                    {data.improvement_metrics.risk_reduction?.toFixed(2)}%
                  </div>
                  <div className="text-xs text-muted-foreground">Risk</div>
                </div>
                <div>
                  <div className="text-sm font-bold text-green-600 dark:text-green-400">
                    +{data.improvement_metrics.sharpe_improvement?.toFixed(2)}
                  </div>
              <div className="text-xs text-muted-foreground">Sharpe</div>
            </div>
          </div>
        </div>
          )}
        </>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Portfolio optimizer data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

PortfolioOptimizerWidget.displayName = 'PortfolioOptimizerWidget';

export default React.memo(PortfolioOptimizerWidget);
