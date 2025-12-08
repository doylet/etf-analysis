'use client';

import { Lock, Target, Settings, CheckCircle, XCircle } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { useState } from 'react';

interface ConstrainedOptimizationProps {
  portfolioId?: string;
}

interface ConstraintData {
  constraints: {
    sector_limits: Array<{
      sector: string;
      min_weight: number;
      max_weight: number;
      current_weight: number;
      target_weight: number;
      status: 'satisfied' | 'violated';
    }>;
    position_limits: Array<{
      symbol: string;
      min_weight: number;
      max_weight: number;
      current_weight: number;
      target_weight: number;
      locked: boolean;
      status: 'satisfied' | 'violated';
    }>;
    risk_constraints: {
      max_volatility: number;
      current_volatility: number;
      target_volatility: number;
      max_beta: number;
      current_beta: number;
      target_beta: number;
      max_tracking_error: number;
      current_tracking_error: number;
      target_tracking_error: number;
    };
  };
  optimization_result: {
    feasible: boolean;
    objective_value: number;
    constraints_satisfied: number;
    constraints_total: number;
    improvement_metrics: {
      return_improvement: number;
      risk_reduction: number;
      sharpe_improvement: number;
    };
  };
}

export default function ConstrainedOptimization({ 
  portfolioId 
}: ConstrainedOptimizationProps) {
  const [sectorConstraintsEnabled, setSectorConstraintsEnabled] = useState(true);
  const [riskConstraintsEnabled, setRiskConstraintsEnabled] = useState(true);
  const [maxVolatility, setMaxVolatility] = useState("18.0");
  
  // Mock data for now - replace with actual API call
  const loading = false;
  const error = null;
  const data: ConstraintData = {
    constraints: {
      sector_limits: [
        { 
          sector: 'Technology', 
          min_weight: 20.0, 
          max_weight: 40.0, 
          current_weight: 45.0, 
          target_weight: 38.5,
          status: 'violated' 
        },
        { 
          sector: 'Healthcare', 
          min_weight: 5.0, 
          max_weight: 20.0, 
          current_weight: 8.0, 
          target_weight: 12.0,
          status: 'satisfied' 
        },
        { 
          sector: 'Financial', 
          min_weight: 10.0, 
          max_weight: 25.0, 
          current_weight: 15.0, 
          target_weight: 18.0,
          status: 'satisfied' 
        },
        { 
          sector: 'Consumer', 
          min_weight: 5.0, 
          max_weight: 20.0, 
          current_weight: 12.0, 
          target_weight: 14.5,
          status: 'satisfied' 
        }
      ],
      position_limits: [
        { 
          symbol: 'AAPL', 
          min_weight: 5.0, 
          max_weight: 15.0, 
          current_weight: 18.0, 
          target_weight: 14.5,
          locked: false,
          status: 'violated' 
        },
        { 
          symbol: 'MSFT', 
          min_weight: 5.0, 
          max_weight: 20.0, 
          current_weight: 12.0, 
          target_weight: 16.0,
          locked: true,
          status: 'satisfied' 
        },
        { 
          symbol: 'GOOGL', 
          min_weight: 3.0, 
          max_weight: 15.0, 
          current_weight: 10.0, 
          target_weight: 8.0,
          locked: false,
          status: 'satisfied' 
        }
      ],
      risk_constraints: {
        max_volatility: 18.0,
        current_volatility: 19.5,
        target_volatility: 17.8,
        max_beta: 1.2,
        current_beta: 1.15,
        target_beta: 1.08,
        max_tracking_error: 3.0,
        current_tracking_error: 3.5,
        target_tracking_error: 2.8
      }
    },
    optimization_result: {
      feasible: true,
      objective_value: 0.68,
      constraints_satisfied: 8,
      constraints_total: 10,
      improvement_metrics: {
        return_improvement: 0.8,
        risk_reduction: 1.7,
        sharpe_improvement: 0.06
      }
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Lock className="h-5 w-5" />
            <Skeleton className="h-6 w-[200px]" />
          </div>
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-[150px]" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Alert variant="destructive">
        <Lock className="h-4 w-4" />
        <AlertTitle>Constrained Optimization Error</AlertTitle>
        <AlertDescription>
          Unable to load constrained optimization data. Please check your portfolio configuration.
        </AlertDescription>
      </Alert>
    );
  }

  const formatPercentage = (value: number) => `${value.toFixed(1)}%`;

  const getConstraintIcon = (status: string) => {
    return status === 'satisfied' 
      ? <CheckCircle className="h-4 w-4 text-financial-positive" />
      : <XCircle className="h-4 w-4 text-financial-negative" />;
  };

  const getConstraintColor = (status: string) => {
    return status === 'satisfied' ? 'text-financial-positive' : 'text-financial-negative';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">Constrained Optimization</h2>
            </div>
            <p className="text-text-secondary text-sm">
              Portfolio optimization with custom constraints and limits
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Configure
            </Button>
            <Button size="sm">
              <Target className="h-4 w-4 mr-2" />
              Optimize
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Optimization Status */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <div className="text-sm text-blue-700">Feasible Solution</div>
              <div className="text-2xl font-bold text-blue-800">
                {data.optimization_result.feasible ? 'Yes' : 'No'}
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Objective Value</div>
              <div className="text-2xl font-bold text-text-primary">
                {data.optimization_result.objective_value.toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Constraints Met</div>
              <div className="text-2xl font-bold text-text-primary">
                {data.optimization_result.constraints_satisfied}/{data.optimization_result.constraints_total}
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Sharpe Improvement</div>
              <div className="text-2xl font-bold text-financial-positive">
                +{data.optimization_result.improvement_metrics.sharpe_improvement.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Constraint Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-text-primary">Sector Constraints</h3>
                <Switch 
                  checked={sectorConstraintsEnabled} 
                  onCheckedChange={setSectorConstraintsEnabled}
                />
              </div>
              {sectorConstraintsEnabled && (
                <div className="text-sm text-text-tertiary">
                  Enforce minimum and maximum sector allocations
                </div>
              )}
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-text-primary">Risk Constraints</h3>
                <Switch 
                  checked={riskConstraintsEnabled} 
                  onCheckedChange={setRiskConstraintsEnabled}
                />
              </div>
              {riskConstraintsEnabled && (
                <div className="flex items-center gap-2">
                  <label className="text-sm text-text-tertiary">Max Volatility:</label>
                  <Input 
                    type="number" 
                    value={maxVolatility} 
                    onChange={(e) => setMaxVolatility(e.target.value)}
                    className="w-20"
                    step="0.1"
                  />
                  <span className="text-sm text-text-tertiary">%</span>
                </div>
              )}
            </div>
          </div>

          {/* Sector Constraints */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Sector Allocation Constraints</h3>
            <div className="space-y-2">
              {data.constraints.sector_limits.map((constraint) => (
                <div key={constraint.sector} className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <div className="flex items-center gap-3">
                    {getConstraintIcon(constraint.status)}
                    <div>
                      <span className="font-medium text-text-primary">{constraint.sector}</span>
                      <div className="text-sm text-text-tertiary">
                        Range: {formatPercentage(constraint.min_weight)} - {formatPercentage(constraint.max_weight)}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-medium ${getConstraintColor(constraint.status)}`}>
                      {formatPercentage(constraint.current_weight)} → {formatPercentage(constraint.target_weight)}
                    </div>
                    <Badge 
                      variant={constraint.status === 'satisfied' ? 'default' : 'destructive'}
                      className="text-xs"
                    >
                      {constraint.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Position Constraints */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Position Limits</h3>
            <div className="space-y-2">
              {data.constraints.position_limits.map((constraint) => (
                <div key={constraint.symbol} className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <div className="flex items-center gap-3">
                    {getConstraintIcon(constraint.status)}
                    <Badge variant="secondary">{constraint.symbol}</Badge>
                    {constraint.locked && (
                      <Badge variant="outline" className="text-xs">
                        <Lock className="h-3 w-3 mr-1" />
                        Locked
                      </Badge>
                    )}
                    <div className="text-sm text-text-tertiary">
                      Range: {formatPercentage(constraint.min_weight)} - {formatPercentage(constraint.max_weight)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-medium ${getConstraintColor(constraint.status)}`}>
                      {formatPercentage(constraint.current_weight)} → {formatPercentage(constraint.target_weight)}
                    </div>
                    <Badge 
                      variant={constraint.status === 'satisfied' ? 'default' : 'destructive'}
                      className="text-xs"
                    >
                      {constraint.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Constraints */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Risk Constraints</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border border-border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  {getConstraintIcon(
                    data.constraints.risk_constraints.current_volatility <= data.constraints.risk_constraints.max_volatility 
                      ? 'satisfied' : 'violated'
                  )}
                  <span className="text-sm font-medium">Volatility</span>
                </div>
                <div className="space-y-1 text-sm">
                  <div>Current: {formatPercentage(data.constraints.risk_constraints.current_volatility)}</div>
                  <div>Target: {formatPercentage(data.constraints.risk_constraints.target_volatility)}</div>
                  <div className="text-text-tertiary">
                    Max: {formatPercentage(data.constraints.risk_constraints.max_volatility)}
                  </div>
                </div>
              </div>

              <div className="p-4 border border-border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  {getConstraintIcon(
                    data.constraints.risk_constraints.current_beta <= data.constraints.risk_constraints.max_beta 
                      ? 'satisfied' : 'violated'
                  )}
                  <span className="text-sm font-medium">Beta</span>
                </div>
                <div className="space-y-1 text-sm">
                  <div>Current: {data.constraints.risk_constraints.current_beta.toFixed(2)}</div>
                  <div>Target: {data.constraints.risk_constraints.target_beta.toFixed(2)}</div>
                  <div className="text-text-tertiary">
                    Max: {data.constraints.risk_constraints.max_beta.toFixed(2)}
                  </div>
                </div>
              </div>

              <div className="p-4 border border-border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  {getConstraintIcon(
                    data.constraints.risk_constraints.current_tracking_error <= data.constraints.risk_constraints.max_tracking_error 
                      ? 'satisfied' : 'violated'
                  )}
                  <span className="text-sm font-medium">Tracking Error</span>
                </div>
                <div className="space-y-1 text-sm">
                  <div>Current: {formatPercentage(data.constraints.risk_constraints.current_tracking_error)}</div>
                  <div>Target: {formatPercentage(data.constraints.risk_constraints.target_tracking_error)}</div>
                  <div className="text-text-tertiary">
                    Max: {formatPercentage(data.constraints.risk_constraints.max_tracking_error)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Optimization Summary */}
          <div className="p-4 bg-gradient-to-r from-slate-50 to-gray-50 rounded-lg border">
            <h3 className="font-medium text-text-primary mb-2">Optimization Summary</h3>
            <div className="space-y-2 text-sm text-text-secondary">
              <div>
                <span className="font-medium">Feasibility:</span> {
                  data.optimization_result.feasible 
                    ? 'Feasible solution found with all critical constraints satisfied'
                    : 'No feasible solution - constraints may be too restrictive'
                }
              </div>
              <div>
                <span className="font-medium">Improvements:</span> {
                  formatPercentage(data.optimization_result.improvement_metrics.return_improvement)
                } return increase, {
                  formatPercentage(data.optimization_result.improvement_metrics.risk_reduction)
                } risk reduction
              </div>
              <div>
                <span className="font-medium">Constraint Status:</span> {data.optimization_result.constraints_satisfied} of {data.optimization_result.constraints_total} constraints satisfied
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}