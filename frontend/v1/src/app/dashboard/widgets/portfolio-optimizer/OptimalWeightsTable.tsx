'use client';

import { ArrowRight } from 'lucide-react';

interface OptimalWeightsTableProps {
  optimalWeights: Record<string, number>;
  currentWeights?: Record<string, number>;
}

export function OptimalWeightsTable({ optimalWeights, currentWeights }: OptimalWeightsTableProps) {
  return (
    <div>
      <div className="text-sm font-medium mb-2">Recommended Allocations</div>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {Object.entries(optimalWeights).map(([symbol, weight]: [string, number]) => {
          const currentWeight = currentWeights?.[symbol] || 0;
          const optimalWeight = typeof weight === 'number' ? weight : 0;
          const change = optimalWeight - currentWeight;
          
          return (
            <div key={symbol} className="flex items-center justify-between p-2 bg-muted rounded text-xs">
              <span className="font-medium">{symbol}</span>
              <div className="flex items-center gap-2">
                {currentWeights && (
                  <>
                    <span className="text-muted-foreground">{(currentWeight * 100).toFixed(1)}%</span>
                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
                  </>
                )}
                <span className="font-medium">{(optimalWeight * 100).toFixed(1)}%</span>
                {change !== 0 && (
                  <span className={`ml-2 ${change > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {change > 0 ? '+' : ''}{(change * 100).toFixed(1)}%
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
