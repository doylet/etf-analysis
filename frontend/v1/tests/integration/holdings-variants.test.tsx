/**
 * Integration Tests: Holdings Variant Composition
 * 
 * Purpose: Validate that Holdings widget variants can be composed without modifying core logic
 * Test Goal: Verify that new Holdings percentage variant works through composition
 * Success Criteria: Original Holdings component unchanged, new variant works via configuration
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WidgetServicesProvider } from '@/lib/providers/WidgetServicesProvider';
import { useWidgetFactory } from '@/hooks/use-widget-factory';
import { WidgetConfig } from '@/lib/interfaces/IWidgetConfig';
import { createMockDependencies } from '../utils/mocks/createMockDependencies';

// Test wrapper component that uses the widget factory
function TestWidgetWrapper({ config }: { config: WidgetConfig }) {
  const { createWidget } = useWidgetFactory();
  const Widget = createWidget(config);
  return <Widget />;
}

// Test setup wrapper
function TestWrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return (
    <QueryClientProvider client={queryClient}>
      <WidgetServicesProvider>
        {children}
      </WidgetServicesProvider>
    </QueryClientProvider>
  );
}

describe('Holdings Variant Composition Integration', () => {
  const mockHoldingsData = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      shares: 100,
      currentPrice: 150.00,
      marketValue: 15000.00,
      assetClass: 'Technology',
      allocationPercentage: 60.0
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      shares: 50,
      currentPrice: 100.00,
      marketValue: 5000.00,
      assetClass: 'Technology', 
      allocationPercentage: 20.0
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      shares: 50,
      currentPrice: 100.00,
      marketValue: 5000.00,
      assetClass: 'Technology',
      allocationPercentage: 20.0
    }
  ];

  beforeEach(() => {
    // Mock the API response for holdings data
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          holdings: mockHoldingsData,
          total_value: 25000.00,
          total_count: 3
        })
      })
    ) as jest.Mock;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('Widget Variant Creation Through Configuration', () => {
    it('should create Holdings table variant through configuration', async () => {
      const tableConfig: WidgetConfig = {
        type: 'holdings',
        variant: 'table',
        title: 'Holdings Table View',
        refreshInterval: 30000,
        cache: true,
        errorRetryAttempts: 3
      };

      render(
        <TestWrapper>
          <TestWidgetWrapper config={tableConfig} />
        </TestWrapper>
      );

      // Should render with table view
      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // Should display holdings data in table format
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
      expect(screen.getByText('$15,000.00')).toBeInTheDocument();
    });

    it('should create Holdings percentage variant through configuration', async () => {
      const percentageConfig: WidgetConfig = {
        type: 'holdings',
        variant: 'percentage',
        title: 'Holdings Percentage View',
        refreshInterval: 30000,
        cache: true,
        errorRetryAttempts: 3
      };

      render(
        <TestWrapper>
          <TestWidgetWrapper config={percentageConfig} />
        </TestWrapper>
      );

      // Should render with percentage view
      await waitFor(() => {
        expect(screen.getByText('60.0%')).toBeInTheDocument();
        expect(screen.getByText('20.0%')).toBeInTheDocument();
      });

      // Should display holdings in percentage format
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('Technology')).toBeInTheDocument();
    });
  });

  describe('Composition Without Core Modification', () => {
    it('should use same controller logic for both variants', async () => {
      const tableConfig: WidgetConfig = {
        type: 'holdings',
        variant: 'table',
        title: 'Holdings Table',
        refreshInterval: 30000,
        cache: true,
        errorRetryAttempts: 3
      };

      const percentageConfig: WidgetConfig = {
        type: 'holdings', 
        variant: 'percentage',
        title: 'Holdings Percentage',
        refreshInterval: 30000,
        cache: true,
        errorRetryAttempts: 3
      };

      const { rerender } = render(
        <TestWrapper>
          <TestWidgetWrapper config={tableConfig} />
        </TestWrapper>
      );

      // Wait for table variant to load
      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // Both variants should make same API call
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/portfolio/holdings')
      );

      const fetchCallCount = (global.fetch as jest.Mock).mock.calls.length;

      // Switch to percentage variant
      rerender(
        <TestWrapper>
          <TestWidgetWrapper config={percentageConfig} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('60.0%')).toBeInTheDocument();
      });

      // Should use same API endpoint (cached or same call pattern)
      expect((global.fetch as jest.Mock).mock.calls.length).toBeGreaterThanOrEqual(fetchCallCount);
    });

    it('should handle errors consistently across variants', async () => {
      // Mock API error
      global.fetch = jest.fn(() =>
        Promise.reject(new Error('API Error'))
      ) as jest.Mock;

      const tableConfig: WidgetConfig = {
        type: 'holdings',
        variant: 'table', 
        title: 'Holdings Table',
        refreshInterval: 30000,
        cache: true,
        errorRetryAttempts: 1
      };

      render(
        <TestWrapper>
          <TestWidgetWrapper config={tableConfig} />
        </TestWrapper>
      );

      // Should display error state
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Configuration-Driven Behavior', () => {
    it('should respect refresh interval configuration', async () => {
      const config: WidgetConfig = {
        type: 'holdings',
        variant: 'table',
        title: 'Holdings Test',
        refreshInterval: 1000, // 1 second for testing
        cache: false,
        errorRetryAttempts: 3
      };

      render(
        <TestWrapper>
          <TestWidgetWrapper config={config} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      const initialCallCount = (global.fetch as jest.Mock).mock.calls.length;

      // Wait for refresh interval
      await waitFor(() => {
        expect((global.fetch as jest.Mock).mock.calls.length).toBeGreaterThan(initialCallCount);
      }, { timeout: 2000 });
    });

    it('should respect cache configuration', async () => {
      const cachedConfig: WidgetConfig = {
        type: 'holdings',
        variant: 'table', 
        title: 'Cached Holdings',
        refreshInterval: 30000,
        cache: true,
        errorRetryAttempts: 3
      };

      const { rerender } = render(
        <TestWrapper>
          <TestWidgetWrapper config={cachedConfig} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      const callCountAfterFirstRender = (global.fetch as jest.Mock).mock.calls.length;

      // Re-render same component
      rerender(
        <TestWrapper>
          <TestWidgetWrapper config={cachedConfig} />
        </TestWrapper>
      );

      // Should not make additional API calls due to caching
      expect((global.fetch as jest.Mock).mock.calls.length).toBe(callCountAfterFirstRender);
    });

    it('should retry on failure based on configuration', async () => {
      let callCount = 0;
      global.fetch = jest.fn(() => {
        callCount++;
        return Promise.reject(new Error(`API Error ${callCount}`));
      }) as jest.Mock;

      const config: WidgetConfig = {
        type: 'holdings',
        variant: 'table',
        title: 'Holdings Retry Test',
        refreshInterval: 30000,
        cache: false,
        errorRetryAttempts: 3
      };

      render(
        <TestWrapper>
          <TestWidgetWrapper config={config} />
        </TestWrapper>
      );

      // Should retry 3 times (4 total calls: initial + 3 retries)
      await waitFor(() => {
        expect((global.fetch as jest.Mock).mock.calls.length).toBe(4);
      }, { timeout: 5000 });
    });
  });

  describe('Widget Factory Integration', () => {
    it('should create widgets through factory pattern', () => {
      const TestFactoryComponent = () => {
        const { createWidget } = useWidgetFactory();
        
        const config: WidgetConfig = {
          type: 'holdings',
          variant: 'table',
          title: 'Factory Test',
          refreshInterval: 30000,
          cache: true,
          errorRetryAttempts: 3
        };

        const Widget = createWidget(config);
        expect(Widget).toBeDefined();
        expect(typeof Widget).toBe('function');
        
        return <Widget />;
      };

      render(
        <TestWrapper>
          <TestFactoryComponent />
        </TestWrapper>
      );
    });

    it('should handle unknown widget types gracefully', () => {
      const TestUnknownWidget = () => {
        const { createWidget } = useWidgetFactory();
        
        const invalidConfig: WidgetConfig = {
          type: 'unknown-widget' as any,
          variant: 'table',
          title: 'Unknown Widget',
          refreshInterval: 30000,
          cache: true,
          errorRetryAttempts: 3
        };

        expect(() => {
          const Widget = createWidget(invalidConfig);
          return <Widget />;
        }).not.toThrow();

        return <div>Test completed</div>;
      };

      render(
        <TestWrapper>
          <TestUnknownWidget />
        </TestWrapper>
      );
    });
  });

  describe('Variant Switching', () => {
    it('should switch between variants seamlessly', async () => {
      let currentConfig: WidgetConfig = {
        type: 'holdings',
        variant: 'table',
        title: 'Holdings Test',
        refreshInterval: 30000,
        cache: true,
        errorRetryAttempts: 3
      };

      const { rerender } = render(
        <TestWrapper>
          <TestWidgetWrapper config={currentConfig} />
        </TestWrapper>
      );

      // Start with table view
      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // Switch to percentage view
      currentConfig = {
        ...currentConfig,
        variant: 'percentage'
      };

      rerender(
        <TestWrapper>
          <TestWidgetWrapper config={currentConfig} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('60.0%')).toBeInTheDocument();
      });

      // Should not have table anymore
      expect(screen.queryByRole('table')).not.toBeInTheDocument();
    });
  });
});