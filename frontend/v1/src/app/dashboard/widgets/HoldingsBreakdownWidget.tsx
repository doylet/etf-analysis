'use client';

import { PieChart, XCircle } from 'lucide-react';
import { useState } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { CacheBadge } from '@/components/ui/cache-badge';
import { DataTable, Column } from '@/components/ui/data-table';
import { FinancialAmount } from '@/components/ui/financial-amount';
import { PercentageChange } from '@/components/ui/percentage-change';
import { WidgetSelect } from '@/components/ui/widget/widget-controls';
import { useHoldingsBreakdown, type BreakdownData } from '@/hooks/use-portfolio-widgets';
import { formatCurrency, formatPercent } from '@/lib/formatters';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 5 },
  contentType: 'balanced' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.0,
  isScrollable: true,
} as const;

interface HoldingsBreakdownProps {
  portfolioId?: string;
  defaultBreakdownType?: 'sector' | 'geography' | 'asset_class';
}

interface HoldingRow extends Record<string, unknown> {
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

export default function HoldingsBreakdownWidget({ 
  portfolioId, 
  defaultBreakdownType = 'asset_class' 
}: HoldingsBreakdownProps) {
  const [breakdownType, setBreakdownType] = useState(defaultBreakdownType);
  
  const { data: breakdown, loading, error, cacheHit } = useHoldingsBreakdown({
    portfolioId,
    breakdownType,
  });

  const breakdownTypeOptions = [
    { value: 'asset_class' as const, label: 'Asset Class' },
    { value: 'sector' as const, label: 'Sector' },
    { value: 'geography' as const, label: 'Geography' },
  ];

  // Define table columns for holdings
  const holdingsColumns: Column<Record<string, unknown>>[] = [
    {
      key: 'symbol',
      header: 'Symbol',
      render: (value: unknown, item: Record<string, unknown>) => {
        const row = item as HoldingRow;
        return (
          <div className="font-medium">
            <div>{row.symbol}</div>
            <div className="text-sm text-muted-foreground truncate max-w-[120px]">
              {row.name}
            </div>
          </div>
        );
      },
    },
    {
      key: 'shares',
      header: 'Shares',
      render: (value: unknown, item: Record<string, unknown>) => {
        const row = item as HoldingRow;
        return (
          <span className="font-mono">
            {new Intl.NumberFormat('en-US', { 
              maximumFractionDigits: 2 
            }).format(row.shares)}
          </span>
        );
      },
    },
    {
      key: 'current_price',
      header: 'Price',
      render: (value: unknown, item: Record<string, unknown>) => {
        const row = item as HoldingRow;
        return <FinancialAmount amount={row.current_price} />;
      },
    },
    {
      key: 'current_value',
      header: 'Value',
      render: (value: unknown, item: Record<string, unknown>) => {
        const row = item as HoldingRow;
        return <FinancialAmount amount={row.current_value} />;
      },
    },
    {
      key: 'weight_percent',
      header: 'Weight',
      render: (value: unknown, item: Record<string, unknown>) => {
        const row = item as HoldingRow;
        return <span className="font-mono">{formatPercent(row.weight_percent)}</span>;
      },
    },
    {
      key: 'day_change',
      header: 'Day Change',
      render: (value: unknown, item: Record<string, unknown>) => {
        const row = item as HoldingRow;
        return <PercentageChange value={row.day_change} />;
      },
    },
    {
      key: 'total_return',
      header: 'Total Return',
      render: (value: unknown, item: Record<string, unknown>) => {
        const row = item as HoldingRow;
        return <PercentageChange value={row.total_return} />;
      },
    },
  ];

  // Define columns for breakdown summary
  const breakdownColumns: Column<Record<string, unknown>>[] = [
    {
      key: 'category',
      header: 'Category',
      render: (value: unknown, item: Record<string, unknown>) => (
        <span className="font-medium">{(item as BreakdownData).category}</span>
      ),
    },
    {
      key: 'value',
      header: 'Value',
      render: (value: unknown, item: Record<string, unknown>) => <FinancialAmount amount={(item as BreakdownData).value} />,
    },
    {
      key: 'weight_percent',
      header: 'Weight',
      render: (value: unknown, item: Record<string, unknown>) => (
        <span className="font-mono text-lg">{formatPercent((item as BreakdownData).weight_percent)}</span>
      ),
    },
    {
      key: 'holdings',
      header: 'Holdings',
      render: (value: unknown, item: Record<string, unknown>) => (
        <span className="text-muted-foreground">
          {(item as BreakdownData).holdings.length} position{(item as BreakdownData).holdings.length !== 1 ? 's' : ''}
        </span>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex flex-col h-full p-4">
        <div className="flex justify-between items-start flex-shrink-0">
          <div>
            <Skeleton className="h-6 w-[180px]" />
            <Skeleton className="h-4 w-[250px] mt-2" />
          </div>
          <Skeleton className="h-8 w-[120px]" />
        </div>
        <div className="flex-1 overflow-y-auto min-h-0 mt-4 space-y-6">
          <div className="flex flex-wrap justify-center gap-4">
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
      </div>
    );
  }

  if (error || !breakdown) {
    return (
      <WidgetInsight
        title="Holdings Data Error"
        description={error || 'Unable to load holdings breakdown. Please try refreshing the page.'}
        icon={XCircle}
        variant="destructive"
      />
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-2 items-center flex-shrink-0">
        <WidgetSelect
          value={breakdownType}
          onChange={setBreakdownType}
          options={breakdownTypeOptions}
          className="flex-1"
        />
        <CacheBadge show={cacheHit} />
      </div>
      
      <div className="flex-1 overflow-y-auto min-h-0 mt-3">
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
          <div className="flex flex-wrap justify-center gap-4 pt-4 border-t border-border">
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
      </div>
    </div>
  );
}