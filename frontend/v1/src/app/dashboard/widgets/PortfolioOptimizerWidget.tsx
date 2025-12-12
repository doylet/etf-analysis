import React, { useState, useMemo } from 'react';
import { usePortfolioOptimizer } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { WidgetSelect, WidgetCheckbox, WidgetNumberInput } from '@/components/ui/widget/widget-controls';
import { TIME_PERIODS, OPTIMIZATION_OBJECTIVES } from '@/lib/widget-constants';
import { formatPercent } from '@/lib/formatters';
import { XCircle, TrendingUp, Activity, Target, ArrowRight } from 'lucide-react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis } from 'recharts';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 8, h: 6 },
  contentType: 'full-width' as ContentType,
  requiresFullWidth: true,
  aspectRatioPreference: 1.5,
  isScrollable: true,
} as const;

interface PortfolioOptimizerWidgetProps {
  portfolioId?: string;
}

const PortfolioOptimizerWidget: React.FC<PortfolioOptimizerWidgetProps> = ({ portfolioId }) => {
  const [mode, setMode] = useState('Max Sharpe');
  const [timePeriod, setTimePeriod] = useState('1Y');
  const [includeDividends, setIncludeDividends] = useState(true);
  const [targetReturn, setTargetReturn] = useState(15);
  const [showCustomWeights, setShowCustomWeights] = useState(false);
  
  const { data, loading, error } = usePortfolioOptimizer({ 
    portfolioId, 
    mode, 
    timePeriod, 
    targetReturn: mode === 'Target Return' ? targetReturn : undefined,
    includeDividends 
  });

  // Prepare chart data for efficient frontier
  const chartData = useMemo(() => {
    if (!data?.efficient_frontier) return [];
    
    return data.efficient_frontier.map((point: any, index: number) => ({
      volatility: point.volatility * 100,
      return: point.expected_return * 100,
      sharpe: point.sharpe_ratio,
      name: `Portfolio ${index + 1}`
    }));
  }, [data]);

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Optimizer Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.expected_return !== undefined && data.expected_risk !== undefined;

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-col gap-2 flex-shrink-0 mb-1">
        <div className="flex gap-2">
          <WidgetSelect
            value={mode}
            onChange={setMode}
            options={OPTIMIZATION_OBJECTIVES}
            className="flex-1"
          />
          <WidgetSelect
            value={timePeriod}
            onChange={setTimePeriod}
            options={TIME_PERIODS.filter(p => p.value !== '1W')}
            className="flex-1"
          />
        </div>
        
        <div className="flex items-center gap-4">
          <WidgetCheckbox
            label="Include Dividends"
            checked={includeDividends}
            onChange={setIncludeDividends}
          />
          
          {mode === 'Target Return' && (
            <WidgetNumberInput
              label="Target Return (%)"
              value={targetReturn}
              onChange={setTargetReturn}
              min={0}
              max={100}
              step={0.5}
            />
          )}
        </div>
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3">
          {/* Key Metrics */}
          <MetricGroup columns={3}>
            <MetricCard
              title="Expected Return"
              value={formatPercent(data.expected_return / 100)}
              subtitle={data.current_return ? `Currently: ${formatPercent(data.current_return / 100)}` : undefined}
              icon={TrendingUp}
              variant="highlighted"
              size="sm"
              trend="positive"
            />
            <MetricCard
              title="Expected Risk"
              value={formatPercent(data.expected_risk / 100)}
              subtitle={data.current_risk ? `Currently: ${formatPercent(data.current_risk / 100)}` : undefined}
              icon={Activity}
              variant="default"
              size="sm"
            />
            <MetricCard
              title="Sharpe Ratio"
              value={data.sharpe_ratio?.toFixed(2)}
              subtitle={data.current_sharpe ? `Currently: ${data.current_sharpe?.toFixed(2)}` : undefined}
              icon={Target}
              variant="default"
              size="sm"
            />
          </MetricGroup>

          {/* Improvements Section */}
          {data.improvement_metrics && (
            <div className="p-3 bg-muted rounded-md">
              <div className="text-xs font-medium text-muted-foreground mb-2">Potential Improvements</div>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <div className="text-sm font-bold text-green-600 dark:text-green-400">
                    +{formatPercent(data.improvement_metrics.return_improvement / 100)}
                  </div>
                  <div className="text-xs text-muted-foreground">Return Gain</div>
                </div>
                <div>
                  <div className="text-sm font-bold text-green-600 dark:text-green-400">
                    {formatPercent(data.improvement_metrics.risk_reduction / 100)}
                  </div>
                  <div className="text-xs text-muted-foreground">Risk Reduction</div>
                </div>
                <div>
                  <div className="text-sm font-bold text-green-600 dark:text-green-400">
                    +{data.improvement_metrics.sharpe_improvement?.toFixed(2)}
                  </div>
                  <div className="text-xs text-muted-foreground">Sharpe Gain</div>
                </div>
              </div>
            </div>
          )}

          {/* Optimal Weight Recommendations */}
          {data.optimal_weights && Object.keys(data.optimal_weights).length > 0 && (
            <div>
              <div className="text-sm font-medium mb-2">Recommended Allocations</div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {Object.entries(data.optimal_weights).map(([symbol, weight]: [string, any]) => {
                  const currentWeight = data.current_weights?.[symbol] || 0;
                  const optimalWeight = typeof weight === 'number' ? weight : 0;
                  const change = optimalWeight - currentWeight;
                  
                  return (
                    <div key={symbol} className="flex items-center justify-between p-2 bg-muted rounded text-xs">
                      <span className="font-medium">{symbol}</span>
                      <div className="flex items-center gap-2">
                        {data.current_weights && (
                          <>
                            <span className="text-muted-foreground">{(currentWeight * 100).toFixed(1)}%</span>
                            <ArrowRight className="h-3 w-3 text-muted-foreground" />
                          </>
                        )}
                        <span className="font-medium">{(optimalWeight * 100).toFixed(1)}%</span>
                        {change !== 0 && (
                          <span className={`ml-2 ${change > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                            {change > 0 ? '+' : ''}{(change * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Efficient Frontier Chart */}
          {chartData.length > 0 && (
            <div>
              <div className="text-sm font-medium mb-2">Efficient Frontier</div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis 
                      type="number" 
                      dataKey="volatility" 
                      name="Risk"
                      unit="%"
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fontSize: 11 }}
                      label={{ value: 'Risk (Volatility %)', position: 'insideBottom', offset: -10, fontSize: 11 }}
                    />
                    <YAxis 
                      type="number" 
                      dataKey="return" 
                      name="Return"
                      unit="%"
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fontSize: 11 }}
                      label={{ value: 'Return %', angle: -90, position: 'insideLeft', fontSize: 11 }}
                    />
                    <ZAxis type="number" dataKey="sharpe" range={[50, 400]} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--background))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '6px',
                        fontSize: '12px'
                      }}
                      formatter={(value: number, name: string) => {
                        if (name === 'return' || name === 'volatility') return [`${value.toFixed(2)}%`, name === 'return' ? 'Return' : 'Risk'];
                        return [value.toFixed(2), 'Sharpe'];
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Scatter 
                      name="Portfolio Options" 
                      data={chartData} 
                      fill="hsl(var(--primary))"
                      opacity={0.6}
                    />
                    {data.current_return && data.current_risk && (
                      <Scatter 
                        name="Current Portfolio" 
                        data={[{ volatility: data.current_risk, return: data.current_return, sharpe: data.current_sharpe }]}
                        fill="hsl(var(--destructive))"
                        shape="star"
                      />
                    )}
                    {data.expected_return && data.expected_risk && (
                      <Scatter 
                        name="Optimal Portfolio" 
                        data={[{ volatility: data.expected_risk, return: data.expected_return, sharpe: data.sharpe_ratio }]}
                        fill="hsl(var(--chart-2))"
                        shape="triangle"
                      />
                    )}
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Portfolio optimizer data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

PortfolioOptimizerWidget.displayName = 'PortfolioOptimizerWidget';

export default React.memo(PortfolioOptimizerWidget);
