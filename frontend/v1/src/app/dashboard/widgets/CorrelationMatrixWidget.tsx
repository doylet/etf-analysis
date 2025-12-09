'use client';

import { Activity, XCircle, Calendar, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { MetricCard } from '@/components/ui/metric-card';
import { useCorrelationMatrix } from '@/hooks/use-portfolio-widgets';

interface CorrelationMatrixProps {
  portfolioId?: string;
  defaultTimeWindow?: number;
}

const formatPercent = (value: number | undefined | null): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00%';
  }
  return `${(value * 100).toFixed(1)}%`;
};

const formatDate = (dateString: string): string => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return 'Invalid Date';
  }
};

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

export default function CorrelationMatrixWidget({ 
  portfolioId, 
  defaultTimeWindow = 252 
}: CorrelationMatrixProps) {
  const [timeWindowDays, setTimeWindowDays] = useState(defaultTimeWindow);
  
  const { data: matrix, loading, error, cacheHit } = useCorrelationMatrix({
    portfolioId,
    timeWindowDays,
  });

  const timeWindowOptions = [
    { value: 30, label: '1 Month' },
    { value: 90, label: '3 Months' },
    { value: 180, label: '6 Months' },
    { value: 252, label: '1 Year' },
    { value: 504, label: '2 Years' },
  ];

  if (loading) {
    return (
      <div className="p-3">
        <div className="space-y-3">
          <div className="flex justify-between items-start">
            <div>
              <Skeleton className="h-5 w-[160px]" />
              <Skeleton className="h-4 w-[200px] mt-1" />
            </div>
            <Skeleton className="h-7 w-[100px]" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
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
      </div>
    );
  }

  if (error || !matrix) {
    return (
      <div className="p-3">
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertTitle>Correlation Data Error</AlertTitle>
          <AlertDescription>
            {error || 'Unable to load correlation matrix. Please try refreshing the page.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const symbols = matrix?.symbols || [];
  
  // Transform correlation matrix from API format to expected format
  let correlationData: Record<string, Record<string, number>> = {};
  if (matrix?.correlation_matrix) {
    if (Array.isArray(matrix.correlation_matrix)) {
      // Convert array format to nested object format
      matrix.correlation_matrix.forEach((item: {symbol1: string, symbol2: string, correlation: number}) => {
        if (!correlationData[item.symbol1]) {
          correlationData[item.symbol1] = {};
        }
        correlationData[item.symbol1][item.symbol2] = item.correlation;
      });
    } else {
      // Already in correct format
      correlationData = matrix.correlation_matrix as Record<string, Record<string, number>>;
    }
  }

  return (
    <div className="p-3">
      <div className="space-y-3">
        <div className="flex justify-between items-start">
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
            {cacheHit && (
              <span className="text-xs bg-muted-100 text-foreground-700 px-2 py-1 rounded-md">
                Cached
              </span>
            )}
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
        <div className="space-y-3">
          {/* Summary Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
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
          {(matrix?.statistics?.max_correlation || 0) > 0.8 && (
            <Alert>
              <TrendingUp className="h-4 w-4" />
              <AlertTitle>High Correlation Alert</AlertTitle>
              <AlertDescription>
                Some assets show high correlation ({formatPercent(matrix?.statistics?.max_correlation || 0)}), 
                which may indicate concentrated risk. Consider diversification.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
}