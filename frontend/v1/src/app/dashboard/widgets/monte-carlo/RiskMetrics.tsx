/**
 * RiskMetrics - Displays comprehensive risk analysis and simulation parameters
 * Shows VaR, CVaR, drawdown, volatility, and Sharpe ratio
 */
import { formatCurrency, formatPercent } from '@/lib/formatters';

interface RiskMetricsProps {
  statistics: {
    historical_sharpe: number;
    historical_volatility: number;
    max_drawdown_median?: number;
    cvar_95?: number;
  };
  var95: number;
  simulationParams: {
    initial_value: number;
    time_horizon_years: number;
    num_simulations: number;
  } | null;
}

export function RiskMetrics({ statistics, var95, simulationParams }: RiskMetricsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="p-4 border rounded-lg">
        <h4 className="font-medium mb-2">Risk Metrics</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Value at Risk (95%):</span>
            <span className="font-mono">{formatCurrency(var95)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Conditional VaR (95%):</span>
            <span className="font-mono">{formatCurrency(statistics.cvar_95 || var95)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Max Drawdown (Median):</span>
            <span className="font-mono">{statistics.max_drawdown_median?.toFixed(1) || '0.0'}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Volatility (Std Dev):</span>
            <span className="font-mono">{formatPercent(statistics.historical_volatility)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Sharpe Ratio:</span>
            <span className="font-mono">{statistics.historical_sharpe.toFixed(2)}</span>
          </div>
        </div>
      </div>
      
      <div className="p-4 border rounded-lg">
        <h4 className="font-medium mb-2">Simulation Parameters</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Initial Value:</span>
            <span className="font-mono">{formatCurrency(simulationParams?.initial_value || 0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Time Horizon:</span>
            <span className="font-mono">{(simulationParams?.time_horizon_years || 0).toFixed(2)} years</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Simulations:</span>
            <span className="font-mono">{(simulationParams?.num_simulations || 0).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
