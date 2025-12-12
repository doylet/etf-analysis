import React, { useState } from 'react';
import { usePerformanceAnalysis } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { MetricCard } from '@/components/ui/metric-card';
import { WidgetSelect } from '@/components/ui/widget/widget-controls';
import { XCircle, TrendingUp, Activity, Target } from 'lucide-react';
import { formatPercent } from '@/lib/formatters';
import { TIME_PERIODS } from '@/lib/widget-constants';
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

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-2 flex-shrink-0">
        <WidgetSelect
          value={timePeriod}
          onChange={setTimePeriod}
          options={TIME_PERIODS}
          disabled={isRefreshing}
          className="flex-1"
        />
        {isRefreshing && (
          <span className="text-xs text-muted-foreground animate-pulse self-center">Updating...</span>
        )}
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 grid grid-cols-2 gap-3 mt-3">
          <MetricCard
            title="Total Return"
            value={formatPercent(data.total_return / 100)}
            icon={TrendingUp}
            variant="default"
            size="sm"
            trend={data.total_return && data.total_return > 0 ? 'positive' : 'negative'}
          />
          <MetricCard
            title="Annualized"
            value={formatPercent(data.annualized_return / 100)}
            icon={TrendingUp}
            variant="default"
            size="sm"
          />
          <MetricCard
            title="Volatility"
            value={formatPercent(data.volatility / 100)}
            icon={Activity}
            variant="default"
            size="sm"
          />
          <MetricCard
            title="Sharpe Ratio"
            value={data.sharpe_ratio?.toFixed(2) || '0.00'}
            icon={Target}
            variant="default"
            size="sm"
          />
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
