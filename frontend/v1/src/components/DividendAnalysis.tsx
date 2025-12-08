'use client';

import { Calendar, DollarSign, TrendingUp, Percent } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

interface DividendAnalysisProps {
  portfolioId?: string;
  timePeriod?: string;
}

interface DividendData {
  total_dividends: number;
  dividend_yield: number;
  dividend_growth_rate: number;
  payout_ratio: number;
  monthly_dividends: Array<{
    month: string;
    amount: number;
    count: number;
  }>;
  top_dividend_holdings: Array<{
    symbol: string;
    yield: number;
    annual_amount: number;
    percentage: number;
  }>;
  next_ex_dates: Array<{
    symbol: string;
    ex_date: string;
    estimated_amount: number;
  }>;
}

export default function DividendAnalysis({ 
  portfolioId, 
  timePeriod = '1Y'
}: DividendAnalysisProps) {
  // Mock data for now - replace with actual API call
  const loading = false;
  const error = null;
  const data: DividendData = {
    total_dividends: 1250.75,
    dividend_yield: 2.8,
    dividend_growth_rate: 5.2,
    payout_ratio: 65.5,
    monthly_dividends: [
      { month: 'Jan', amount: 105.25, count: 3 },
      { month: 'Feb', amount: 98.50, count: 2 },
      { month: 'Mar', amount: 115.75, count: 4 },
      { month: 'Apr', amount: 102.25, count: 3 },
      { month: 'May', amount: 108.50, count: 3 },
      { month: 'Jun', amount: 95.75, count: 2 }
    ],
    top_dividend_holdings: [
      { symbol: 'AAPL', yield: 0.5, annual_amount: 245.50, percentage: 35.2 },
      { symbol: 'MSFT', yield: 0.7, annual_amount: 189.25, percentage: 28.1 },
      { symbol: 'VTI', yield: 1.8, annual_amount: 156.75, percentage: 22.3 },
      { symbol: 'KO', yield: 3.2, annual_amount: 98.50, percentage: 14.4 }
    ],
    next_ex_dates: [
      { symbol: 'AAPL', ex_date: '2024-02-15', estimated_amount: 23.50 },
      { symbol: 'MSFT', ex_date: '2024-02-20', estimated_amount: 18.75 },
      { symbol: 'KO', ex_date: '2024-03-01', estimated_amount: 25.25 }
    ]
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            <Skeleton className="h-6 w-[200px]" />
          </div>
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-[80px]" />
              ))}
            </div>
            <Skeleton className="h-[200px]" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Alert variant="destructive">
        <DollarSign className="h-4 w-4" />
        <AlertTitle>Dividend Analysis Error</AlertTitle>
        <AlertDescription>
          Unable to load dividend analysis data. Please check your portfolio configuration.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <DollarSign className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold">Dividend Analysis</h2>
        </div>
        <p className="text-text-secondary text-sm">
          Income tracking and dividend metrics • {timePeriod} period
        </p>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
              <div className="text-sm text-green-700">Total Dividends</div>
              <div className="text-2xl font-bold text-green-800">
                ${data.total_dividends.toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Dividend Yield</div>
              <div className="text-2xl font-bold text-text-primary">
                {data.dividend_yield.toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Growth Rate</div>
              <div className="text-2xl font-bold text-financial-positive">
                +{data.dividend_growth_rate.toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Payout Ratio</div>
              <div className="text-2xl font-bold text-text-primary">
                {data.payout_ratio.toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Monthly Distribution */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Monthly Dividend Distribution</h3>
            <div className="grid grid-cols-6 gap-2">
              {data.monthly_dividends.map((month) => (
                <div key={month.month} className="text-center p-3 border border-border rounded-lg">
                  <div className="text-xs text-text-tertiary">{month.month}</div>
                  <div className="text-sm font-semibold text-text-primary">
                    ${month.amount.toFixed(0)}
                  </div>
                  <div className="text-xs text-text-tertiary">{month.count} payments</div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Dividend Holdings */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Top Dividend Holdings</h3>
            <div className="space-y-2">
              {data.top_dividend_holdings.map((holding) => (
                <div key={holding.symbol} className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge variant="secondary">{holding.symbol}</Badge>
                    <div>
                      <div className="text-sm font-medium text-text-primary">
                        ${holding.annual_amount.toFixed(2)}/year
                      </div>
                      <div className="text-xs text-text-tertiary">
                        {holding.percentage.toFixed(1)}% of portfolio dividends
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-financial-positive">
                      {holding.yield.toFixed(1)}% yield
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Upcoming Ex-Dividend Dates */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Upcoming Ex-Dividend Dates</h3>
            <div className="space-y-2">
              {data.next_ex_dates.map((item) => (
                <div key={item.symbol} className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-4 w-4 text-blue-600" />
                    <div>
                      <div className="text-sm font-medium text-text-primary">{item.symbol}</div>
                      <div className="text-xs text-text-tertiary">Ex-Date: {item.ex_date}</div>
                    </div>
                  </div>
                  <div className="text-sm font-medium text-blue-700">
                    ~${item.estimated_amount.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Summary */}
          <div className="p-4 bg-gradient-to-r from-slate-50 to-gray-50 rounded-lg border">
            <h3 className="font-medium text-text-primary mb-2">Income Summary</h3>
            <div className="space-y-2 text-sm text-text-secondary">
              <div>
                Your portfolio generated <span className="font-medium text-financial-positive">${data.total_dividends.toFixed(2)}</span> in dividends over the past year.
              </div>
              <div>
                Current yield of <span className="font-medium">{data.dividend_yield.toFixed(1)}%</span> with a growth rate of <span className="font-medium text-financial-positive">{data.dividend_growth_rate.toFixed(1)}%</span>.
              </div>
              <div>
                Payout ratio of {data.payout_ratio.toFixed(1)}% indicates {
                  data.payout_ratio < 60 ? 'conservative' : data.payout_ratio < 80 ? 'moderate' : 'aggressive'
                } dividend sustainability.
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}