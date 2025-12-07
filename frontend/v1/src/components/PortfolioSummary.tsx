'use client';

import { TrendingUp, TrendingDown, DollarSign, PieChart, XCircle } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { MetricCard } from '@/components/ui/metric-card';
import { usePortfolioSummary } from '@/hooks/use-portfolio-widgets';

// Utility functions
const formatCurrency = (amount: number | undefined | null): string => {
  if (amount === undefined || amount === null || isNaN(amount)) {
    return '$0.00';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

const formatPercent = (value: number | undefined | null): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00%';
  }
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

const determineMetricTrend = (value: number | undefined | null): 'positive' | 'negative' | 'neutral' => {
  if (value === undefined || value === null || isNaN(value)) {
    return 'neutral';
  }
  return value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';
};

export default function PortfolioSummaryComponent() {
  const { data: summary, loading, error, metadata, cacheHit } = usePortfolioSummary();

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-[200px]" />
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <MetricCard
                key={i}
                title="Loading..."
                value="$0.00"
                loading
                variant="default"
              />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !summary) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Portfolio Data Error</AlertTitle>
        <AlertDescription>
          {error || 'Unable to load portfolio data. Please try refreshing the page.'}
        </AlertDescription>
      </Alert>
    );
  }

  const metrics = [
    {
      title: 'Total Value',
      value: formatCurrency(summary.total_value),
      icon: DollarSign,
      variant: 'highlighted' as const,
      trend: 'neutral' as const,
    },
    {
      title: 'Total Return',
      value: formatCurrency(summary.total_return),
      subtitle: formatPercent(summary.total_return_percent),
      icon: summary.total_return >= 0 ? TrendingUp : TrendingDown,
      variant: 'default' as const,
      trend: determineMetricTrend(summary.total_return),
    },
    {
      title: 'Day Change',
      value: formatCurrency(summary.day_change),
      subtitle: formatPercent(summary.day_change_percent),
      icon: summary.day_change >= 0 ? TrendingUp : TrendingDown,
      variant: 'default' as const,
      trend: determineMetricTrend(summary.day_change),
    },
    {
      title: 'Positions',
      value: (summary.positions ?? 0).toString(),
      subtitle: `${formatCurrency(summary.allocated_cash)} cash`,
      icon: PieChart,
      variant: 'subtle' as const,
      trend: 'neutral' as const,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold text-foreground">Portfolio Summary</h2>
            <p className="text-muted-foreground text-sm mt-1">Real-time portfolio overview</p>
          </div>
          {cacheHit && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-md">
              Cached
            </span>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <MetricCard
              key={index}
              title={metric.title}
              value={metric.value}
              subtitle={metric.subtitle}
              icon={metric.icon}
              variant={metric.variant}
              trend={metric.trend}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}