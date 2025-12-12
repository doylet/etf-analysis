/**
 * MonteCarloControls - Configuration panel for simulation parameters
 * Handles all user inputs for the Monte Carlo simulation
 */
import { WidgetSelect, WidgetNumberInput, WidgetCheckbox } from '@/components/ui/widget/widget-controls';
import { SIMULATION_COUNTS, CONFIDENCE_LEVELS, FREQUENCY_OPTIONS, ESTIMATION_METHODS } from '@/lib/widget-constants';
import type { MonteCarloConfig, MonteCarloConfigActions } from './useMonteCarloConfig';

interface MonteCarloControlsProps {
  config: MonteCarloConfig;
  actions: MonteCarloConfigActions;
}

export function MonteCarloControls({ config, actions }: MonteCarloControlsProps) {
  return (
    <div className="grid grid-cols-2 gap-2 px-1 py-3 bg-muted rounded-md flex-shrink-0 mt-3">
      <WidgetSelect
        label="Simulations"
        value={config.numSimulations.toString()}
        onChange={(val) => actions.setNumSimulations(Number(val))}
        options={SIMULATION_COUNTS.map(opt => ({ value: opt.value.toString(), label: opt.label }))}
      />
      
      <WidgetNumberInput
        label="Time Horizon (Years)"
        value={config.timeHorizonYears}
        onChange={actions.setTimeHorizonYears}
        min={1}
        max={30}
        step={1}
      />
      
      <WidgetNumberInput
        label="Initial Portfolio Value"
        value={config.initialValue}
        onChange={actions.setInitialValue}
        min={1000}
        max={10000000}
        step={10000}
      />
      
      <WidgetSelect
        label="Estimation Method"
        value={config.estimationMethod}
        onChange={(val) => actions.setEstimationMethod(val as 'Historical Mean' | 'Exponentially Weighted')}
        options={ESTIMATION_METHODS}
      />
      
      <WidgetSelect
        label="Confidence Level"
        value={config.confidenceLevel.toString()}
        onChange={(val) => actions.setConfidenceLevel(Number(val))}
        options={CONFIDENCE_LEVELS.map(opt => ({ value: opt.value.toString(), label: opt.label }))}
      />
      
      <WidgetCheckbox
        checked={config.includeDividends}
        onChange={actions.setIncludeDividends}
        label="Include Dividends"
      />
      
      <WidgetCheckbox
        checked={config.enableContributions}
        onChange={actions.setEnableContributions}
        label="Enable Contributions"
      />
      
      {config.enableContributions && (
        <>
          <WidgetNumberInput
            label="Contribution Amount"
            value={config.contributionAmount}
            onChange={actions.setContributionAmount}
            min={0}
            step={100}
          />
          
          <WidgetSelect
            label="Frequency"
            value={config.contributionFrequency}
            onChange={(val) => actions.setContributionFrequency(val as 'Monthly' | 'Quarterly' | 'Annual')}
            options={FREQUENCY_OPTIONS.filter(opt => ['Monthly', 'Quarterly', 'Annual'].includes(opt.value))}
          />
        </>
      )}
    </div>
  );
}
