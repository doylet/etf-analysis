import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

// Widget API response types
export interface WidgetError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface WidgetMetadata {
  execution_time: string;
  parameters: Record<string, any>;
  widget_description: string;
  cache_hit?: boolean;
  cached_at?: string;
}

export interface WidgetResponse<T = any> {
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

export type PortfolioSummaryResponse = WidgetResponse<PortfolioSummaryData>;

export interface UsePortfolioWidgetReturn {
  data: PortfolioSummaryData | null;
  loading: boolean;
  error: string | null;
  metadata: WidgetMetadata | null;
  cacheHit: boolean;
  refetch: () => Promise<void>;
}

const WIDGET_API_BASE = '/api/widgets';

/**
 * Custom hook for fetching portfolio summary data from the widget API
 * Provides access to portfolio performance metrics through the new widget endpoint
 */
export function usePortfolioSummary(portfolioId?: string): UsePortfolioWidgetReturn {
  const [data, setData] = useState<PortfolioSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);
  const [cacheHit, setCacheHit] = useState(false);

  const fetchPortfolioSummary = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Build URL with optional portfolio ID
      const url = `${WIDGET_API_BASE}/portfolio/summary`;
      const params = portfolioId ? { portfolio_id: portfolioId } : {};
      
      const response = await axios.get<PortfolioSummaryResponse>(url, { params });
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
      
    } catch (err: any) {
      console.error('Failed to fetch portfolio summary widget:', err);
      
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
      
      setData(null);
      setMetadata(null);
    } finally {
      setLoading(false);
    }
  }, [portfolioId]);

  useEffect(() => {
    fetchPortfolioSummary();
  }, [fetchPortfolioSummary]);

  return {
    data,
    loading,
    error,
    metadata,
    cacheHit,
    refetch: fetchPortfolioSummary,
  };
}

// Hook for other widget types - extensible pattern
export function useHoldingsBreakdown(portfolioId?: string, breakdownType?: 'sector' | 'geography' | 'asset_class') {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);

  const fetchHoldingsBreakdown = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = `${WIDGET_API_BASE}/portfolio/holdings`;
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        ...(breakdownType && { breakdown_type: breakdownType })
      };
      
      const response = await axios.get(url, { params });
      const widgetResponse = response.data;
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No data available');
        setData(null);
      }
      
    } catch (err: any) {
      console.error('Failed to fetch holdings breakdown:', err);
      setError(err.response?.data?.detail || 'Failed to load holdings breakdown');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [portfolioId, breakdownType]);

  useEffect(() => {
    fetchHoldingsBreakdown();
  }, [fetchHoldingsBreakdown]);

  return {
    data,
    loading, 
    error,
    metadata,
    refetch: fetchHoldingsBreakdown,
  };
}

export function useCorrelationMatrix(portfolioId?: string, timeWindow?: number) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);

  const fetchCorrelationMatrix = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = `${WIDGET_API_BASE}/portfolio/correlation`;
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        ...(timeWindow && { time_window_days: timeWindow })
      };
      
      const response = await axios.get(url, { params });
      const widgetResponse = response.data;
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'No correlation data available');
        setData(null);
      }
      
    } catch (err: any) {
      console.error('Failed to fetch correlation matrix:', err);
      setError(err.response?.data?.detail || 'Failed to load correlation matrix');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [portfolioId, timeWindow]);

  useEffect(() => {
    fetchCorrelationMatrix();
  }, [fetchCorrelationMatrix]);

  return {
    data,
    loading,
    error,
    metadata,
    refetch: fetchCorrelationMatrix,
  };
}

export function useMonteCarloSimulation(
  portfolioId?: string, 
  simulations?: number, 
  timeHorizonDays?: number
) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<WidgetMetadata | null>(null);

  const runSimulation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = `${WIDGET_API_BASE}/portfolio/monte-carlo`;
      const params = {
        ...(portfolioId && { portfolio_id: portfolioId }),
        ...(simulations && { num_simulations: simulations }),
        ...(timeHorizonDays && { time_horizon_days: timeHorizonDays })
      };
      
      const response = await axios.get(url, { params });
      const widgetResponse = response.data;
      
      if (widgetResponse.success && widgetResponse.data) {
        setData(widgetResponse.data);
        setMetadata(widgetResponse.metadata);
        setError(null);
      } else {
        setError(widgetResponse.error?.message || 'Monte Carlo simulation failed');
        setData(null);
      }
      
    } catch (err: any) {
      console.error('Failed to run Monte Carlo simulation:', err);
      setError(err.response?.data?.detail || 'Failed to run simulation');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [portfolioId, simulations, timeHorizonDays]);

  useEffect(() => {
    runSimulation();
  }, [runSimulation]);

  return {
    data,
    loading,
    error,
    metadata,
    refetch: runSimulation,
  };
}