/**
 * HoldingsTableView - Table variant component for holdings display
 * Demonstrates the Strategy pattern with tabular data presentation
 */
import React, { useState, useMemo } from 'react';
import { TrendingUp, TrendingDown, ChevronUp, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Holding } from '@/types/widget-types';

interface HoldingsTableViewProps {
  holdings: Holding[];
  totalValue: number;
  isLoading: boolean;
  onRefresh?: () => void;
  showMetrics?: boolean;
  precision?: number;
  maxItems?: number;
  className?: string;
  sortBy?: keyof Holding;
  sortOrder?: 'asc' | 'desc';
  onSort?: (field: keyof Holding, order: 'asc' | 'desc') => void;
}

type SortableField = 'symbol' | 'assetClass' | 'quantity' | 'weight' | 'marketValue' | 'currentPrice' | 'dayChangePercent';

// Utility functions
const formatWeight = (value: number, precision: number = 2): string => {
  return `${(value * 100).toFixed(precision)}%`;
};

const formatQuantity = (quantity: number): string => {
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

interface SortHeaderProps {
  field: SortableField;
  label: string;
  currentSort?: keyof Holding;
  currentOrder?: 'asc' | 'desc';
  onSort: (field: keyof Holding, order: 'asc' | 'desc') => void;
  className?: string;
}

function SortHeader({ field, label, currentSort, currentOrder, onSort, className }: SortHeaderProps) {
  const isActive = currentSort === field;
  
  const handleClick = () => {
    if (isActive) {
      onSort(field, currentOrder === 'asc' ? 'desc' : 'asc');
    } else {
      onSort(field, 'desc');
    }
  };

  return (
    <th className={cn("text-left cursor-pointer hover:bg-muted/50 transition-colors", className)}>
      <div className="flex items-center gap-1 px-2 py-1.5" onClick={handleClick}>
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {label}
        </span>
        <div className="flex flex-col">
          <ChevronUp 
            className={cn(
              "h-3 w-3 text-muted-foreground transition-colors",
              isActive && currentOrder === 'asc' && "text-foreground"
            )} 
          />
          <ChevronDown 
            className={cn(
              "h-3 w-3 text-muted-foreground transition-colors -mt-1",
              isActive && currentOrder === 'desc' && "text-foreground"
            )} 
          />
        </div>
      </div>
    </th>
  );
}

export function HoldingsTableView({
  holdings,
  totalValue,
  isLoading,
  onRefresh,
  showMetrics = true,
  precision = 2,
  maxItems = 50,
  className,
  sortBy: initialSortBy = 'marketValue',
  sortOrder: initialSortOrder = 'desc',
  onSort: externalOnSort
}: HoldingsTableViewProps) {
  const [internalSortBy, setInternalSortBy] = useState<keyof Holding>(initialSortBy);
  const [internalSortOrder, setInternalSortOrder] = useState<'asc' | 'desc'>(initialSortOrder);

  const sortBy = externalOnSort ? initialSortBy : internalSortBy;
  const sortOrder = externalOnSort ? initialSortOrder : internalSortOrder;

  const handleSort = (field: keyof Holding, order: 'asc' | 'desc') => {
    if (externalOnSort) {
      externalOnSort(field, order);
    } else {
      setInternalSortBy(field);
      setInternalSortOrder(order);
    }
  };

  // Sort and paginate holdings
  const sortedHoldings = useMemo(() => {
    const sorted = [...holdings].sort((a, b) => {
      const aVal = a[sortBy] || 0;
      const bVal = b[sortBy] || 0;
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortOrder === 'asc' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      
      const aNum = Number(aVal);
      const bNum = Number(bVal);
      
      return sortOrder === 'asc' ? aNum - bNum : bNum - aNum;
    });
    
    return sorted.slice(0, maxItems);
  }, [holdings, sortBy, sortOrder, maxItems]);

  if (isLoading) {
    return (
      <div className={cn("p-3", className)}>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-foreground">Holdings Table</h3>
          </div>
          <div className="border rounded-lg overflow-hidden">
            <div className="animate-pulse">
              <div className="bg-muted h-10 border-b" />
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-background h-12 border-b last:border-b-0" />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!holdings.length) {
    return (
      <div className={cn("p-3", className)}>
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-foreground">Holdings Table</h3>
          <div className="border rounded-lg p-8 text-center">
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
            <h3 className="text-sm font-medium text-foreground">Holdings Table</h3>
            <p className="text-xs text-muted-foreground">
              {sortedHoldings.length} of {holdings.length} positions • {formatCurrency(totalValue)}
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

        <div className="border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50 border-b">
                <tr>
                  <SortHeader 
                    field="symbol" 
                    label="Symbol"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={handleSort}
                  />
                  <SortHeader 
                    field="assetClass" 
                    label="Class"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={handleSort}
                  />
                  <SortHeader 
                    field="quantity" 
                    label="Quantity"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={handleSort}
                    className="text-right"
                  />
                  <SortHeader 
                    field="weight" 
                    label="Weight"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={handleSort}
                    className="text-right"
                  />
                  <SortHeader 
                    field="marketValue" 
                    label="Value"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={handleSort}
                    className="text-right"
                  />
                  <SortHeader 
                    field="currentPrice" 
                    label="Price"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={handleSort}
                    className="text-right"
                  />
                  {showMetrics && (
                    <SortHeader 
                      field="dayChangePercent" 
                      label="Day Change"
                      currentSort={sortBy}
                      currentOrder={sortOrder}
                      onSort={handleSort}
                      className="text-right"
                    />
                  )}
                </tr>
              </thead>
              <tbody>
                {sortedHoldings.map((holding, index) => {
                  const isPositive = (holding.dayChangePercent || 0) >= 0;
                  const Icon = isPositive ? TrendingUp : TrendingDown;
                  
                  return (
                    <tr 
                      key={holding.symbol} 
                      className={cn(
                        "border-b last:border-b-0 hover:bg-muted/25 transition-colors",
                        index % 2 === 0 ? "bg-background" : "bg-muted/10"
                      )}
                    >
                      <td className="px-2 py-3">
                        <div>
                          <div className="font-medium text-sm text-foreground tabular-nums">
                            {holding.symbol}
                          </div>
                          <div className="text-xs text-muted-foreground truncate max-w-32">
                            {holding.name}
                          </div>
                        </div>
                      </td>
                      <td className="px-2 py-3">
                        <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                          {holding.assetClass}
                        </span>
                      </td>
                      <td className="px-2 py-3 text-right">
                        <span className="text-sm tabular-nums">
                          {formatQuantity(holding.quantity || 0)}
                        </span>
                      </td>
                      <td className="px-2 py-3 text-right">
                        <span className="text-sm font-medium tabular-nums">
                          {formatWeight(holding.weight || 0, precision)}
                        </span>
                      </td>
                      <td className="px-2 py-3 text-right">
                        <span className="text-sm font-medium tabular-nums">
                          {formatCurrency(holding.marketValue || 0)}
                        </span>
                      </td>
                      <td className="px-2 py-3 text-right">
                        <span className="text-sm tabular-nums">
                          {formatCurrency(holding.currentPrice || 0)}
                        </span>
                      </td>
                      {showMetrics && (
                        <td className="px-2 py-3 text-right">
                          {holding.dayChangePercent !== undefined && (
                            <div className={cn(
                              'flex items-center justify-end gap-1 text-sm',
                              isPositive ? 'text-green-600' : 'text-red-600'
                            )}>
                              <Icon className="h-3 w-3" />
                              <span className="tabular-nums">
                                {formatWeight(holding.dayChangePercent / 100, 1)}
                              </span>
                            </div>
                          )}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer summary */}
        <div className="flex justify-between items-center text-xs text-muted-foreground pt-2 border-t">
          <span>Showing {sortedHoldings.length} of {holdings.length} positions</span>
          <span>Sorted by {sortBy} ({sortOrder})</span>
        </div>
      </div>
    </div>
  );
}

export default HoldingsTableView;