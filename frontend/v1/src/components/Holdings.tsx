'use client';

import { TrendingUp, TrendingDown } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { useHoldingsBreakdown } from '@/hooks/use-portfolio-widgets';

interface Holding {
  symbol?: string;
  name?: string;
  asset_class?: string;
  quantity?: number;
  weight?: number;
  market_value?: number;
  current_price?: number;
}

// Utility functions for tabular data formatting
const formatWeight = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

const formatQuantity = (quantity: number): string => {
  // Use tabular numerals for consistent alignment
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 4,
  }).format(quantity);
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount);
};

export default function HoldingsComponent() {
  const { data: breakdown, loading, error } = useHoldingsBreakdown();
  
  // Extract holdings from the breakdown response
  const holdings: Holding[] = breakdown?.holdings || [];

  if (loading) {
    return (
      <div className="p-3">
        <div className="space-y-3">
          <div>
            <h3 className="text-sm font-medium text-foreground">Holdings</h3>
          </div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center justify-between p-2 border rounded-lg">
              <div className="space-y-1">
                <Skeleton className="h-4 w-[60px]" />
                <Skeleton className="h-3 w-[100px]" />
              </div>
              <div className="text-right space-y-1">
                <Skeleton className="h-4 w-[80px]" />
                <Skeleton className="h-3 w-[60px]" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !holdings.length) {
    return (
      <div className="p-3">
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-foreground">Holdings</h3>
          <div className="text-center py-4">
            <p className="text-muted-foreground text-sm">
              {error || 'No holdings data available'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-3 h-full overflow-auto">
      <div className="space-y-3">
        <div>
          <h3 className="text-sm font-medium text-foreground">Holdings</h3>
          <p className="text-xs text-muted-foreground">{holdings.length} positions</p>
        </div>
        <div className="space-y-2">
          {holdings.map((holding, index) => {
            // Calculate P&L based on weight and market value
            const isPositive = (holding.weight || 0) > 0.1; // Simple heuristic for display
            const Icon = isPositive ? TrendingUp : TrendingDown;
            
            return (
              <div key={`${holding.symbol || 'unknown'}-${index}`} className="flex items-center justify-between p-2 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-sm text-foreground tabular-nums">{holding.symbol}</h4>
                    <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                      {holding.asset_class || 'Unknown'}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground truncate">{holding.name || 'Unnamed'}</p>
                  <p className="text-xs text-muted-foreground mt-0.5 tabular-nums">
                    {formatQuantity(holding.quantity || 0)} • {formatWeight(holding.weight || 0)}
                  </p>
                </div>
                
                <div className="text-right space-y-0.5">
                  <div className="font-medium text-sm">
                    {formatCurrency(holding.market_value || 0)}
                  </div>
                  <div className={cn(
                    'flex items-center justify-end gap-1 text-xs',
                    isPositive ? 'text-green-600' : 'text-red-600'
                  )}>
                    <Icon className="h-3 w-3" />
                    <span>{formatWeight(holding.weight || 0)}</span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {formatCurrency(holding.current_price || 0)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}