/**
 * RebalancingAnalysis - REUSABLE rebalancing recommendations display
 * Shows rebalancing calendar, metrics, and cost/benefit analysis
 * Can be used in other portfolio management widgets
 */
import { Target } from 'lucide-react';

interface RebalancingRec {
  rebalance_dates: string[];
  drift_at_rebalance: number[];
  symbols: string[];
  avg_drift: number;
  sharpe_improvement: number;
  cost_benefit_ratio: number;
  description: string;
}

interface RebalancingAnalysisProps {
  rebalancingRec: RebalancingRec | null;
  enabled: boolean;
  driftThreshold: number;
  frequency: string;
}

export function RebalancingAnalysis({ rebalancingRec, enabled, driftThreshold, frequency }: RebalancingAnalysisProps) {
  if (!enabled) {
    return null;
  }

  if (!rebalancingRec) {
    return (
      <div className="border border-amber-200 bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
        <h3 className="text-sm font-medium text-amber-900 dark:text-amber-200 mb-2">
          Rebalancing Analysis Not Available
        </h3>
        <p className="text-xs text-amber-700 dark:text-amber-300">
          Rebalancing recommendations require backend implementation. The simulation will include rebalancing 
          effects once the feature is fully enabled.
        </p>
      </div>
    );
  }

  return (
    <div className="border border-border rounded-lg p-4">
      <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
        <Target className="h-5 w-5" />
        Rebalancing Recommendations
      </h3>
      
      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="text-center p-2 bg-background-accent rounded">
          <div className="text-xs text-muted-foreground">Rebalance Count</div>
          <div className="text-lg font-bold text-text-primary">
            {rebalancingRec.rebalance_dates.length}
          </div>
        </div>
        <div className="text-center p-2 bg-background-accent rounded">
          <div className="text-xs text-muted-foreground">Avg. Drift</div>
          <div className="text-lg font-bold text-text-primary">
            {rebalancingRec.avg_drift.toFixed(1)}%
          </div>
        </div>
        <div className="text-center p-2 bg-background-accent rounded">
          <div className="text-xs text-muted-foreground">Sharpe Improvement</div>
          <div className="text-lg font-bold text-financial-positive">
            +{rebalancingRec.sharpe_improvement.toFixed(2)}
          </div>
        </div>
        <div className="text-center p-2 bg-background-accent rounded">
          <div className="text-xs text-muted-foreground">Cost/Benefit</div>
          <div className="text-lg font-bold text-text-primary">
            {rebalancingRec.cost_benefit_ratio.toFixed(2)}x
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4">
        {rebalancingRec.description}
      </p>

      {/* Rebalancing Calendar */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium">Rebalancing Calendar</h4>
        <div className="border border-border rounded overflow-hidden">
          <table className="w-full text-xs">
            <thead className="bg-muted">
              <tr>
                <th className="text-left p-2">Date</th>
                <th className="text-right p-2">Max Drift</th>
                <th className="text-left p-2">Instruments Affected</th>
              </tr>
            </thead>
            <tbody>
              {rebalancingRec.rebalance_dates.map((date, idx) => (
                <tr key={idx} className="border-t border-border hover:bg-muted/50">
                  <td className="p-2">{new Date(date).toLocaleDateString()}</td>
                  <td className="text-right p-2 font-mono">
                    {rebalancingRec.drift_at_rebalance[idx].toFixed(1)}%
                  </td>
                  <td className="p-2">
                    <span className="text-muted-foreground">
                      {rebalancingRec.symbols.slice(0, 3).join(', ')}
                      {rebalancingRec.symbols.length > 3 && ` +${rebalancingRec.symbols.length - 3} more`}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Drift Threshold Info */}
      <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded text-xs">
        <strong>Drift Threshold:</strong> Rebalancing triggered when any position drifts {driftThreshold}% from target weight. 
        Frequency: {frequency}.
      </div>
    </div>
  );
}
