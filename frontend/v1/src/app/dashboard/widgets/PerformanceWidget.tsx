import React, { useState } from 'react';
import { usePerformanceAnalysis } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { XCircle } from 'lucide-react';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 6, h: 4 },
  contentType: 'width-heavy' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.6,
  isScrollable: false,
} as const;

interface PerformanceWidgetProps {
  portfolioId?: string;
}

const PerformanceWidget: React.FC<PerformanceWidgetProps> = ({ portfolioId }) => {
  const [timePeriod, setTimePeriod] = useState('1Y');
  
  const { data, loading, isRefreshing, error } = usePerformanceAnalysis({ portfolioId, timePeriod });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Performance Data Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.total_return !== undefined && data.annualized_return !== undefined;

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
    <div className="flex flex-col h-full p-4">
      <div className="flex gap-2 flex-shrink-0">
        <select 
          value={timePeriod} 
          onChange={(e) => setTimePeriod(e.target.value)}
          className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
          disabled={isRefreshing}
        >
          {periods.map(p => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        {isRefreshing && (
          <span className="text-xs text-muted-foreground animate-pulse self-center">Updating...</span>
        )}
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 grid grid-cols-2 gap-3">
          <div className="text-center p-3 bg-muted rounded-md">
            <div className="text-lg font-bold text-foreground">{data.total_return?.toFixed(2)}%</div>
            <div className="text-xs text-muted-foreground">Total Return</div>
          </div>
          <div className="text-center p-3 bg-muted rounded-md">
            <div className="text-lg font-bold text-foreground">{data.annualized_return?.toFixed(2)}%</div>
            <div className="text-xs text-muted-foreground">Annualized</div>
          </div>
          <div className="text-center p-3 bg-muted rounded-md">
            <div className="text-lg font-bold text-foreground">{data.volatility?.toFixed(2)}%</div>
            <div className="text-xs text-muted-foreground">Volatility</div>
          </div>
          <div className="text-center p-3 bg-muted rounded-md">
            <div className="text-lg font-bold text-foreground">{data.sharpe_ratio?.toFixed(2)}</div>
            <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
          </div>
        </div>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Performance data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

PerformanceWidget.displayName = 'PerformanceWidget';

export default React.memo(PerformanceWidget);
