/**
 * Widget Constants
 * Shared constants used across multiple widgets for consistency
 */

/**
 * Standard time period options used in most widgets
 */
export const TIME_PERIODS = [
  { value: '1W', label: '1 Week' },
  { value: '1M', label: '1 Month' },
  { value: '3M', label: '3 Months' },
  { value: '6M', label: '6 Months' },
  { value: '1Y', label: '1 Year' },
  { value: '2Y', label: '2 Years' },
  { value: '5Y', label: '5 Years' },
] as const;

/**
 * Extended time period options including longer durations
 */
export const TIME_PERIODS_EXTENDED = [
  ...TIME_PERIODS,
  { value: '10Y', label: '10 Years' },
  { value: 'All', label: 'All Time' },
] as const;

/**
 * Common benchmark indices for comparison
 */
export const COMMON_BENCHMARKS = [
  { value: 'SPY', label: 'S&P 500' },
  { value: 'QQQ', label: 'Nasdaq 100' },
  { value: 'DIA', label: 'Dow Jones' },
  { value: 'IWM', label: 'Russell 2000' },
  { value: 'VTI', label: 'Total US Market' },
  { value: 'EFA', label: 'International' },
  { value: 'AGG', label: 'US Bonds' },
  { value: 'GLD', label: 'Gold' },
] as const;

/**
 * Monte Carlo simulation count options
 */
export const SIMULATION_COUNTS = [
  { value: 1000, label: '1K Simulations' },
  { value: 5000, label: '5K Simulations' },
  { value: 10000, label: '10K Simulations' },
  { value: 25000, label: '25K Simulations' },
] as const;

/**
 * Standard confidence levels for risk analysis
 */
export const CONFIDENCE_LEVELS = [
  { value: 0.90, label: '90%' },
  { value: 0.95, label: '95%' },
  { value: 0.99, label: '99%' },
] as const;

/**
 * Frequency options for contributions and rebalancing
 */
export const FREQUENCY_OPTIONS = [
  { value: 'Monthly', label: 'Monthly' },
  { value: 'Quarterly', label: 'Quarterly' },
  { value: 'Semi-Annual', label: 'Semi-Annual' },
  { value: 'Annual', label: 'Annual' },
] as const;

/**
 * Portfolio optimization objectives
 */
export const OPTIMIZATION_OBJECTIVES = [
  { value: 'Max Sharpe', label: 'Max Sharpe Ratio' },
  { value: 'Min Volatility', label: 'Min Volatility' },
  { value: 'Target Return', label: 'Target Return' },
  { value: 'Efficient Frontier', label: 'Efficient Frontier' },
] as const;

/**
 * Weight allocation methods
 */
export const WEIGHT_METHODS = [
  { value: 'Equal Weights', label: 'Equal Weights' },
  { value: 'Max Sharpe Ratio', label: 'Max Sharpe Ratio' },
  { value: 'Min Volatility', label: 'Min Volatility' },
  { value: 'Current Portfolio', label: 'Current Portfolio' },
  { value: 'Custom', label: 'Custom' },
] as const;

/**
 * Estimation methods for Monte Carlo simulations
 */
export const ESTIMATION_METHODS = [
  { value: 'Historical Mean', label: 'Historical Mean' },
  { value: 'Exponentially Weighted', label: 'Exp. Weighted' },
] as const;
