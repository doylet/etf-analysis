import React, { useState, useMemo } from 'react';
import { usePortfolioOptimizer } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { WidgetSelect, WidgetCheckbox, WidgetNumberInput } from '@/components/ui/widget/widget-controls';
import { TIME_PERIODS, OPTIMIZATION_OBJECTIVES } from '@/lib/widget-constants';
import { XCircle } from 'lucide-react';
import type { ContentType } from './widget-metadata';
import { OptimizerMetrics } from './portfolio-optimizer/OptimizerMetrics';
import { ImprovementSection } from './portfolio-optimizer/ImprovementSection';
import { OptimalWeightsTable } from './portfolio-optimizer/OptimalWeightsTable';
import { EfficientFrontierChart } from './portfolio-optimizer/EfficientFrontierChart';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 8, h: 6 },
  contentType: 'full-width' as ContentType,
  requiresFullWidth: true,
  aspectRatioPreference: 1.5,
  isScrollable: true,
} as const;

interface PortfolioOptimizerWidgetProps {
  portfolioId?: string;
}

const PortfolioOptimizerWidget: React.FC<PortfolioOptimizerWidgetProps> = ({ portfolioId }) => {
  const [mode, setMode] = useState('Max Sharpe');
  const [timePeriod, setTimePeriod] = useState('1Y');
  const [includeDividends, setIncludeDividends] = useState(true);
  const [targetReturn, setTargetReturn] = useState(15);
  
  const { data, loading, error } = usePortfolioOptimizer({ 
    portfolioId, 
    mode, 
    timePeriod, 
    targetReturn: mode === 'Target Return' ? targetReturn : undefined,
    includeDividends 
  });

  // Prepare chart data for efficient frontier
  const chartData = useMemo(() => {
    if (!data?.efficient_frontier) return [];
    
    return data.efficient_frontier.map((point: {volatility: number; expected_return: number; sharpe_ratio: number}, index: number) => ({
      volatility: point.volatility * 100,
      return: point.expected_return * 100,
      sharpe: point.sharpe_ratio,
      name: `Portfolio ${index + 1}`
    }));
  }, [data]);

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Optimizer Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  // Handle minimal API response structure
  const hasFullData = data.expected_return !== undefined && data.expected_risk !== undefined;

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-col gap-2 flex-shrink-0 mb-1">
        <div className="flex gap-2">
          <WidgetSelect
            value={mode}
            onChange={setMode}
            options={OPTIMIZATION_OBJECTIVES}
            className="flex-1"
          />
          <WidgetSelect
            value={timePeriod}
            onChange={setTimePeriod}
            options={TIME_PERIODS.filter(p => p.value !== '1W')}
            className="flex-1"
          />
        </div>
        
        <div className="flex items-center gap-4">
          <WidgetCheckbox
            label="Include Dividends"
            checked={includeDividends}
            onChange={setIncludeDividends}
          />
          
          {mode === 'Target Return' && (
            <WidgetNumberInput
              label="Target Return (%)"
              value={targetReturn}
              onChange={setTargetReturn}
              min={0}
              max={100}
              step={0.5}
            />
          )}
        </div>
      </div>
      
      {hasFullData ? (
        <div className="flex-1 overflow-y-auto min-h-0 space-y-3">
          <OptimizerMetrics
            expectedReturn={data.expected_return}
            expectedRisk={data.expected_risk}
            sharpeRatio={data.sharpe_ratio}
            currentReturn={data.current_return}
            currentRisk={data.current_risk}
            currentSharpe={data.current_sharpe}
          />

          {data.improvement_metrics && (
            <ImprovementSection improvements={data.improvement_metrics} />
          )}

          {data.optimal_weights && Object.keys(data.optimal_weights).length > 0 && (
            <OptimalWeightsTable 
              optimalWeights={data.optimal_weights} 
              currentWeights={data.current_weights}
            />
          )}

          <EfficientFrontierChart
            chartData={chartData}
            currentReturn={data.current_return}
            currentRisk={data.current_risk}
            currentSharpe={data.current_sharpe}
            expectedReturn={data.expected_return}
            expectedRisk={data.expected_risk}
            sharpeRatio={data.sharpe_ratio}
          />
        </div>
      ) : (
        <div className="text-center p-4 text-muted-foreground">
          <div className="text-sm">{data.status || data.message || 'Portfolio optimizer data available'}</div>
          {data.holdings_count && <div className="text-xs mt-2">{data.holdings_count} holdings</div>}
        </div>
      )}
    </div>
  );
};

PortfolioOptimizerWidget.displayName = 'PortfolioOptimizerWidget';

export default React.memo(PortfolioOptimizerWidget);
