import React, { useState } from 'react';
import { useDividendAnalysis } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { MetricCard } from '@/components/ui/metric-card';
import { WidgetSelect } from '@/components/ui/widget/widget-controls';
import { XCircle, DollarSign, Percent } from 'lucide-react';
import { formatCurrency, formatPercent } from '@/lib/formatters';
import { TIME_PERIODS_EXTENDED } from '@/lib/widget-constants';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 4 },
  contentType: 'balanced' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.5,
  isScrollable: true,
} as const;

interface DividendAnalysisWidgetProps {
  portfolioId?: string;
}

const DividendAnalysisWidget: React.FC<DividendAnalysisWidgetProps> = ({ portfolioId }) => {
  const [timePeriod, setTimePeriod] = useState('All');
  
  const { data, loading, error } = useDividendAnalysis({ portfolioId, timePeriod });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Dividend Data Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.total_dividends !== undefined && data.dividend_yield !== undefined;

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-2 flex-shrink-0">
        <WidgetSelect
          value={timePeriod}
          onChange={setTimePeriod}
          options={TIME_PERIODS_EXTENDED.filter(p => ['All', '1Y', '2Y', '5Y'].includes(p.value))}
          className="flex-1"
        />
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3 mt-3">
          <div className="flex flex-wrap justify-center gap-3">
            <MetricCard
              title="Total Dividends"
              value={formatCurrency(data.total_dividends)}
              icon={DollarSign}
              variant="default"
              size="sm"
            />
            <MetricCard
              title="Yield"
              value={formatPercent(data.dividend_yield / 100)}
              icon={Percent}
              variant="default"
              size="sm"
            />
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
        </div>
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
