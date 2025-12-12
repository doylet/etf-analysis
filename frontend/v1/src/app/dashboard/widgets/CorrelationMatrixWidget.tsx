'use client';

import { Activity, XCircle, Calendar, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { useState, useMemo } from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { MetricCard } from '@/components/ui/metric-card';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { CacheBadge } from '@/components/ui/cache-badge';
import { WidgetSelect, WidgetSlider } from '@/components/ui/widget/widget-controls';
import { useCorrelationMatrix } from '@/hooks/use-portfolio-widgets';
import { formatPercent, formatDate } from '@/lib/formatters';
import type { ContentType } from './widget-metadata';

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

const getCorrelationColor = (value: number): string => {
  const absValue = Math.abs(value);
  if (absValue >= 0.8) return value > 0 ? 'bg-red-500' : 'bg-blue-500';
  if (absValue >= 0.6) return value > 0 ? 'bg-red-400' : 'bg-blue-400';
  if (absValue >= 0.4) return value > 0 ? 'bg-orange-400' : 'bg-cyan-400';
  if (absValue >= 0.2) return value > 0 ? 'bg-yellow-400' : 'bg-teal-400';
  return 'bg-gray-300';
};

const getCorrelationIntensity = (value: number): number => {
  return Math.abs(value);
};

// Generate dynamic insights based on correlation data
const generateCorrelationInsights = (
  maxCorrelation: number,
  avgCorrelation: number,
  symbols: string[]
) => {
  const insights: Array<{ 
    title: string; 
    description: string; 
    icon: typeof TrendingUp; 
    variant: 'default' | 'destructive' 
  }> = [];

  if (maxCorrelation > 0.9) {
    insights.push({
      title: 'Critical Correlation Risk',
      description: `Extremely high correlation detected (${(maxCorrelation * 100).toFixed(1)}%). Assets are moving almost identically, indicating severe concentration risk. Immediate diversification recommended.`,
      icon: AlertTriangle,
      variant: 'destructive'
    });
  } else if (maxCorrelation > 0.8) {
    insights.push({
      title: 'High Correlation Alert',
      description: `Strong correlation detected (${(maxCorrelation * 100).toFixed(1)}%). Some assets show high correlation, which may indicate concentrated risk. Consider diversification across ${symbols.length} holdings.`,
      icon: TrendingUp,
      variant: 'default'
    });
  } else if (maxCorrelation > 0.6) {
    insights.push({
      title: 'Moderate Correlation',
      description: `Moderate correlation detected (${(maxCorrelation * 100).toFixed(1)}%). Portfolio shows reasonable but not excessive correlation. Monitor for increased concentration.`,
      icon: TrendingUp,
      variant: 'default'
    });
  }

  if (avgCorrelation < 0.3 && symbols.length > 5) {
    insights.push({
      title: 'Well Diversified Portfolio',
      description: `Average correlation of ${(avgCorrelation * 100).toFixed(1)}% indicates good diversification across ${symbols.length} assets. Holdings are moving relatively independently.`,
      icon: CheckCircle,
      variant: 'default'
    });
  }

  return insights;
};


export default function CorrelationMatrixWidget({ 
  portfolioId, 
  defaultTimeWindow = 252 
}: CorrelationMatrixProps) {
  const [timeWindowDays, setTimeWindowDays] = useState(defaultTimeWindow);
  
  const { data: matrix, loading, error, cacheHit } = useCorrelationMatrix({
    portfolioId,
    timeWindowDays,
  });

  // Memoize symbols to avoid dependency issues
  const symbols = useMemo(() => matrix?.symbols || [], [matrix?.symbols]);

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

  // Generate dynamic insights based on actual data
  const insights = useMemo(() => {
    return generateCorrelationInsights(
      matrix?.statistics?.max_correlation || 0,
      matrix?.statistics?.avg_correlation || 0,
      symbols
    );
  }, [matrix, symbols]);

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
        {/* Summary Statistics */}
        <div className="flex flex-wrap justify-center gap-2">
          <MetricCard
            title="Average Correlation"
              value={formatPercent(matrix?.statistics?.avg_correlation || 0)}
              icon={Activity}
              variant="default"
              trend="neutral"
            />
            <MetricCard
              title="Highest Correlation"
              value={formatPercent(matrix?.statistics?.max_correlation || 0)}
              icon={TrendingUp}
              variant="default"
              trend={(matrix?.statistics?.max_correlation || 0) > 0.7 ? 'negative' : 'neutral'}
            />
            <MetricCard
              title="Time Period"
              value={`${matrix?.analysis_period?.days_analyzed || 0} days`}
              icon={Calendar}
              variant="subtle"
              trend="neutral"
            />
          </div>

          {/* Correlation Matrix Grid */}
          <div>
            <h4 className="text-sm font-medium mb-2">Correlation Heatmap</h4>
            <div className="overflow-x-auto">
              <div className="min-w-max">
                {/* Header Row */}
                <div className="flex">
                  <div className="w-16 h-12 flex items-center justify-center text-sm font-medium">
                    {/* Empty corner cell */}
                  </div>
                  {symbols.map((symbol) => (
                    <div
                      key={symbol}
                      className="w-16 h-12 flex items-center justify-center text-xs font-medium border-l border-border"
                    >
                      {symbol}
                    </div>
                  ))}
                </div>

                {/* Data Rows */}
                {symbols.map((rowSymbol) => (
                  <div key={rowSymbol} className="flex border-t border-border">
                    {/* Row Header */}
                    <div className="w-16 h-12 flex items-center justify-center text-xs font-medium bg-muted">
                      {rowSymbol}
                    </div>
                    
                    {/* Correlation Cells */}
                    {symbols.map((colSymbol) => {
                      const correlationValue = correlationData[rowSymbol]?.[colSymbol] ?? 0;
                      const isIdentity = rowSymbol === colSymbol;
                      
                      return (
                        <div
                          key={colSymbol}
                          className={`w-16 h-12 flex items-center justify-center text-xs font-mono border-l border-border relative group cursor-help
                            ${isIdentity ? 'bg-gray-100' : getCorrelationColor(correlationValue)}
                            ${isIdentity ? 'text-gray-800' : 'text-white'}
                          `}
                          style={{
                            opacity: isIdentity ? 0.5 : 0.7 + (getCorrelationIntensity(correlationValue) * 0.3)
                          }}
                          title={`${rowSymbol} vs ${colSymbol}: ${(correlationValue * 100).toFixed(1)}%`}
                        >
                          {isIdentity ? '1.0' : (correlationValue * 100).toFixed(0)}
                          
                          {/* Tooltip */}
                          {/* <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap">
                            {rowSymbol} vs {colSymbol}: {formatPercent(correlationValue)}
                          </div> */}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>

            {/* Legend */}
            <div className="mt-4 flex items-center gap-4 text-sm">
              <span className="text-text-tertiary">Correlation strength:</span>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-gray-300 rounded"></div>
                <span className="text-text-secondary">Weak (0-20%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-400 rounded"></div>
                <span className="text-text-secondary">Moderate (20-60%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-400 rounded"></div>
                <span className="text-text-secondary">Strong (60%+)</span>
              </div>
            </div>
          </div>

          {/* Insights */}
          {insights.map((insight, index) => (
            <WidgetInsight
              key={index}
              title={insight.title}
              description={insight.description}
              icon={insight.icon}
              variant={insight.variant}
            />
          ))}
        </div>
    </div>
  );
}