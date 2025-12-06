/**
 * Portfolio API
 * 
 * API calls for portfolio data and holdings.
 */

import apiClient from './client';

export interface HoldingResponse {
  symbol: string;
  name: string;
  type: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  cost_basis: number;
  current_value: number;
  unrealized_gain_loss: number;
  unrealized_gain_loss_pct: number;
  weight_pct: number;
}

export interface PortfolioSummaryResponse {
  total_value: number;
  total_cost_basis: number;
  total_unrealized_gain_loss: number;
  total_unrealized_gain_loss_pct: number;
  num_holdings: number;
  holdings: HoldingResponse[];
  last_updated: string;
}

class PortfolioAPI {
  /**
   * Get complete portfolio summary with holdings
   */
  async getPortfolioSummary(): Promise<PortfolioSummaryResponse> {
    const response = await apiClient.get<PortfolioSummaryResponse>('/api/portfolio/summary');
    return response.data;
  }

  /**
   * Get holdings list only
   */
  async getHoldings(): Promise<HoldingResponse[]> {
    const response = await apiClient.get<HoldingResponse[]>('/api/portfolio/holdings');
    return response.data;
  }
}

export default new PortfolioAPI();
