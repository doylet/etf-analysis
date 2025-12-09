import React, { useState } from 'react';
import { useBenchmarkComparison } from '@/hooks/use-portfolio-widgets';

interface BenchmarkComparisonWidgetProps {
  portfolioId?: string;
}

const BenchmarkComparisonWidget: React.FC<BenchmarkComparisonWidgetProps> = ({ portfolioId }) => {
  const [benchmark, setBenchmark] = useState('SPY');
  const [timePeriod, setTimePeriod] = useState('1Y');
  
  const { data, loading, error } = useBenchmarkComparison({ 
    portfolioId, 
    benchmark,
    timePeriod 
  });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.portfolio_return !== undefined && data.benchmark_return !== undefined;

  const benchmarks = [
    { value: 'SPY', label: 'S&P 500' },
    { value: 'QQQ', label: 'Nasdaq 100' },
    { value: 'DIA', label: 'Dow Jones' },
    { value: 'IWM', label: 'Russell 2000' },
    { value: 'VTI', label: 'Total US Market' },
    { value: 'EFA', label: 'International' },
    { value: 'AGG', label: 'US Bonds' },
    { value: 'GLD', label: 'Gold' },
  ];

  const periods = [
    { value: '1W', label: '1 Week' },
    { value: '1M', label: '1 Month' },
    { value: '3M', label: '3 Months' },
    { value: '6M', label: '6 Months' },
    { value: '1Y', label: '1 Year' },
    { value: '2Y', label: '2 Years' },
    { value: '5Y', label: '5 Years' },
  ];

  return (
    <div className="p-4 space-y-3">
      <div className="flex gap-2">
        <select 
          value={benchmark} 
          onChange={(e) => setBenchmark(e.target.value)}
          className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
        >
          {benchmarks.map(b => (
            <option key={b.value} value={b.value}>{b.label}</option>
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
      
      {hasFullData ? (
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center p-3 bg-muted rounded-md">
            <div className="text-lg font-bold text-foreground">{data.portfolio_return?.toFixed(2)}%</div>
            <div className="text-xs text-muted-foreground">Portfolio Return</div>
          </div>
          <div className="text-center p-3 bg-muted rounded-md">
            <div className="text-lg font-bold text-foreground">{data.benchmark_return?.toFixed(2)}%</div>
            <div className="text-xs text-muted-foreground">Benchmark Return</div>
          </div>
          <div className="text-center p-3 bg-muted rounded-md">
            <div className="text-lg font-bold text-foreground">{data.alpha?.toFixed(2)}</div>
            <div className="text-xs text-muted-foreground">Alpha</div>
          </div>
          <div className="text-center p-3 bg-muted rounded-md">
            <div className="text-lg font-bold text-foreground">{data.sharpe_ratio?.toFixed(2)}</div>
            <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
          </div>
        </div>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Benchmark comparison data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
          {data.benchmarks && <div className="text-xs mt-1">{Object.keys(data.benchmarks).length} benchmarks available</div>}
        </div>
      )}
    </div>
  );
};

BenchmarkComparisonWidget.displayName = 'BenchmarkComparisonWidget';

export default React.memo(BenchmarkComparisonWidget);
