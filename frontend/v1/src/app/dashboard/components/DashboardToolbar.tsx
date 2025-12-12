import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Plus, RefreshCw, RotateCcw } from 'lucide-react';

interface DashboardToolbarProps {
  widgetCount: number;
  availableToAdd: number;
  onAddWidget: () => void;
  onRefresh: () => void;
  onReset: () => void;
  isRefreshing: boolean;
}

const DashboardToolbar: React.FC<DashboardToolbarProps> = ({
  widgetCount,
  availableToAdd,
  onAddWidget,
  onRefresh,
  onReset,
  isRefreshing,
}) => {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="font-semibold text-lg">Portfolio Dashboard</h1>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>{widgetCount} widgets</span>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <Button
          onClick={onAddWidget}
          className="gap-2"
          disabled={availableToAdd === 0}
        >
          <Plus className="h-4 w-4" />
          Add Widget
        </Button>
        <Button
          onClick={onRefresh}
          variant="outline"
          className="gap-2"
          disabled={isRefreshing}
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
        <Button
          onClick={onReset}
          variant="outline"
          className="gap-2"
        >
          <RotateCcw className="h-4 w-4" />
          Reset
        </Button>
      </div>
    </div>
  );
};

DashboardToolbar.displayName = 'DashboardToolbar';

export default React.memo(DashboardToolbar);
