/**
 * Widget Factory Hook
 * 
 * Purpose: React hook for creating SOLID widgets through factory pattern
 * Responsibilities: Widget instantiation, dependency injection, error handling
 */

import React from 'react';
import { useWidgetServices } from './use-widget-services';
import { WidgetConfig } from '@/lib/interfaces/IWidgetConfig';
import { IWidgetController } from '@/lib/interfaces/IWidgetController';
import { HoldingsViewModel, PortfolioSummaryViewModel } from '@/lib/interfaces/IViewModels';
import { HoldingsController, HoldingsData } from '@/lib/controllers/HoldingsController';
import { PortfolioSummaryController, PortfolioSummaryData } from '@/lib/controllers/PortfolioSummaryController';
import { PortfolioDataProvider } from '@/lib/providers/PortfolioDataProvider';
import { MarketDataProvider } from '@/lib/providers/MarketDataProvider';
import { IWidgetConfiguration } from '@/lib/interfaces/IWidgetConfiguration';
import { PortfolioSummaryConfig } from '@/lib/controllers/PortfolioSummaryController';
import { HoldingsConfiguration } from '@/types/widget-types';
import { WidgetType } from '@/lib/interfaces/IWidgetConfiguration';

/**
 * Transform HoldingsData to HoldingsViewModel
 */
function transformHoldingsData(data: HoldingsData | null, controller: IWidgetController<HoldingsData, HoldingsConfiguration>): HoldingsViewModel | null {
  if (!data) return null;

  return {
    holdings: data.holdings.map(holding => ({
      symbol: holding.symbol,
      name: holding.name,
      assetClass: holding.assetClass,
      quantity: holding.quantity,
      weight: holding.weight,
      marketValue: new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD' 
      }).format(holding.marketValue),
      currentPrice: new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD' 
      }).format(holding.currentPrice || 0),
      allocationPercentage: ((holding.weight || 0) * 100).toFixed(2),
      dayChange: new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD',
        signDisplay: 'always' 
      }).format(holding.dayChange || 0),
      dayChangePercent: `${(holding.dayChangePercent || 0) >= 0 ? '+' : ''}${(holding.dayChangePercent || 0).toFixed(2)}%`,
      totalReturn: new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD',
        signDisplay: 'always' 
      }).format(holding.totalReturn || 0),
      totalReturnPercent: `${(holding.totalReturnPercent || 0) >= 0 ? '+' : ''}${(holding.totalReturnPercent || 0).toFixed(2)}%`,
    })),
    metadata: {
      totalValue: new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD' 
      }).format(data.metadata.totalValue),
      totalPositions: data.metadata.totalPositions,
      lastUpdated: data.metadata.lastUpdated.toLocaleString(),
      executionTime: data.metadata.executionTime,
    },
    refreshData: () => controller.refresh(true),
    toggleView: () => {}, // Placeholder for view toggling
    isLoading: controller.isLoading,
    error: controller.error?.message || null,
  };
}

/**
 * Transform PortfolioSummaryData to PortfolioSummaryViewModel
 */
function transformPortfolioSummaryData(
  data: PortfolioSummaryData | null, 
  controller: IWidgetController<PortfolioSummaryData, PortfolioSummaryConfig>
): PortfolioSummaryViewModel | null {
  if (!data) return null;

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  
  const formatPercent = (value: number) => 
    `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;

  return {
    totalValue: formatCurrency(data.total_value),
    totalReturn: formatCurrency(data.total_return),
    totalReturnPercent: formatPercent(data.total_return_percent),
    dayChange: formatCurrency(data.day_change),
    dayChangePercent: formatPercent(data.day_change_percent),
    positionsCount: data.positions.toString(),
    allocatedCash: formatCurrency(data.allocated_cash),
    lastUpdated: new Date(data.last_updated).toLocaleString(),
    marketStatus: data.market_status,
    showPercentages: true,
    showCashAllocation: true,
    showMarketStatus: true,
    totalReturnTrend: data.total_return_percent > 0 ? 'positive' : 
                     data.total_return_percent < 0 ? 'negative' : 'neutral',
    dayChangeTrend: data.day_change_percent > 0 ? 'positive' : 
                    data.day_change_percent < 0 ? 'negative' : 'neutral',
    refreshData: () => controller.refresh(true),
    togglePercentageView: () => {}, // Placeholder
    isLoading: controller.isLoading,
    error: controller.error?.message || null,
  };
}

/**
 * Hook for creating widgets using the factory pattern
 */
export function useWidgetFactory() {
  const services = useWidgetServices();

  /**
   * Create a widget component based on configuration
   */
  const createWidget = (config: WidgetConfig): React.ComponentType => {
    switch (config.type) {
      case 'holdings':
        return function HoldingsWidget() {
          const dataProvider = new PortfolioDataProvider(
            'holdings-portfolio-provider',
            services.logger,
            undefined // cacheService not available in services
          );

          // Convert HoldingsWidgetConfig to HoldingsConfiguration
          const holdingsConfig: HoldingsConfiguration = {
            ...config,
            id: `holdings-${Date.now()}`,
            type: WidgetType.HOLDINGS,
            portfolioId: (config as any).portfolioId || 'default',
            displayMode: ((config as any).variant as 'table' | 'percentage' === 'table') ? 'table' : 'percentage',
            sortBy: (config as any).sortBy || 'weight',
            sortDirection: (config as any).sortOrder || 'desc'
          };

          const controller = new HoldingsController(
            `holdings-${Date.now()}`, // id
            'holdings', // type
            holdingsConfig, // configuration
            dataProvider, // dataProvider
            services.logger, // logger
            services.eventBus // eventBus
          );

          const { viewModel, loading, error } = useControllerViewModel(
            controller,
            transformHoldingsData
          );

          if (loading) {
            return <div className="p-4 text-center">Loading holdings...</div>;
          }

          if (error) {
            return (
              <div className="p-4 text-center text-red-600">
                Error loading holdings: {error}
              </div>
            );
          }

          if (!viewModel) {
            return <div className="p-4 text-center text-gray-500">No holdings data</div>;
          }

          // Render based on variant
          if (config.variant === 'percentage') {
            return renderHoldingsPercentageView(viewModel);
          } else {
            return renderHoldingsTableView(viewModel);
          }
        };

      case 'portfolio-summary':
        return function PortfolioSummaryWidget() {
          const dataProvider = new MarketDataProvider(
            'portfolio-summary-market-provider',
            services.logger,
            undefined, // cacheService not available in services
            undefined  // configService not available in services
          );

          const controller = new PortfolioSummaryController(
            dataProvider, // marketDataProvider
            config as PortfolioSummaryConfig, // config
            services.logger, // logger
            services.eventBus, // eventBus
            undefined, // cacheService not available in services
            undefined  // configService not available in services
          );

          const { viewModel, loading, error } = useControllerViewModel(
            controller,
            transformPortfolioSummaryData
          );

          if (loading) {
            return <div className="p-4 text-center">Loading portfolio summary...</div>;
          }

          if (error) {
            return (
              <div className="p-4 text-center text-red-600">
                Error loading portfolio: {error}
              </div>
            );
          }

          if (!viewModel) {
            return <div className="p-4 text-center text-gray-500">No portfolio data</div>;
          }

          return renderPortfolioSummaryView(viewModel);
        };

      default:
        return function UnknownWidget() {
          return (
            <div className="p-4 text-center text-gray-500">
              Unknown widget type: {config.type}
            </div>
          );
        };
    }
  };

  return { createWidget };
}

/**
 * Hook to manage controller lifecycle and get view model
 */
function useControllerViewModel<TData = unknown, TConfig = unknown, TViewModel = unknown>(
  controller: IWidgetController<TData, TConfig>,
  transformToViewModel: (data: TData | null, controller: IWidgetController<TData, TConfig>) => TViewModel | null
): {
  viewModel: TViewModel | null;
  loading: boolean;
  error: string | null;
} {
  const [viewModel, setViewModel] = React.useState<TViewModel | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;

    const initializeController = async () => {
      try {
        setLoading(true);
        setError(null);

        // Initialize with current configuration
        await controller.initialize(controller.configuration);
        
        if (mounted) {
          // Subscribe to data changes
          const unsubscribe = controller.subscribe((data: TData | null) => {
            if (mounted) {
              const vm = transformToViewModel(data, controller);
              setViewModel(vm);
              setLoading(controller.isLoading);
              setError(controller.error?.message || null);
            }
          });

          return unsubscribe;
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Unknown error');
          setLoading(false);
        }
      }
    };

    const unsubscribePromise = initializeController();

    return () => {
      mounted = false;
      unsubscribePromise.then(unsubscribe => unsubscribe?.());
      controller.dispose();
    };
  }, [controller, transformToViewModel]);

  return { viewModel, loading, error };
}

/**
 * Render Holdings in table format
 */
function renderHoldingsTableView(viewModel: HoldingsViewModel): React.JSX.Element {
  return (
    <div className="p-3">
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h3 className="text-sm font-semibold">Holdings</h3>
          {viewModel.refreshData && (
            <button 
              onClick={viewModel.refreshData}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Refresh
            </button>
          )}
        </div>
        
        {viewModel.holdings && viewModel.holdings.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-1">Symbol</th>
                  <th className="text-left p-1">Name</th>
                  <th className="text-right p-1">Shares</th>
                  <th className="text-right p-1">Price</th>
                  <th className="text-right p-1">Value</th>
                  <th className="text-right p-1">Weight</th>
                </tr>
              </thead>
              <tbody>
                {viewModel.holdings.map((holding, index: number) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="p-1 font-medium">{holding.symbol}</td>
                    <td className="p-1 truncate max-w-[100px]" title={holding.name}>
                      {holding.name}
                    </td>
                    <td className="p-1 text-right">{holding.quantity}</td>
                    <td className="p-1 text-right">{holding.currentPrice}</td>
                    <td className="p-1 text-right">{holding.marketValue}</td>
                    <td className="p-1 text-right">{holding.allocationPercentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500">No holdings data available</div>
        )}
      </div>
    </div>
  );
}

/**
 * Render Holdings in percentage format
 */
function renderHoldingsPercentageView(viewModel: HoldingsViewModel): React.JSX.Element {
  return (
    <div className="p-3">
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h3 className="text-sm font-semibold">Holdings %</h3>
          {viewModel.refreshData && (
            <button 
              onClick={viewModel.refreshData}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Refresh
            </button>
          )}
        </div>
        
        {viewModel.holdings && viewModel.holdings.length > 0 ? (
          <div className="space-y-2">
            {viewModel.holdings.map((holding, index: number) => (
              <div key={index} className="flex justify-between items-center">
                <div className="flex-1">
                  <div className="text-xs font-medium">{holding.symbol}</div>
                  <div className="text-xs text-gray-600 truncate">{holding.assetClass}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold">{holding.allocationPercentage}%</div>
                  <div className="text-xs text-gray-600">{holding.marketValue}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500">No holdings data available</div>
        )}
      </div>
    </div>
  );
}

/**
 * Render Portfolio Summary view
 */
function renderPortfolioSummaryView(viewModel: PortfolioSummaryViewModel): React.JSX.Element {
  return (
    <div className="p-3">
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h3 className="text-sm font-semibold">Portfolio Summary</h3>
          {viewModel.refreshData && (
            <button 
              onClick={viewModel.refreshData}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Refresh
            </button>
          )}
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          <div className="text-center p-2 bg-gray-50 rounded">
            <div className="text-lg font-bold">{viewModel.totalValue}</div>
            <div className="text-xs text-gray-600">Total Value</div>
          </div>
          
          <div className="text-center p-2 bg-gray-50 rounded">
            <div className={`text-lg font-bold ${
              viewModel.totalReturnTrend === 'positive' ? 'text-green-600' : 
              viewModel.totalReturnTrend === 'negative' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {viewModel.totalReturn}
            </div>
            <div className="text-xs text-gray-600">Total Return</div>
          </div>
          
          <div className="text-center p-2 bg-gray-50 rounded">
            <div className={`text-lg font-bold ${
              viewModel.dayChangeTrend === 'positive' ? 'text-green-600' : 
              viewModel.dayChangeTrend === 'negative' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {viewModel.dayChange}
            </div>
            <div className="text-xs text-gray-600">Day Change</div>
          </div>
          
          <div className="text-center p-2 bg-gray-50 rounded">
            <div className="text-lg font-bold">{viewModel.positionsCount}</div>
            <div className="text-xs text-gray-600">Positions</div>
          </div>
        </div>
        
        {viewModel.showMarketStatus && (
          <div className="text-center text-xs text-gray-600">
            {viewModel.marketStatus} • Last updated: {viewModel.lastUpdated}
          </div>
        )}
      </div>
    </div>
  );
}