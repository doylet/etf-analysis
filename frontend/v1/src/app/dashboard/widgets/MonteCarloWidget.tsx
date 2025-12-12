/**
 * Monte Carlo Widget - Async Update Pattern
 * 
 * This widget demonstrates the async update pattern for widget data:
 * - Initial load: Shows full loading state (loading = true)
 * - Background refresh: Shows subtle "updating..." indicator (isRefreshing = true)
 * - Manual run: User changes params, clicks button, new simulation runs without reload
 * - No full page reload needed - data updates in place
 * 
 * Key features:
 * - Dual state: input params vs saved params (prevents auto-refresh on every input change)
 * - isRefreshing: Shows background update without blocking UI
 * - mutate: Enables optimistic updates (not used here, but available)
 * 
 * REFACTORED: Component decomposed into focused subcomponents for better maintainability
 */
'use client';

import { BarChart3, XCircle, AlertTriangle } from 'lucide-react';
import { useMemo } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { CacheBadge } from '@/components/ui/cache-badge';
import { formatCurrency, formatPercent } from '@/lib/formatters';
import { useMonteCarloSimulation } from '@/hooks/use-portfolio-widgets';
import type { ContentType } from './widget-metadata';

import {
  useMonteCarloConfig,
  MonteCarloControls,
  MonteCarloMetrics,
  MonteCarloHistogram,
  MonteCarloTimeseries,
  PercentileBreakdown,
  PortfolioComposition,
  RebalancingAnalysis,
  RiskMetrics,
  type HistogramBucket,
  type TimeseriesDataPoint,
} from './monte-carlo';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 5 },
  contentType: 'width-heavy' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.0,
  isScrollable: true,
} as const;

interface MonteCarloSimulationProps {
  portfolioId?: string;
  defaultSimulations?: number;
}

export default function MonteCarloWidget({ 
  portfolioId, 
  defaultSimulations = 10000
}: MonteCarloSimulationProps) {
  // Configuration state management
  const { config, actions, calculatedDays } = useMonteCarloConfig(defaultSimulations);
  
  // Fetch simulation data
  const { data: simulation, loading, isRefreshing, error, cacheHit } = useMonteCarloSimulation({
    portfolioId,
    numSimulations: config.numSimulations,
    timeHorizonDays: calculatedDays,
    initialValue: config.initialValue,
    estimationMethod: config.estimationMethod,
    confidenceLevel: config.confidenceLevel,
    includeDividends: config.includeDividends,
    enableContributions: config.enableContributions,
    contributionAmount: config.contributionAmount,
    contributionFrequency: config.contributionFrequency,
  });

  // Create histogram data for visualization
  const histogramData = useMemo((): HistogramBucket[] => {
    if (!simulation?.scenarios || simulation.scenarios.length === 0) return [];
    
    const values = simulation.scenarios.map(s => s.final_value);
    if (values.length === 0) return [];
    
    const bucketCount = 30;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const bucketSize = (max - min) / bucketCount;
    
    const buckets = Array(bucketCount).fill(0);
    values.forEach(value => {
      const bucketIndex = Math.min(Math.floor((value - min) / bucketSize), bucketCount - 1);
      buckets[bucketIndex]++;
    });
    
    return buckets.map((count, index) => ({
      range: `${formatCurrency(min + index * bucketSize)} - ${formatCurrency(min + (index + 1) * bucketSize)}`,
      count,
      percentage: (count / values.length) * 100,
      midpoint: min + (index + 0.5) * bucketSize,
      minValue: min + index * bucketSize,
      maxValue: min + (index + 1) * bucketSize,
    }));
  }, [simulation]);

  // Create timeseries data for path visualization
  const timeseriesData = useMemo((): TimeseriesDataPoint[] | null => {
    if (!simulation?.path_statistics) return null;
    
    const { time_points, percentile_10, percentile_50, percentile_90, median_drawdown } = simulation.path_statistics;
    
    return time_points.map((days, i) => ({
      days,
      years: days / 252,
      percentile_10: percentile_10[i],
      percentile_50: percentile_50[i],
      percentile_90: percentile_90[i],
      median_drawdown: median_drawdown[i],
    }));
  }, [simulation]);

  // Extract statistics with defaults
  const statistics = simulation?.statistics || {
    mean_final_value: 0,
    std_final_value: 0,
    mean_return_percent: 0,
    probability_of_loss: 0,
    cagr_median: 0,
    cagr_10th: 0,
    cagr_90th: 0,
    historical_sharpe: 0,
    historical_volatility: 0,
    max_drawdown_median: 0
  };
  
  const percentiles = simulation?.percentiles || { "10": 0, "50": 0, "90": 0 };
  const var95 = simulation?.var_95 || 0;
  const simulationInitialValue = simulation?.simulation_params?.initial_value || 0;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-start flex-shrink-0">
        <div>
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Monte Carlo Simulation
            {isRefreshing && (
              <span className="text-xs text-muted-foreground animate-pulse">(updating...)</span>
            )}
          </h3>
          <p className="text-xs text-muted-foreground mt-1">
            Risk analysis over {config.timeHorizonYears} years ({config.numSimulations.toLocaleString()} simulations)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <CacheBadge show={cacheHit} />
        </div>
      </div>
      
      {/* Configuration Controls */}
      <MonteCarloControls config={config} actions={actions} />

      {/* Portfolio Composition (Collapsible) */}
      <PortfolioComposition
        config={{
          weightMethod: config.weightMethod,
          customWeights: config.customWeights,
          showWeightConfig: config.showWeightConfig,
          enableRebalancing: config.enableRebalancing,
          rebalancingFrequency: config.rebalancingFrequency,
          driftThreshold: config.driftThreshold,
        }}
        actions={{
          setWeightMethod: actions.setWeightMethod,
          setCustomWeights: actions.setCustomWeights,
          setShowWeightConfig: actions.setShowWeightConfig,
          setEnableRebalancing: actions.setEnableRebalancing,
          setRebalancingFrequency: actions.setRebalancingFrequency,
          setDriftThreshold: actions.setDriftThreshold,
        }}
      />
      
      {/* Main Content - Scrollable */}
      <div className="flex-1 overflow-y-auto space-y-2 min-h-0">
        {loading ? (
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="p-3 border rounded-lg">
                  <Skeleton className="h-4 w-[80px] mb-2" />
                  <Skeleton className="h-6 w-[100px]" />
                </div>
              ))}
            </div>
          </div>
        ) : error || !simulation ? (
          <WidgetInsight
            title="Monte Carlo Simulation Error"
            description={error || 'Unable to run Monte Carlo simulation. Click the button above to run a simulation.'}
            icon={XCircle}
            variant="destructive"
          />
        ) : (
          <>
            {/* Key Metrics Cards */}
            <MonteCarloMetrics statistics={statistics} percentiles={percentiles} />

            {/* Percentile Breakdown */}
            <PercentileBreakdown percentiles={percentiles} initialValue={simulationInitialValue} />

            {/* Histogram */}
            <MonteCarloHistogram data={histogramData} />

            {/* Timeseries Chart */}
            <MonteCarloTimeseries data={timeseriesData} initialValue={simulationInitialValue} />

            {/* Risk Metrics & Parameters */}
            <RiskMetrics
              statistics={statistics}
              var95={var95}
              simulationParams={simulation.simulation_params}
            />

            {/* Rebalancing Analysis */}
            <RebalancingAnalysis
              rebalancingRec={simulation.rebalancing_rec || null}
              enabled={config.enableRebalancing}
              driftThreshold={config.driftThreshold}
              frequency={config.rebalancingFrequency}
            />

            {/* High Risk Warning */}
            {statistics.probability_of_loss > 0.4 && (
              <WidgetInsight
                title="High Risk Warning"
                description={`The simulation shows a ${formatPercent(statistics.probability_of_loss)} probability of loss. Consider reviewing your portfolio allocation and risk tolerance.`}
                icon={AlertTriangle}
                variant="destructive"
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}
