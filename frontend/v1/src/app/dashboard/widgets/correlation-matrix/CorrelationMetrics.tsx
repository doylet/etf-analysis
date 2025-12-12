'use client';

import { Activity, TrendingUp, Calendar } from 'lucide-react';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { formatPercent } from '@/lib/formatters';

interface CorrelationMetricsProps {
  avgCorrelation: number;
  maxCorrelation: number;
  daysAnalyzed: number;
}

export function CorrelationMetrics({
  avgCorrelation,
  maxCorrelation,
  daysAnalyzed,
}: CorrelationMetricsProps) {
  return (
    <MetricGroup layout="horizontal">
      <MetricCard
        title="Average Correlation"
        value={formatPercent(avgCorrelation)}
        icon={Activity}
        variant="default"
        trend="neutral"
      />
      <MetricCard
        title="Highest Correlation"
        value={formatPercent(maxCorrelation)}
        icon={TrendingUp}
        variant="default"
        trend={maxCorrelation > 0.7 ? 'negative' : 'neutral'}
      />
      <MetricCard
        title="Time Period"
        value={`${daysAnalyzed} days`}
        icon={Calendar}
        variant="subtle"
        trend="neutral"
      />
    </MetricGroup>
  );
}
