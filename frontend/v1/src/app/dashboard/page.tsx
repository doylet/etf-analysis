'use client';

import PortfolioSummary from '@/components/PortfolioSummary';
import Holdings from '@/components/Holdings';
import PerformanceChart from '@/components/PerformanceChart';
import { Section, ChartGrid } from '@/components/ui/grid-layout';
import { usePortfolioSummary } from '@/hooks/use-portfolio-summary';

export default function DashboardPage() {
  const { summary } = usePortfolioSummary();
  
  return (
    <div className="space-y-8">
      {/* Portfolio Overview Section */}
      <Section 
        title="Portfolio Overview" 
        subtitle="Real-time portfolio metrics and performance"
      >
        <PortfolioSummary />
      </Section>

      {/* Detailed Analysis Section */}
      <Section 
        title="Analysis & Performance" 
        subtitle="Holdings breakdown and performance tracking"
      >
        <ChartGrid columns={2}>
          <Holdings />
          <PerformanceChart totalValue={summary?.total_value} />
        </ChartGrid>
      </Section>
    </div>
  );
}