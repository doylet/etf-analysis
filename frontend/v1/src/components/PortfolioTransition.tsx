'use client';

import { ArrowRightLeft, Calendar, RefreshCw, Target } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface PortfolioTransitionProps {
  portfolioId?: string;
  targetPortfolioId?: string;
}

interface TransitionData {
  current_portfolio: {
    total_value: number;
    holdings: Array<{
      symbol: string;
      shares: number;
      current_value: number;
      percentage: number;
    }>;
  };
  target_portfolio: {
    total_value: number;
    holdings: Array<{
      symbol: string;
      target_shares: number;
      target_value: number;
      target_percentage: number;
    }>;
  };
  transition_plan: {
    total_transactions: number;
    estimated_cost: number;
    estimated_time: string;
    transactions: Array<{
      action: 'buy' | 'sell';
      symbol: string;
      shares: number;
      estimated_price: number;
      total_value: number;
      reason: string;
    }>;
  };
  impact_analysis: {
    tax_implications: number;
    transaction_costs: number;
    market_impact: number;
    tracking_error: number;
  };
}

export default function PortfolioTransition({ 
  portfolioId, 
  targetPortfolioId 
}: PortfolioTransitionProps) {
  // Mock data for now - replace with actual API call
  const loading = false;
  const error = null;
  const data: TransitionData = {
    current_portfolio: {
      total_value: 50000,
      holdings: [
        { symbol: 'AAPL', shares: 100, current_value: 17500, percentage: 35 },
        { symbol: 'MSFT', shares: 75, current_value: 12500, percentage: 25 },
        { symbol: 'GOOGL', shares: 50, current_value: 10000, percentage: 20 },
        { symbol: 'VTI', shares: 40, current_value: 10000, percentage: 20 }
      ]
    },
    target_portfolio: {
      total_value: 50000,
      holdings: [
        { symbol: 'AAPL', target_shares: 75, target_value: 13125, target_percentage: 26.25 },
        { symbol: 'MSFT', target_shares: 85, target_value: 14167, target_percentage: 28.33 },
        { symbol: 'GOOGL', target_shares: 60, target_value: 12000, target_percentage: 24 },
        { symbol: 'VTI', target_shares: 45, target_value: 11250, target_percentage: 22.5 },
        { symbol: 'NVDA', target_shares: 10, target_value: 7000, target_percentage: 14 }
      ]
    },
    transition_plan: {
      total_transactions: 5,
      estimated_cost: 125.50,
      estimated_time: '2-3 business days',
      transactions: [
        { action: 'sell', symbol: 'AAPL', shares: 25, estimated_price: 175, total_value: 4375, reason: 'Reduce overweight position' },
        { action: 'buy', symbol: 'MSFT', shares: 10, estimated_price: 167, total_value: 1670, reason: 'Increase target allocation' },
        { action: 'buy', symbol: 'GOOGL', shares: 10, estimated_price: 200, total_value: 2000, reason: 'Increase target allocation' },
        { action: 'buy', symbol: 'VTI', shares: 5, estimated_price: 250, total_value: 1250, reason: 'Minor rebalancing' },
        { action: 'buy', symbol: 'NVDA', shares: 10, estimated_price: 700, total_value: 7000, reason: 'New position' }
      ]
    },
    impact_analysis: {
      tax_implications: 450.75,
      transaction_costs: 125.50,
      market_impact: 0.02,
      tracking_error: 1.8
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <ArrowRightLeft className="h-5 w-5" />
            <Skeleton className="h-6 w-[200px]" />
          </div>
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-[200px]" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Alert variant="destructive">
        <ArrowRightLeft className="h-4 w-4" />
        <AlertTitle>Portfolio Transition Error</AlertTitle>
        <AlertDescription>
          Unable to load portfolio transition data. Please check your portfolio configuration.
        </AlertDescription>
      </Alert>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <ArrowRightLeft className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">Portfolio Transition</h2>
            </div>
            <p className="text-text-secondary text-sm">
              Transition plan from current to target allocation
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Recalculate
            </Button>
            <Button size="sm">
              <Target className="h-4 w-4 mr-2" />
              Execute Plan
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Transition Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <div className="text-sm text-blue-700">Total Transactions</div>
              <div className="text-2xl font-bold text-blue-800">
                {data.transition_plan.total_transactions}
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Estimated Cost</div>
              <div className="text-2xl font-bold text-text-primary">
                ${data.transition_plan.estimated_cost.toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Estimated Time</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.transition_plan.estimated_time}
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Tax Impact</div>
              <div className="text-2xl font-bold text-financial-negative">
                ${data.impact_analysis.tax_implications.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Transaction Plan */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Transition Plan</h3>
            <div className="space-y-2">
              {data.transition_plan.transactions.map((transaction, index) => (
                <div key={index} className="flex items-center justify-between p-4 border border-border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge 
                      variant={transaction.action === 'buy' ? 'default' : 'destructive'}
                      className="capitalize min-w-[60px] justify-center"
                    >
                      {transaction.action}
                    </Badge>
                    <div>
                      <div className="font-medium text-text-primary">
                        {transaction.symbol} • {transaction.shares} shares
                      </div>
                      <div className="text-sm text-text-tertiary">
                        {transaction.reason}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-text-primary">
                      {formatCurrency(transaction.total_value)}
                    </div>
                    <div className="text-sm text-text-tertiary">
                      @ ${transaction.estimated_price.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Portfolio Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-text-primary mb-3">Current Portfolio</h3>
              <div className="space-y-2">
                {data.current_portfolio.holdings.map((holding) => (
                  <div key={holding.symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <span className="font-medium text-text-primary">{holding.symbol}</span>
                      <div className="text-sm text-text-tertiary">
                        {holding.shares} shares • {holding.percentage}%
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-text-primary">
                        {formatCurrency(holding.current_value)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-medium text-text-primary mb-3">Target Portfolio</h3>
              <div className="space-y-2">
                {data.target_portfolio.holdings.map((holding) => (
                  <div key={holding.symbol} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div>
                      <span className="font-medium text-text-primary">{holding.symbol}</span>
                      <div className="text-sm text-text-tertiary">
                        {holding.target_shares} shares • {holding.target_percentage}%
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-text-primary">
                        {formatCurrency(holding.target_value)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Impact Analysis */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Tax Impact</div>
              <div className="text-lg font-semibold text-financial-negative">
                ${data.impact_analysis.tax_implications.toFixed(2)}
              </div>
            </div>
            <div className="text-center p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Transaction Costs</div>
              <div className="text-lg font-semibold text-text-primary">
                ${data.impact_analysis.transaction_costs.toFixed(2)}
              </div>
            </div>
            <div className="text-center p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Market Impact</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.impact_analysis.market_impact.toFixed(2)}%
              </div>
            </div>
            <div className="text-center p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Tracking Error</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.impact_analysis.tracking_error.toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Execution Notes */}
          <div className="p-4 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg border border-amber-200">
            <h3 className="font-medium text-amber-800 mb-2">
              <Calendar className="h-4 w-4 inline mr-2" />
              Execution Notes
            </h3>
            <div className="space-y-1 text-sm text-amber-700">
              <div>• Execute transactions during market hours for best pricing</div>
              <div>• Consider tax implications before year-end</div>
              <div>• Review market conditions before execution</div>
              <div>• Monitor tracking error during transition period</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}