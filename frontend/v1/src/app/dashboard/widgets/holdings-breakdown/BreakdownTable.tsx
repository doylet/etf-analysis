'use client';

import { PieChart } from 'lucide-react';
import { DataTable, Column } from '@/components/ui/data-table';
import { FinancialAmount } from '@/components/ui/financial-amount';
import { formatPercent } from '@/lib/formatters';
import type { BreakdownData } from '@/hooks/use-portfolio-widgets';

interface BreakdownTableProps {
  breakdown: BreakdownData[];
  breakdownType: string;
}

export function BreakdownTable({ breakdown, breakdownType }: BreakdownTableProps) {
  const columns: Column<Record<string, unknown>>[] = [
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

  return (
    <div>
      <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
        <PieChart className="h-5 w-5" />
        {breakdownType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Distribution
      </h3>
      <DataTable
        data={breakdown}
        columns={columns}
        variant="striped"
        size="sm"
      />
    </div>
  );
}
