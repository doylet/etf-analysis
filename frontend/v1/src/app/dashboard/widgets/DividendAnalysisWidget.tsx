import React, { useState } from 'react';
import { useDividendAnalysis } from '@/hooks/use-portfolio-widgets';

interface DividendAnalysisWidgetProps {
  portfolioId?: string;
}

const DividendAnalysisWidget: React.FC<DividendAnalysisWidgetProps> = ({ portfolioId }) => {
  const [timePeriod, setTimePeriod] = useState('All');
  
  const { data, loading, error } = useDividendAnalysis({ portfolioId, timePeriod });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.total_dividends !== undefined && data.dividend_yield !== undefined;

  const periods = [
    { value: 'All', label: 'All Time' },
    { value: '1Y', label: '1 Year' },
    { value: '2Y', label: '2 Years' },
    { value: '5Y', label: '5 Years' },
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
      </div>
      
      {hasFullData ? (
        <>
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">${data.total_dividends?.toLocaleString()}</div>
              <div className="text-xs text-muted-foreground">Total Dividends</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">{data.dividend_yield?.toFixed(2)}%</div>
              <div className="text-xs text-muted-foreground">Yield</div>
            </div>
          </div>
          {data.top_dividend_holdings && data.top_dividend_holdings.length > 0 && (
            <div className="mt-3">
              <div className="text-xs font-medium text-muted-foreground mb-2">Top Dividend Holdings</div>
              <div className="space-y-1">
                {data.top_dividend_holdings.slice(0, 3).map((holding) => (
                  <div key={holding.symbol} className="flex justify-between text-xs">
                    <span className="text-foreground">{holding.symbol}</span>
                    <span className="text-muted-foreground">{holding.yield?.toFixed(2)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Dividend analysis data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

DividendAnalysisWidget.displayName = 'DividendAnalysisWidget';

export default React.memo(DividendAnalysisWidget);
