'use client';

import { TrendingUp, TrendingDown, PieChart, XCircle, Filter } from 'lucide-react';
import { useState } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { DataTable } from '@/components/ui/data-table';
import { FinancialAmount } from '@/components/ui/financial-amount';
import { PercentageChange } from '@/components/ui/percentage-change';
import { useHoldingsBreakdown } from '@/hooks/use-portfolio-widgets';

interface HoldingsBreakdownProps {
  portfolioId?: string;
  defaultBreakdownType?: 'sector' | 'geography' | 'asset_class';
}

interface HoldingRow {
  symbol: string;
  name: string;
  shares: number;
  current_price: number;
  current_value: number;
  weight_percent: number;
  day_change: number;
  day_change_percent: number;
  total_return: number;
  total_return_percent: number;
}

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
  return `${value.toFixed(2)}%`;
};

export default function HoldingsBreakdownComponent({ 
  portfolioId, 
  defaultBreakdownType = 'asset_class' 
}: HoldingsBreakdownProps) {
  const [breakdownType, setBreakdownType] = useState(defaultBreakdownType);
  
  const { data: breakdown, loading, error, metadata, cacheHit } = useHoldingsBreakdown({
    portfolioId,
    breakdownType,
  });

  const breakdownTypeOptions = [
    { value: 'asset_class', label: 'Asset Class' },
    { value: 'sector', label: 'Sector' },
    { value: 'geography', label: 'Geography' },
  ];

  // Define table columns for holdings
  const holdingsColumns = [
    {
      key: 'symbol',
      header: 'Symbol',
      render: (value: string, row: HoldingRow) => (
        <div className="font-medium">
          <div>{value}</div>
          <div className="text-sm text-muted-foreground truncate max-w-[120px]">
            {row.name}
          </div>
        </div>
      ),
    },
    {
      key: 'shares',
      header: 'Shares',
      render: (value: number) => (
        <span className="font-mono">
          {new Intl.NumberFormat('en-US', { 
            maximumFractionDigits: 2 
          }).format(value)}
        </span>
      ),
    },
    {
      key: 'current_price',
      header: 'Price',
      render: (value: HoldingRow) => <FinancialAmount amount={value.current_price} />,
    },
    {
      key: 'current_value',
      header: 'Value',
      render: (value: number) => <FinancialAmount amount={value} />,
    },
    {
      key: 'weight_percent',
      header: 'Weight',
      render: (value: number) => (
        <span className="font-mono">{formatPercent(value)}</span>
      ),
    },
    {
      key: 'day_change',
      header: 'Day Change',
      render: (value: number, row: HoldingRow) => (
        <PercentageChange 
          value={value} 
        />
      ),
    },
    {
      key: 'total_return',
      header: 'Total Return',
      render: (value: number,row: HoldingRow) => (
        <PercentageChange 
          value={value} 
        />
      ),
    },
  ];

  // Define columns for breakdown summary
  const breakdownColumns = [
    {
      key: 'category',
      header: 'Category',
      render: (value: string) => (
        <span className="font-medium">{value}</span>
      ),
    },
    {
      key: 'value',
      header: 'Value',
      render: (value: number) => <FinancialAmount amount={value} />,
    },
    {
      key: 'weight_percent',
      header: 'Weight',
      render: (value: number) => (
        <span className="font-mono text-lg">{formatPercent(value)}</span>
      ),
    },
    {
      key: 'holdings',
      header: 'Holdings',
      render: (value: HoldingRow[]) => (
        <span className="text-muted-foreground">
          {value.length} position{value.length !== 1 ? 's' : ''}
        </span>
      ),
    },
  ];

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <Skeleton className="h-6 w-[180px]" />
              <Skeleton className="h-4 w-[250px] mt-2" />
            </div>
            <Skeleton className="h-8 w-[120px]" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="p-4 border rounded-lg">
                  <Skeleton className="h-4 w-[100px]" />
                  <Skeleton className="h-8 w-[120px] mt-2" />
                  <Skeleton className="h-4 w-[80px] mt-1" />
                </div>
              ))}
            </div>
            <div>
              <Skeleton className="h-6 w-[150px]" />
              <div className="mt-4 space-y-3">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="flex justify-between">
                    <Skeleton className="h-4 w-[60px]" />
                    <Skeleton className="h-4 w-[80px]" />
                    <Skeleton className="h-4 w-[100px]" />
                    <Skeleton className="h-4 w-[90px]" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !breakdown) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Holdings Data Error</AlertTitle>
        <AlertDescription>
          {error || 'Unable to load holdings breakdown. Please try refreshing the page.'}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold text-foreground">Holdings Breakdown</h2>
            <p className="text-muted-foreground text-sm mt-1">
              Portfolio composition by {breakdownType.replace('_', ' ')}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {cacheHit && (
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-md">
                Cached
              </span>
            )}
            <select
              value={breakdownType}
              onChange={(e) => setBreakdownType(e.target.value as typeof breakdownType)}
              className="text-sm border border-border rounded-md px-3 py-1 bg-background"
            >
              {breakdownTypeOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Breakdown Summary */}
          {breakdown?.breakdown && breakdown.breakdown.length > 0 && (
            <div>
              <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
                <PieChart className="h-5 w-5" />
                {breakdownType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Distribution
              </h3>
              <DataTable 
                data={breakdown.breakdown}
                columns={breakdownColumns}
                variant="striped"
                size="sm"
              />
            </div>
          )}

          {/* Individual Holdings */}
          {breakdown?.holdings && breakdown.holdings.length > 0 && (
            <div>
              <h3 className="text-lg font-medium mb-3">Individual Holdings</h3>
              <DataTable 
                data={breakdown.holdings}
                columns={holdingsColumns}
                variant="default"
                size="sm"
              />
            </div>
          )}

          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-border">
            <div className="text-center">
              <div className="text-2xl font-bold text-text-primary">
                {formatCurrency(breakdown?.total_value)}
              </div>
              <div className="text-sm text-text-tertiary">Total Value</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-text-primary">
                {breakdown?.holdings?.length || 0}
              </div>
              <div className="text-sm text-text-tertiary">
                Total Positions
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-text-primary">
                {breakdown?.breakdown?.length || 0}
              </div>
              <div className="text-sm text-text-tertiary">
                {breakdownType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}s
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}