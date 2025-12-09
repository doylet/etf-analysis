/**
 * HoldingsController - Specific controller for Holdings widget functionality
 * Implements SOLID principles with Single Responsibility and Open/Closed principles
 */
import { BaseWidgetController } from './BaseWidgetController';
import { IDataProvider } from '../interfaces/IDataProvider';
import { Holding, HoldingsConfiguration } from '../../types/widget-types';

export interface HoldingsData {
  holdings: Holding[];
  metadata: {
    totalValue: number;
    totalPositions: number;
    lastUpdated: Date;
    executionTime: number;
  };
}

export interface HoldingsMetrics {
  totalValue: number;
  totalPositions: number;
  averageWeight: number;
  largestPosition: Holding | null;
  diversification: {
    byAssetClass: Record<string, number>;
    topHoldings: Holding[];
  };
}

export class HoldingsController extends BaseWidgetController<HoldingsData, HoldingsConfiguration> {
  
  /**
   * Build query parameters from widget configuration
   */
  protected buildQuery(config: HoldingsConfiguration): Record<string, any> {
    return {
      portfolio_id: config.portfolioId,
      include_metadata: true,
      format: 'detailed',
      sort_by: config.sortBy,
      sort_direction: config.sortDirection,
      max_items: config.maxItems,
      display_mode: config.displayMode
    };
  }
  
  protected async fetchData(): Promise<HoldingsData> {
    try {
      // Build query parameters from configuration
      const queryParams = this.buildQuery(this.configuration);
      
      // Use the portfolio data provider to fetch holdings
      const rawData = await this.dataProvider.fetchData('holdings', queryParams);

      // Transform snake_case API data to camelCase for UI consumption
      const transformedHoldings = this.transformHoldings(rawData.holdings || []);
      
      // Calculate derived metrics
      const metadata = this.calculateMetadata(transformedHoldings);

      const data: HoldingsData = {
        holdings: transformedHoldings,
        metadata
      };

      this.logger?.debug('Holdings data fetched and transformed', {
        holdingsCount: transformedHoldings.length,
        totalValue: metadata.totalValue,
        executionTime: metadata.executionTime
      });

      return data;
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      this.logger?.error('Failed to fetch holdings data', error instanceof Error ? error : undefined);
      throw new Error(`Holdings fetch failed: ${errorMessage}`);
    }
  }

  /**
   * Transform snake_case API fields to camelCase UI fields
   * This handles the legacy field mapping requirement
   */
  private transformHoldings(rawHoldings: any[]): Holding[] {
    return rawHoldings.map((holding) => ({
      symbol: holding.symbol || '',
      name: holding.name || '',
      assetClass: holding.asset_class || '', // snake_case → camelCase
      quantity: Number(holding.quantity || 0),
      weight: Number(holding.weight || 0),
      marketValue: Number(holding.market_value || 0), // snake_case → camelCase
      currentPrice: Number(holding.current_price || 0), // snake_case → camelCase
      // Additional fields for comprehensive data model
      dayChange: Number(holding.day_change || 0),
      dayChangePercent: Number(holding.day_change_percent || 0),
      totalReturn: Number(holding.total_return || 0),
      totalReturnPercent: Number(holding.total_return_percent || 0)
    }));
  }

  /**
   * Calculate metadata and derived metrics from holdings
   */
  private calculateMetadata(holdings: Holding[]): HoldingsData['metadata'] {
    const totalValue = holdings.reduce((sum, holding) => sum + holding.marketValue, 0);
    const totalPositions = holdings.length;
    
    return {
      totalValue,
      totalPositions,
      lastUpdated: new Date(),
      executionTime: Date.now() - this.lastFetchStart
    };
  }

  /**
   * Calculate comprehensive metrics for analytics
   */
  public calculateMetrics(): HoldingsMetrics {
    if (!this._data) {
      throw new Error('No holdings data available for metrics calculation');
    }

    const { holdings } = this._data;
    const totalValue = this._data.metadata.totalValue;
    const totalPositions = this._data.metadata.totalPositions;
    
    // Calculate average weight
    const averageWeight = holdings.length > 0 
      ? holdings.reduce((sum, h) => sum + h.weight, 0) / holdings.length 
      : 0;

    // Find largest position by market value
    const largestPosition = holdings.reduce((largest, current) => 
      (current.marketValue > (largest?.marketValue || 0)) ? current : largest, 
      null as Holding | null
    );

    // Diversification by asset class
    const byAssetClass = holdings.reduce((acc, holding) => {
      const assetClass = holding.assetClass || 'Unknown';
      acc[assetClass] = (acc[assetClass] || 0) + holding.marketValue;
      return acc;
    }, {} as Record<string, number>);

    // Top 10 holdings by market value
    const topHoldings = holdings
      .sort((a, b) => b.marketValue - a.marketValue)
      .slice(0, 10);

    return {
      totalValue,
      totalPositions,
      averageWeight,
      largestPosition,
      diversification: {
        byAssetClass,
        topHoldings
      }
    };
  }

  /**
   * Filter holdings by asset class
   */
  public filterByAssetClass(assetClass: string): Holding[] {
    if (!this._data) return [];

    return this._data.holdings.filter(
      holding => holding.assetClass?.toLowerCase() === assetClass.toLowerCase()
    );
  }

  /**
   * Search holdings by symbol or name
   */
  public searchHoldings(query: string): Holding[] {
    if (!this._data) return [];
    
    const lowerQuery = query.toLowerCase();
    return this._data.holdings.filter(holding => 
      holding.symbol?.toLowerCase().includes(lowerQuery) ||
      holding.name?.toLowerCase().includes(lowerQuery)
    );
  }

  /**
   * Get holdings sorted by specified criteria
   */
  public getSortedHoldings(
    sortBy: keyof Holding = 'marketValue',
    order: 'asc' | 'desc' = 'desc'
  ): Holding[] {
    if (!this._data) return [];
    
    const holdings = [...this._data.holdings];
    
    holdings.sort((a, b) => {
      const aVal = a[sortBy] || 0;
      const bVal = b[sortBy] || 0;
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return order === 'asc' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      
      const aNum = Number(aVal);
      const bNum = Number(bVal);
      
      return order === 'asc' ? aNum - bNum : bNum - aNum;
    });
    
    return holdings;
  }

  /**
   * Override configuration validation for Holdings-specific rules
   */
  protected validateConfiguration(config: HoldingsConfiguration): boolean {
    if (!super.validateConfiguration(config)) return false;
    
    // Holdings-specific validation
    if (config.portfolioId && typeof config.portfolioId !== 'string') {
      this.logger?.error('Invalid portfolioId configuration', undefined, { portfolioId: config.portfolioId });
      return false;
    }
    
    if (config.displayMode && !['list', 'table', 'percentage'].includes(config.displayMode)) {
      this.logger?.error('Invalid displayMode configuration', undefined, { displayMode: config.displayMode });
      return false;
    }
    
    if (config.sortBy && !['symbol', 'marketValue', 'weight', 'assetClass'].includes(config.sortBy)) {
      this.logger?.error('Invalid sortBy configuration', undefined, { sortBy: config.sortBy });
      return false;
    }
    
    return true;
  }

  /**
   * Track last fetch start time for execution timing
   */
  private lastFetchStart = Date.now();
}