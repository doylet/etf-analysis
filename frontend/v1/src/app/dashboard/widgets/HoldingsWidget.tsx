import React from 'react';
import { useHoldingsBreakdown } from '@/hooks/use-portfolio-widgets';

interface HoldingsWidgetProps {
  portfolioId?: string;
}

const HoldingsWidget: React.FC<HoldingsWidgetProps> = ({ portfolioId }) => {
  const { data, loading, error } = useHoldingsBreakdown({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-2 overflow-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left p-2 text-muted-foreground font-medium">Symbol</th>
            <th className="text-right p-2 text-muted-foreground font-medium">Value</th>
            <th className="text-right p-2 text-muted-foreground font-medium">Weight</th>
            <th className="text-right p-2 text-muted-foreground font-medium">Return</th>
          </tr>
        </thead>
        <tbody>
          {data.holdings.map((holding) => (
            <tr key={holding.symbol} className="border-b border-border hover:bg-muted/50">
              <td className="p-2 font-medium text-foreground">{holding.symbol}</td>
              <td className="text-right p-2 text-foreground">${holding.current_value.toLocaleString()}</td>
              <td className="text-right p-2 text-foreground">{(holding.weight_percent * 100).toFixed(1)}%</td>
              <td className={`text-right p-2 ${holding.total_return >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {holding.total_return >= 0 ? '+' : ''}{holding.total_return_percent.toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

HoldingsWidget.displayName = 'HoldingsWidget';

export default React.memo(HoldingsWidget);
