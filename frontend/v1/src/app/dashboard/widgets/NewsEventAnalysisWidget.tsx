import React, { useState } from 'react';
import { useNewsEventAnalysis } from '@/hooks/use-portfolio-widgets';

interface NewsEventAnalysisWidgetProps {
  portfolioId?: string;
}

const NewsEventAnalysisWidget: React.FC<NewsEventAnalysisWidgetProps> = ({ portfolioId }) => {
  const [lookbackDays, setLookbackDays] = useState(30);
  const [surpriseThreshold, setSurpriseThreshold] = useState(5);
  
  const { data, loading, error } = useNewsEventAnalysis({ portfolioId, lookbackDays, surpriseThreshold });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
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

  return (
    <div className="p-4 space-y-3">
      <div className="flex flex-col gap-2">
        <select 
          value={lookbackDays} 
          onChange={(e) => setLookbackDays(Number(e.target.value))}
          className="px-2 py-1 text-sm border rounded-md bg-background"
        >
          {lookbackOptions.map(l => (
            <option key={l.value} value={l.value}>{l.label}</option>
          ))}
        </select>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-muted-foreground">
            Surprise Threshold: {surpriseThreshold}%
          </label>
          <input 
            type="range" 
            min="1" 
            max="20" 
            value={surpriseThreshold} 
            onChange={(e) => setSurpriseThreshold(Number(e.target.value))}
            className="w-full"
          />
        </div>
      </div>
      
      {hasFullData ? (
        <>
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">
                {data.sentiment_analysis?.overall_sentiment?.toFixed(2) || 0}
              </div>
              <div className="text-xs text-muted-foreground">Overall Sentiment</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">
                {data.market_impact?.price_correlation?.toFixed(2) || 0}
              </div>
              <div className="text-xs text-muted-foreground">Price Correlation</div>
            </div>
          </div>
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
        </>
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
