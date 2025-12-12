import React, { useState } from 'react';
import { useConstrainedOptimization } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { WidgetSelect, WidgetSlider } from '@/components/ui/widget/widget-controls';
import { OPTIMIZATION_OBJECTIVES } from '@/lib/widget-constants';
import { formatPercent } from '@/lib/formatters';
import { XCircle, TrendingUp, Activity, Target, CheckCircle } from 'lucide-react';
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

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex flex-col gap-2 flex-shrink-0">
        <WidgetSelect
          value={objective}
          onChange={setObjective}
          options={OPTIMIZATION_OBJECTIVES.filter(o => ['Max Sharpe', 'Min Volatility', 'Max Return', 'Risk Parity'].includes(o.value))}
        />
        <WidgetSlider
          label="Max Weight (%)"
          value={maxWeight}
          onChange={setMaxWeight}
          min={10}
          max={100}
          step={1}
        />
        <WidgetSlider
          label="Min Weight (%)"
          value={minWeight}
          onChange={setMinWeight}
          min={0}
          max={30}
          step={1}
        />
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3">
          <MetricGroup layout="horizontal">
            <MetricCard
              icon={TrendingUp}
              title="Return"
              value={formatPercent(data.optimization_result.return / 100)}
              size="sm"
            />
            <MetricCard
              icon={Activity}
              title="Risk"
              value={formatPercent(data.optimization_result.risk / 100)}
              size="sm"
            />
            <MetricCard
              icon={Target}
              title="Sharpe Ratio"
              value={data.optimization_result.sharpe_ratio?.toFixed(2)}
              size="sm"
            />
            <MetricCard
              icon={CheckCircle}
              title="Constraints Met"
              value={(!data.constraint_violations || data.constraint_violations.length === 0) ? 'YES' : 'NO'}
              variant={(!data.constraint_violations || data.constraint_violations.length === 0) ? 'success' : 'destructive'}
              size="sm"
            />
          </MetricGroup>
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
