import React from 'react';
import { usePortfolioSummary } from '@/hooks/use-portfolio-widgets';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { MetricCard } from '@/components/ui/metric-card';
import { MetricGroup } from '@/components/ui/financial/metric-group';
import { XCircle, DollarSign, TrendingUp, Briefcase, Wallet } from 'lucide-react';
import { formatCurrency } from '@/lib/formatters';
import type { ContentType } from './widget-metadata';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 3, h: 2 },
  contentType: 'compact' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.5,
  isScrollable: false,
} as const;

interface PortfolioSummaryWidgetProps {
  portfolioId?: string;
}

const PortfolioSummaryWidget: React.FC<PortfolioSummaryWidgetProps> = ({ portfolioId }) => {
  const { data, loading, error } = usePortfolioSummary({ portfolioId });

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>;
  if (error) return (
    <WidgetInsight
      title="Portfolio Data Error"
      description={error}
      icon={XCircle}
      variant="destructive"
    />
  );
  if (!data) return <div className="p-4 text-center text-muted-foreground">No data</div>;

  return (
    <div className="flex flex-col h-full">
      <MetricGroup layout="horizontal" className="flex-1 overflow-y-auto min-h-0">
        <MetricCard
          title="Total Value"
          value={formatCurrency(data.total_value)}
          icon={DollarSign}
          variant="default"
          size="sm"
        />
        <MetricCard
          title="Total Return"
          value={formatCurrency(data.total_return)}
          icon={TrendingUp}
          variant="default"
          size="sm"
          trend={data.total_return >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          title="Positions"
          value={data.positions.toString()}
          icon={Briefcase}
          variant="default"
          size="sm"
        />
        <MetricCard
          title="Cash"
          value={formatCurrency(data.allocated_cash)}
          icon={Wallet}
          variant="default"
          size="sm"
        />
      </MetricGroup>
    </div>
  );
};

PortfolioSummaryWidget.displayName = 'PortfolioSummaryWidget';

export default React.memo(PortfolioSummaryWidget);
