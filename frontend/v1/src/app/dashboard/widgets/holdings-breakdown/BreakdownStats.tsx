'use client';

import { formatCurrency } from '@/lib/formatters';

interface BreakdownStatsProps {
  totalValue: number;
  holdingsCount: number;
  categoriesCount: number;
  breakdownType: string;
}

export function BreakdownStats({
  totalValue,
  holdingsCount,
  categoriesCount,
  breakdownType,
}: BreakdownStatsProps) {
  return (
    <div className="flex flex-wrap justify-center gap-4 pt-4 border-t border-border">
      <div className="text-center">
        <div className="text-2xl font-bold text-text-primary">
          {formatCurrency(totalValue)}
        </div>
        <div className="text-sm text-text-tertiary">Total Value</div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold text-text-primary">
          {holdingsCount}
        </div>
        <div className="text-sm text-text-tertiary">
          Total Positions
        </div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold text-text-primary">
          {categoriesCount}
        </div>
        <div className="text-sm text-text-tertiary">
          {breakdownType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}s
        </div>
      </div>
    </div>
  );
}
