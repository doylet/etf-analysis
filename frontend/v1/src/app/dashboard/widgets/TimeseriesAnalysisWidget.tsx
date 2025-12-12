import React, { useState } from 'react';
import { useTimeseriesAnalysis } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { WidgetSelect } from '@/components/ui/widget/widget-controls';
import { TIME_PERIODS } from '@/lib/widget-constants';
import { formatPercent } from '@/lib/formatters';
import { XCircle, TrendingUp, Activity, Target, TrendingDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 12, h: 6 },
  contentType: 'full-width' as ContentType,
  requiresFullWidth: true,
  aspectRatioPreference: 2.0,
  isScrollable: false,
} as const;

interface TimeseriesAnalysisWidgetProps {
  portfolioId?: string;
}

const TimeseriesAnalysisWidget: React.FC<TimeseriesAnalysisWidgetProps> = ({ portfolioId }) => {
  const [timePeriod, setTimePeriod] = useState('1Y');
  const [analysisType, setAnalysisType] = useState('Portfolio Overview');
  
  const { data, loading, error } = useTimeseriesAnalysis({ portfolioId, timePeriod, analysisType });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Timeseries Data Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.statistics?.total_return !== undefined;

  const analysisTypes = [
    { value: 'Portfolio Overview', label: 'Portfolio Overview' },
    { value: 'Stationarity', label: 'Stationarity' },
    { value: 'Seasonality', label: 'Seasonality' },
    { value: 'Trend Analysis', label: 'Trend Analysis' },
    { value: 'Volatility', label: 'Volatility' },
  ];

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex gap-2 flex-shrink-0">
        <WidgetSelect
          value={timePeriod}
          onChange={setTimePeriod}
          options={TIME_PERIODS}
          className="flex-1"
        />
        <WidgetSelect
          value={analysisType}
          onChange={setAnalysisType}
          options={analysisTypes}
          className="flex-1"
        />
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3">
          {/* Price Chart */}
          {data.price_data && data.price_data.length > 0 && (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.price_data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis 
                    dataKey="date" 
                    stroke="hsl(var(--muted-foreground))"
                    tick={{ fontSize: 11 }}
                    tickFormatter={(value) => {
                      const date = new Date(value);
                      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                    }}
                  />
                  <YAxis 
                    stroke="hsl(var(--muted-foreground))"
                    tick={{ fontSize: 11 }}
                    tickFormatter={(value) => value.toFixed(2)}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '6px',
                    }}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value: number) => [value.toFixed(4), 'Value']}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="hsl(var(--primary))" 
                    strokeWidth={2}
                    dot={false}
                    name="Portfolio Value"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
          
          {/* Statistics */}
          <MetricGroup columns={2}>
            <MetricCard
              icon={TrendingUp}
              title="Total Return"
              value={formatPercent(data.statistics.total_return / 100)}
              trend={data.statistics.total_return > 0 ? 'up' : 'down'}
              size="sm"
            />
            <MetricCard
              icon={Activity}
              title="Volatility"
              value={formatPercent(data.statistics.volatility / 100)}
              size="sm"
            />
            <MetricCard
              icon={Target}
              title="Sharpe Ratio"
              value={data.statistics.sharpe_ratio?.toFixed(2)}
              size="sm"
            />
            <MetricCard
              icon={TrendingDown}
              title="Max Drawdown"
              value={formatPercent(data.statistics.max_drawdown / 100)}
              variant="destructive"
              size="sm"
            />
          </MetricGroup>
        </div>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Time series data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

TimeseriesAnalysisWidget.displayName = 'TimeseriesAnalysisWidget';

export default React.memo(TimeseriesAnalysisWidget);
