'use client';

import { TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { usePortfolioSummary } from '@/hooks/use-portfolio-summary';
import { BackendHolding } from '@/lib/portfolio-service';

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

const formatPercent = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

const formatWeight = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

export default function HoldingsComponent() {
  const { summary, loading, error } = usePortfolioSummary();
  
  // Extract holdings from the summary response
  const holdings = summary?.holdings || [];

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-foreground">Holdings</h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-[80px]" />
                  <Skeleton className="h-3 w-[120px]" />
                </div>
                <div className="text-right space-y-2">
                  <Skeleton className="h-4 w-[100px]" />
                  <Skeleton className="h-3 w-[80px]" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !holdings.length) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-foreground">Holdings</h3>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            {error || 'No holdings data available'}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-foreground">Holdings</h3>
        <p className="text-sm text-muted-foreground">{holdings.length} positions</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {holdings.map((holding: BackendHolding, index: number) => {
            const isPositive = holding.unrealized_gain_loss >= 0;
            const Icon = isPositive ? TrendingUp : TrendingDown;
            
            return (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-shadow">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-foreground">{holding.symbol}</h4>
                    <span className="text-xs text-muted-foreground bg-gray-100 px-2 py-1 rounded">
                      {holding.type}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground truncate">{holding.name}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {holding.quantity} shares • {formatWeight(holding.weight_pct)} of portfolio
                  </p>
                </div>
                
                <div className="text-right">
                  <p className="font-semibold text-foreground">
                    {formatCurrency(holding.current_value)}
                  </p>
                  <div className={cn(
                    'flex items-center gap-1 text-sm',
                    isPositive ? 'text-green-600' : 'text-red-600'
                  )}>
                    <Icon className="h-3 w-3" />
                    <span>{formatPercent(holding.unrealized_gain_loss_pct)}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {formatCurrency(holding.current_price)} per share
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}