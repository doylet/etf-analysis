import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';

// Debounce utility for parameter changes
function useDebouncedCallback<T extends (...args: any[]) => void>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  return useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]) as T;
}

// Widget API response types
export interface WidgetError {
  code: string;
  message: string;
  details?: Record<string, string>;
}

export interface WidgetMetadata {
  execution_time: string;
  parameters: Record<string, string>;
  widget_description: string;
  cache_hit?: boolean;
  cached_at?: string;
}

export interface WidgetResponse<T> {
  widget_name: string;
  success: boolean;
  data: T | null;
  metadata: WidgetMetadata;
  error: WidgetError | null;
}

export interface PortfolioSummaryData {
  total_value: number;
  total_return: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
  positions: number;
  allocated_cash: number;
  last_updated: string;
}

export interface HoldingData extends Record<string, unknown> {
  symbol: string;
  name: string;
  shares: number;
  current_price: number;
  current_value: number;
  weight_percent: number;
  day_change: number;
  day_change_percent: number;
  total_return: number;
  total_return_percent: number;
}

export interface BreakdownData extends Record<string, unknown> {
  category: string;
  value: number;
  weight_percent: number;
  holdings: HoldingData[];
}

export interface HoldingsBreakdownData {
  holdings: HoldingData[];
  breakdown: BreakdownData[];
  breakdown_type: string;
  total_value: number;
  last_updated: string;
}

export interface CorrelationMatrixData {
  correlation_matrix: Record<string, Record<string, number>> | Array<{symbol1: string, symbol2: string, correlation: number}>;
  symbols: string[];
  analysis_period: {
    start_date: string;
    end_date: string;
    days_analyzed: number;
  };
  statistics: {
    avg_correlation: number;
    max_correlation: number;
    min_correlation: number;
  };
  last_updated: string;
}

export interface MonteCarloData {
  scenarios: Array<{
    final_value: number;
    return_percent: number;
    max_drawdown: number;
  }>;
  statistics: {
    mean_final_value: number;
    std_final_value: number;
    mean_return_percent: number;
    probability_of_loss: number;
    cagr_median: number;
    cagr_10th: number;
    cagr_90th: number;
    historical_sharpe: number;
    historical_volatility: number;
    max_drawdown_median: number;
    cvar_95?: number;
  };
  percentiles: {
    "10": number;
    "50": number;
    "90": number;
  };
  var_95: number;
  var_99: number;
  simulation_params: {
    num_simulations: number;
    time_horizon_years: number;
    initial_value: number;
    confidence_level: number;
  };
  path_statistics?: {
    time_points: number[];
    percentile_10: number[];
    percentile_50: number[];
    percentile_90: number[];
    median_drawdown: number[];
  };
  rebalancing_rec?: {
    rebalance_dates: string[];
    drift_at_rebalance: number[];
    trigger_threshold: number;
    avg_drift: number;
    cost_benefit_ratio: number;
    sharpe_improvement: number;
    description: string;
    symbols: string[];
  };
  execution_time_seconds: number;
  last_updated: string;
}

export interface BenchmarkComparisonData {
  portfolio_return: number;
  benchmark_return: number;
  alpha: number;
  beta: number;
  sharpe_ratio: number;
  benchmark_sharpe?: number;
  portfolio_volatility?: number;
  benchmark_volatility?: number;
  information_ratio?: number;
  tracking_error: number;
  outperformance: number;
  correlation: number;
  benchmark_symbol: string;
  time_period: string;
  last_updated: string;
  // Optional fallback properties for minimal responses
  status?: string;
  message?: string;
  holdings_count?: number;
  benchmarks?: Record<string, string>;
}

export interface DividendAnalysisData {
  total_dividends: number;
  dividend_yield: number;
  dividend_growth_rate: number;
  payout_ratio: number;
  monthly_dividends: Array<{
    month: string;
    amount: number;
    count: number;
  }>;
  top_dividend_holdings: Array<{
    symbol: string;
    yield: number;
    annual_amount: number;
    percentage: number;
  }>;
  next_ex_dates: Array<{
    symbol: string;
    ex_date: string;
    estimated_amount: number;
  }>;
  last_updated: string;
  // Optional fallback properties for minimal responses
  status?: string;
  message?: string;
  holdings_count?: number;
}

export interface PerformanceData {
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  best_day: { date: string; return: number };
  worst_day: { date: string; return: number };
  win_rate: number;
  performance_periods: Array<{
    period: string;
    return: number;
    volatility: number;
  }>;
  risk_metrics: {
    var_95: number;
    var_99: number;
    cvar_95: number;
    calmar_ratio: number;
  };
  last_updated: string;
  // Optional fallback properties for minimal responses
  status?: string;
  message?: string;
  holdings_count?: number;
}

export interface TimeseriesData {
  price_data: Array<{
    date: string;
    value: number;
    return: number;
  }>;
  statistics: {
    total_return: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
  };
  rolling_metrics: Array<{
    date: string;
    rolling_return: number;
    rolling_volatility: number;
  }>;
  last_updated: string;
  // Optional fallback properties for minimal responses
  status?: string;
  message?: string;
  holdings_count?: number;
}

export interface PortfolioTransitionData {
  current_allocation: Record<string, number>;
  target_allocation: Record<string, number>;
  required_trades: Array<{
    symbol: string;
    action: 'buy' | 'sell';
    shares: number;
    value: number;
  }>;
  transition_cost: number;
  expected_impact: {
    risk_change: number;
    return_change: number;
  };
  last_updated: string;
  // Optional fallback properties for minimal responses
  status?: string;
  message?: string;
  holdings_count?: number;
}

export interface NewsEventData {
  events: Array<{
    date: string;
    title: string;
    sentiment: number;
    impact_score: number;
    affected_symbols: string[];
  }>;
  sentiment_analysis: {
    overall_sentiment: number;
    sentiment_trend: number;
  };
  market_impact: {
    price_correlation: number;
    volatility_impact: number;
  };
  last_updated: string;
  // Optional fallback properties for minimal responses
  status?: string;
  message?: string;
  holdings_count?: number;
}

export interface PortfolioOptimizerData {
  current_weights?: Record<string, number>;
  optimal_weights?: Record<string, number>;
  optimized_weights?: Record<string, number>;
  expected_return: number;
  expected_risk: number;
  sharpe_ratio: number;
  current_return?: number;
  current_risk?: number;
  current_sharpe?: number;
  improvement_metrics?: {
    return_improvement: number;
    risk_reduction: number;
    sharpe_improvement: number;
  };
  efficient_frontier?: Array<{
    expected_return: number;
    volatility: number;
    sharpe_ratio: number;
    weights?: Record<string, number>;
  }>;
  constraints_satisfied?: boolean;
  last_updated?: string;
  // Optional fallback properties for minimal responses
  status?: string;
  message?: string;
  holdings_count?: number;
  holdings_analyzed?: number;
}

export interface ConstrainedOptimizationData {
  constraints: Record<string, string | number | boolean | string[]>;
  optimized_weights: Record<string, number>;
  optimization_result: {
    objective_value: number;
    risk: number;
    return: number;
    sharpe_ratio: number;
  };
  constraint_violations: Array<{
    constraint: string;
    violation: number;
  }>;
  last_updated: string;
  // Optional fallback properties for minimal responses
  status?: string;
  message?: string;
  holdings_count?: number;
}

export type PortfolioSummaryResponse = WidgetResponse<PortfolioSummaryData>;
export type HoldingsBreakdownResponse = WidgetResponse<HoldingsBreakdownData>;
export type CorrelationMatrixResponse = WidgetResponse<CorrelationMatrixData>;
export type MonteCarloResponse = WidgetResponse<MonteCarloData>;
export type BenchmarkComparisonResponse = WidgetResponse<BenchmarkComparisonData>;
export type DividendAnalysisResponse = WidgetResponse<DividendAnalysisData>;
export type PerformanceResponse = WidgetResponse<PerformanceData>;

export interface UseWidgetReturn<T> {
  data: T | null;
  loading: boolean;
  isRefreshing: boolean;
  error: string | null;
  metadata: WidgetMetadata | null;
  cacheHit: boolean;
  refetch: () => Promise<void>;
  mutate: (updater: T | ((current: T | null) => T | null)) => void;
}

export interface UsePortfolioSummaryOptions {
  portfolioId?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseHoldingsBreakdownOptions {
  portfolioId?: string;
  breakdownType?: 'sector' | 'geography' | 'asset_class';
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseCorrelationMatrixOptions {
  portfolioId?: string;
  timeWindowDays?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseMonteCarloOptions {
  portfolioId?: string;
  numSimulations?: number;
  timeHorizonDays?: number;
  estimationMethod?: 'Historical Mean' | 'Exponentially Weighted';
  confidenceLevel?: number;
  initialValue?: number;
  includeDividends?: boolean;
  enableContributions?: boolean;
  contributionAmount?: number;
  contributionFrequency?: 'Monthly' | 'Quarterly' | 'Annual';
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseBenchmarkComparisonOptions {
  portfolioId?: string;
  benchmark?: string;
  timePeriod?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseDividendAnalysisOptions {
  portfolioId?: string;
  timePeriod?: string;
  symbol?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UsePerformanceOptions {
  portfolioId?: string;
  timePeriod?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseTimeseriesOptions {
  portfolioId?: string;
  timePeriod?: string;
  analysisType?: string;
  symbol?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UsePortfolioTransitionOptions {
  currentPortfolioId?: string;
  targetPortfolioId?: string;
  transitionMethod?: string;
  optimizationPriority?: string;
  targetWeights?: Record<string, number>;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseNewsEventOptions {
  portfolioId?: string;
  timePeriod?: string;
  lookbackDays?: number;
  surpriseThreshold?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UsePortfolioOptimizerOptions {
  portfolioId?: string;
  mode?: string;
  timePeriod?: string;
  targetReturn?: number;
  includeDividends?: boolean;
  optimizationType?: string;
  riskTolerance?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseConstrainedOptimizationOptions {
  portfolioId?: string;
  objective?: string;
  maxWeight?: number;
  minWeight?: number;
  targetReturn?: number;
  constraints?: Record<string, string | number | boolean | string[]>;
  optimizationType?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const WIDGET_API_BASE = '/api/widgets';

// Generic widget fetcher function
async function fetchWidget<T>(
  endpoint: string,
  params?: Record<string, string | number | boolean> | undefined
): Promise<WidgetResponse<T>> {
  try {
    const response = await axios.get<WidgetResponse<T>>(`${WIDGET_API_BASE}${endpoint}`, { params });
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response?.data) {
      return error.response.data;
    }
    throw error;
  }
}

/**
 * Custom hook for fetching portfolio summary data from the widget API
 * Provides access to portfolio performance metrics through the new widget endpoint
 */
export function usePortfolioSummary(options: UsePortfolioSummaryOptions = {}): UseWidgetReturn<PortfolioSummaryData> {
  const { portfolioId, autoRefresh = false, refreshInterval = 300000 } = options; // 5 min default
  
  const [data, setData] = useState<PortfolioSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  // Use ref to avoid re-fetching on every render
  const hasFetchedRef = useRef(false);

  const fetchPortfolioSummary = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = portfolioId ? { portfolio_id: portfolioId } : undefined;
      const widgetResponse = await fetchWidget<PortfolioSummaryData>('/portfolio/summary', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else if (widgetResponse.error) {
        setError(widgetResponse.error.message);
        setData(null);
        setMetadata(widgetResponse.metadata);
      } else {
        setError('No data received from portfolio summary widget');
        setData(null);
      }
      
    } catch (err: unknown) {
      console.error('Failed to fetch portfolio summary widget:', err);
      
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          setError('Authentication required to access portfolio data');
        } else if (err.response?.status === 403) {
          setError('Insufficient permissions to access portfolio data');
        } else if (err.response?.status === 422) {
          setError('Invalid portfolio parameters provided');
        } else if (err.response?.data?.detail) {
          setError(err.response.data.detail);
        } else {
          setError('Failed to load portfolio summary data');
        }
      } else {
        setError('Failed to load portfolio summary data');
      }
      
      setData(null);
      setMetadata(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId]);

  const mutate = useCallback((updater: PortfolioSummaryData | ((current: PortfolioSummaryData | null) => PortfolioSummaryData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchPortfolioSummary(true);
    } else {
      fetchPortfolioSummary(false);
    }
  }, [fetchPortfolioSummary]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchPortfolioSummary(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchPortfolioSummary]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchPortfolioSummary(false),
    mutate,
  };
}

/**
 * Custom hook for fetching holdings breakdown data
 */
export function useHoldingsBreakdown(options: UseHoldingsBreakdownOptions = {}): UseWidgetReturn<HoldingsBreakdownData> {
  const { portfolioId, breakdownType = 'asset_class', autoRefresh = false, refreshInterval = 600000 } = options; // 10 min default
  
  const [data, setData] = useState<HoldingsBreakdownData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  const hasFetchedRef = useRef(false);

  const fetchHoldingsBreakdown = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        breakdown_type: breakdownType
      };
      
      const widgetResponse = await fetchWidget<HoldingsBreakdownData>('/portfolio/holdings', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No holdings data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
      
    } catch (err: unknown) {
      console.error('Failed to fetch holdings breakdown:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load holdings breakdown');
      } else {
        setError('Failed to load holdings breakdown');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, breakdownType]);

  const mutate = useCallback((updater: HoldingsBreakdownData | ((current: HoldingsBreakdownData | null) => HoldingsBreakdownData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchHoldingsBreakdown(true);
    } else {
      fetchHoldingsBreakdown(false);
    }
  }, [fetchHoldingsBreakdown]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchHoldingsBreakdown(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchHoldingsBreakdown]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchHoldingsBreakdown(false),
    mutate,
  };
}

/**
 * Custom hook for fetching correlation matrix data
 */
export function useCorrelationMatrix(options: UseCorrelationMatrixOptions = {}): UseWidgetReturn<CorrelationMatrixData> {
  const { portfolioId, timeWindowDays = 252, autoRefresh = false, refreshInterval = 900000 } = options; // 15 min default
  
  const [data, setData] = useState<CorrelationMatrixData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  const hasFetchedRef = useRef(false);

  const fetchCorrelationMatrix = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        time_window_days: timeWindowDays.toString()
      };
      
      const widgetResponse = await fetchWidget<CorrelationMatrixData>('/portfolio/correlation', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No correlation data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
      
    } catch (err: unknown) {
      console.error('Failed to fetch correlation matrix:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load correlation matrix');
      } else {
        setError('Failed to load correlation matrix');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, timeWindowDays]);

  const mutate = useCallback((updater: CorrelationMatrixData | ((current: CorrelationMatrixData | null) => CorrelationMatrixData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchCorrelationMatrix(true);
    } else {
      fetchCorrelationMatrix(false);
    }
  }, [fetchCorrelationMatrix]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchCorrelationMatrix(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchCorrelationMatrix]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchCorrelationMatrix(false),
    mutate,
  };
}

/**
 * Custom hook for running Monte Carlo simulations
 */
export function useMonteCarloSimulation(options: UseMonteCarloOptions = {}): UseWidgetReturn<MonteCarloData> {
  const { 
    portfolioId, 
    numSimulations = 10000, 
    timeHorizonDays = 252, 
    estimationMethod = 'Historical Mean',
    confidenceLevel = 0.95,
    initialValue,
    includeDividends = true,
    enableContributions = false,
    contributionAmount = 0,
    contributionFrequency = 'Annual',
    autoRefresh = false, 
    refreshInterval = 1200000 // 20 min default
  } = options;
  
  const [data, setData] = useState<MonteCarloData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  const hasFetchedRef = useRef(false);

  const runSimulation = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        num_simulations: numSimulations.toString(),
        time_horizon_days: timeHorizonDays.toString(),
        estimation_method: estimationMethod,
        confidence_level: confidenceLevel.toString(),
        ...(initialValue !== undefined && { initial_value: initialValue.toString() }),
        include_dividends: includeDividends.toString(),
        enable_contributions: enableContributions.toString(),
        contribution_amount: contributionAmount.toString(),
        contribution_frequency: contributionFrequency
      };
      
      const widgetResponse = await fetchWidget<MonteCarloData>('/portfolio/monte-carlo', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'Monte Carlo simulation failed');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
      
    } catch (err: unknown) {
      console.error('Failed to run Monte Carlo simulation:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to run simulation');
      } else {
        setError('Failed to run simulation');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, numSimulations, timeHorizonDays, estimationMethod, confidenceLevel, initialValue, includeDividends, enableContributions, contributionAmount, contributionFrequency]);

  const mutate = useCallback((updater: MonteCarloData | ((current: MonteCarloData | null) => MonteCarloData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  // Debounced trigger for parameter changes
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      runSimulation(true); // Initial load happens immediately
    } else {
      // Clear any pending debounced call
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      // Debounce subsequent runs to batch rapid parameter changes
      debounceTimeoutRef.current = setTimeout(() => {
        runSimulation(false);
      }, 300);
    }

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [runSimulation]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        runSimulation(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, runSimulation]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => runSimulation(false),
    mutate,
  };
}

/**
 * Custom hook for benchmark comparison analysis
 */
export function useBenchmarkComparison(options: UseBenchmarkComparisonOptions = {}): UseWidgetReturn<BenchmarkComparisonData> {
  const { portfolioId, benchmark = 'SPY', timePeriod = '1Y', autoRefresh = false, refreshInterval = 900000 } = options;
  
  const [data, setData] = useState<BenchmarkComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  const hasFetchedRef = useRef(false);

  const fetchBenchmarkComparison = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        benchmark,
        time_period: timePeriod
      };
      
      const widgetResponse = await fetchWidget<BenchmarkComparisonData>('/benchmark-comparison', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No benchmark comparison data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
    } catch (err: unknown) {
      console.error('Failed to fetch benchmark comparison:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load benchmark comparison');
      } else {
        setError('Failed to load benchmark comparison');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, benchmark, timePeriod]);

  const mutate = useCallback((updater: BenchmarkComparisonData | ((current: BenchmarkComparisonData | null) => BenchmarkComparisonData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchBenchmarkComparison(true);
    } else {
      fetchBenchmarkComparison(false);
    }
  }, [fetchBenchmarkComparison]);

  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchBenchmarkComparison(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchBenchmarkComparison]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchBenchmarkComparison(false),
    mutate,
  };
}

/**
 * Custom hook for dividend analysis
 */
export function useDividendAnalysis(options: UseDividendAnalysisOptions = {}): UseWidgetReturn<DividendAnalysisData> {
  const { portfolioId, timePeriod = '1Y', symbol, autoRefresh = false, refreshInterval = 900000 } = options;
  
  const [data, setData] = useState<DividendAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  const hasFetchedRef = useRef(false);

  const fetchDividendAnalysis = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params: Record<string, string> = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        time_period: timePeriod,
        ...(symbol && { symbol })
      };
      
      const widgetResponse = await fetchWidget<DividendAnalysisData>('/dividend-analysis', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No dividend analysis data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
    } catch (err: unknown) {
      console.error('Failed to fetch dividend analysis:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load dividend analysis');
      } else {
        setError('Failed to load dividend analysis');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, timePeriod, symbol]);

  const mutate = useCallback((updater: DividendAnalysisData | ((current: DividendAnalysisData | null) => DividendAnalysisData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchDividendAnalysis(true);
    } else {
      fetchDividendAnalysis(false);
    }
  }, [fetchDividendAnalysis]);

  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchDividendAnalysis(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchDividendAnalysis]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchDividendAnalysis(false),
    mutate,
  };
}

/**
 * Custom hook for performance analysis
 */
export function usePerformanceAnalysis(options: UsePerformanceOptions = {}): UseWidgetReturn<PerformanceData> {
  const { portfolioId, timePeriod = '1Y', autoRefresh = false, refreshInterval = 900000 } = options;
  
  const [data, setData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  const hasFetchedRef = useRef(false);

  const fetchPerformanceAnalysis = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        time_period: timePeriod
      };
      
      const widgetResponse = await fetchWidget<PerformanceData>('/performance', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No performance analysis data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
    } catch (err: unknown) {
      console.error('Failed to fetch performance analysis:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load performance analysis');
      } else {
        setError('Failed to load performance analysis');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, timePeriod]);

  const mutate = useCallback((updater: PerformanceData | ((current: PerformanceData | null) => PerformanceData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchPerformanceAnalysis(true);
    } else {
      fetchPerformanceAnalysis(false);
    }
  }, [fetchPerformanceAnalysis]);

  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchPerformanceAnalysis(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchPerformanceAnalysis]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchPerformanceAnalysis(false),
    mutate,
  };
}

/**
 * Custom hook for timeseries analysis
 */
export function useTimeseriesAnalysis(options: UseTimeseriesOptions = {}): UseWidgetReturn<TimeseriesData> {
  const { portfolioId, timePeriod = '1Y', analysisType, symbol, autoRefresh = false, refreshInterval = 900000 } = options;
  
  const [data, setData] = useState<TimeseriesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  const hasFetchedRef = useRef(false);

  const fetchTimeseriesAnalysis = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        time_period: timePeriod,
        ...(analysisType && { analysis_type: analysisType }),
        ...(symbol && { symbol })
      };
      
      const widgetResponse = await fetchWidget<TimeseriesData>('/timeseries-analysis', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No timeseries analysis data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
    } catch (err: unknown) {
      console.error('Failed to fetch timeseries analysis:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load timeseries analysis');
      } else {
        setError('Failed to load timeseries analysis');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, timePeriod, analysisType, symbol]);

  const mutate = useCallback((updater: TimeseriesData | ((current: TimeseriesData | null) => TimeseriesData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchTimeseriesAnalysis(true);
    } else {
      fetchTimeseriesAnalysis(false);
    }
  }, [fetchTimeseriesAnalysis]);

  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchTimeseriesAnalysis(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchTimeseriesAnalysis]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchTimeseriesAnalysis(false),
    mutate,
  };
}

/**
 * Custom hook for portfolio transition analysis
 */
export function usePortfolioTransition(options: UsePortfolioTransitionOptions = {}): UseWidgetReturn<PortfolioTransitionData> {
  const { currentPortfolioId, targetPortfolioId, transitionMethod, optimizationPriority, targetWeights, autoRefresh = false, refreshInterval = 900000 } = options;
  
  const [data, setData] = useState<PortfolioTransitionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  const hasFetchedRef = useRef(false);

  const fetchPortfolioTransition = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(currentPortfolioId && { current_portfolio_id: currentPortfolioId }),
        ...(targetPortfolioId && { target_portfolio_id: targetPortfolioId }),
        ...(transitionMethod && { transition_method: transitionMethod }),
        ...(optimizationPriority && { optimization_priority: optimizationPriority }),
        ...(targetWeights && { target_weights: JSON.stringify(targetWeights) })
      };
      
      const widgetResponse = await fetchWidget<PortfolioTransitionData>('/portfolio-transition', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No portfolio transition data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
    } catch (err: unknown) {
      console.error('Failed to fetch portfolio transition:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load portfolio transition');
      } else {
        setError('Failed to load portfolio transition');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [currentPortfolioId, targetPortfolioId, transitionMethod, optimizationPriority, targetWeights]);

  const mutate = useCallback((updater: PortfolioTransitionData | ((current: PortfolioTransitionData | null) => PortfolioTransitionData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchPortfolioTransition(true);
    } else {
      fetchPortfolioTransition(false);
    }
  }, [fetchPortfolioTransition]);

  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchPortfolioTransition(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchPortfolioTransition]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchPortfolioTransition(false),
    mutate,
  };
}

/**
 * Custom hook for news event analysis
 */
export function useNewsEventAnalysis(options: UseNewsEventOptions = {}): UseWidgetReturn<NewsEventData> {
  const { portfolioId, timePeriod = '7D', lookbackDays, surpriseThreshold, autoRefresh = false, refreshInterval = 300000 } = options;
  
  const [data, setData] = useState<NewsEventData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  const hasFetchedRef = useRef(false);

  const fetchNewsEventAnalysis = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        time_period: timePeriod,
        ...(lookbackDays !== undefined && { lookback_days: lookbackDays }),
        ...(surpriseThreshold !== undefined && { surprise_threshold: surpriseThreshold })
      };
      
      const widgetResponse = await fetchWidget<NewsEventData>('/news-event-analysis', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No news event data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
    } catch (err: unknown) {
      console.error('Failed to fetch news event analysis:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load news event analysis');
      } else {
        setError('Failed to load news event analysis');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, timePeriod, lookbackDays, surpriseThreshold]);

  const mutate = useCallback((updater: NewsEventData | ((current: NewsEventData | null) => NewsEventData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchNewsEventAnalysis(true);
    } else {
      fetchNewsEventAnalysis(false);
    }
  }, [fetchNewsEventAnalysis]);

  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchNewsEventAnalysis(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchNewsEventAnalysis]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchNewsEventAnalysis(false),
    mutate,
  };
}

/**
 * Custom hook for portfolio optimization
 */
export function usePortfolioOptimizer(options: UsePortfolioOptimizerOptions = {}): UseWidgetReturn<PortfolioOptimizerData> {
  const { portfolioId, mode, timePeriod, targetReturn, includeDividends, optimizationType = 'MAX_SHARPE', riskTolerance = 0.5, autoRefresh = false, refreshInterval = 1800000 } = options;
  
  const [data, setData] = useState<PortfolioOptimizerData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  const hasFetchedRef = useRef(false);

  const fetchPortfolioOptimizer = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        ...(mode && { mode }),
        ...(timePeriod && { time_period: timePeriod }),
        ...(targetReturn !== undefined && { target_return: targetReturn }),
        ...(includeDividends !== undefined && { include_dividends: includeDividends }),
        optimization_type: optimizationType,
        risk_tolerance: riskTolerance.toString()
      };
      
      const widgetResponse = await fetchWidget<PortfolioOptimizerData>('/portfolio-optimizer', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No portfolio optimization data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
    } catch (err: unknown) {
      console.error('Failed to fetch portfolio optimizer:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load portfolio optimizer');
      } else {
        setError('Failed to load portfolio optimizer');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, mode, timePeriod, targetReturn, includeDividends, optimizationType, riskTolerance]);

  const mutate = useCallback((updater: PortfolioOptimizerData | ((current: PortfolioOptimizerData | null) => PortfolioOptimizerData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchPortfolioOptimizer(true);
    } else {
      fetchPortfolioOptimizer(false);
    }
  }, [fetchPortfolioOptimizer]);

  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchPortfolioOptimizer(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchPortfolioOptimizer]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchPortfolioOptimizer(false),
    mutate,
  };
}

/**
 * Custom hook for constrained optimization
 */
export function useConstrainedOptimization(options: UseConstrainedOptimizationOptions = {}): UseWidgetReturn<ConstrainedOptimizationData> {
  const { portfolioId, objective, maxWeight, minWeight, targetReturn, constraints, optimizationType = 'MAX_SHARPE', autoRefresh = false, refreshInterval = 1800000 } = options;
  
  const [data, setData] = useState<ConstrainedOptimizationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  
  const hasFetchedRef = useRef(false);

  const fetchConstrainedOptimization = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        ...(objective && { objective }),
        ...(maxWeight !== undefined && { max_weight: maxWeight }),
        ...(minWeight !== undefined && { min_weight: minWeight }),
        ...(targetReturn !== undefined && { target_return: targetReturn }),
        optimization_type: optimizationType,
        ...(constraints && { constraints: JSON.stringify(constraints) })
      };
      
      const widgetResponse = await fetchWidget<ConstrainedOptimizationData>('/constrained-optimization', params);
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No constrained optimization data available');
        setData(null);
        setMetadata(widgetResponse.metadata || null);
      }
    } catch (err: unknown) {
      console.error('Failed to fetch constrained optimization:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to load constrained optimization');
      } else {
        setError('Failed to load constrained optimization');
      }
      setData(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, [portfolioId, objective, maxWeight, minWeight, targetReturn, constraints, optimizationType]);

  const mutate = useCallback((updater: ConstrainedOptimizationData | ((current: ConstrainedOptimizationData | null) => ConstrainedOptimizationData | null)) => {
    setData(current => typeof updater === 'function' ? updater(current) : updater);
  }, []);

  useEffect(() => {
    const isFirstRun = !hasFetchedRef.current;
    if (isFirstRun) {
      hasFetchedRef.current = true;
      fetchConstrainedOptimization(true);
    } else {
      fetchConstrainedOptimization(false);
    }
  }, [fetchConstrainedOptimization]);

  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      if (!loading && !isRefreshing) {
        fetchConstrainedOptimization(false);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loading, isRefreshing, fetchConstrainedOptimization]);

  return {
    data,
    loading,
    isRefreshing,
    error,
    metadata,
    cacheHit,
    refetch: () => fetchConstrainedOptimization(false),
    mutate,
  };
}

/**
 * Bulk hook to fetch all widget data at once
 * Useful for dashboard views that need multiple widgets
 */
export function useAllWidgets(portfolioId?: string) {
  const portfolioSummary = usePortfolioSummary({ portfolioId });
  const holdingsBreakdown = useHoldingsBreakdown({ portfolioId });
  const correlationMatrix = useCorrelationMatrix({ portfolioId });
  const monteCarloSimulation = useMonteCarloSimulation({ portfolioId });
  const benchmarkComparison = useBenchmarkComparison({ portfolioId });
  const dividendAnalysis = useDividendAnalysis({ portfolioId });
  const performanceAnalysis = usePerformanceAnalysis({ portfolioId });
  const timeseriesAnalysis = useTimeseriesAnalysis({ portfolioId });
  const portfolioTransition = usePortfolioTransition({ currentPortfolioId: portfolioId });
  const newsEventAnalysis = useNewsEventAnalysis({ portfolioId });
  const portfolioOptimizer = usePortfolioOptimizer({ portfolioId });
  const constrainedOptimization = useConstrainedOptimization({ portfolioId });

  const isLoading = portfolioSummary.loading || 
                   holdingsBreakdown.loading || 
                   correlationMatrix.loading || 
                   monteCarloSimulation.loading ||
                   benchmarkComparison.loading ||
                   dividendAnalysis.loading ||
                   performanceAnalysis.loading ||
                   timeseriesAnalysis.loading ||
                   portfolioTransition.loading ||
                   newsEventAnalysis.loading ||
                   portfolioOptimizer.loading ||
                   constrainedOptimization.loading;

  const hasError = portfolioSummary.error || 
                  holdingsBreakdown.error || 
                  correlationMatrix.error || 
                  monteCarloSimulation.error ||
                  benchmarkComparison.error ||
                  dividendAnalysis.error ||
                  performanceAnalysis.error ||
                  timeseriesAnalysis.error ||
                  portfolioTransition.error ||
                  newsEventAnalysis.error ||
                  portfolioOptimizer.error ||
                  constrainedOptimization.error;

  const refetchAll = useCallback(async () => {
    await Promise.all([
      portfolioSummary.refetch(),
      holdingsBreakdown.refetch(),
      correlationMatrix.refetch(),
      monteCarloSimulation.refetch(),
      benchmarkComparison.refetch(),
      dividendAnalysis.refetch(),
      performanceAnalysis.refetch(),
      timeseriesAnalysis.refetch(),
      portfolioTransition.refetch(),
      newsEventAnalysis.refetch(),
      portfolioOptimizer.refetch(),
      constrainedOptimization.refetch()
    ]);
  }, [
    portfolioSummary,
    holdingsBreakdown,
    correlationMatrix,
    monteCarloSimulation,
    benchmarkComparison,
    dividendAnalysis,
    performanceAnalysis,
    timeseriesAnalysis,
    portfolioTransition,
    newsEventAnalysis,
    portfolioOptimizer,
    constrainedOptimization
  ]);

  return {
    portfolioSummary,
    holdingsBreakdown,
    correlationMatrix,
    monteCarloSimulation,
    benchmarkComparison,
    dividendAnalysis,
    performanceAnalysis,
    timeseriesAnalysis,
    portfolioTransition,
    newsEventAnalysis,
    portfolioOptimizer,
    constrainedOptimization,
    isLoading,
    hasError,
    refetchAll
  };
}