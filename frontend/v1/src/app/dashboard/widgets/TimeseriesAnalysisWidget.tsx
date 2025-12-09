import React, { useState } from 'react';
import { useTimeseriesAnalysis } from '@/hooks/use-portfolio-widgets';

interface TimeseriesAnalysisWidgetProps {
  portfolioId?: string;
}

const TimeseriesAnalysisWidget: React.FC<TimeseriesAnalysisWidgetProps> = ({ portfolioId }) => {
  const [timePeriod, setTimePeriod] = useState('1Y');
  const [analysisType, setAnalysisType] = useState('Portfolio Overview');
  
  const { data, loading, error } = useTimeseriesAnalysis({ portfolioId, timePeriod, analysisType });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.statistics?.total_return !== undefined;

  const periods = [
    { value: '1W', label: '1 Week' },
    { value: '1M', label: '1 Month' },
    { value: '3M', label: '3 Months' },
    { value: '6M', label: '6 Months' },
    { value: '1Y', label: '1 Year' },
    { value: '2Y', label: '2 Years' },
    { value: '5Y', label: '5 Years' },
  ];

  const analysisTypes = [
    { value: 'Portfolio Overview', label: 'Portfolio Overview' },
    { value: 'Stationarity', label: 'Stationarity' },
    { value: 'Seasonality', label: 'Seasonality' },
    { value: 'Trend Analysis', label: 'Trend Analysis' },
    { value: 'Volatility', label: 'Volatility' },
  ];

  return (
    <div className="p-4 space-y-3">
      <div className="flex gap-2">
        <select 
          value={timePeriod} 
          onChange={(e) => setTimePeriod(e.target.value)}
          className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
        >
          {periods.map(p => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        <select 
          value={analysisType} 
          onChange={(e) => setAnalysisType(e.target.value)}
          className="flex-1 px-2 py-1 text-sm border rounded-md bg-background"
        >
          {analysisTypes.map(a => (
            <option key={a.value} value={a.value}>{a.label}</option>
          ))}
        </select>
      </div>
      
      {hasFullData ? (
        <>
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">{data.statistics.total_return?.toFixed(2)}%</div>
              <div className="text-xs text-muted-foreground">Total Return</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">{data.statistics.volatility?.toFixed(2)}%</div>
              <div className="text-xs text-muted-foreground">Volatility</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">{data.statistics.sharpe_ratio?.toFixed(2)}</div>
              <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-destructive">{data.statistics.max_drawdown?.toFixed(2)}%</div>
              <div className="text-xs text-muted-foreground">Max Drawdown</div>
            </div>
          </div>
          {data.price_data && data.price_data.length > 0 && (
            <div className="mt-2 text-xs text-muted-foreground text-center">
              {data.price_data.length} data points
            </div>
          )}
        </>
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
