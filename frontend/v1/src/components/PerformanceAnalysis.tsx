'use client';

import { Activity, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

interface PerformanceAnalysisProps {
  portfolioId?: string;
  timePeriod?: string;
}

interface PerformanceData {
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  best_day: { date: string; return: number };
  worst_day: { date: string; return: number };
  win_rate: number;
  performance_periods: Array<{
    period: string;
    return: number;
    volatility: number;
  }>;
  risk_metrics: {
    var_95: number;
    var_99: number;
    cvar_95: number;
    calmar_ratio: number;
  };
}

export default function PerformanceAnalysis({ 
  portfolioId, 
  timePeriod = '1Y'
}: PerformanceAnalysisProps) {
  // Mock data for now - replace with actual API call
  const loading = false;
  const error = null;
  const data: PerformanceData = {
    total_return: 15.8,
    annualized_return: 14.2,
    volatility: 18.5,
    sharpe_ratio: 0.92,
    max_drawdown: -12.3,
    best_day: { date: '2024-01-15', return: 3.2 },
    worst_day: { date: '2024-03-08', return: -2.8 },
    win_rate: 58.5,
    performance_periods: [
      { period: '1M', return: 2.1, volatility: 15.2 },
      { period: '3M', return: 6.8, volatility: 16.1 },
      { period: '6M', return: 11.2, volatility: 17.8 },
      { period: '1Y', return: 15.8, volatility: 18.5 },
      { period: '3Y', return: 42.5, volatility: 19.2 }
    ],
    risk_metrics: {
      var_95: -2.1,
      var_99: -3.8,
      cvar_95: -2.9,
      calmar_ratio: 1.15
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            <Skeleton className="h-6 w-[200px]" />
          </div>
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
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
        <Activity className="h-4 w-4" />
        <AlertTitle>Performance Analysis Error</AlertTitle>
        <AlertDescription>
          Unable to load performance analysis data. Please check your portfolio configuration.
        </AlertDescription>
      </Alert>
    );
  }

  const getRiskLevel = (volatility: number) => {
    if (volatility < 10) return { label: 'Low', color: 'bg-green-100 text-green-800' };
    if (volatility < 20) return { label: 'Moderate', color: 'bg-yellow-100 text-yellow-800' };
    return { label: 'High', color: 'bg-red-100 text-red-800' };
  };

  const getPerformanceColor = (value: number) => {
    return value >= 0 ? 'text-financial-positive' : 'text-financial-negative';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold">Performance Analysis</h2>
        </div>
        <p className="text-text-secondary text-sm">
          Comprehensive performance and risk metrics • {timePeriod} period
        </p>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Key Performance Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <div className="text-sm text-blue-700">Total Return</div>
              <div className={`text-2xl font-bold ${getPerformanceColor(data.total_return)}`}>
                {data.total_return > 0 ? '+' : ''}{data.total_return.toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Annualized Return</div>
              <div className={`text-2xl font-bold ${getPerformanceColor(data.annualized_return)}`}>
                {data.annualized_return > 0 ? '+' : ''}{data.annualized_return.toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Volatility</div>
              <div className="text-2xl font-bold text-text-primary">
                {data.volatility.toFixed(1)}%
              </div>
              <Badge className={`mt-1 ${getRiskLevel(data.volatility).color}`} variant="secondary">
                {getRiskLevel(data.volatility).label} Risk
              </Badge>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Sharpe Ratio</div>
              <div className="text-2xl font-bold text-text-primary">
                {data.sharpe_ratio.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Risk Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Max Drawdown</div>
              <div className="text-lg font-semibold text-financial-negative">
                {data.max_drawdown.toFixed(1)}%
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Win Rate</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.win_rate.toFixed(1)}%
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">VaR (95%)</div>
              <div className="text-lg font-semibold text-financial-negative">
                {data.risk_metrics.var_95.toFixed(1)}%
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Calmar Ratio</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.risk_metrics.calmar_ratio.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Performance Periods */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Performance by Time Period</h3>
            <div className="space-y-2">
              {data.performance_periods.map((period) => (
                <div key={period.period} className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">{period.period}</Badge>
                    <div>
                      <div className={`text-sm font-medium ${getPerformanceColor(period.return)}`}>
                        {period.return > 0 ? '+' : ''}{period.return.toFixed(1)}%
                      </div>
                      <div className="text-xs text-text-tertiary">Return</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-text-primary">
                      {period.volatility.toFixed(1)}%
                    </div>
                    <div className="text-xs text-text-tertiary">Volatility</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Best/Worst Days */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-700">Best Day</span>
              </div>
              <div className="text-lg font-bold text-green-800">
                +{data.best_day.return.toFixed(1)}%
              </div>
              <div className="text-xs text-green-600">{data.best_day.date}</div>
            </div>
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingDown className="h-4 w-4 text-red-600" />
                <span className="text-sm font-medium text-red-700">Worst Day</span>
              </div>
              <div className="text-lg font-bold text-red-800">
                {data.worst_day.return.toFixed(1)}%
              </div>
              <div className="text-xs text-red-600">{data.worst_day.date}</div>
            </div>
          </div>

          {/* Risk Analysis */}
          <div className="p-4 bg-gradient-to-r from-slate-50 to-gray-50 rounded-lg border">
            <h3 className="font-medium text-text-primary mb-2">Risk Assessment</h3>
            <div className="space-y-2 text-sm text-text-secondary">
              <div>
                <span className="font-medium">Risk Level:</span> {getRiskLevel(data.volatility).label} - {data.volatility.toFixed(1)}% annualized volatility
              </div>
              <div>
                <span className="font-medium">Downside Risk:</span> 95% VaR of {data.risk_metrics.var_95.toFixed(1)}% with CVaR of {data.risk_metrics.cvar_95.toFixed(1)}%
              </div>
              <div>
                <span className="font-medium">Risk-Adjusted Return:</span> Sharpe ratio of {data.sharpe_ratio.toFixed(2)} indicates {
                  data.sharpe_ratio > 1 ? 'excellent' : data.sharpe_ratio > 0.5 ? 'good' : 'poor'
                } risk-adjusted performance
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}