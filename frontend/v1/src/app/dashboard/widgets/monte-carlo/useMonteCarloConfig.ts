/**
 * Custom hook for managing Monte Carlo simulation configuration state
 * Centralizes all configuration state and derived values
 */
import { useState } from 'react';

export interface MonteCarloConfig {
  // Basic simulation parameters
  numSimulations: number;
  timeHorizonYears: number;
  initialValue: number;
  estimationMethod: 'Historical Mean' | 'Exponentially Weighted';
  confidenceLevel: number;
  includeDividends: boolean;
  
  // Contribution options
  enableContributions: boolean;
  contributionAmount: number;
  contributionFrequency: 'Monthly' | 'Quarterly' | 'Annual';
  
  // Portfolio composition
  selectedSymbols: string[];
  weightMethod: 'Equal Weights' | 'Max Sharpe Ratio' | 'Min Volatility' | 'Current Portfolio' | 'Custom';
  customWeights: Record<string, number>;
  showWeightConfig: boolean;
  
  // Rebalancing options
  enableRebalancing: boolean;
  rebalancingFrequency: 'Quarterly' | 'Semi-Annual' | 'Annual';
  driftThreshold: number;
}

export interface MonteCarloConfigActions {
  setNumSimulations: (value: number) => void;
  setTimeHorizonYears: (value: number) => void;
  setInitialValue: (value: number) => void;
  setEstimationMethod: (value: 'Historical Mean' | 'Exponentially Weighted') => void;
  setConfidenceLevel: (value: number) => void;
  setIncludeDividends: (value: boolean) => void;
  setEnableContributions: (value: boolean) => void;
  setContributionAmount: (value: number) => void;
  setContributionFrequency: (value: 'Monthly' | 'Quarterly' | 'Annual') => void;
  setSelectedSymbols: (value: string[]) => void;
  setWeightMethod: (value: MonteCarloConfig['weightMethod']) => void;
  setCustomWeights: (value: Record<string, number>) => void;
  setShowWeightConfig: (value: boolean) => void;
  setEnableRebalancing: (value: boolean) => void;
  setRebalancingFrequency: (value: 'Quarterly' | 'Semi-Annual' | 'Annual') => void;
  setDriftThreshold: (value: number) => void;
}

export function useMonteCarloConfig(defaultSimulations: number = 10000) {
  const [numSimulations, setNumSimulations] = useState(defaultSimulations);
  const [timeHorizonYears, setTimeHorizonYears] = useState(10);
  const [initialValue, setInitialValue] = useState(100000);
  const [estimationMethod, setEstimationMethod] = useState<'Historical Mean' | 'Exponentially Weighted'>('Historical Mean');
  const [confidenceLevel, setConfidenceLevel] = useState(0.95);
  const [includeDividends, setIncludeDividends] = useState(true);
  
  // Contribution options
  const [enableContributions, setEnableContributions] = useState(false);
  const [contributionAmount, setContributionAmount] = useState(0);
  const [contributionFrequency, setContributionFrequency] = useState<'Monthly' | 'Quarterly' | 'Annual'>('Annual');
  
  // Portfolio composition
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [weightMethod, setWeightMethod] = useState<MonteCarloConfig['weightMethod']>('Current Portfolio');
  const [customWeights, setCustomWeights] = useState<Record<string, number>>({});
  const [showWeightConfig, setShowWeightConfig] = useState(false);
  
  // Rebalancing options
  const [enableRebalancing, setEnableRebalancing] = useState(false);
  const [rebalancingFrequency, setRebalancingFrequency] = useState<'Quarterly' | 'Semi-Annual' | 'Annual'>('Annual');
  const [driftThreshold, setDriftThreshold] = useState(5);
  
  // Derived values
  const calculatedDays = Math.round(timeHorizonYears * 252);
  
  const config: MonteCarloConfig = {
    numSimulations,
    timeHorizonYears,
    initialValue,
    estimationMethod,
    confidenceLevel,
    includeDividends,
    enableContributions,
    contributionAmount,
    contributionFrequency,
    selectedSymbols,
    weightMethod,
    customWeights,
    showWeightConfig,
    enableRebalancing,
    rebalancingFrequency,
    driftThreshold,
  };
  
  const actions: MonteCarloConfigActions = {
    setNumSimulations,
    setTimeHorizonYears,
    setInitialValue,
    setEstimationMethod,
    setConfidenceLevel,
    setIncludeDividends,
    setEnableContributions,
    setContributionAmount,
    setContributionFrequency,
    setSelectedSymbols,
    setWeightMethod,
    setCustomWeights,
    setShowWeightConfig,
    setEnableRebalancing,
    setRebalancingFrequency,
    setDriftThreshold,
  };
  
  return {
    config,
    actions,
    calculatedDays,
  };
}
