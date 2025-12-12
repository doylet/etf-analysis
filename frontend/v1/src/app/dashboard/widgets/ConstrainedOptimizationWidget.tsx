import React, { useState } from 'react';
import { useConstrainedOptimization } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { XCircle } from 'lucide-react';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 5 },
  contentType: 'height-heavy' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.2,
  isScrollable: true,
} as const;

interface ConstrainedOptimizationWidgetProps {
  portfolioId?: string;
}

const ConstrainedOptimizationWidget: React.FC<ConstrainedOptimizationWidgetProps> = ({ portfolioId }) => {
  const [objective, setObjective] = useState('Max Sharpe');
  const [maxWeight, setMaxWeight] = useState(30);
  const [minWeight, setMinWeight] = useState(0);
  
  const { data, loading, error } = useConstrainedOptimization({ portfolioId, objective, maxWeight, minWeight });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Optimization Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.optimization_result?.return !== undefined;

  const objectives = [
    { value: 'Max Sharpe', label: 'Max Sharpe' },
    { value: 'Min Volatility', label: 'Min Volatility' },
    { value: 'Max Return', label: 'Max Return' },
    { value: 'Risk Parity', label: 'Risk Parity' },
  ];

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex flex-col gap-2 flex-shrink-0">
        <select 
          value={objective} 
          onChange={(e) => setObjective(e.target.value)}
          className="px-2 py-1 text-sm border rounded-md bg-background"
        >
          {objectives.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-muted-foreground">
            Max Weight: {maxWeight}%
          </label>
          <input 
            type="range" 
            min="10" 
            max="100" 
            value={maxWeight} 
            onChange={(e) => setMaxWeight(Number(e.target.value))}
            className="w-full"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-muted-foreground">
            Min Weight: {minWeight}%
          </label>
          <input 
            type="range" 
            min="0" 
            max="30" 
            value={minWeight} 
            onChange={(e) => setMinWeight(Number(e.target.value))}
            className="w-full"
          />
        </div>
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3">
          <div className="flex flex-wrap justify-center gap-3">
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">
                {data.optimization_result.return?.toFixed(2)}%
              </div>
              <div className="text-xs text-muted-foreground">Return</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">
                {data.optimization_result.risk?.toFixed(2)}%
              </div>
              <div className="text-xs text-muted-foreground">Risk</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className="text-lg font-bold text-foreground">
                {data.optimization_result.sharpe_ratio?.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">Sharpe Ratio</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-md">
              <div className={`text-lg font-bold ${
                (!data.constraint_violations || data.constraint_violations.length === 0) ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              }`}>
                {(!data.constraint_violations || data.constraint_violations.length === 0) ? 'YES' : 'NO'}
              </div>
              <div className="text-xs text-muted-foreground">Constraints Met</div>
            </div>
          </div>
          {data.constraint_violations && data.constraint_violations.length > 0 && (
            <div className="mt-3 p-2 bg-destructive/10 rounded-md">
              <div className="text-xs font-medium text-destructive mb-1">Violations</div>
              {data.constraint_violations.slice(0, 3).map((violation, idx) => (
                <div key={idx} className="text-xs text-muted-foreground">
                  {violation.constraint}: {violation.violation?.toFixed(2)}
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Constrained optimization data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

ConstrainedOptimizationWidget.displayName = 'ConstrainedOptimizationWidget';

export default React.memo(ConstrainedOptimizationWidget);
