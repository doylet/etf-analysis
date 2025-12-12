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
 */
'use client';

import { BarChart3, XCircle, AlertTriangle, TrendingUp, Target, ChevronDown } from 'lucide-react';
import { useState, useMemo } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { MetricCard } from '@/components/ui/metric-card';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { CacheBadge } from '@/components/ui/cache-badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { WidgetSelect, WidgetNumberInput, WidgetCheckbox } from '@/components/ui/widget/widget-controls';
import type { ContentType } from './widget-metadata';
import { formatCurrency, formatPercent } from '@/lib/formatters';
import { SIMULATION_COUNTS, CONFIDENCE_LEVELS, FREQUENCY_OPTIONS, WEIGHT_METHODS, ESTIMATION_METHODS } from '@/lib/widget-constants';

import { useMonteCarloSimulation } from '@/hooks/use-portfolio-widgets';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 5 },
  contentType: 'height-heavy' as ContentType,
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
  const [numSimulations, setNumSimulations] = useState(defaultSimulations);
  const [timeHorizonYears, setTimeHorizonYears] = useState(10);
  const [initialValue, setInitialValue] = useState(100000);
  const [estimationMethod, setEstimationMethod] = useState<'Historical Mean' | 'Exponentially Weighted'>('Historical Mean');
  const [confidenceLevel, setConfidenceLevel] = useState(0.95);
  const [includeDividends, setIncludeDividends] = useState(true);
  const [enableContributions, setEnableContributions] = useState(false);
  const [contributionAmount, setContributionAmount] = useState(0);
  const [contributionFrequency, setContributionFrequency] = useState<'Monthly' | 'Quarterly' | 'Annual'>('Annual');
  
  // Portfolio Selection & Weighting
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [weightMethod, setWeightMethod] = useState<'Equal Weights' | 'Max Sharpe Ratio' | 'Min Volatility' | 'Current Portfolio' | 'Custom'>('Current Portfolio');
  const [customWeights, setCustomWeights] = useState<Record<string, number>>({});
  const [showWeightConfig, setShowWeightConfig] = useState(false);
  
  // Rebalancing Options
  const [enableRebalancing, setEnableRebalancing] = useState(false);
  const [rebalancingFrequency, setRebalancingFrequency] = useState<'Quarterly' | 'Semi-Annual' | 'Annual'>('Annual');
  const [driftThreshold, setDriftThreshold] = useState(5);
  
  // Convert years to days (252 trading days per year)
  const calculatedDays = Math.round(timeHorizonYears * 252);
  
  const { data: simulation, loading, isRefreshing, error, cacheHit } = useMonteCarloSimulation({
    portfolioId,
    numSimulations,
    timeHorizonDays: calculatedDays,
    initialValue,
    estimationMethod,
    confidenceLevel,
    includeDividends,
    enableContributions,
    contributionAmount,
    contributionFrequency,
  });

  // Create histogram data for visualization (proper vertical histogram)
  const histogramData = useMemo(() => {
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
  const timeseriesData = useMemo(() => {
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

  const statistics = simulation?.statistics || { mean_final_value: 0, std_final_value: 0, mean_return_percent: 0, probability_of_loss: 0, cagr_median: 0, cagr_10th: 0, cagr_90th: 0, historical_sharpe: 0, historical_volatility: 0, max_drawdown_median: 0 };
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
            Risk analysis over {timeHorizonYears} years ({numSimulations.toLocaleString()} simulations)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <CacheBadge show={cacheHit} />
        </div>
      </div>
      
      {/* Configuration Controls */}
      <div className="grid grid-cols-2 gap-2 px-1 py-3 bg-muted rounded-md flex-shrink-0 mt-3">
        <WidgetSelect
          label="Simulations"
          value={numSimulations.toString()}
          onChange={(val) => setNumSimulations(Number(val))}
          options={SIMULATION_COUNTS.map(opt => ({ value: opt.value.toString(), label: opt.label }))}
        />
        
        <WidgetNumberInput
          label="Time Horizon (Years)"
          value={timeHorizonYears}
          onChange={setTimeHorizonYears}
          min={1}
          max={30}
          step={1}
        />
        
        <WidgetNumberInput
          label="Initial Portfolio Value"
          value={initialValue}
          onChange={setInitialValue}
          min={1000}
          max={10000000}
          step={10000}
        />
        
        <WidgetSelect
          label="Estimation Method"
          value={estimationMethod}
          onChange={(val) => setEstimationMethod(val as 'Historical Mean' | 'Exponentially Weighted')}
          options={ESTIMATION_METHODS}
        />
        
        <WidgetSelect
          label="Confidence Level"
          value={confidenceLevel.toString()}
          onChange={(val) => setConfidenceLevel(Number(val))}
          options={CONFIDENCE_LEVELS.map(opt => ({ value: opt.value.toString(), label: opt.label }))}
        />
        
        <WidgetCheckbox
          checked={includeDividends}
          onChange={setIncludeDividends}
          label="Include Dividends"
        />
        
        <WidgetCheckbox
          checked={enableContributions}
          onChange={setEnableContributions}
          label="Enable Contributions"
        />
        
        {enableContributions && (
          <>
            <WidgetNumberInput
              label="Contribution Amount"
              value={contributionAmount}
              onChange={setContributionAmount}
              min={0}
              step={100}
            />
            
            <WidgetSelect
              label="Frequency"
              value={contributionFrequency}
              onChange={(val) => setContributionFrequency(val as 'Monthly' | 'Quarterly' | 'Annual')}
              options={FREQUENCY_OPTIONS.filter(opt => ['Monthly', 'Quarterly', 'Annual'].includes(opt.value))}
            />
          </>
        )}
      </div>

      {/* Portfolio Selection & Weighting */}
      <Collapsible open={showWeightConfig} onOpenChange={setShowWeightConfig} className="flex-shrink-0 mt-3">
        <CollapsibleTrigger 
          className="w-full flex items-center justify-between text-sm font-medium text-foreground p-2 hover:bg-muted rounded-md transition-colors"
          onPointerDown={(e) => e.stopPropagation()}
          onMouseDown={(e) => e.stopPropagation()}
        >
          <span>Portfolio Composition</span>
          <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${showWeightConfig ? 'rotate-180' : ''}`} />
        </CollapsibleTrigger>
        
        <CollapsibleContent>
          <div className="mt-2 p-3 border border-border rounded-md space-y-3">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Weight Allocation Method</label>
              <select
                value={weightMethod}
                onChange={(e) => setWeightMethod(e.target.value as any)}
                className="w-full text-xs border border-border rounded-md px-2 py-1 bg-background"
              >
                <option value="Current Portfolio">Current Portfolio</option>
                <option value="Equal Weights">Equal Weights</option>
                <option value="Max Sharpe Ratio">Max Sharpe Ratio</option>
                <option value="Min Volatility">Min Volatility</option>
                <option value="Custom">Custom Weights</option>
              </select>
              <p className="text-[10px] text-muted-foreground mt-1">
                {weightMethod === 'Current Portfolio' && 'Use current portfolio holdings and weights'}
                {weightMethod === 'Equal Weights' && 'Distribute capital equally across selected instruments'}
                {weightMethod === 'Max Sharpe Ratio' && 'Optimize for maximum risk-adjusted returns'}
                {weightMethod === 'Min Volatility' && 'Optimize for minimum portfolio volatility'}
                {weightMethod === 'Custom' && 'Manually specify weight for each instrument'}
              </p>
            </div>

            {weightMethod === 'Custom' && (
              <div className="space-y-2">
                <label className="text-xs font-medium">Custom Weights</label>
                <div className="text-xs text-amber-600 bg-amber-50 dark:bg-amber-900/20 p-2 rounded">
                  Custom weight allocation requires instrument selection. This feature will be fully enabled when portfolio holdings data is available.
                </div>
              </div>
            )}

            {/* Rebalancing Options */}
            <div className="pt-2 border-t border-border">
              <div className="flex items-center gap-2 mb-2">
                <input
                  type="checkbox"
                  id="enableRebalancing"
                  checked={enableRebalancing}
                  onChange={(e) => setEnableRebalancing(e.target.checked)}
                  className="rounded border-border"
                />
                <label htmlFor="enableRebalancing" className="text-xs font-medium cursor-pointer">
                  Enable Rebalancing Analysis
                </label>
              </div>

              {enableRebalancing && (
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <div>
                    <label className="text-xs text-muted-foreground block mb-1">Frequency</label>
                    <select
                      value={rebalancingFrequency}
                      onChange={(e) => setRebalancingFrequency(e.target.value as any)}
                      className="w-full text-xs border border-border rounded-md px-2 py-1 bg-background"
                    >
                      <option value="Quarterly">Quarterly</option>
                      <option value="Semi-Annual">Semi-Annual</option>
                      <option value="Annual">Annual</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground block mb-1">Drift Threshold (%)</label>
                    <input
                      type="number"
                      value={driftThreshold}
                      onChange={(e) => setDriftThreshold(Math.max(1, Math.min(20, Number(e.target.value))))}
                      className="w-full text-xs border border-border rounded-md px-2 py-1 bg-background"
                      min="1"
                      max="20"
                      step="1"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </CollapsibleContent>
      </Collapsible>
      
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
            {/* Key Metrics */}
            <div className="flex flex-wrap justify-center gap-3">
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
          </div>

          {/* Percentile Breakdown */}
          <div>
            <h3 className="text-lg font-medium mb-3">Outcome Percentiles</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-3 border border-border rounded-lg bg-background-secondary">
                <div className="text-sm text-text-tertiary">10th Percentile</div>
                <div className="text-lg font-bold text-financial-negative">
                  {formatCurrency(percentiles["10"])}
                </div>
                <div className="text-xs text-text-tertiary">
                  {formatPercent((percentiles["10"] - simulationInitialValue) / simulationInitialValue)}
                </div>
              </div>
              <div className="text-center p-3 border border-border rounded-lg bg-background-accent">
                <div className="text-sm text-text-tertiary">50th Percentile (Median)</div>
                <div className="text-lg font-bold text-text-primary">
                  {formatCurrency(percentiles["50"])}
                </div>
                <div className="text-xs text-text-tertiary">
                  {formatPercent((percentiles["50"] - simulationInitialValue) / simulationInitialValue)}
                </div>
              </div>
              <div className="text-center p-3 border border-border rounded-lg bg-background-secondary">
                <div className="text-sm text-text-tertiary">90th Percentile</div>
                <div className="text-lg font-bold text-financial-positive">
                  {formatCurrency(percentiles["90"])}
                </div>
                <div className="text-xs text-text-tertiary">
                  {formatPercent((percentiles["90"] - simulationInitialValue) / simulationInitialValue)}
                </div>
              </div>
            </div>
          </div>

          {/* Vertical Histogram */}
          <div>
            <h3 className="text-lg font-medium mb-3">Distribution of Final Values</h3>
            {histogramData.length > 0 ? (
            <div className="flex items-end justify-between h-64 gap-0.5 px-2">
              {histogramData.map((bucket, index) => {
                const maxCount = Math.max(...histogramData.map(b => b.count));
                const barHeight = (bucket.count / maxCount) * 100;
                
                return (
                  <div key={index} className="flex flex-col items-center flex-1 min-w-0">
                    <div 
                      className="w-full bg-chart-1 hover:bg-chart-1/80 transition-all duration-200 rounded-t"
                      style={{ height: `${barHeight}%` }}
                      title={`${bucket.range}\nCount: ${bucket.count} (${bucket.percentage.toFixed(1)}%)`}
                    />
                    {index % 5 === 0 && (
                      <div className="text-[9px] text-muted-foreground mt-1 -rotate-45 origin-top-left whitespace-nowrap">
                        {formatCurrency(bucket.minValue)}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-sm text-muted-foreground">
                No distribution data available
              </div>
            )}
            <div className="text-xs text-center text-muted-foreground mt-6">Final Portfolio Value</div>
          </div>

          {/* Dual-Axis Timeseries: Forward Returns + Drawdown */}
          {timeseriesData && timeseriesData.length > 0 ? (
            <div>
              <h3 className="text-lg font-medium mb-3">Portfolio Path Projections</h3>
              <div className="relative h-80">
                <svg viewBox="0 0 800 300" className="w-full h-full text-muted-foreground">
                  <defs>
                    <linearGradient id="confidenceBand" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" className="[stop-color:hsl(var(--chart-1))]" stopOpacity="0.2" />
                      <stop offset="100%" className="[stop-color:hsl(var(--chart-1))]" stopOpacity="0.05" />
                    </linearGradient>
                  </defs>
                  
                  {/* Grid lines */}
                  {[0, 1, 2, 3, 4].map(i => (
                    <line 
                      key={`grid-${i}`}
                      x1="60" 
                      y1={50 + i * 50} 
                      x2="740" 
                      y2={50 + i * 50}
                      stroke="currentColor"
                      strokeOpacity="0.1"
                      strokeDasharray="2,2"
                    />
                  ))}
                  
                  {/* Confidence band (10th to 90th percentile) */}
                  <path
                    d={timeseriesData.map((d, i) => {
                      const x = 60 + (i / (timeseriesData.length - 1)) * 680;
                      const yMax = simulationInitialValue > 0 ? 250 - ((d.percentile_90 / simulationInitialValue - 1) * 200) : 150;
                      return `${i === 0 ? 'M' : 'L'} ${x} ${Math.max(50, Math.min(250, yMax))}`;
                    }).join(' ') + ' ' + timeseriesData.slice().reverse().map((d, i) => {
                      const x = 740 - (i / (timeseriesData.length - 1)) * 680;
                      const yMin = simulationInitialValue > 0 ? 250 - ((d.percentile_10 / simulationInitialValue - 1) * 200) : 150;
                      return `L ${x} ${Math.max(50, Math.min(250, yMin))}`;
                    }).join(' ') + ' Z'}
                    fill="url(#confidenceBand)"
                  />
                  
                  {/* Median line (left axis - portfolio value) */}
                  <path
                    d={timeseriesData.map((d, i) => {
                      const x = 60 + (i / (timeseriesData.length - 1)) * 680;
                      const y = simulationInitialValue > 0 ? 250 - ((d.percentile_50 / simulationInitialValue - 1) * 200) : 150;
                      return `${i === 0 ? 'M' : 'L'} ${x} ${Math.max(50, Math.min(250, y))}`;
                    }).join(' ')}
                    fill="none"
                    className="stroke-chart-1"
                    strokeWidth="2"
                  />
                  
                  {/* Median drawdown line (right axis - inverted) */}
                  <path
                    d={timeseriesData.map((d, i) => {
                      const x = 60 + (i / (timeseriesData.length - 1)) * 680;
                      const y = 50 + Math.abs(d.median_drawdown) * 4; // Scale: 50% drawdown = 200px
                      return `${i === 0 ? 'M' : 'L'} ${x} ${Math.min(250, y)}`;
                    }).join(' ')}
                    fill="none"
                    className="stroke-financial-negative"
                    strokeWidth="1.5"
                    strokeDasharray="4,2"
                  />
                  
                  {/* Y-axis labels (left - returns) */}
                  <text x="5" y="55" fontSize="10" fill="currentColor" opacity="0.6">+100%</text>
                  <text x="15" y="155" fontSize="10" fill="currentColor" opacity="0.6">0%</text>
                  <text x="5" y="255" fontSize="10" fill="currentColor" opacity="0.6">-50%</text>
                  
                  {/* Y-axis labels (right - drawdown) */}
                  <text x="750" y="55" fontSize="10" className="fill-financial-negative" opacity="0.8">0%</text>
                  <text x="745" y="155" fontSize="10" className="fill-financial-negative" opacity="0.8">-25%</text>
                  <text x="745" y="255" fontSize="10" className="fill-financial-negative" opacity="0.8">-50%</text>
                  
                  {/* X-axis labels (time in years) */}
                  {[0, 0.25, 0.5, 0.75, 1].map(fraction => {
                    const x = 60 + fraction * 680;
                    const years = (timeseriesData[Math.floor(fraction * (timeseriesData.length - 1))]?.years || 0).toFixed(1);
                    return (
                      <text key={fraction} x={x} y="275" fontSize="10" fill="currentColor" opacity="0.6" textAnchor="middle">
                        {years}y
                      </text>
                    );
                  })}
                  
                  {/* Axis labels */}
                  <text x="400" y="295" fontSize="11" fill="currentColor" opacity="0.7" textAnchor="middle">Time (Years)</text>
                  <text x="30" y="20" fontSize="11" className="fill-chart-1" opacity="0.9" textAnchor="middle">Returns</text>
                  <text x="770" y="20" fontSize="11" className="fill-financial-negative" opacity="0.9" textAnchor="middle">Drawdown</text>
                </svg>
                
                <div className="mt-2 flex items-center justify-center gap-4 text-xs">
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-chart-1 rounded"></div>
                    <span className="text-muted-foreground">Median Path</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-chart-1/20 border border-chart-1/40 rounded"></div>
                    <span className="text-muted-foreground">10th-90th Percentile</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-6 h-0.5 bg-financial-negative" style={{borderTop: '1.5px dashed'}}></div>
                    <span className="text-muted-foreground">Median Drawdown</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4 border border-blue-200 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h3 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">
                Path Projections Unavailable
              </h3>
              <p className="text-xs text-blue-700 dark:text-blue-300">
                The timeseries visualization requires path statistics from the backend. Run a new simulation to generate this data.
              </p>
            </div>
          )}

          {/* Risk Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-2">Risk Metrics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Value at Risk (95%):</span>
                  <span className="font-mono">{formatCurrency(var95)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Conditional VaR (95%):</span>
                  <span className="font-mono">{formatCurrency(simulation?.statistics?.cvar_95 || var95)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Max Drawdown (Median):</span>
                  <span className="font-mono">{statistics.max_drawdown_median?.toFixed(1) || '0.0'}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Volatility (Std Dev):</span>
                  <span className="font-mono">{formatPercent(statistics.historical_volatility)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sharpe Ratio:</span>
                  <span className="font-mono">{statistics.historical_sharpe.toFixed(2)}</span>
                </div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-2">Simulation Parameters</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Initial Value:</span>
                  <span className="font-mono">{formatCurrency(simulation?.simulation_params?.initial_value || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Time Horizon:</span>
                  <span className="font-mono">{(simulation?.simulation_params?.time_horizon_years || 0).toFixed(2)} years</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Simulations:</span>
                  <span className="font-mono">{(simulation?.simulation_params?.num_simulations || 0).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Rebalancing Recommendations */}
          {enableRebalancing && simulation?.rebalancing_rec && (
            <div className="border border-border rounded-lg p-4">
              <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
                <Target className="h-5 w-5" />
                Rebalancing Recommendations
              </h3>
              
              {/* Summary Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="text-center p-2 bg-background-accent rounded">
                  <div className="text-xs text-muted-foreground">Rebalance Count</div>
                  <div className="text-lg font-bold text-text-primary">
                    {simulation.rebalancing_rec.rebalance_dates.length}
                  </div>
                </div>
                <div className="text-center p-2 bg-background-accent rounded">
                  <div className="text-xs text-muted-foreground">Avg. Drift</div>
                  <div className="text-lg font-bold text-text-primary">
                    {simulation.rebalancing_rec.avg_drift.toFixed(1)}%
                  </div>
                </div>
                <div className="text-center p-2 bg-background-accent rounded">
                  <div className="text-xs text-muted-foreground">Sharpe Improvement</div>
                  <div className="text-lg font-bold text-financial-positive">
                    +{simulation.rebalancing_rec.sharpe_improvement.toFixed(2)}
                  </div>
                </div>
                <div className="text-center p-2 bg-background-accent rounded">
                  <div className="text-xs text-muted-foreground">Cost/Benefit</div>
                  <div className="text-lg font-bold text-text-primary">
                    {simulation.rebalancing_rec.cost_benefit_ratio.toFixed(2)}x
                  </div>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-muted-foreground mb-4">
                {simulation.rebalancing_rec.description}
              </p>

              {/* Rebalancing Calendar */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Rebalancing Calendar</h4>
                <div className="border border-border rounded overflow-hidden">
                  <table className="w-full text-xs">
                    <thead className="bg-muted">
                      <tr>
                        <th className="text-left p-2">Date</th>
                        <th className="text-right p-2">Max Drift</th>
                        <th className="text-left p-2">Instruments Affected</th>
                      </tr>
                    </thead>
                    <tbody>
                      {simulation.rebalancing_rec.rebalance_dates.map((date, idx) => (
                        <tr key={idx} className="border-t border-border hover:bg-muted/50">
                          <td className="p-2">{new Date(date).toLocaleDateString()}</td>
                          <td className="text-right p-2 font-mono">
                            {simulation.rebalancing_rec!.drift_at_rebalance[idx].toFixed(1)}%
                          </td>
                          <td className="p-2">
                            <span className="text-muted-foreground">
                              {simulation.rebalancing_rec!.symbols.slice(0, 3).join(', ')}
                              {simulation.rebalancing_rec!.symbols.length > 3 && ` +${simulation.rebalancing_rec!.symbols.length - 3} more`}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Drift Threshold Info */}
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded text-xs">
                <strong>Drift Threshold:</strong> Rebalancing triggered when any position drifts {driftThreshold}% from target weight. 
                Frequency: {rebalancingFrequency}.
              </div>
            </div>
          )}

          {enableRebalancing && !simulation?.rebalancing_rec && (
            <div className="border border-amber-200 bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
              <h3 className="text-sm font-medium text-amber-900 dark:text-amber-200 mb-2">
                Rebalancing Analysis Not Available
              </h3>
              <p className="text-xs text-amber-700 dark:text-amber-300">
                Rebalancing recommendations require backend implementation. The simulation will include rebalancing 
                effects once the feature is fully enabled.
              </p>
            </div>
          )}

          {/* Warnings */}
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