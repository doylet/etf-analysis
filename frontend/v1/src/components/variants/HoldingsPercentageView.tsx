/**
 * HoldingsPercentageView - Variant component for percentage-based holdings display
 * Demonstrates the Strategy pattern and composition for widget extensions
 */
import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Holding } from '@/types/widget-types';

interface HoldingsPercentageViewProps {
  holdings: Holding[];
  totalValue: number;
  isLoading: boolean;
  onRefresh?: () => void;
  showMetrics?: boolean;
  precision?: number;
  maxItems?: number;
  className?: string;
}

// Utility functions for percentage formatting
const formatPercentage = (value: number, precision: number = 2): string => {
  return `${(value * 100).toFixed(precision)}%`;
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount);
};

export function HoldingsPercentageView({
  holdings,
  totalValue,
  isLoading,
  onRefresh,
  showMetrics = true,
  precision = 1,
  maxItems = 10,
  className
}: HoldingsPercentageViewProps) {
  // Sort by weight (percentage) and take top N
  const topHoldings = holdings
    .sort((a, b) => (b.weight || 0) - (a.weight || 0))
    .slice(0, maxItems);

  // Calculate "Others" category for remaining holdings
  const displayedWeight = topHoldings.reduce((sum, h) => sum + (h.weight || 0), 0);
  const othersWeight = 1 - displayedWeight;
  const othersValue = totalValue * othersWeight;

  if (isLoading) {
    return (
      <div className={cn("p-3", className)}>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-foreground">Holdings Breakdown</h3>
          </div>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-3 h-3 bg-muted rounded animate-pulse" />
                  <div className="h-4 bg-muted rounded w-16 animate-pulse" />
                </div>
                <div className="text-right space-y-1">
                  <div className="h-4 bg-muted rounded w-12 animate-pulse" />
                  <div className="h-3 bg-muted rounded w-16 animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!holdings.length) {
    return (
      <div className={cn("p-3", className)}>
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-foreground">Holdings Breakdown</h3>
          <div className="text-center py-8">
            <p className="text-muted-foreground text-sm">No holdings data available</p>
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
              >
                Refresh
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("p-3", className)}>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-foreground">Holdings Breakdown</h3>
            <p className="text-xs text-muted-foreground">
              Top {topHoldings.length} positions • {formatCurrency(totalValue)}
            </p>
          </div>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
              disabled={isLoading}
            >
              Refresh
            </button>
          )}
        </div>

        <div className="space-y-2">
          {topHoldings.map((holding, index) => {
            const isPositive = (holding.dayChangePercent || 0) >= 0;
            const Icon = isPositive ? TrendingUp : TrendingDown;
            const weight = holding.weight || 0;
            
            // Color scheme for percentage bars
            const colors = [
              'bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-red-500',
              'bg-cyan-500', 'bg-pink-500', 'bg-yellow-500', 'bg-indigo-500', 'bg-emerald-500'
            ];
            const barColor = colors[index % colors.length];

            return (
              <div key={holding.symbol} className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 flex-1">
                    <div className={cn("w-3 h-3 rounded", barColor)} />
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-foreground tabular-nums">
                        {holding.symbol}
                      </span>
                      <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                        {holding.assetClass}
                      </span>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium tabular-nums">
                        {formatPercentage(weight, precision)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatCurrency(holding.marketValue)}
                      </span>
                    </div>
                    {showMetrics && holding.dayChangePercent !== undefined && (
                      <div className={cn(
                        'flex items-center justify-end gap-1 text-xs mt-0.5',
                        isPositive ? 'text-green-600' : 'text-red-600'
                      )}>
                        <Icon className="h-3 w-3" />
                        <span>{formatPercentage(holding.dayChangePercent / 100, 1)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Visual percentage bar */}
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className={cn("h-2 rounded-full transition-all duration-300", barColor)}
                    style={{ width: `${weight * 100}%` }}
                  />
                </div>
              </div>
            );
          })}

          {/* Others category if there are remaining holdings */}
          {othersWeight > 0.01 && (
            <div className="space-y-1 border-t pt-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-1">
                  <div className="w-3 h-3 rounded bg-gray-400" />
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-muted-foreground">
                      Others
                    </span>
                    <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                      {holdings.length - maxItems} positions
                    </span>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium tabular-nums text-muted-foreground">
                      {formatPercentage(othersWeight, precision)}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {formatCurrency(othersValue)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-gray-400 transition-all duration-300"
                  style={{ width: `${othersWeight * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Summary footer */}
        <div className="border-t pt-2 text-xs text-muted-foreground">
          <div className="flex justify-between">
            <span>{holdings.length} total positions</span>
            <span>100% allocated</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HoldingsPercentageView;