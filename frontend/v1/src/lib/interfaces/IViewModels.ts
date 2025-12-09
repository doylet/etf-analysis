/**
 * View Model Interfaces
 * 
 * Purpose: Define the data structures that controllers provide to the UI layer
 * These interfaces ensure type safety between the SOLID architecture and React components
 */

export interface HoldingsViewModel {
  holdings: Array<{
    symbol: string;
    name: string;
    assetClass: string;
    quantity: number;
    weight: number;
    marketValue: string; // Formatted currency string
    currentPrice: string; // Formatted currency string
    allocationPercentage: string; // Formatted percentage string
    dayChange: string;
    dayChangePercent: string;
    totalReturn: string;
    totalReturnPercent: string;
  }>;
  metadata: {
    totalValue: string; // Formatted currency
    totalPositions: number;
    lastUpdated: string; // Formatted date
    executionTime: number;
  };
  // Actions
  refreshData: () => Promise<void>;
  toggleView: () => void;
  // UI state
  isLoading: boolean;
  error: string | null;
}

export interface PortfolioSummaryViewModel {
  // Formatted display data
  totalValue: string;
  totalReturn: string;
  totalReturnPercent: string;
  dayChange: string;
  dayChangePercent: string;
  positionsCount: string;
  allocatedCash: string;
  lastUpdated: string;
  marketStatus: string;
  
  // UI state
  showPercentages: boolean;
  showCashAllocation: boolean;
  showMarketStatus: boolean;
  
  // Trend indicators
  totalReturnTrend: 'positive' | 'negative' | 'neutral';
  dayChangeTrend: 'positive' | 'negative' | 'neutral';
  
  // Actions
  refreshData: () => Promise<void>;
  togglePercentageView: () => void;
  
  // Loading and error states
  isLoading: boolean;
  error: string | null;
}