/**
 * PercentileBreakdown - Displays detailed percentile outcomes
 * Shows 10th, 50th, and 90th percentiles with returns
 */
import { formatCurrency, formatPercent } from '@/lib/formatters';

interface PercentileBreakdownProps {
  percentiles: {
    "10": number;
    "50": number;
    "90": number;
  };
  initialValue: number;
}

export function PercentileBreakdown({ percentiles, initialValue }: PercentileBreakdownProps) {
  const calculateReturn = (finalValue: number) => {
    if (initialValue === 0) return 0;
    return (finalValue - initialValue) / initialValue;
  };

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Outcome Percentiles</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center p-3 border border-border rounded-lg bg-background-secondary">
          <div className="text-sm text-text-tertiary">10th Percentile</div>
          <div className="text-lg font-bold text-financial-negative">
            {formatCurrency(percentiles["10"])}
          </div>
          <div className="text-xs text-text-tertiary">
            {formatPercent(calculateReturn(percentiles["10"]))}
          </div>
        </div>
        <div className="text-center p-3 border border-border rounded-lg bg-background-accent">
          <div className="text-sm text-text-tertiary">50th Percentile (Median)</div>
          <div className="text-lg font-bold text-text-primary">
            {formatCurrency(percentiles["50"])}
          </div>
          <div className="text-xs text-text-tertiary">
            {formatPercent(calculateReturn(percentiles["50"]))}
          </div>
        </div>
        <div className="text-center p-3 border border-border rounded-lg bg-background-secondary">
          <div className="text-sm text-text-tertiary">90th Percentile</div>
          <div className="text-lg font-bold text-financial-positive">
            {formatCurrency(percentiles["90"])}
          </div>
          <div className="text-xs text-text-tertiary">
            {formatPercent(calculateReturn(percentiles["90"]))}
          </div>
        </div>
      </div>
    </div>
  );
}
