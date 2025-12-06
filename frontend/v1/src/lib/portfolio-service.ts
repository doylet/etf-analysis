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
  holdings?: BackendHolding[]; // Add holdings to the interface
}

export interface BackendHolding {
  symbol: string;
  name: string;
  type: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  current_value: number;
  cost_basis: number;
  unrealized_gain_loss: number;
  unrealized_gain_loss_pct: number;
  weight_pct: number;
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

// Backend API response interface (different from frontend interface)
interface BackendPortfolioSummary {
  total_value: number;
  total_cost_basis: number;
  total_unrealized_gain_loss: number;
  total_unrealized_gain_loss_pct: number;
  num_holdings: number;
  holdings: BackendHolding[];
  last_updated: string;
}

class PortfolioService {
  /**
   * Get portfolio summary
   */
  async getSummary(): Promise<PortfolioSummary> {
    const response = await apiClient.get<BackendPortfolioSummary>('/api/portfolio/summary');
    const backendData = response.data;
    
    // Transform backend data to frontend interface
    const transformedData: PortfolioSummary = {
      total_value: backendData.total_value,
      total_return: backendData.total_unrealized_gain_loss,
      total_return_percent: backendData.total_unrealized_gain_loss_pct,
      day_change: 0, // Not provided by backend yet
      day_change_percent: 0, // Not provided by backend yet
      positions: backendData.num_holdings,
      cash: 0, // Not provided by backend yet
      allocated_cash: 0, // Not provided by backend yet
      holdings: backendData.holdings, // Pass through holdings data
    };
    
    return transformedData;
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