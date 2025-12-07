'use client'

import React from 'react'
import { MetricCard } from '@/components/ui/metric-card'
import { FinancialAmount } from '@/components/ui/financial-amount'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card'
import { StatusIndicator } from '@/components/ui/status-indicator'
import { PercentageChange } from '@/components/ui/percentage-change'
import { DataTable } from '@/components/ui/data-table'
import { MetricGroup, PortfolioMetrics, RiskMetrics, CompactMetrics } from '@/components/ui/metric-group'
import { ModeToggle } from '@/components/ui/mode-toggle'
import { LoadingSpinner, LoadingCard, LoadingTable, FinancialDataLoader, LoadingMetricCard } from '@/components/ui/loading-states'
import { ErrorState, NetworkError, DataError, EmptyPortfolio, NoSearchResults } from '@/components/ui/error-states'
import { GridLayout, MetricGrid, ChartGrid } from '@/components/ui/grid-layout'

export default function DesignSystemPage() {
  const [isLoading, setIsLoading] = React.useState(false)
  const [showError, setShowError] = React.useState(false)

  const sampleData = [
    { symbol: 'AAPL', shares: 100, price: 150.25, change: 2.5 },
    { symbol: 'GOOGL', shares: 50, price: 2800.75, change: -1.2 },
    { symbol: 'MSFT', shares: 75, price: 420.50, change: 0.8 },
    { symbol: 'TSLA', shares: 25, price: 850.25, change: -5.3 },
  ]

  const columns = [
    { key: 'symbol', header: 'Symbol', sortable: true },
    { key: 'shares', header: 'Shares', sortable: true, align: 'right' as const },
    { key: 'price', header: 'Price', sortable: true, align: 'right' as const },
    { key: 'change', header: 'Change %', sortable: true, align: 'right' as const },
  ]

  return (
    <div className="min-h-screen bg-background-primary p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Design System Test Page</h1>
            <p className="text-gray-600 mt-2">Professional Data-Focused Design System Components</p>
          </div>
          <div className="flex items-center gap-4">
            <ModeToggle />
          </div>
        </div>

        {/* Color Palette */}
        <Card>
          <CardHeader>
            <CardTitle>Color Palette</CardTitle>
            <CardDescription>Financial semantic colors and professional palette</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="space-y-2">
                <div className="h-16 bg-financial-positive rounded-lg"></div>
                <p className="text-sm font-medium">Financial Positive</p>
                <p className="text-xs text-theme-secondary">Dynamic green</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 bg-financial-negative rounded-lg"></div>
                <p className="text-sm font-medium">Financial Negative</p>
                <p className="text-xs text-theme-secondary">Dynamic red</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 bg-financial-neutral rounded-lg"></div>
                <p className="text-sm font-medium">Financial Neutral</p>
                <p className="text-xs text-theme-secondary">Dynamic gray</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 bg-scheme-primary rounded-lg"></div>
                <p className="text-sm font-medium">Primary Scheme</p>
                <p className="text-xs text-theme-secondary">Dynamic theme</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 bg-warning rounded-lg"></div>
                <p className="text-sm font-medium">Warning Amber</p>
                <p className="text-xs text-gray-500">#d97706</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Typography */}
        <Card>
          <CardHeader>
            <CardTitle>Typography</CardTitle>
            <CardDescription>Financial data optimized typography with tabular numerals</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">Headings</p>
                <h1 className="text-3xl font-bold">Heading 1 - Portfolio Dashboard</h1>
                <h2 className="text-2xl font-semibold">Heading 2 - Performance Analysis</h2>
                <h3 className="text-xl font-medium">Heading 3 - Risk Metrics</h3>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">Financial Numbers (Tabular)</p>
                <div className="space-y-1 tabular-nums">
                  <p className="text-2xl font-bold">$1,234,567.89</p>
                  <p className="text-lg">€987,654.32</p>
                  <p className="text-base">¥123,456.78</p>
                  <p className="text-sm">£98,765.43</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Buttons */}
        <Card>
          <CardHeader>
            <CardTitle>Buttons</CardTitle>
            <CardDescription>Professional button variants with hover animations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="default">Default</Button>
              <Button variant="professional">Professional</Button>
              <Button variant="data-action">Data Action</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="success">Success</Button>
              <Button variant="warning">Warning</Button>
              <Button variant="destructive">Destructive</Button>
            </div>
            <div className="mt-4 space-x-2">
              <Button size="sm">Small</Button>
              <Button size="default">Default</Button>
              <Button size="lg">Large</Button>
              <Button size="xl">Extra Large</Button>
            </div>
          </CardContent>
        </Card>

        {/* Status Indicators */}
        <Card>
          <CardHeader>
            <CardTitle>Status Indicators</CardTitle>
            <CardDescription>Financial status indicators with semantic meaning</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatusIndicator variant="success">Live Data</StatusIndicator>
              <StatusIndicator variant="warning">Delayed</StatusIndicator>
              <StatusIndicator variant="danger">Data Issues</StatusIndicator>
              <StatusIndicator variant="info">Processing</StatusIndicator>
              <StatusIndicator variant="positive">+2.5%</StatusIndicator>
              <StatusIndicator variant="negative">-1.8%</StatusIndicator>
              <StatusIndicator variant="neutral">Unchanged</StatusIndicator>
              <StatusIndicator variant="processing">Market Open</StatusIndicator>
            </div>
          </CardContent>
        </Card>

        {/* Metric Cards */}
        <Card>
          <CardHeader>
            <CardTitle>Metric Cards</CardTitle>
            <CardDescription>Financial metrics with trend-based styling and hover effects</CardDescription>
          </CardHeader>
          <CardContent>
            <MetricGrid>
              <MetricCard
                title="Portfolio Value"
                value={1234567.89}
                change={{ value: 12345.67, type: 'absolute' }}
                trend="positive"
                size="lg"
              />
              <MetricCard
                title="Day Change"
                value={2.47}
                trend="positive"
              />
              <MetricCard
                title="YTD Return"
                value={-1.2}
                trend="negative"
                variant="highlighted"
              />
              <MetricCard
                title="Risk Level"
                value={7.3}
                trend="neutral"
                variant="subtle"
              />
            </MetricGrid>
          </CardContent>
        </Card>

        {/* Financial Amounts & Percentages */}
        <Card>
          <CardHeader>
            <CardTitle>Financial Components</CardTitle>
            <CardDescription>Specialized components for financial data display</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <p className="text-sm font-medium">Financial Amount</p>
                <FinancialAmount amount={1234567.89} showTrend size="lg" />
                <FinancialAmount amount={-9876.54} showTrend />
                <FinancialAmount amount={0} showTrend size="sm" />
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Percentage Change</p>
                <PercentageChange value={5.47} showIcon animate />
                <PercentageChange value={-2.31} showIcon variant="bold" />
                <PercentageChange value={0} variant="compact" />
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Variants</p>
                <PercentageChange value={3.2} variant="badge" />
                <PercentageChange value={-1.5} variant="subtle" showIcon />
                <PercentageChange value={2.8} variant="default" />
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Different Currencies</p>
                <FinancialAmount amount={2500.75} currency="EUR" />
                <FinancialAmount amount={187650} currency="JPY" precision={0} />
                <FinancialAmount amount={1850.25} currency="GBP" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Data Table */}
        <Card>
          <CardHeader>
            <CardTitle>Data Table</CardTitle>
            <CardDescription>Sortable table optimized for financial data</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable
              data={sampleData}
              columns={columns}
              loading={isLoading}
              variant="striped"
              hoverable
            />
            <div className="flex gap-2 mt-4">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setIsLoading(!isLoading)}
              >
                Toggle Loading
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setShowError(!showError)}
              >
                Toggle Error
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Metric Groups */}
        <Card>
          <CardHeader>
            <CardTitle>Metric Groups</CardTitle>
            <CardDescription>Compound components for organizing related metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <PortfolioMetrics columns={3}>
              <MetricCard title="Total Value" value={1000000} />
              <MetricCard title="Cash" value={50000} />
              <MetricCard title="Invested" value={950000} />
            </PortfolioMetrics>

            <RiskMetrics>
              <MetricCard title="Beta" value={1.2} />
              <MetricCard title="Sharpe Ratio" value={0.85} />
              <MetricCard title="Max Drawdown" value={-15.3} trend="negative" />
            </RiskMetrics>

            <CompactMetrics>
              <StatusIndicator variant="success" size="sm">Live</StatusIndicator>
              <PercentageChange value={2.5} variant="compact" />
              <span className="text-sm tabular-nums">Last updated: 2:34 PM</span>
            </CompactMetrics>
          </CardContent>
        </Card>

        {/* Loading States */}
        <Card>
          <CardHeader>
            <CardTitle>Loading States</CardTitle>
            <CardDescription>Professional loading indicators and skeletons</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-medium">Loading Spinners</h4>
                <div className="flex items-center gap-4">
                  <LoadingSpinner size="sm" variant="primary" />
                  <LoadingSpinner size="default" variant="success" />
                  <LoadingSpinner size="lg" variant="warning" />
                </div>
                <FinancialDataLoader />
              </div>
              <div className="space-y-4">
                <h4 className="font-medium">Loading Cards</h4>
                <LoadingMetricCard />
                <LoadingCard rows={2} showFooter />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error States */}
        <Card>
          <CardHeader>
            <CardTitle>Error States</CardTitle>
            <CardDescription>Comprehensive error handling with professional styling</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <NetworkError onRetry={() => console.log('Retry network')} />
                <DataError onRetry={() => console.log('Retry data')} />
              </div>
              <div className="space-y-4">
                <EmptyPortfolio onAddHolding={() => console.log('Add holding')} />
                <NoSearchResults 
                  searchTerm="INVALID" 
                  onClearSearch={() => console.log('Clear search')} 
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Grid Layouts */}
        <Card>
          <CardHeader>
            <CardTitle>Grid Layouts</CardTitle>
            <CardDescription>Responsive grid systems for dashboard organization</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <h4 className="font-medium mb-3">Basic Grid</h4>
                <GridLayout columns={4} gap="sm">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="h-16 bg-scheme-primary-subtle rounded-lg flex items-center justify-center">
                      Item {i + 1}
                    </div>
                  ))}
                </GridLayout>
              </div>
              
              <div>
                <h4 className="font-medium mb-3">Chart Grid</h4>
                <ChartGrid>
                  <div className="h-32 bg-gradient-to-br from-financial-positive-subtle to-financial-positive-light rounded-lg flex items-center justify-center">
                    Chart 1
                  </div>
                  <div className="h-32 bg-gradient-to-br from-scheme-primary-subtle to-scheme-primary-light rounded-lg flex items-center justify-center">
                    Chart 2
                  </div>
                </ChartGrid>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Test Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Interactive Tests</CardTitle>
            <CardDescription>Test various states and interactions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Button onClick={() => console.log('Professional action')}>
                  Test Professional Button
                </Button>
                <Button variant="data-action" onClick={() => console.log('Data action')}>
                  Test Data Action
                </Button>
                <Button variant="success" onClick={() => console.log('Success action')}>
                  Test Success Button
                </Button>
              </div>
              
              <div className="text-sm text-gray-600">
                <p>• Hover over metric cards to see animation effects</p>
                <p>• Click buttons to test hover and active states</p>
                <p>• Switch themes using the controls in the header</p>
                <p>• Test responsive behavior by resizing the window</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}