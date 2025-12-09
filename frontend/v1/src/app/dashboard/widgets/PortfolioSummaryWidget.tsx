import React from 'react';
import { usePortfolioSummary } from '@/hooks/use-portfolio-widgets';

interface PortfolioSummaryWidgetProps {
  portfolioId?: string;
}

const PortfolioSummaryWidget: React.FC<PortfolioSummaryWidgetProps> = ({ portfolioId }) => {
  const { data, loading, error } = usePortfolioSummary({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-4 text-center text-destructive">{error}</div>;
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-xl font-bold text-foreground">${data.total_value.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Total Value</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className={`text-xl font-bold ${data.total_return >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            ${data.total_return.toLocaleString()}
          </div>
          <div className="text-xs text-muted-foreground">Total Return</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-xl font-bold text-foreground">{data.positions}</div>
          <div className="text-xs text-muted-foreground">Positions</div>
        </div>
        <div className="text-center p-3 bg-muted rounded-md">
          <div className="text-xl font-bold text-foreground">${data.allocated_cash.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Cash</div>
        </div>
      </div>
    </div>
  );
};

PortfolioSummaryWidget.displayName = 'PortfolioSummaryWidget';

export default React.memo(PortfolioSummaryWidget);
