'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, DollarSign, PieChart } from 'lucide-react';
import { Card, CardHeader, CardContent, Alert, Skeleton } from '@/components/shared';
import { cn } from '@/lib/utils';

// Simple utility functions
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

const isPositiveChange = (value: number | undefined | null): boolean => {
  if (value === undefined || value === null || isNaN(value)) {
    return false;
  }
  return value >= 0;
};

// Types
interface PortfolioSummary {
  total_value: number;
  total_return: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
  positions: number;
  cash: number;
}

interface UsePortfolioDataResult {
  summary: PortfolioSummary | null;
  loading: boolean;
  error: Error | null;
}

// Custom hook for portfolio data
const usePortfolioData = (): UsePortfolioDataResult => {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/portfolio/summary');
        if (!response.ok) {
          throw new Error('Failed to fetch portfolio data');
        }
        const data = await response.json();
        setSummary(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
        setSummary(null);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolioData();
  }, []);

  return { summary, loading, error };
};

export default function PortfolioSummaryComponent() {
  const { summary, loading, error } = usePortfolioData();

  if (loading) {
    return (
      <Card variant="default" size="md">
        <CardHeader>
          <Skeleton width="200px" height="24px" />
          <Skeleton width="300px" height="16px" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <Skeleton width="80px" height="16px" />
                  <Skeleton variant="circle" width="32px" height="32px" />
                </div>
                <Skeleton width="100px" height="32px" />
                <Skeleton width="60px" height="16px" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !summary) {
    return (
      <Alert 
        variant="error" 
        title="Portfolio Data Error"
        size="md"
      >
        {error?.message || 'Unable to load portfolio data. Please try refreshing the page.'}
      </Alert>
    );
  }

  const metrics = [
    {
      title: 'Total Value',
      value: formatCurrency(summary.total_value),
      icon: DollarSign,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Total Return',
      value: formatCurrency(summary.total_return),
      subtitle: formatPercent(summary.total_return_percent),
      icon: isPositiveChange(summary.total_return) ? TrendingUp : TrendingDown,
      color: isPositiveChange(summary.total_return) ? 'text-green-600' : 'text-red-600',
      bgColor: isPositiveChange(summary.total_return) ? 'bg-green-50' : 'bg-red-50',
    },
    {
      title: 'Day Change',
      value: formatCurrency(summary.day_change),
      subtitle: formatPercent(summary.day_change_percent),
      icon: isPositiveChange(summary.day_change) ? TrendingUp : TrendingDown,
      color: isPositiveChange(summary.day_change) ? 'text-green-600' : 'text-red-600',
      bgColor: isPositiveChange(summary.day_change) ? 'bg-green-50' : 'bg-red-50',
    },
    {
      title: 'Positions',
      value: (summary.positions ?? 0).toString(),
      subtitle: `${formatCurrency(summary.cash)} cash`,
      icon: PieChart,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

  return (
    <Card variant="default" size="md">
      <CardHeader>
        <h2 className="text-xl font-semibold text-gray-900">Portfolio Summary</h2>
        <p className="text-gray-600 text-sm mt-1">Real-time portfolio overview</p>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => {
            const Icon = metric.icon;
            return (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">{metric.title}</h3>
                  <div className={cn('p-2 rounded-lg', metric.bgColor)}>
                    <Icon className={cn('h-4 w-4', metric.color)} />
                  </div>
                </div>
                
                <div className="space-y-1">
                  <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                  {metric.subtitle && (
                    <p className={cn('text-sm', metric.color)}>{metric.subtitle}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}