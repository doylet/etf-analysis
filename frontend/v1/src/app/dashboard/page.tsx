'use client';

import PortfolioSummary from '@/components/PortfolioSummary';
import Holdings from '@/components/Holdings';
import PerformanceChart from '@/components/PerformanceChart';
import { usePortfolioSummary } from '@/hooks/use-portfolio-summary';

export default function DashboardPage() {
  const { summary } = usePortfolioSummary();
  
  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      <PortfolioSummary />

      {/* Holdings and Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Holdings */}
        <Holdings />

        {/* Performance Chart */}
        <PerformanceChart totalValue={summary?.total_value} />
      </div>
    </div>
  );
}