'use client';

import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, PieChart, XCircle } from 'lucide-react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { MetricCard } from '@/components/ui/metric-card';
import { usePortfolioSummary } from '@/hooks/use-portfolio-widgets';

export default function PortfolioSummaryComponent() {
  // Use portfolio summary hook
  const { data, loading, error } = usePortfolioSummary({
    autoRefresh: true,
    refreshInterval: 30000
  });

  if (loading) {
    return (
      <div className="p-3">
        <div className="space-y-3">
          <div className="flex justify-between items-start">
            <div>
              <Skeleton className="h-5 w-[140px]" />
              <Skeleton className="h-4 w-[180px] mt-1" />
            </div>
            <Skeleton className="h-5 w-[50px]" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="p-3 border rounded-lg">
                <Skeleton className="h-4 w-[80px] mb-2" />
                <Skeleton className="h-6 w-[70px]" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3">
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertTitle>Portfolio Data Error</AlertTitle>
          <AlertDescription>
            {error || 'Unable to load portfolio data. Please try refreshing the page.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const formatPercent = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value / 100);
  };

  const metrics = [
    {
      title: 'Total Value',
      value: formatCurrency(data.total_value),
      icon: DollarSign,
      variant: 'highlighted' as const,
      trend: 'neutral' as const,
    },
    {
      title: 'Total Return',
      value: formatCurrency(data.total_return),
      subtitle: formatPercent(data.total_return_percent),
      icon: data.total_return >= 0 ? TrendingUp : TrendingDown,
      variant: 'default' as const,
      trend: data.total_return >= 0 ? ('positive' as const) : ('negative' as const),
    },
    {
      title: 'Day Change',
      value: formatCurrency(data.day_change),
      subtitle: formatPercent(data.day_change_percent),
      icon: data.day_change >= 0 ? TrendingUp : TrendingDown,
      variant: 'default' as const,
      trend: data.day_change >= 0 ? ('positive' as const) : ('negative' as const),
    },
    {
      title: 'Positions',
      value: data.positions.toString(),
      subtitle: formatCurrency(data.allocated_cash),
      icon: PieChart,
      variant: 'subtle' as const,
      trend: 'neutral' as const,
    },
  ];

  return (
    <div className="p-3">
      <div className="space-y-3">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-sm font-semibold text-foreground">Portfolio Summary</h3>
            <p className="text-xs text-muted-foreground mt-1">Real-time portfolio overview</p>
          </div>
          <div className="flex items-center gap-2">
            {(data as any).market_status && (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-md capitalize">
                {(data as any).market_status.replace('_', ' ')}
              </span>
            )}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
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
        
        <div className="text-xs text-muted-foreground text-center">
          Last updated: {new Date(data.last_updated).toLocaleString()}
        </div>
      </div>
    </div>
  );
}