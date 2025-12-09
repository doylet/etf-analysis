'use client';

import { TrendingUp, TrendingDown } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { useWidgetController } from '@/hooks/use-widget-controller';
import { WidgetType } from '@/lib/interfaces/IWidgetConfiguration';
import { Holding, HoldingsConfiguration } from '@/types/widget-types';
import { HoldingsData } from '@/lib/controllers/HoldingsController';
import HoldingsPercentageView from './variants/HoldingsPercentageView';
import HoldingsTableView from './variants/HoldingsTableView';

// Default configuration for Holdings widget
const DEFAULT_CONFIG: HoldingsConfiguration = {
  id: 'holdings-widget',
  type: WidgetType.HOLDINGS,
  title: 'Holdings',
  portfolioId: 'default', // This should come from app context
  displayMode: 'detailed',
  sortBy: 'marketValue',
  sortDirection: 'desc',
  maxItems: 50,
  showMetrics: true,
  currencyCode: 'USD',
  precision: 2,
  showSkeleton: true,
  refreshInterval: 30000 // 30 seconds
};

// Props interface for external configuration
interface HoldingsComponentProps {
  configuration?: Partial<HoldingsConfiguration>;
  className?: string;
}

// Utility functions for tabular data formatting (used by compact/detailed views)
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

export default function HoldingsComponent({ 
  configuration: configOverrides, 
  className 
}: HoldingsComponentProps = {}) {
  // Merge provided configuration with defaults
  const finalConfig: HoldingsConfiguration = {
    ...DEFAULT_CONFIG,
    ...configOverrides
  };

  // Use SOLID architecture with dependency injection
  const { data, isLoading, error, refresh } = useWidgetController<HoldingsData, HoldingsConfiguration>({
    configuration: finalConfig,
    type: WidgetType.HOLDINGS,
    autoInitialize: true,
    autoDispose: true,
    onError: (error) => {
      console.error('Holdings widget error:', error);
    },
    onRefresh: (data) => {
      console.debug('Holdings data refreshed:', data);
    }
  });
  
  // Extract holdings from the transformed data
  const holdings: Holding[] = data?.holdings || [];

  // Strategy Pattern: Select presentation component based on display mode
  const renderHoldingsView = () => {
    const commonProps = {
      holdings,
      totalValue: data?.metadata.totalValue || 0,
      isLoading,
      onRefresh: () => refresh(true),
      showMetrics: finalConfig.showMetrics,
      precision: finalConfig.precision,
      maxItems: finalConfig.maxItems,
      className
    };

    switch (finalConfig.displayMode) {
      case 'percentage':
        return <HoldingsPercentageView {...commonProps} />;
        
      case 'table':
        return (
          <HoldingsTableView 
            {...commonProps}
            sortBy={finalConfig.sortBy}
            sortOrder={finalConfig.sortDirection}
          />
        );
        
      case 'compact':
      case 'detailed':
      default:
        return renderDetailedView(commonProps);
    }
  };

  // Legacy detailed view implementation (maintains backwards compatibility)
  const renderDetailedView = ({ 
    holdings, 
    totalValue, 
    isLoading, 
    onRefresh, 
    showMetrics 
  }: {
    holdings: Holding[];
    totalValue: number;
    isLoading: boolean;
    onRefresh?: () => void;
    showMetrics?: boolean;
  }) => {
    if (isLoading || (!data && !error)) {
      return (
        <div className={cn("p-3", className)}>
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
        <div className={cn("p-3", className)}>
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-foreground">Holdings</h3>
            <div className="text-center py-4">
              <p className="text-muted-foreground text-sm">
                {error?.message || 'No holdings data available'}
              </p>
              <button 
                onClick={onRefresh}
                className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className={cn("p-3 h-full overflow-auto", className)}>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-foreground">Holdings</h3>
              <p className="text-xs text-muted-foreground">
                {holdings.length} positions • {formatCurrency(totalValue)}
              </p>
            </div>
            <button
              onClick={onRefresh}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
              disabled={isLoading}
            >
              Refresh
            </button>
          </div>
          <div className="space-y-2">
            {holdings.slice(0, finalConfig.maxItems).map((holding, index) => {
              // Calculate P&L based on weight and market value
              const isPositive = (holding.dayChangePercent || 0) >= 0;
              const Icon = isPositive ? TrendingUp : TrendingDown;
              
              return (
                <div key={`${holding.symbol || 'unknown'}-${index}`} className="flex items-center justify-between p-2 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-sm text-foreground tabular-nums">{holding.symbol}</h4>
                      <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                        {holding.assetClass || 'Unknown'}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground truncate">{holding.name || 'Unnamed'}</p>
                    <p className="text-xs text-muted-foreground mt-0.5 tabular-nums">
                      {formatQuantity(holding.quantity || 0)} • {formatWeight(holding.weight || 0)}
                    </p>
                  </div>
                  
                  <div className="text-right space-y-0.5">
                    <div className="font-medium text-sm">
                      {formatCurrency(holding.marketValue || 0)}
                    </div>
                    {showMetrics && holding.dayChangePercent !== undefined && (
                      <div className={cn(
                        'flex items-center justify-end gap-1 text-xs',
                        isPositive ? 'text-green-600' : 'text-red-600'
                      )}>
                        <Icon className="h-3 w-3" />
                        <span>{formatWeight(holding.dayChangePercent / 100)}</span>
                      </div>
                    )}
                    <div className="text-xs text-muted-foreground">
                      {formatCurrency(holding.currentPrice || 0)}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  // Render the appropriate view based on configuration
  return renderHoldingsView();
}