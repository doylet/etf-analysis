import React, { useState } from 'react';
import { useNewsEventAnalysis } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { WidgetSelect, WidgetSlider } from '@/components/ui/widget/widget-controls';
import { formatNumber } from '@/lib/formatters';
import { XCircle, MessageSquare, TrendingUp } from 'lucide-react';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 5 },
  contentType: 'height-heavy' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.2,
  isScrollable: true,
} as const;

interface NewsEventAnalysisWidgetProps {
  portfolioId?: string;
}

const NewsEventAnalysisWidget: React.FC<NewsEventAnalysisWidgetProps> = ({ portfolioId }) => {
  const [lookbackDays, setLookbackDays] = useState(30);
  const [surpriseThreshold, setSurpriseThreshold] = useState(5);
  
  const { data, loading, error } = useNewsEventAnalysis({ portfolioId, lookbackDays, surpriseThreshold });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="News Data Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.sentiment_analysis?.overall_sentiment !== undefined;

  const lookbackOptions = [
    { value: 7, label: '1 Week' },
    { value: 14, label: '2 Weeks' },
    { value: 30, label: '1 Month' },
    { value: 60, label: '2 Months' },
    { value: 90, label: '3 Months' },
  ];

  const lookbackOptionsForSelect = lookbackOptions.map(opt => ({
    value: String(opt.value),
    label: opt.label
  }));

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex flex-col gap-2 flex-shrink-0">
        <WidgetSelect
          value={String(lookbackDays)}
          onChange={(value) => setLookbackDays(Number(value))}
          options={lookbackOptionsForSelect}
        />
        <WidgetSlider
          label="Surprise Threshold (%)"
          value={surpriseThreshold}
          onChange={setSurpriseThreshold}
          min={1}
          max={20}
          step={1}
        />
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3">
          <MetricGroup columns={2}>
            <MetricCard
              icon={MessageSquare}
              title="Overall Sentiment"
              value={formatNumber(data.sentiment_analysis?.overall_sentiment || 0, 2)}
              trend={data.sentiment_analysis?.overall_sentiment > 0 ? 'up' : 'down'}
              size="sm"
            />
            <MetricCard
              icon={TrendingUp}
              title="Price Correlation"
              value={formatNumber(data.market_impact?.price_correlation || 0, 2)}
              size="sm"
            />
          </MetricGroup>
          {data.events && data.events.length > 0 && (
            <div className="mt-3">
              <div className="text-xs font-medium text-muted-foreground mb-2">Recent Events</div>
              <div className="space-y-2 max-h-40 overflow-auto">
                {data.events.slice(0, 3).map((event, idx) => (
                  <div key={idx} className="p-2 bg-muted rounded-md">
                    <div className="text-xs font-medium text-foreground mb-1">{event.title}</div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">
                        {new Date(event.date).toLocaleDateString()}
                      </span>
                      <span className={`text-xs ${
                        event.sentiment >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                      }`}>
                        Sentiment: {event.sentiment?.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'News and event analysis data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

NewsEventAnalysisWidget.displayName = 'NewsEventAnalysisWidget';

export default React.memo(NewsEventAnalysisWidget);
