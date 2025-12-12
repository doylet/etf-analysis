/**
 * MonteCarloMetrics - Displays key statistics from simulation results
 * Shows median, percentiles, and risk metrics in card format
 */
import { TrendingUp, AlertTriangle, Target } from 'lucide-react';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { formatCurrency, formatPercent } from '@/lib/formatters';

interface MonteCarloMetricsProps {
  statistics: {
    mean_final_value: number;
    std_final_value: number;
    mean_return_percent: number;
    probability_of_loss: number;
    cagr_median: number;
    cagr_10th: number;
    cagr_90th: number;
    historical_sharpe?: number;
    historical_volatility?: number;
    max_drawdown_median?: number;
  };
  percentiles: {
    "10": number;
    "50": number;
    "90": number;
  };
}

export function MonteCarloMetrics({ statistics, percentiles }: MonteCarloMetricsProps) {
  return (
    <MetricGroup layout="horizontal">
      <MetricCard
        title="Median Final Value"
        value={formatCurrency(percentiles["50"])}
        subtitle={`${statistics.cagr_median?.toFixed(2) || '0.00'}% CAGR`}
        icon={TrendingUp}
        variant="highlighted"
        size="sm"
        trend={statistics.cagr_median > 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        title="10th Percentile (Downside)"
        value={formatCurrency(percentiles["10"])}
        subtitle={`${statistics.cagr_10th?.toFixed(2) || '0.00'}% CAGR`}
        icon={AlertTriangle}
        variant="default"
        size="sm"
        trend="negative"
      />
      <MetricCard
        title="90th Percentile (Upside)"
        value={formatCurrency(percentiles["90"])}
        subtitle={`${statistics.cagr_90th?.toFixed(2) || '0.00'}% CAGR`}
        icon={Target}
        variant="default"
        size="sm"
        trend="positive"
      />
      <MetricCard
        title="Probability of Loss"
        value={formatPercent(statistics.probability_of_loss)}
        subtitle="Chance of loss"
        icon={AlertTriangle}
        variant="subtle"
        size="sm"
        trend={statistics.probability_of_loss > 0.3 ? 'negative' : 'neutral'}
      />
    </MetricGroup>
  );
}
