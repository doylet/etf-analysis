import { useState, useEffect, useCallback } from 'react';
import portfolioService, { PortfolioSummary } from '@/lib/portfolio-service';

export interface UsePortfolioSummaryReturn {
  summary: PortfolioSummary | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for fetching and managing portfolio summary data
 * Follows SRP by handling only data fetching concerns
 * Follows DIP by allowing service injection (could be extended)
 */
export function usePortfolioSummary(): UsePortfolioSummaryReturn {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await portfolioService.getSummary();
      setSummary(data);
    } catch (err) {
      console.error('Failed to fetch portfolio summary:', err);
      setError('Failed to load portfolio data');
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  return {
    summary,
    loading,
    error,
    refetch: fetchSummary,
  };
}