'use client';

import { usePortfolioSummary, useHoldingsBreakdown, useCorrelationMatrix } from '@/hooks/use-portfolio-widgets';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

export default function WidgetTestPage() {
  const summary = usePortfolioSummary();
  const holdings = useHoldingsBreakdown();
  const correlation = useCorrelationMatrix();

  const widgets = [
    { name: 'Portfolio Summary', hook: summary },
    { name: 'Holdings Breakdown', hook: holdings },
    { name: 'Correlation Matrix', hook: correlation },
  ];

  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Widget API Test</h1>
        <p className="text-gray-600">Testing connectivity between React components and FastAPI widget endpoints</p>
      </div>

      <div className="grid gap-6">
        {widgets.map(({ name, hook }) => (
          <Card key={name}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{name}</h3>
                <div className="flex items-center gap-2">
                  {hook.loading ? (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                      Loading
                    </Badge>
                  ) : hook.error ? (
                    <Badge variant="destructive">
                      <XCircle className="h-3 w-3 mr-1" />
                      Error
                    </Badge>
                  ) : hook.data ? (
                    <Badge variant="default" className="bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Success
                    </Badge>
                  ) : (
                    <Badge variant="secondary">No Data</Badge>
                  )}
                  {hook.cacheHit && (
                    <Badge variant="outline" className="text-xs">Cached</Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              {hook.loading && (
                <div className="text-gray-500">Loading widget data...</div>
              )}
              
              {hook.error && (
                <div className="text-red-600">
                  <p className="font-medium">Error:</p>
                  <p className="text-sm">{hook.error}</p>
                </div>
              )}
              
              {hook.data && (
                <div className="space-y-2">
                  <div className="text-sm text-gray-600">
                    <strong>Data Preview:</strong>
                  </div>
                  <div className="bg-gray-50 p-3 rounded text-sm font-mono">
                    {name === 'Portfolio Summary' && (
                      <div>
                        Total Value: ${hook.data.total_value?.toFixed(2)}<br/>
                        Positions: {hook.data.positions}<br/>
                        Return: {hook.data.total_return_percent?.toFixed(2)}%
                      </div>
                    )}
                    {name === 'Holdings Breakdown' && (
                      <div>
                        Holdings: {hook.data.holdings?.length || 0}<br/>
                        Total Value: ${hook.data.total_value?.toFixed(2)}<br/>
                        Type: {hook.data.breakdown_type}
                      </div>
                    )}
                    {name === 'Correlation Matrix' && (
                      <div>
                        Symbols: {hook.data.symbols?.length || 0}<br/>
                        Period: {hook.data.time_period?.days} days<br/>
                        Avg Correlation: {hook.data.statistics?.avg_correlation?.toFixed(3)}
                      </div>
                    )}
                  </div>
                  {hook.metadata && (
                    <div className="text-xs text-gray-500 mt-2">
                      Execution Time: {hook.metadata.execution_time}<br/>
                      {hook.metadata.cache_hit && `Cache Hit: ${hook.metadata.cached_at}`}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">API Test Actions</h3>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <button 
              onClick={() => {
                summary.refetch();
                holdings.refetch(); 
                correlation.refetch();
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refetch All
            </button>
            <button
              onClick={() => window.open('/api/widgets/', '_blank')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              View API Docs
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}