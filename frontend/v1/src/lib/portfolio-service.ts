/**
 * Portfolio API Service
 * 
 * API calls for portfolio data from the FastAPI backend.
 */

import apiClient from './api-client';

export interface PortfolioSummary {
  total_value: number;
  total_return: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
  positions: number;
  cash: number;
  allocated_cash: number;
}

export interface PortfolioHolding {
  symbol: string;
  name: string;
  quantity: number;
  current_price: number;
  market_value: number;
  cost_basis: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  weight: number;
  sector?: string;
}

export interface PortfolioPerformance {
  dates: string[];
  values: number[];
  returns: number[];
  benchmark?: {
    dates: string[];
    values: number[];
    returns: number[];
  };
}

class PortfolioService {
  /**
   * Get portfolio summary
   */
  async getSummary(): Promise<PortfolioSummary> {
    const response = await apiClient.get<PortfolioSummary>('/api/portfolio/summary');
    return response.data;
  }

  /**
   * Get historical performance data
   */
  async getPerformance(period: string = '1Y'): Promise<PortfolioPerformance> {
    const response = await apiClient.get<PortfolioPerformance>(`/api/portfolio/performance?period=${period}`);
    return response.data;
  }
}

// Export singleton instance
const portfolioService = new PortfolioService();
export default portfolioService;