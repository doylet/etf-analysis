'use client';

import { formatPercent } from '@/lib/formatters';

interface ImprovementMetrics {
  return_improvement: number;
  risk_reduction: number;
  sharpe_improvement: number;
}

interface ImprovementSectionProps {
  improvements: ImprovementMetrics;
}

export function ImprovementSection({ improvements }: ImprovementSectionProps) {
  return (
    <div className="p-3 bg-muted rounded-md">
      <div className="text-xs font-medium text-muted-foreground mb-2">Potential Improvements</div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <div className="text-sm font-bold text-green-600 dark:text-green-400">
            +{formatPercent(improvements.return_improvement / 100)}
          </div>
          <div className="text-xs text-muted-foreground">Return Gain</div>
        </div>
        <div>
          <div className="text-sm font-bold text-green-600 dark:text-green-400">
            {formatPercent(improvements.risk_reduction / 100)}
          </div>
          <div className="text-xs text-muted-foreground">Risk Reduction</div>
        </div>
        <div>
          <div className="text-sm font-bold text-green-600 dark:text-green-400">
            +{improvements.sharpe_improvement?.toFixed(2)}
          </div>
          <div className="text-xs text-muted-foreground">Sharpe Gain</div>
        </div>
      </div>
    </div>
  );
}
