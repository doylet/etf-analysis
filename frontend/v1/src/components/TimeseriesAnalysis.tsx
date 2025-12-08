'use client';

import { BarChart3, Clock, TrendingUp, ArrowUpDown } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface TimeseriesAnalysisProps {
  portfolioId?: string;
  period?: string;
  granularity?: 'daily' | 'weekly' | 'monthly';
}

interface TimeseriesData {
  returns: Array<{
    date: string;
    value: number;
    cumulative_return: number;
    drawdown: number;
  }>;
  statistics: {
    mean_return: number;
    std_return: number;
    skewness: number;
    kurtosis: number;
    autocorrelation: number;
  };
  trends: {
    trend_direction: 'upward' | 'downward' | 'sideways';
    trend_strength: number;
    support_level: number;
    resistance_level: number;
  };
  volatility_analysis: {
    rolling_volatility: Array<{ date: string; volatility: number }>;
    volatility_regime: 'low' | 'normal' | 'high';
    garch_forecast: number;
  };
}

export default function TimeseriesAnalysis({ 
  portfolioId, 
  period = '1Y',
  granularity = 'daily'
}: TimeseriesAnalysisProps) {
  // Mock data for now - replace with actual API call
  const loading = false;
  const error = null;
  const data: TimeseriesData = {
    returns: [
      { date: '2024-01-01', value: 0.5, cumulative_return: 0.5, drawdown: 0 },
      { date: '2024-01-02', value: -0.2, cumulative_return: 0.3, drawdown: 0 },
      { date: '2024-01-03', value: 1.1, cumulative_return: 1.4, drawdown: 0 },
      { date: '2024-01-04', value: -0.8, cumulative_return: 0.6, drawdown: -0.8 },
      { date: '2024-01-05', value: 0.3, cumulative_return: 0.9, drawdown: -0.5 }
    ],
    statistics: {
      mean_return: 0.08,
      std_return: 1.2,
      skewness: -0.15,
      kurtosis: 3.2,
      autocorrelation: 0.05
    },
    trends: {
      trend_direction: 'upward',
      trend_strength: 0.72,
      support_level: 98.5,
      resistance_level: 105.2
    },
    volatility_analysis: {
      rolling_volatility: [
        { date: '2024-01-01', volatility: 15.2 },
        { date: '2024-01-08', volatility: 16.8 },
        { date: '2024-01-15', volatility: 18.1 },
        { date: '2024-01-22', volatility: 17.3 },
        { date: '2024-01-29', volatility: 16.9 }
      ],
      volatility_regime: 'normal',
      garch_forecast: 17.5
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            <Skeleton className="h-6 w-[200px]" />
          </div>
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {[...Array(6)].map((_, i) => (
                <Skeleton key={i} className="h-[80px]" />
              ))}
            </div>
            <Skeleton className="h-[300px]" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Alert variant="destructive">
        <Clock className="h-4 w-4" />
        <AlertTitle>Timeseries Analysis Error</AlertTitle>
        <AlertDescription>
          Unable to load timeseries analysis data. Please check your portfolio configuration.
        </AlertDescription>
      </Alert>
    );
  }

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'upward': return <TrendingUp className="h-4 w-4 text-financial-positive" />;
      case 'downward': return <TrendingUp className="h-4 w-4 text-financial-negative rotate-180" />;
      default: return <ArrowUpDown className="h-4 w-4 text-text-tertiary" />;
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'upward': return 'text-financial-positive';
      case 'downward': return 'text-financial-negative';
      default: return 'text-text-tertiary';
    }
  };

  const getVolatilityColor = (regime: string) => {
    switch (regime) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">Timeseries Analysis</h2>
            </div>
            <p className="text-text-secondary text-sm">
              Statistical analysis and trend detection • {granularity} {period} data
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">Daily</Button>
            <Button variant="outline" size="sm">Weekly</Button>
            <Button variant="outline" size="sm">Monthly</Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Statistical Summary */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Mean Return</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.statistics.mean_return.toFixed(2)}%
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Std Deviation</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.statistics.std_return.toFixed(2)}%
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Skewness</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.statistics.skewness.toFixed(2)}
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Kurtosis</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.statistics.kurtosis.toFixed(2)}
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg">
              <div className="text-sm text-text-tertiary">Autocorrelation</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.statistics.autocorrelation.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Trend Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-medium text-text-primary">Trend Analysis</h3>
              <div className="p-4 border border-border rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  {getTrendIcon(data.trends.trend_direction)}
                  <span className={`font-medium capitalize ${getTrendColor(data.trends.trend_direction)}`}>
                    {data.trends.trend_direction} Trend
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-tertiary">Trend Strength:</span>
                    <span className="font-medium">{(data.trends.trend_strength * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-tertiary">Support Level:</span>
                    <span className="font-medium">${data.trends.support_level.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-tertiary">Resistance Level:</span>
                    <span className="font-medium">${data.trends.resistance_level.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-medium text-text-primary">Volatility Analysis</h3>
              <div className="p-4 border border-border rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <BarChart3 className="h-4 w-4" />
                  <Badge className={getVolatilityColor(data.volatility_analysis.volatility_regime)} variant="secondary">
                    {data.volatility_analysis.volatility_regime.charAt(0).toUpperCase() + data.volatility_analysis.volatility_regime.slice(1)} Volatility
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-tertiary">Current Regime:</span>
                    <span className="font-medium capitalize">{data.volatility_analysis.volatility_regime}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-tertiary">GARCH Forecast:</span>
                    <span className="font-medium">{data.volatility_analysis.garch_forecast.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Returns Table */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Recent Returns</h3>
            <div className="border border-border rounded-lg overflow-hidden">
              <div className="grid grid-cols-4 gap-4 p-3 bg-background-secondary text-sm font-medium text-text-tertiary">
                <div>Date</div>
                <div className="text-right">Daily Return</div>
                <div className="text-right">Cumulative</div>
                <div className="text-right">Drawdown</div>
              </div>
              <div className="divide-y divide-border">
                {data.returns.slice(-5).map((item, index) => (
                  <div key={index} className="grid grid-cols-4 gap-4 p-3 text-sm">
                    <div className="text-text-primary">
                      {new Date(item.date).toLocaleDateString()}
                    </div>
                    <div className={`text-right font-medium ${
                      item.value >= 0 ? 'text-financial-positive' : 'text-financial-negative'
                    }`}>
                      {item.value > 0 ? '+' : ''}{item.value.toFixed(2)}%
                    </div>
                    <div className={`text-right font-medium ${
                      item.cumulative_return >= 0 ? 'text-financial-positive' : 'text-financial-negative'
                    }`}>
                      {item.cumulative_return > 0 ? '+' : ''}{item.cumulative_return.toFixed(2)}%
                    </div>
                    <div className={`text-right font-medium ${
                      item.drawdown === 0 ? 'text-text-tertiary' : 'text-financial-negative'
                    }`}>
                      {item.drawdown === 0 ? '0.00%' : `${item.drawdown.toFixed(2)}%`}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Statistical Insights */}
          <div className="p-4 bg-gradient-to-r from-slate-50 to-gray-50 rounded-lg border">
            <h3 className="font-medium text-text-primary mb-2">Statistical Insights</h3>
            <div className="space-y-2 text-sm text-text-secondary">
              <div>
                <span className="font-medium">Distribution:</span> Skewness of {data.statistics.skewness.toFixed(2)} indicates {
                  Math.abs(data.statistics.skewness) < 0.5 ? 'roughly symmetric' : 
                  data.statistics.skewness > 0 ? 'right-skewed' : 'left-skewed'
                } returns.
              </div>
              <div>
                <span className="font-medium">Tail Risk:</span> Kurtosis of {data.statistics.kurtosis.toFixed(2)} suggests {
                  data.statistics.kurtosis > 3 ? 'heavier tails' : 'lighter tails'
                } than normal distribution.
              </div>
              <div>
                <span className="font-medium">Serial Correlation:</span> Autocorrelation of {data.statistics.autocorrelation.toFixed(2)} indicates {
                  Math.abs(data.statistics.autocorrelation) < 0.1 ? 'minimal' : 'significant'
                } momentum effects.
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}