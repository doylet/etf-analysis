'use client';

import { TrendingUp, TrendingDown, Target, BarChart } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { FinancialAmount } from '@/components/ui/financial-amount';
import { PercentageChange } from '@/components/ui/percentage-change';

interface BenchmarkComparisonProps {
  portfolioId?: string;
  benchmark?: string;
  timePeriod?: string;
}

interface BenchmarkData {
  portfolio_return: number;
  benchmark_return: number;
  alpha: number;
  beta: number;
  sharpe_ratio: number;
  tracking_error: number;
  outperformance: number;
  correlation: number;
}

export default function BenchmarkComparison({ 
  portfolioId, 
  benchmark = 'SPY',
  timePeriod = '1Y'
}: BenchmarkComparisonProps) {
  // Mock data for now - replace with actual API call
  const loading = false;
  const error = null;
  const data: BenchmarkData = {
    portfolio_return: 12.5,
    benchmark_return: 10.2,
    alpha: 2.3,
    beta: 1.05,
    sharpe_ratio: 0.85,
    tracking_error: 3.2,
    outperformance: 2.3,
    correlation: 0.92
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            <Skeleton className="h-6 w-[200px]" />
          </div>
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="p-4 border rounded-lg">
                <Skeleton className="h-4 w-[80px]" />
                <Skeleton className="h-6 w-[120px] mt-2" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Alert variant="destructive">
        <Target className="h-4 w-4" />
        <AlertTitle>Benchmark Analysis Error</AlertTitle>
        <AlertDescription>
          Unable to load benchmark comparison data. Please check your portfolio configuration.
        </AlertDescription>
      </Alert>
    );
  }

  const isOutperforming = data.outperformance > 0;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Target className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold">Benchmark Comparison</h2>
        </div>
        <p className="text-text-secondary text-sm">
          Portfolio vs {benchmark} • {timePeriod} period
        </p>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Performance Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Portfolio Return</div>
              <div className="text-2xl font-bold text-text-primary">
                {data.portfolio_return.toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">{benchmark} Return</div>
              <div className="text-2xl font-bold text-text-primary">
                {data.benchmark_return.toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <div className="text-sm text-blue-700">Outperformance</div>
              <div className={`text-2xl font-bold flex items-center gap-1 ${
                isOutperforming ? 'text-financial-positive' : 'text-financial-negative'
              }`}>
                {isOutperforming ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                {data.outperformance > 0 ? '+' : ''}{data.outperformance.toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Risk Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Alpha</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.alpha.toFixed(2)}%
              </div>
            </div>
            <div className="text-center p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Beta</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.beta.toFixed(2)}
              </div>
            </div>
            <div className="text-center p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Sharpe Ratio</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.sharpe_ratio.toFixed(2)}
              </div>
            </div>
            <div className="text-center p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Tracking Error</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.tracking_error.toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Analysis Summary */}
          <div className="p-4 bg-gradient-to-r from-slate-50 to-gray-50 rounded-lg border">
            <h3 className="font-medium text-text-primary mb-2">Analysis Summary</h3>
            <div className="space-y-2 text-sm text-text-secondary">
              <div>
                <span className="font-medium">Beta:</span> A beta of {data.beta.toFixed(2)} indicates {
                  data.beta > 1 ? 'higher' : 'lower'
                } volatility than the market.
              </div>
              <div>
                <span className="font-medium">Alpha:</span> The portfolio generated {
                  data.alpha > 0 ? 'positive' : 'negative'
                } alpha of {data.alpha.toFixed(2)}%, indicating {
                  data.alpha > 0 ? 'outperformance' : 'underperformance'
                } vs expected returns.
              </div>
              <div>
                <span className="font-medium">Correlation:</span> {(data.correlation * 100).toFixed(0)}% correlation with {benchmark}.
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}