'use client';

import { XCircle } from 'lucide-react';
import { useState } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { WidgetInsight } from '@/components/ui/widget-insight';
import { CacheBadge } from '@/components/ui/cache-badge';
import { WidgetSelect } from '@/components/ui/widget/widget-controls';
import { useHoldingsBreakdown } from '@/hooks/use-portfolio-widgets';
import type { ContentType } from './widget-metadata';
import { BreakdownTable } from './holdings-breakdown/BreakdownTable';
import { HoldingsTable } from './holdings-breakdown/HoldingsTable';
import { BreakdownStats } from './holdings-breakdown/BreakdownStats';

export const WIDGET_SIZE_CONFIG = {
  minSize: { w: 5, h: 5 },
  contentType: 'balanced' as ContentType,
  requiresFullWidth: false,
  aspectRatioPreference: 1.0,
  isScrollable: true,
} as const;

interface HoldingsBreakdownProps {
  portfolioId?: string;
  defaultBreakdownType?: 'sector' | 'geography' | 'asset_class';
}

export default function HoldingsBreakdownWidget({ 
  portfolioId, 
  defaultBreakdownType = 'asset_class' 
}: HoldingsBreakdownProps) {
  const [breakdownType, setBreakdownType] = useState(defaultBreakdownType);
  
  const { data: breakdown, loading, error, cacheHit } = useHoldingsBreakdown({
    portfolioId,
    breakdownType,
  });

  const breakdownTypeOptions = [
    { value: 'asset_class' as const, label: 'Asset Class' },
    { value: 'sector' as const, label: 'Sector' },
    { value: 'geography' as const, label: 'Geography' },
  ];

  if (loading) {
    return (
      <div className="flex flex-col h-full p-4">
        <div className="flex justify-between items-start flex-shrink-0">
          <div>
            <Skeleton className="h-6 w-[180px]" />
            <Skeleton className="h-4 w-[250px] mt-2" />
          </div>
          <Skeleton className="h-8 w-[120px]" />
        </div>
        <div className="flex-1 overflow-y-auto min-h-0 mt-4 space-y-6">
          <div className="flex flex-wrap justify-center gap-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-4 border rounded-lg">
                <Skeleton className="h-4 w-[100px]" />
                <Skeleton className="h-8 w-[120px] mt-2" />
                <Skeleton className="h-4 w-[80px] mt-1" />
              </div>
            ))}
          </div>
          <div>
            <Skeleton className="h-6 w-[150px]" />
            <div className="mt-4 space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex justify-between">
                  <Skeleton className="h-4 w-[60px]" />
                  <Skeleton className="h-4 w-[80px]" />
                  <Skeleton className="h-4 w-[100px]" />
                  <Skeleton className="h-4 w-[90px]" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !breakdown) {
    return (
      <WidgetInsight
        title="Holdings Data Error"
        description={error || 'Unable to load holdings breakdown. Please try refreshing the page.'}
        icon={XCircle}
        variant="destructive"
      />
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-2 items-center flex-shrink-0">
        <WidgetSelect
          value={breakdownType}
          onChange={setBreakdownType}
          options={breakdownTypeOptions}
          className="flex-1"
        />
        <CacheBadge show={cacheHit} />
      </div>
      
      <div className="flex-1 overflow-y-auto min-h-0 mt-3">
        <div className="space-y-6">
          {breakdown?.breakdown && breakdown.breakdown.length > 0 && (
            <BreakdownTable breakdown={breakdown.breakdown} breakdownType={breakdownType} />
          )}

          {breakdown?.holdings && breakdown.holdings.length > 0 && (
            <HoldingsTable holdings={breakdown.holdings} />
          )}

          <BreakdownStats
            totalValue={breakdown?.total_value || 0}
            holdingsCount={breakdown?.holdings?.length || 0}
            categoriesCount={breakdown?.breakdown?.length || 0}
            breakdownType={breakdownType}
          />
        </div>
      </div>
    </div>
  );
}