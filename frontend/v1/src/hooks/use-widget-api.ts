/**
 * Comprehensive Widget API Types and Hooks
 * 
 * TypeScript definitions and React hooks for consuming the portfolio widget APIs.
 * Provides type-safe access to portfolio summary, holdings breakdown, correlation matrix, 
 * and Monte Carlo simulation data.
 */

import { useState, useEffect, useCallback } from 'react';
import axios, { AxiosResponse } from 'axios';

// ============================================================================
// Base Widget API Types
// ============================================================================

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

export interface WidgetResponse<T = Record<string, unknown>> {
  widget_name: string;
  success: boolean;
  data: T | null;
  metadata: WidgetMetadata;
  error: WidgetError | null;
}

// ============================================================================
// Portfolio Summary Types
// ============================================================================

export interface PortfolioSummaryData {
  total_value: number;
  total_return: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
  positions: number;
  allocated_cash: number;
  last_updated: string; // ISO date string
}

export type PortfolioSummaryResponse = WidgetResponse<PortfolioSummaryData>;

// ============================================================================
// Holdings Breakdown Types
// ============================================================================

export interface HoldingPosition {
  symbol: string;
  name: string;
  quantity: number;
  current_price: number;
  market_value: number;
  weight: number;
  sector: string;
  geography: string;
  asset_class: string;
}

export interface CategoryBreakdown {
  name: string;
  value: number;
  weight: number;
  positions: number;
}

export interface HoldingsBreakdownData {
  holdings: HoldingPosition[];
  total_positions: number;
  total_value: number;
  breakdown_by_sector: CategoryBreakdown[];
  breakdown_by_geography: CategoryBreakdown[];
  breakdown_by_asset_class: CategoryBreakdown[];
  concentration_risk_score: number;
  last_updated: string;
}

export type HoldingsBreakdownResponse = WidgetResponse<HoldingsBreakdownData>;

// ============================================================================
// Correlation Matrix Types
// ============================================================================

export interface CorrelationPair {
  symbol1: string;
  symbol2: string;
  correlation: number;
}

export interface CorrelationPairs {
  asset1: string;
  asset2: string;
  correlation: number;
}

export interface CorrelationStatistics {
  avg_correlation: number;
  max_correlation: number;
  min_correlation: number;
  num_days: number;
}

export interface AnalysisPeriod {
  start_date: string;
  end_date: string;
  days_analyzed: number;
}

export interface CorrelationMatrixData {
  symbols: string[];
  correlation_matrix: CorrelationPair[];
  correlation_pairs: CorrelationPairs[];
  benchmark_comparison: Record<string, string | number>[];
  statistics: CorrelationStatistics;
  analysis_period: AnalysisPeriod;
  last_updated: string;
}

export type CorrelationMatrixResponse = WidgetResponse<CorrelationMatrixData>;

// ============================================================================
// Monte Carlo Types
// ============================================================================

export interface MonteCarloScenario {
  final_value: number;
  return_percent: number;
  max_drawdown: number;
}

export interface MonteCarloStatistics {
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
}

export interface MonteCarloSimulationParams {
  num_simulations: number;
  time_horizon_years: number;
  initial_value: number;
  confidence_level: number;
}

export interface MonteCarloData {
  scenarios: MonteCarloScenario[];
  statistics: MonteCarloStatistics;
  percentiles: Record<string, number>;
  var_95: number;
  var_99: number;
  simulation_params: MonteCarloSimulationParams;
  execution_time_seconds: number;
  last_updated: string;
}

export type MonteCarloResponse = WidgetResponse<MonteCarloData>;

// ============================================================================
// Hook Return Types
// ============================================================================

export interface UseWidgetReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  metadata: WidgetMetadata | null;
  cacheHit: boolean;
  refetch: () => Promise<void>;
}

export interface UseOptionalParams {
  portfolioId?: string;
  autoRefetch?: boolean;
  refreshInterval?: number;
}

// ============================================================================
// API Configuration
// ============================================================================

const WIDGET_API_BASE = '/api/widgets';

// ============================================================================
// Enhanced Widget Hooks
// ============================================================================

/**
 * Hook for portfolio summary widget
 * Provides portfolio performance metrics and overview data
 */
export function usePortfolioSummary(
  options: UseOptionalParams = {}
): UseWidgetReturn<PortfolioSummaryData> {
  const { portfolioId, autoRefetch = true, refreshInterval } = options;

  const [data, setData] = useState<PortfolioSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = `${WIDGET_API_BASE}/portfolio/summary`;
      const params = portfolioId ? { portfolio_id: portfolioId } : {};
      
      const response: AxiosResponse<PortfolioSummaryResponse> = await axios.get(url, { params });
      const widgetResponse = response.data;
      
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
      setError(handleApiError(err));
      setData(null);
      setMetadata(null);
    } finally {
      setLoading(false);
    }
  }, [portfolioId]);

  useEffect(() => {
    if (autoRefetch) {
      fetchData();
    }
  }, [fetchData, autoRefetch]);

  // Auto-refresh interval
  useEffect(() => {
    if (refreshInterval && refreshInterval > 0) {
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchData, refreshInterval]);

  return { data, loading, error, metadata, cacheHit, refetch: fetchData };
}

/**
 * Hook for holdings breakdown widget
 * Provides detailed portfolio position analysis with sector/geography breakdowns
 */
export function useHoldingsBreakdown(
  options: UseOptionalParams & { 
    breakdownType?: 'sector' | 'geography' | 'asset_class' | 'all' 
  } = {}
): UseWidgetReturn<HoldingsBreakdownData> {
  const { portfolioId, autoRefetch = true, breakdownType = 'all' } = options;

  const [data, setData] = useState<HoldingsBreakdownData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = `${WIDGET_API_BASE}/portfolio/holdings`;
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        breakdown_type: breakdownType
      };
      
      const response: AxiosResponse<HoldingsBreakdownResponse> = await axios.get(url, { params });
      const widgetResponse = response.data;
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else if (widgetResponse.error) {
        setError(widgetResponse.error.message);
        setData(null);
      } else {
        setError('No holdings data available');
        setData(null);
      }
      
    } catch (err: unknown) {
      console.error('Failed to fetch holdings breakdown widget:', err);
      setError(handleApiError(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [portfolioId, breakdownType]);

  useEffect(() => {
    if (autoRefetch) {
      fetchData();
    }
  }, [fetchData, autoRefetch]);

  return { data, loading, error, metadata, cacheHit, refetch: fetchData };
}

/**
 * Hook for correlation matrix widget
 * Provides asset correlation analysis between portfolio holdings and benchmarks
 */
export function useCorrelationMatrix(
  options: UseOptionalParams & {
    timeWindowDays?: number;
    additionalSymbols?: string[];
    includeHoldings?: boolean;
  } = {}
): UseWidgetReturn<CorrelationMatrixData> {
  const { 
    portfolioId, 
    autoRefetch = true, 
    timeWindowDays = 252,
    additionalSymbols = ['SPY', 'QQQ'],
    includeHoldings = true 
  } = options;

  const [data, setData] = useState<CorrelationMatrixData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = `${WIDGET_API_BASE}/portfolio/correlation`;
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        time_window_days: timeWindowDays,
        additional_symbols: additionalSymbols.join(','),
        include_holdings: includeHoldings
      };
      
      const response: AxiosResponse<CorrelationMatrixResponse> = await axios.get(url, { params });
      const widgetResponse = response.data;
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else if (widgetResponse.error) {
        setError(widgetResponse.error.message);
        setData(null);
      } else {
        setError('No correlation data available');
        setData(null);
      }
      
    } catch (err: unknown) {
      console.error('Failed to fetch correlation matrix widget:', err);
      setError(handleApiError(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [portfolioId, timeWindowDays, additionalSymbols, includeHoldings]);

  useEffect(() => {
    if (autoRefetch) {
      fetchData();
    }
  }, [fetchData, autoRefetch]);

  return { data, loading, error, metadata, cacheHit, refetch: fetchData };
}

/**
 * Hook for Monte Carlo simulation widget
 * Provides portfolio risk modeling and scenario analysis
 */
export function useMonteCarloSimulation(
  options: UseOptionalParams & {
    numSimulations?: number;
    timeHorizonDays?: number;
    confidenceLevel?: number;
    initialValue?: number;
    includeDividends?: boolean;
    estimationMethod?: 'Historical Mean' | 'Exponentially Weighted';
  } = {}
): UseWidgetReturn<MonteCarloData> {
  const { 
    portfolioId, 
    autoRefetch = false, // Default false for expensive calculations
    numSimulations = 1000,
    timeHorizonDays = 252,
    confidenceLevel = 0.95,
    initialValue,
    includeDividends = true,
    estimationMethod = 'Historical Mean'
  } = options;

  const [data, setData] = useState<MonteCarloData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);

  const runSimulation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = `${WIDGET_API_BASE}/portfolio/monte-carlo`;
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        num_simulations: numSimulations,
        time_horizon_days: timeHorizonDays,
        confidence_level: confidenceLevel,
        ...(initialValue && { initial_value: initialValue }),
        include_dividends: includeDividends,
        estimation_method: estimationMethod
      };
      
      const response: AxiosResponse<MonteCarloResponse> = await axios.get(url, { params });
      const widgetResponse = response.data;
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setCacheHit(widgetResponse.metadata.cache_hit || false);
        setError(null);
      } else if (widgetResponse.error) {
        setError(widgetResponse.error.message);
        setData(null);
      } else {
        setError('Monte Carlo simulation failed');
        setData(null);
      }
      
    } catch (err: unknown) {
      console.error('Failed to run Monte Carlo simulation widget:', err);
      setError(handleApiError(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [portfolioId, numSimulations, timeHorizonDays, confidenceLevel, initialValue, includeDividends, estimationMethod]);

  useEffect(() => {
    if (autoRefetch) {
      runSimulation();
    }
  }, [runSimulation, autoRefetch]);

  return { data, loading, error, metadata, cacheHit, refetch: runSimulation };
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Handle API errors with consistent error messages
 */
function handleApiError(err: unknown): string {
  // Handle Axios errors with proper type checking
  if (axios.isAxiosError(err)) {
    if (err.response?.status === 401) {
      return 'Authentication required to access portfolio data';
    } else if (err.response?.status === 403) {
      return 'Insufficient permissions to access portfolio data';
    } else if (err.response?.status === 422) {
      return 'Invalid parameters provided';
    } else if (err.response?.status === 500) {
      return 'Server error - please try again later';
    } else if (err.response?.data?.detail) {
      return err.response.data.detail;
    }
  }
  
  // Handle generic JavaScript errors
  if (err instanceof Error) {
    return err.message;
  }
  
  return 'An unexpected error occurred';
}

/**
 * Bulk fetch multiple widget data
 * Useful for dashboard views that need multiple widgets
 */
export function useAllWidgets(portfolioId?: string) {
  const portfolioSummary = usePortfolioSummary({ portfolioId, autoRefetch: true });
  const holdingsBreakdown = useHoldingsBreakdown({ portfolioId, autoRefetch: true });
  const correlationMatrix = useCorrelationMatrix({ portfolioId, autoRefetch: true });
  
  // Monte Carlo is not auto-fetched due to computational cost
  const monteCarloSimulation = useMonteCarloSimulation({ portfolioId, autoRefetch: false });

  const isLoading = portfolioSummary.loading || holdingsBreakdown.loading || correlationMatrix.loading;
  const hasError = portfolioSummary.error || holdingsBreakdown.error || correlationMatrix.error;

  const refetchAll = useCallback(async () => {
    await Promise.all([
      portfolioSummary.refetch(),
      holdingsBreakdown.refetch(),
      correlationMatrix.refetch()
    ]);
  }, [portfolioSummary.refetch, holdingsBreakdown.refetch, correlationMatrix.refetch]);

  return {
    portfolioSummary,
    holdingsBreakdown,
    correlationMatrix,
    monteCarloSimulation,
    isLoading,
    hasError,
    refetchAll
  };
}