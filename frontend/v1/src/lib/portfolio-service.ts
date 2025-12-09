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
   * TODO: Replace with actual backend endpoint when available
   */
  async getPerformance(period: string = '1Y'): Promise<PortfolioPerformance> {
    try {
      const response = await apiClient.get<PortfolioPerformance>(`/api/portfolio/performance?period=${period}`);
      return response.data;
    } catch (error: unknown) {
      // Check if it's a 404 error (endpoint doesn't exist) - use fallback data
      if (error && typeof error === 'object' && 'response' in error && 
          error.response && typeof error.response === 'object' && 'status' in error.response && 
          error.response.status === 404) {
        console.warn('Performance endpoint not available, using fallback data');
        
        // Generate realistic mock performance data based on current portfolio
        try {
          const summary = await this.getSummary();
          const mockPerformance = this.generateMockPerformanceData(period, summary);
          return mockPerformance;
        } catch (summaryError) {
          // If we can't get summary data either, return basic mock data
          return this.generateBasicMockPerformanceData(period);
        }
      }
      
      // For other errors, re-throw
      throw error;
    }
  }

  /**
   * Generate realistic mock performance data
   * This will be removed once the actual backend endpoint is implemented
   */
  private generateMockPerformanceData(period: string, summary: PortfolioSummary): PortfolioPerformance {
    const now = new Date();
    const periodDays = {
      '1D': 1,
      '7D': 7,
      '30D': 30,
      '90D': 90,
      '1Y': 365,
      '5Y': 1825,
    }[period] || 365;

    const dataPoints = Math.min(periodDays, 100); // Limit data points for performance
    const dates: string[] = [];
    const values: number[] = [];
    const returns: number[] = [];
    
    const currentValue = summary.total_value;
    const startValue = currentValue * (1 - (summary.total_return_percent / 100));
    
    for (let i = dataPoints - 1; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      dates.push(date.toISOString().split('T')[0]);
      
      // Generate realistic progression from start to current value
      const progress = (dataPoints - 1 - i) / (dataPoints - 1);
      const baseValue = startValue + (currentValue - startValue) * progress;
      
      // Add some realistic volatility (±2% daily variation)
      const volatility = (Math.random() - 0.5) * 0.04;
      const dailyValue = baseValue * (1 + volatility);
      
      values.push(Math.max(dailyValue, 0)); // Ensure no negative values
      
      // Calculate daily return percentage
      if (i === dataPoints - 1) {
        returns.push(0); // First day has no return
      } else {
        const prevValue = values[values.length - 2] || startValue;
        const dailyReturn = ((dailyValue - prevValue) / prevValue) * 100;
        returns.push(dailyReturn);
      }
    }
    
    // Ensure the last value matches current portfolio value
    values[values.length - 1] = currentValue;
    
    // Recalculate final return
    const finalReturn = ((currentValue - values[values.length - 2]) / values[values.length - 2]) * 100;
    returns[returns.length - 1] = finalReturn;

    return {
      dates,
      values,
      returns,
      // Optional benchmark data (could be S&P 500 or similar)
      benchmark: {
        dates,
        values: values.map(v => v * 0.95), // Mock benchmark performing slightly worse
        returns: returns.map(r => r * 0.9), // Mock benchmark returns slightly lower
      }
    };
  }

  /**
   * Generate basic mock performance data when summary data is unavailable
   */
  private generateBasicMockPerformanceData(period: string): PortfolioPerformance {
    const dataPoints = period === '1D' ? 24 : period === '7D' ? 7 : period === '30D' ? 30 : period === '90D' ? 90 : 365;
    const dates: string[] = [];
    const values: number[] = [];
    const returns: number[] = [];
    
    // Use default values when summary is unavailable
    const baseValue = 100000; // $100k as default
    const currentValue = baseValue * 1.08; // Assume 8% growth
    
    // Generate time series
    for (let i = dataPoints - 1; i >= 0; i--) {
      const date = new Date();
      if (period === '1D') {
        date.setHours(date.getHours() - i);
      } else {
        date.setDate(date.getDate() - i);
      }
      dates.push(date.toISOString());
      
      // Generate realistic progression
      const progress = (dataPoints - 1 - i) / (dataPoints - 1);
      const dailyValue = baseValue + (currentValue - baseValue) * progress;
      
      // Add small volatility
      const volatility = (Math.random() - 0.5) * 0.02;
      const value = dailyValue * (1 + volatility);
      
      values.push(Math.max(value, 0));
      
      // Calculate returns
      if (i === dataPoints - 1) {
        returns.push(0);
      } else {
        const prevValue = values[values.length - 2] || baseValue;
        const dailyReturn = ((value - prevValue) / prevValue) * 100;
        returns.push(dailyReturn);
      }
    }

    return {
      dates,
      values,
      returns,
      benchmark: {
        dates,
        values: values.map(v => v * 0.95),
        returns: returns.map(r => r * 0.9),
      }
    };
  }
}

// Export singleton instance
const portfolioService = new PortfolioService();
export default portfolioService;