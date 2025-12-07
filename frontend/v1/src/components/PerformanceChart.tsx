'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { FinancialAmount } from '@/components/ui/financial-amount';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import portfolioService from '@/lib/portfolio-service';

interface PerformanceChartProps {
  totalValue?: number;
}

interface PerformanceDataPoint {
  date: string;
  value: number;
  formattedDate: string;
}

interface PerformanceChartProps {
  totalValue?: number;
}

export default function PerformanceChart({ totalValue = 100000 }: PerformanceChartProps) {
  const [data, setData] = useState<PerformanceDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPerformanceData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Get portfolio performance data from API (with fallback to mock data)
        const performanceData = await portfolioService.getPerformance('30D'); // 30-day data
        
        // Transform API data to chart format
        const chartData = performanceData.dates.map((date, index) => ({
          date,
          value: performanceData.values[index],
          formattedDate: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        }));
        
        setData(chartData);
        
      } catch (err) {
        console.error('Failed to fetch performance data:', err);
        setError('Unable to load performance data. Please try again later.');
        
        // Fallback: Set empty data to prevent crash
        setData([]);
        
        // Fallback to summary data for a single point
        try {
          const summary = await portfolioService.getSummary();
          const currentValue = summary.total_value || totalValue;
          
          // Create minimal fallback data with just current value
          const fallbackData = Array.from({ length: 30 }, (_, i) => {
            const date = new Date();
            date.setDate(date.getDate() - (29 - i));
            const variance = (Math.random() - 0.5) * 0.01; // Smaller variance for fallback
            return {
              date: date.toISOString().split('T')[0],
              value: i === 29 ? currentValue : currentValue * (1 + variance), // Last point is exact
              formattedDate: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            };
          });
          setData(fallbackData);
          setError('Using estimated performance data - full historical data unavailable');
        } catch (summaryErr) {
          console.error('Failed to fetch summary data:', summaryErr);
          // Final fallback with static data
          const staticFallback = Array.from({ length: 30 }, (_, i) => {
            const date = new Date();
            date.setDate(date.getDate() - (29 - i));
            return {
              date: date.toISOString().split('T')[0],
              value: totalValue,
              formattedDate: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            };
          });
          setData(staticFallback);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPerformanceData();
  }, [totalValue]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-foreground">Performance</h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-4">
              <Skeleton className="h-6 w-[100px]" />
              <Skeleton className="h-6 w-[100px]" />
            </div>
            <Skeleton className="h-[300px] w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-foreground">Performance</h3>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">{error}</p>
        </CardContent>
      </Card>
    );
  }

  const currentValue = data[data.length - 1]?.value || totalValue;
  const startValue = data[0]?.value || totalValue;
  const totalReturn = currentValue - startValue;
  const totalReturnPercent = ((totalReturn / startValue) * 100);
  const isPositive = totalReturn >= 0;

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  interface TooltipProps {
    active?: boolean;
    payload?: Array<{ value: number; payload: PerformanceDataPoint }>;
    label?: string;
  }

  const CustomTooltip = ({ active, payload }: TooltipProps) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background-primary border border-border-primary rounded-lg shadow-lg p-3">
          <p className="font-semibold text-text-primary tabular-nums">{payload[0].payload.formattedDate}</p>
          <div className="mt-1">
            <FinancialAmount
              amount={payload[0].value}
              size="sm"
              className="text-scheme-primary"
            />
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-foreground">Performance</h3>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">30-Day Return:</span>
            <FinancialAmount
              amount={totalReturn}
              size="sm"
              showTrend={true}
              className="font-medium"
            />
            <span className="text-muted-foreground">•</span>
            <FinancialAmount
              amount={totalReturnPercent}
              currency={undefined}
              suffix="%"
              precision={2}
              size="sm"
              showTrend={true}
              className="font-medium"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="var(--color-border-subtle)" 
                opacity={0.6}
              />
              <XAxis 
                dataKey="formattedDate" 
                stroke="var(--color-text-muted)"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                className="tabular-nums"
              />
              <YAxis 
                stroke="var(--color-text-muted)"
                fontSize={12}
                tickFormatter={(value) => formatCurrency(value)}
                tickLine={false}
                axisLine={false}
                className="tabular-nums"
                width={80}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="value"
                stroke={isPositive ? "var(--color-success)" : "var(--color-danger)"}
                strokeWidth={2}
                dot={false}
                activeDot={{ 
                  r: 4, 
                  stroke: isPositive ? "var(--color-success)" : "var(--color-danger)", 
                  strokeWidth: 2,
                  fill: "white"
                }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}