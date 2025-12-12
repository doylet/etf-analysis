'use client';

import { DataTable, Column } from '@/components/ui/data-table';
import { FinancialAmount } from '@/components/ui/financial-amount';
import { PercentageChange } from '@/components/ui/percentage-change';
import { formatPercent } from '@/lib/formatters';

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

interface HoldingsTableProps {
  holdings: HoldingRow[];
}

export function HoldingsTable({ holdings }: HoldingsTableProps) {
  const columns: Column<Record<string, unknown>>[] = [
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

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Individual Holdings</h3>
      <DataTable
        data={holdings}
        columns={columns}
        variant="default"
        size="sm"
      />
    </div>
  );
}
