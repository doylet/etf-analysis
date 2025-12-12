import React, { useState } from 'react';
import { useBenchmarkComparison } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { WidgetSelect } from '@/components/ui/widget/widget-controls';
import { XCircle, TrendingUp, TrendingDown, Activity, Target } from 'lucide-react';
import { formatPercent } from '@/lib/formatters';
import { TIME_PERIODS, COMMON_BENCHMARKS } from '@/lib/widget-constants';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 5 },
  contentType: 'balanced' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.0,
  isScrollable: true,
} as const;

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
  if (error) return (
    <WidgetInsight
      title="Benchmark Data Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.portfolio_return !== undefined && data.benchmark_return !== undefined;

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex gap-2 flex-shrink-0">
        <WidgetSelect
          value={benchmark}
          onChange={setBenchmark}
          options={COMMON_BENCHMARKS}
          className="flex-1"
        />
        <WidgetSelect
          value={timePeriod}
          onChange={setTimePeriod}
          options={TIME_PERIODS}
          className="flex-1"
        />
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3 mt-3">
          {/* Primary Metrics */}
          <div className="flex flex-wrap justify-center gap-3">
            <MetricCard
              title="Portfolio Return"
              value={formatPercent(data.portfolio_return / 100)}
              icon={data.portfolio_return && data.portfolio_return > 0 ? TrendingUp : TrendingDown}
              variant="default"
              size="sm"
              trend={data.portfolio_return && data.portfolio_return > 0 ? 'positive' : 'negative'}
            />
            <MetricCard
              title="Benchmark Return"
              value={formatPercent(data.benchmark_return / 100)}
              icon={data.benchmark_return && data.benchmark_return > 0 ? TrendingUp : TrendingDown}
              variant="default"
              size="sm"
              trend={data.benchmark_return && data.benchmark_return > 0 ? 'positive' : 'negative'}
            />
            <MetricCard
              title="Alpha"
              value={formatPercent(data.alpha / 100)}
              subtitle="Excess Return"
              icon={Target}
              variant={data.alpha && data.alpha > 0 ? 'highlighted' : 'default'}
              size="sm"
              trend={data.alpha && data.alpha > 0 ? 'positive' : 'negative'}
            />
            <MetricCard
              title="Beta"
              value={data.beta?.toFixed(2)}
              subtitle="Market Sensitivity"
              icon={Activity}
              variant="default"
              size="sm"
            />
          </MetricGroup>
          
          {/* Risk Metrics */}
          <MetricGroup layout="horizontal">
            <MetricCard
              title="Portfolio Sharpe"
              value={data.sharpe_ratio?.toFixed(2)}
              subtitle="Risk-Adjusted Return"
              icon={TrendingUp}
              variant="default"
              size="sm"
            />
            <MetricCard
              title="Benchmark Sharpe"
              value={data.benchmark_sharpe?.toFixed(2) ?? 'N/A'}
              subtitle="Risk-Adjusted Return"
              icon={TrendingUp}
              variant="default"
              size="sm"
            />
            <MetricCard
              title="Portfolio Vol"
              value={data.portfolio_volatility ? `${data.portfolio_volatility.toFixed(2)}%` : 'N/A'}
              subtitle="Annualized"
              icon={Activity}
              variant="subtle"
              size="sm"
            />
            <MetricCard
              title="Benchmark Vol"
              value={data.benchmark_volatility ? `${data.benchmark_volatility.toFixed(2)}%` : 'N/A'}
              subtitle="Annualized"
              icon={Activity}
              variant="subtle"
              size="sm"
            />
          </div>
          
          {/* Information Ratio */}
          {data.information_ratio !== undefined && (
            <MetricCard
              title="Information Ratio"
              value={data.information_ratio.toFixed(2)}
              subtitle="Risk-Adjusted Excess Return"
              icon={Target}
              variant="highlighted"
              size="sm"
              trend={data.information_ratio > 0 ? 'positive' : 'negative'}
            />
          )}
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
