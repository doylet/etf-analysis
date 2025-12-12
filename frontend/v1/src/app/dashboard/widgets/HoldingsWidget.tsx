import React from 'react';
import { useHoldingsBreakdown } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { XCircle } from 'lucide-react';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 4 },
  contentType: 'width-heavy' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.5,
  isScrollable: true,
} as const;

interface HoldingsWidgetProps {
  portfolioId?: string;
}

const HoldingsWidget: React.FC<HoldingsWidgetProps> = ({ portfolioId }) => {
  const { data, loading, error } = useHoldingsBreakdown({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Holdings Data Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="flex flex-col h-full p-2 overflow-y-auto min-h-0">
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
