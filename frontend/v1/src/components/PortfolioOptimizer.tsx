'use client';

import { Target, Zap, BarChart, Settings } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { useState } from 'react';

interface PortfolioOptimizerProps {
  portfolioId?: string;
  optimizationType?: 'max_sharpe' | 'min_variance' | 'max_return';
}

interface OptimizerData {
  current_allocation: Array<{
    symbol: string;
    weight: number;
    expected_return: number;
    risk: number;
  }>;
  optimized_allocation: Array<{
    symbol: string;
    weight: number;
    expected_return: number;
    risk: number;
  }>;
  metrics: {
    current: {
      expected_return: number;
      volatility: number;
      sharpe_ratio: number;
    };
    optimized: {
      expected_return: number;
      volatility: number;
      sharpe_ratio: number;
    };
  };
  constraints: {
    max_weight: number;
    min_weight: number;
    target_return?: number;
    max_risk?: number;
  };
  efficient_frontier: Array<{
    return: number;
    risk: number;
    sharpe: number;
  }>;
}

export default function PortfolioOptimizer({ 
  portfolioId, 
  optimizationType = 'max_sharpe'
}: PortfolioOptimizerProps) {
  const [riskTolerance, setRiskTolerance] = useState([50]);
  const [maxWeight, setMaxWeight] = useState([25]);
  
  // Mock data for now - replace with actual API call
  const loading = false;
  const error = null;
  const data: OptimizerData = {
    current_allocation: [
      { symbol: 'AAPL', weight: 35.0, expected_return: 12.5, risk: 22.1 },
      { symbol: 'MSFT', weight: 25.0, expected_return: 11.8, risk: 20.5 },
      { symbol: 'GOOGL', weight: 20.0, expected_return: 13.2, risk: 25.3 },
      { symbol: 'VTI', weight: 20.0, expected_return: 10.5, risk: 15.8 }
    ],
    optimized_allocation: [
      { symbol: 'AAPL', weight: 28.5, expected_return: 12.5, risk: 22.1 },
      { symbol: 'MSFT', weight: 32.0, expected_return: 11.8, risk: 20.5 },
      { symbol: 'GOOGL', weight: 15.5, expected_return: 13.2, risk: 25.3 },
      { symbol: 'VTI', weight: 24.0, expected_return: 10.5, risk: 15.8 }
    ],
    metrics: {
      current: {
        expected_return: 11.9,
        volatility: 19.2,
        sharpe_ratio: 0.62
      },
      optimized: {
        expected_return: 12.1,
        volatility: 17.8,
        sharpe_ratio: 0.68
      }
    },
    constraints: {
      max_weight: 35.0,
      min_weight: 5.0,
      target_return: 12.0,
      max_risk: 20.0
    },
    efficient_frontier: [
      { return: 8.5, risk: 12.0, sharpe: 0.71 },
      { return: 10.0, risk: 14.5, sharpe: 0.69 },
      { return: 11.5, risk: 17.0, sharpe: 0.68 },
      { return: 13.0, risk: 20.5, sharpe: 0.63 },
      { return: 14.5, risk: 25.0, sharpe: 0.58 }
    ]
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
        <Target className="h-4 w-4" />
        <AlertTitle>Portfolio Optimizer Error</AlertTitle>
        <AlertDescription>
          Unable to load portfolio optimization data. Please check your portfolio configuration.
        </AlertDescription>
      </Alert>
    );
  }

  const formatPercentage = (value: number) => `${value.toFixed(1)}%`;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">Portfolio Optimizer</h2>
            </div>
            <p className="text-text-secondary text-sm">
              Mean-variance optimization with risk constraints
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Constraints
            </Button>
            <Button size="sm">
              <Zap className="h-4 w-4 mr-2" />
              Optimize
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Optimization Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-medium text-text-primary">Risk Tolerance</h3>
              <div className="px-2">
                <Slider
                  value={riskTolerance}
                  onValueChange={setRiskTolerance}
                  max={100}
                  step={5}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-text-tertiary mt-1">
                  <span>Conservative</span>
                  <span>{riskTolerance[0]}%</span>
                  <span>Aggressive</span>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <h3 className="font-medium text-text-primary">Max Weight per Asset</h3>
              <div className="px-2">
                <Slider
                  value={maxWeight}
                  onValueChange={setMaxWeight}
                  max={50}
                  min={10}
                  step={5}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-text-tertiary mt-1">
                  <span>10%</span>
                  <span>{maxWeight[0]}%</span>
                  <span>50%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-text-primary mb-3">Current Portfolio</h3>
              <div className="p-4 bg-gray-50 rounded-lg space-y-3">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-text-tertiary">Expected Return</div>
                    <div className="text-lg font-semibold text-text-primary">
                      {formatPercentage(data.metrics.current.expected_return)}
                    </div>
                  </div>
                  <div>
                    <div className="text-text-tertiary">Volatility</div>
                    <div className="text-lg font-semibold text-text-primary">
                      {formatPercentage(data.metrics.current.volatility)}
                    </div>
                  </div>
                  <div>
                    <div className="text-text-tertiary">Sharpe Ratio</div>
                    <div className="text-lg font-semibold text-text-primary">
                      {data.metrics.current.sharpe_ratio.toFixed(2)}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-medium text-text-primary mb-3">Optimized Portfolio</h3>
              <div className="p-4 bg-green-50 rounded-lg space-y-3 border border-green-200">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-green-700">Expected Return</div>
                    <div className="text-lg font-semibold text-green-800">
                      {formatPercentage(data.metrics.optimized.expected_return)}
                    </div>
                  </div>
                  <div>
                    <div className="text-green-700">Volatility</div>
                    <div className="text-lg font-semibold text-green-800">
                      {formatPercentage(data.metrics.optimized.volatility)}
                    </div>
                  </div>
                  <div>
                    <div className="text-green-700">Sharpe Ratio</div>
                    <div className="text-lg font-semibold text-green-800">
                      {data.metrics.optimized.sharpe_ratio.toFixed(2)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Allocation Comparison */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Allocation Changes</h3>
            <div className="space-y-2">
              {data.current_allocation.map((current, index) => {
                const optimized = data.optimized_allocation.find(opt => opt.symbol === current.symbol);
                if (!optimized) return null;
                
                const weightChange = optimized.weight - current.weight;
                
                return (
                  <div key={current.symbol} className="flex items-center justify-between p-3 border border-border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary">{current.symbol}</Badge>
                      <div className="text-sm text-text-tertiary">
                        Expected Return: {formatPercentage(current.expected_return)}
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right text-sm">
                        <div className="font-medium text-text-primary">
                          {formatPercentage(current.weight)} → {formatPercentage(optimized.weight)}
                        </div>
                        <div className={`text-xs ${weightChange >= 0 ? 'text-financial-positive' : 'text-financial-negative'}`}>
                          {weightChange > 0 ? '+' : ''}{formatPercentage(weightChange)}
                        </div>
                      </div>
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all"
                          style={{ width: `${(optimized.weight / 40) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Efficient Frontier */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Efficient Frontier Points</h3>
            <div className="grid grid-cols-5 gap-2">
              {data.efficient_frontier.map((point, index) => (
                <div key={index} className="text-center p-3 border border-border rounded-lg">
                  <div className="text-xs text-text-tertiary">Risk/Return</div>
                  <div className="text-sm font-semibold text-text-primary">
                    {formatPercentage(point.risk)} / {formatPercentage(point.return)}
                  </div>
                  <div className="text-xs text-text-tertiary">
                    Sharpe: {point.sharpe.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Optimization Summary */}
          <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
            <h3 className="font-medium text-blue-800 mb-2">
              <BarChart className="h-4 w-4 inline mr-2" />
              Optimization Results
            </h3>
            <div className="space-y-1 text-sm text-blue-700">
              <div>
                • Expected return improvement: <span className="font-medium">
                  +{(data.metrics.optimized.expected_return - data.metrics.current.expected_return).toFixed(1)}%
                </span>
              </div>
              <div>
                • Risk reduction: <span className="font-medium">
                  -{(data.metrics.current.volatility - data.metrics.optimized.volatility).toFixed(1)}%
                </span>
              </div>
              <div>
                • Sharpe ratio improvement: <span className="font-medium">
                  +{(data.metrics.optimized.sharpe_ratio - data.metrics.current.sharpe_ratio).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}