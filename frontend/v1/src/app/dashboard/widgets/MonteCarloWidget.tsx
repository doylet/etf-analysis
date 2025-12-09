'use client';

import { BarChart3, XCircle, AlertTriangle, TrendingUp, Target } from 'lucide-react';
import { useState, useMemo } from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { MetricCard } from '@/components/ui/metric-card';

import { useMonteCarloSimulation } from '@/hooks/use-portfolio-widgets';

interface MonteCarloSimulationProps {
  portfolioId?: string;
  defaultSimulations?: number;
  defaultTimeHorizon?: number;
}

const formatPercent = (value: number | undefined | null): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00%';
  }
  return `${(value * 100).toFixed(1)}%`;
};

const formatCurrency = (amount: number | undefined | null): string => {
  if (amount === undefined || amount === null || isNaN(amount)) {
    return '$0.00';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export default function MonteCarloWidget({ 
  portfolioId, 
  defaultSimulations = 10000,
  defaultTimeHorizon = 252
}: MonteCarloSimulationProps) {
  const [numSimulations, setNumSimulations] = useState(defaultSimulations);
  const [timeHorizonDays, setTimeHorizonDays] = useState(defaultTimeHorizon);
  
  const { data: simulation, loading, error, cacheHit } = useMonteCarloSimulation({
    portfolioId,
    numSimulations,
    timeHorizonDays,
  });

  const simulationOptions = [
    { value: 1000, label: '1K Simulations' },
    { value: 5000, label: '5K Simulations' },
    { value: 10000, label: '10K Simulations' },
    { value: 25000, label: '25K Simulations' },
  ];

  const timeHorizonOptions = [
    { value: 30, label: '1 Month' },
    { value: 90, label: '3 Months' },
    { value: 180, label: '6 Months' },
    { value: 252, label: '1 Year' },
    { value: 504, label: '2 Years' },
  ];

  // Create histogram data for visualization
  const histogramData = useMemo(() => {
    if (!simulation?.simulation_results?.final_values) return [];
    
    const values = simulation?.simulation_results?.final_values || [];
    if (values.length === 0) return [];
    
    const bucketCount = 20;
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
    }));
  }, [simulation?.simulation_results?.final_values]);

  if (loading) {
    return (
      <div className="p-3">
        <div className="space-y-3">
          <div className="flex justify-between items-start">
            <div>
              <Skeleton className="h-5 w-[180px]" />
              <Skeleton className="h-4 w-[240px] mt-1" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="p-3 border rounded-lg">
                <Skeleton className="h-4 w-[80px] mb-2" />
                <Skeleton className="h-6 w-[100px]" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !simulation) {
    return (
      <div className="p-3">
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertTitle>Monte Carlo Simulation Error</AlertTitle>
          <AlertDescription>
            {error || 'Unable to run Monte Carlo simulation. Please try refreshing the page.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const results = simulation?.simulation_results || { final_values: [], percentiles: { p5: 0, p25: 0, p50: 0, p75: 0, p95: 0 }, statistics: { mean: 0, std: 0, min: 0, max: 0 } };
  const percentiles = results?.percentiles || { p5: 0, p25: 0, p50: 0, p75: 0, p95: 0 };
  const riskMetrics = simulation?.risk_metrics || { var_95: 0, var_99: 0, expected_shortfall_95: 0, probability_of_loss: 0 };
  const initialValue = simulation?.parameters?.initial_value || 0;

  return (
    <div className="p-3">
      <div className="space-y-3">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Monte Carlo Simulation
            </h3>
            <p className="text-xs text-muted-foreground mt-1">
              Risk analysis over {timeHorizonDays} days ({numSimulations.toLocaleString()} simulations)
            </p>
          </div>
          <div className="flex items-center gap-2">
            {cacheHit && (
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-md">
                Cached
              </span>
            )}
            <select
              value={numSimulations}
              onChange={(e) => setNumSimulations(Number(e.target.value))}
              className="text-xs border border-border rounded-md px-2 py-1 bg-background"
            >
              {simulationOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <select
              value={timeHorizonDays}
              onChange={(e) => setTimeHorizonDays(Number(e.target.value))}
              className="text-xs border border-border rounded-md px-2 py-1 bg-background"
            >
              {timeHorizonOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {/* Main Content */}
        <div className="space-y-3">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <MetricCard
              title="Expected Return"
              value={formatPercent(simulation?.expected_return || 0)}
              subtitle={formatCurrency(percentiles.p50)}
              icon={TrendingUp}
              variant="highlighted"
              trend={(simulation?.expected_return || 0) > 0 ? 'positive' : 'negative'}
            />
            <MetricCard
              title="Value at Risk (95%)"
              value={formatCurrency(riskMetrics.var_95)}
              subtitle="Worst case (5%)"
              icon={AlertTriangle}
              variant="default"
              trend="negative"
            />
            <MetricCard
              title="Best Case (95%)"
              value={formatCurrency(percentiles.p95)}
              subtitle="Top 5% outcomes"
              icon={Target}
              variant="default"
              trend="positive"
            />
            <MetricCard
              title="Loss Probability"
              value={formatPercent(riskMetrics.probability_of_loss)}
              subtitle="Chance of loss"
              icon={AlertTriangle}
              variant="subtle"
              trend={riskMetrics.probability_of_loss > 0.3 ? 'negative' : 'neutral'}
            />
          </div>

          {/* Percentile Breakdown */}
          <div>
            <h3 className="text-lg font-medium mb-3">Outcome Percentiles</h3>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="text-center p-3 border border-border rounded-lg bg-background-secondary">
                <div className="text-sm text-text-tertiary">5th Percentile</div>
                <div className="text-lg font-bold text-financial-negative">
                  {formatCurrency(percentiles.p5)}
                </div>
                <div className="text-xs text-text-tertiary">
                  {formatPercent((percentiles.p5 - initialValue) / initialValue)}
                </div>
              </div>
              <div className="text-center p-3 border border-border rounded-lg bg-background-secondary">
                <div className="text-sm text-text-tertiary">25th Percentile</div>
                <div className="text-lg font-bold text-financial-warning">
                  {formatCurrency(percentiles.p25)}
                </div>
                <div className="text-xs text-text-tertiary">
                  {formatPercent((percentiles.p25 - initialValue) / initialValue)}
                </div>
              </div>
              <div className="text-center p-3 border border-border rounded-lg bg-background-accent">
                <div className="text-sm text-text-tertiary">50th Percentile</div>
                <div className="text-lg font-bold text-text-primary">
                  {formatCurrency(percentiles.p50)}
                </div>
                <div className="text-xs text-text-tertiary">
                  {formatPercent((percentiles.p50 - initialValue) / initialValue)}
                </div>
              </div>
              <div className="text-center p-3 border border-border rounded-lg bg-background-secondary">
                <div className="text-sm text-text-tertiary">75th Percentile</div>
                <div className="text-lg font-bold text-financial-positive">
                  {formatCurrency(percentiles.p75)}
                </div>
                <div className="text-xs text-text-tertiary">
                  {formatPercent((percentiles.p75 - initialValue) / initialValue)}
                </div>
              </div>
              <div className="text-center p-3 border border-border rounded-lg bg-background-secondary">
                <div className="text-sm text-text-tertiary">95th Percentile</div>
                <div className="text-lg font-bold text-financial-positive">
                  {formatCurrency(percentiles.p95)}
                </div>
                <div className="text-xs text-text-tertiary">
                  {formatPercent((percentiles.p95 - initialValue) / initialValue)}
                </div>
              </div>
            </div>
          </div>

          {/* Simple Histogram Visualization */}
          <div>
            <h3 className="text-lg font-medium mb-3">Distribution of Outcomes</h3>
            <div className="space-y-1">
              {histogramData.map((bucket, index) => {
                const maxCount = Math.max(...histogramData.map(b => b.count));
                const barWidth = (bucket.count / maxCount) * 100;
                
                return (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <div className="w-32 text-xs text-muted-foreground truncate">
                      {formatCurrency(bucket.midpoint)}
                    </div>
                    <div className="flex-1 bg-muted rounded-full h-2 overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 transition-all duration-300"
                        style={{ width: `${barWidth}%` }}
                      />
                    </div>
                    <div className="w-12 text-xs text-muted-foreground text-right">
                      {bucket.percentage.toFixed(1)}%
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Risk Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-2">Risk Metrics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Value at Risk (99%):</span>
                  <span className="font-mono">{formatCurrency(riskMetrics.var_99)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Expected Shortfall:</span>
                  <span className="font-mono">{formatCurrency(riskMetrics.expected_shortfall_95)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Standard Deviation:</span>
                  <span className="font-mono">{formatCurrency(results.statistics.std)}</span>
                </div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-2">Simulation Parameters</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Initial Value:</span>
                  <span className="font-mono">{formatCurrency(simulation?.parameters?.initial_value || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Time Horizon:</span>
                  <span className="font-mono">{simulation?.parameters?.time_horizon_days || 0} days</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Simulations:</span>
                  <span className="font-mono">{(simulation?.parameters?.num_simulations || 0).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Warnings */}
          {riskMetrics.probability_of_loss > 0.4 && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>High Risk Warning</AlertTitle>
              <AlertDescription>
                The simulation shows a {formatPercent(riskMetrics.probability_of_loss)} probability of loss. 
                Consider reviewing your portfolio allocation and risk tolerance.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
}