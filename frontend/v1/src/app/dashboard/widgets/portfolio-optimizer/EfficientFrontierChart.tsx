'use client';

import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis } from 'recharts';

interface ChartDataPoint {
  volatility: number;
  return: number;
  sharpe: number;
  name: string;
}

interface EfficientFrontierChartProps {
  chartData: ChartDataPoint[];
  currentReturn?: number;
  currentRisk?: number;
  currentSharpe?: number;
  expectedReturn?: number;
  expectedRisk?: number;
  sharpeRatio?: number;
}

export function EfficientFrontierChart({
  chartData,
  currentReturn,
  currentRisk,
  currentSharpe,
  expectedReturn,
  expectedRisk,
  sharpeRatio,
}: EfficientFrontierChartProps) {
  if (chartData.length === 0) return null;

  return (
    <div>
      <div className="text-sm font-medium mb-2">Efficient Frontier</div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              type="number" 
              dataKey="volatility" 
              name="Risk"
              unit="%"
              stroke="hsl(var(--muted-foreground))"
              tick={{ fontSize: 11 }}
              label={{ value: 'Risk (Volatility %)', position: 'insideBottom', offset: -10, fontSize: 11 }}
            />
            <YAxis 
              type="number" 
              dataKey="return" 
              name="Return"
              unit="%"
              stroke="hsl(var(--muted-foreground))"
              tick={{ fontSize: 11 }}
              label={{ value: 'Return %', angle: -90, position: 'insideLeft', fontSize: 11 }}
            />
            <ZAxis type="number" dataKey="sharpe" range={[50, 400]} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--background))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '6px',
                fontSize: '12px'
              }}
              formatter={(value: number, name: string) => {
                if (name === 'return' || name === 'volatility') return [`${value.toFixed(2)}%`, name === 'return' ? 'Return' : 'Risk'];
                return [value.toFixed(2), 'Sharpe'];
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Scatter 
              name="Portfolio Options" 
              data={chartData} 
              fill="hsl(var(--primary))"
              opacity={0.6}
            />
            {currentReturn && currentRisk && (
              <Scatter 
                name="Current Portfolio" 
                data={[{ volatility: currentRisk, return: currentReturn, sharpe: currentSharpe }]}
                fill="hsl(var(--destructive))"
                shape="star"
              />
            )}
            {expectedReturn && expectedRisk && (
              <Scatter 
                name="Optimal Portfolio" 
                data={[{ volatility: expectedRisk, return: expectedReturn, sharpe: sharpeRatio }]}
                fill="hsl(var(--chart-2))"
                shape="triangle"
              />
            )}
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
