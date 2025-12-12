'use client';

import { TrendingUp, Activity, Target } from 'lucide-react';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { formatPercent } from '@/lib/formatters';

interface OptimizerMetricsProps {
  expectedReturn: number;
  expectedRisk: number;
  sharpeRatio: number;
  currentReturn?: number;
  currentRisk?: number;
  currentSharpe?: number;
}

export function OptimizerMetrics({
  expectedReturn,
  expectedRisk,
  sharpeRatio,
  currentReturn,
  currentRisk,
  currentSharpe,
}: OptimizerMetricsProps) {
  return (
    <MetricGroup layout="horizontal">
      <MetricCard
        title="Expected Return"
        value={formatPercent(expectedReturn / 100)}
        subtitle={currentReturn ? `Currently: ${formatPercent(currentReturn / 100)}` : undefined}
        icon={TrendingUp}
        variant="highlighted"
        size="sm"
        trend="positive"
      />
      <MetricCard
        title="Expected Risk"
        value={formatPercent(expectedRisk / 100)}
        subtitle={currentRisk ? `Currently: ${formatPercent(currentRisk / 100)}` : undefined}
        icon={Activity}
        variant="default"
        size="sm"
      />
      <MetricCard
        title="Sharpe Ratio"
        value={sharpeRatio?.toFixed(2)}
        subtitle={currentSharpe ? `Currently: ${currentSharpe?.toFixed(2)}` : undefined}
        icon={Target}
        variant="default"
        size="sm"
      />
    </MetricGroup>
  );
}
