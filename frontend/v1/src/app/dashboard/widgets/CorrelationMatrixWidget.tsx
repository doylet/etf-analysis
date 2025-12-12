'use client';

import { Activity, XCircle } from 'lucide-react';
import { useState, useMemo } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { CacheBadge } from '@/components/ui/cache-badge';
import { useCorrelationMatrix } from '@/hooks/use-portfolio-widgets';
import { formatDate } from '@/lib/formatters';
import type { ContentType } from './widget-metadata';
import { CorrelationMetrics } from './correlation-matrix/CorrelationMetrics';
import { CorrelationGrid } from './correlation-matrix/CorrelationGrid';
import { CorrelationInsights } from './correlation-matrix/CorrelationInsights';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 4, h: 6 },
  contentType: 'square' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.0,
  isScrollable: false,
} as const;

interface CorrelationMatrixProps {
  portfolioId?: string;
  defaultTimeWindow?: number;
}

export default function CorrelationMatrixWidget({ 
  portfolioId, 
  defaultTimeWindow = 252 
}: CorrelationMatrixProps) {
  const [timeWindowDays, setTimeWindowDays] = useState(defaultTimeWindow);
  
  const { data: matrix, loading, error, cacheHit } = useCorrelationMatrix({
    portfolioId,
    timeWindowDays,
  });

  // Transform correlation matrix from API format to expected format
  const correlationData = useMemo(() => {
    const data: Record<string, Record<string, number>> = {};
    if (matrix?.correlation_matrix) {
      if (Array.isArray(matrix.correlation_matrix)) {
        // Convert array format to nested object format
        matrix.correlation_matrix.forEach((item: {symbol1: string, symbol2: string, correlation: number}) => {
          if (!data[item.symbol1]) {
            data[item.symbol1] = {};
          }
          data[item.symbol1][item.symbol2] = item.correlation;
        });
      } else {
        // Already in correct format
        return matrix.correlation_matrix as Record<string, Record<string, number>>;
      }
    }
    return data;
  }, [matrix]);

  const timeWindowOptions = [
    { value: '30', label: '1 Month' },
    { value: '90', label: '3 Months' },
    { value: '180', label: '6 Months' },
    { value: '252', label: '1 Year' },
    { value: '504', label: '2 Years' },
  ] as const;

  if (loading) {
    return (
      <div className="space-y-2">
        <div className="flex justify-between items-start">
          <div>
            <Skeleton className="h-5 w-[160px]" />
            <Skeleton className="h-4 w-[200px] mt-1" />
          </div>
          <Skeleton className="h-7 w-[100px]" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="p-3 border rounded-lg">
              <Skeleton className="h-4 w-[80px] mb-2" />
              <Skeleton className="h-6 w-[60px]" />
            </div>
          ))}
        </div>
        <div className="h-48 bg-muted rounded-lg flex items-center justify-center">
          <Skeleton className="h-6 w-[120px]" />
        </div>
      </div>
    );
  }

  if (error || !matrix) {
    return (
      <WidgetInsight
        title="Correlation Data Error"
        description={error || 'Unable to load correlation matrix. Please try refreshing the page.'}
        icon={XCircle}
        variant="destructive"
      />
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-start flex-shrink-0">
        <div>
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Correlation Matrix
          </h3>
          <p className="text-xs text-muted-foreground mt-1">
            Asset correlation between {`${formatDate(matrix?.analysis_period?.start_date || '')} and ${formatDate(matrix?.analysis_period?.end_date || '')}`}.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <CacheBadge show={cacheHit} />
          <select
            value={timeWindowDays}
            onChange={(e) => setTimeWindowDays(Number(e.target.value))}
            className="text-xs border border-border rounded-md px-2 py-1 bg-background"
          >
            {timeWindowOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 overflow-y-auto min-h-0 space-y-2">
        <CorrelationMetrics
          avgCorrelation={matrix?.statistics?.avg_correlation || 0}
          maxCorrelation={matrix?.statistics?.max_correlation || 0}
          daysAnalyzed={matrix?.analysis_period?.days_analyzed || 0}
        />

        {/* Correlation Matrix Grid */}
        <CorrelationGrid
          symbols={matrix?.symbols || []}
          correlationData={correlationData}
        />

        <CorrelationInsights
          maxCorrelation={matrix?.statistics?.max_correlation || 0}
          avgCorrelation={matrix?.statistics?.avg_correlation || 0}
          symbolCount={matrix?.symbols?.length || 0}
        />
        </div>
    </div>
  );
}