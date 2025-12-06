'use client';

import PortfolioSummary from '@/components/PortfolioSummary';
import { Card, CardHeader, CardContent } from '@/components/shared/card';
import { PageHeader } from '@/components/layout/page-header';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      
      {/* Page Title */}
      <PageHeader
        title="Dashboard"
        description="Your portfolio overview and analytics"
      />

      {/* Portfolio Summary */}
      <PortfolioSummary />

      {/* Additional sections can go here */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Placeholder for Holdings */}
        <Card variant="default" size="md">
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Holdings</h3>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500 text-center py-8">
              Holdings component coming soon...
            </p>
          </CardContent>
        </Card>

        {/* Placeholder for Performance Chart */}
        <Card variant="outlined" size="md">
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500 text-center py-8">
              Performance chart coming soon...
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}