/**
 * MonteCarloHistogram - Vertical bar chart showing distribution of final values
 * Displays frequency distribution of simulation outcomes
 */
import { formatCurrency } from '@/lib/formatters';

export interface HistogramBucket {
  range: string;
  count: number;
  percentage: number;
  midpoint: number;
  minValue: number;
  maxValue: number;
}

interface MonteCarloHistogramProps {
  data: HistogramBucket[];
}

export function MonteCarloHistogram({ data }: MonteCarloHistogramProps) {
  if (data.length === 0) {
    return (
      <div>
        <h3 className="text-lg font-medium mb-3">Distribution of Final Values</h3>
        <div className="h-64 flex items-center justify-center text-sm text-muted-foreground">
          No distribution data available
        </div>
      </div>
    );
  }

  const maxCount = Math.max(...data.map(b => b.count));

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Distribution of Final Values</h3>
      <div className="flex items-end justify-between h-64 gap-0.5 px-2">
        {data.map((bucket, index) => {
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
      <div className="text-xs text-center text-muted-foreground mt-6">Final Portfolio Value</div>
    </div>
  );
}
