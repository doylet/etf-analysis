/**
 * PortfolioComposition - REUSABLE weight allocation configuration
 * Allows selection of weight methods and custom weight specification
 * Can be used in other optimization/portfolio construction widgets
 */
import { ChevronDown } from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import type { MonteCarloConfig, MonteCarloConfigActions } from './useMonteCarloConfig';

interface PortfolioCompositionProps {
  config: Pick<MonteCarloConfig, 'weightMethod' | 'customWeights' | 'showWeightConfig' | 'enableRebalancing' | 'rebalancingFrequency' | 'driftThreshold'>;
  actions: Pick<MonteCarloConfigActions, 'setWeightMethod' | 'setCustomWeights' | 'setShowWeightConfig' | 'setEnableRebalancing' | 'setRebalancingFrequency' | 'setDriftThreshold'>;
}

export function PortfolioComposition({ config, actions }: PortfolioCompositionProps) {
  return (
    <Collapsible open={config.showWeightConfig} onOpenChange={actions.setShowWeightConfig} className="flex-shrink-0 mt-3">
      <CollapsibleTrigger 
        className="w-full flex items-center justify-between text-sm font-medium text-foreground p-2 hover:bg-muted rounded-md transition-colors"
        onPointerDown={(e) => e.stopPropagation()}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <span>Portfolio Composition</span>
        <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${config.showWeightConfig ? 'rotate-180' : ''}`} />
      </CollapsibleTrigger>
      
      <CollapsibleContent>
        <div className="mt-2 p-3 border border-border rounded-md space-y-3">
          <div>
            <label className="text-xs text-muted-foreground block mb-1">Weight Allocation Method</label>
            <select
              value={config.weightMethod}
              onChange={(e) => actions.setWeightMethod(e.target.value as any)}
              className="w-full text-xs border border-border rounded-md px-2 py-1 bg-background"
            >
              <option value="Current Portfolio">Current Portfolio</option>
              <option value="Equal Weights">Equal Weights</option>
              <option value="Max Sharpe Ratio">Max Sharpe Ratio</option>
              <option value="Min Volatility">Min Volatility</option>
              <option value="Custom">Custom Weights</option>
            </select>
            <p className="text-[10px] text-muted-foreground mt-1">
              {config.weightMethod === 'Current Portfolio' && 'Use current portfolio holdings and weights'}
              {config.weightMethod === 'Equal Weights' && 'Distribute capital equally across selected instruments'}
              {config.weightMethod === 'Max Sharpe Ratio' && 'Optimize for maximum risk-adjusted returns'}
              {config.weightMethod === 'Min Volatility' && 'Optimize for minimum portfolio volatility'}
              {config.weightMethod === 'Custom' && 'Manually specify weight for each instrument'}
            </p>
          </div>

          {config.weightMethod === 'Custom' && (
            <div className="space-y-2">
              <label className="text-xs font-medium">Custom Weights</label>
              <div className="text-xs text-amber-600 bg-amber-50 dark:bg-amber-900/20 p-2 rounded">
                Custom weight allocation requires instrument selection. This feature will be fully enabled when portfolio holdings data is available.
              </div>
            </div>
          )}

          {/* Rebalancing Options */}
          <div className="pt-2 border-t border-border">
            <div className="flex items-center gap-2 mb-2">
              <input
                type="checkbox"
                id="enableRebalancing"
                checked={config.enableRebalancing}
                onChange={(e) => actions.setEnableRebalancing(e.target.checked)}
                className="rounded border-border"
              />
              <label htmlFor="enableRebalancing" className="text-xs font-medium cursor-pointer">
                Enable Rebalancing Analysis
              </label>
            </div>

            {config.enableRebalancing && (
              <div className="grid grid-cols-2 gap-2 mt-2">
                <div>
                  <label className="text-xs text-muted-foreground block mb-1">Frequency</label>
                  <select
                    value={config.rebalancingFrequency}
                    onChange={(e) => actions.setRebalancingFrequency(e.target.value as any)}
                    className="w-full text-xs border border-border rounded-md px-2 py-1 bg-background"
                  >
                    <option value="Quarterly">Quarterly</option>
                    <option value="Semi-Annual">Semi-Annual</option>
                    <option value="Annual">Annual</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-muted-foreground block mb-1">Drift Threshold (%)</label>
                  <input
                    type="number"
                    value={config.driftThreshold}
                    onChange={(e) => actions.setDriftThreshold(Math.max(1, Math.min(20, Number(e.target.value))))}
                    className="w-full text-xs border border-border rounded-md px-2 py-1 bg-background"
                    min="1"
                    max="20"
                    step="1"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
