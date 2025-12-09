/**
 * Dashboard Page - Clean Modular Architecture
 * Orchestrates dashboard layout and widget management
 */

'use client';

import React, { useState, useCallback } from 'react';
import { Layout } from 'react-grid-layout';
import DashboardToolbar from './components/DashboardToolbar';
import WidgetPalette from './components/WidgetPalette';
import WidgetGrid, { type WidgetInstance } from './components/WidgetGrid';
import { AVAILABLE_WIDGETS } from './widgets/widget-registry';

export default function DashboardPage() {
  const [portfolioId] = useState<string>('default');
  const [showWidgetPalette, setShowWidgetPalette] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Initialize with default widgets
  const [widgets, setWidgets] = useState<WidgetInstance[]>([
    {
      i: 'portfolio-summary-1',
      widgetId: 'portfolio-summary',
      x: 0,
      y: 0,
      w: 4,
      h: 4
    },
    {
      i: 'holdings-1',
      widgetId: 'holdings',
      x: 4,
      y: 0,
      w: 4,
      h: 4
    },
    {
      i: 'correlation-matrix-1',
      widgetId: 'correlation-matrix',
      x: 8,
      y: 0,
      w: 4,
      h: 4
    },
    {
      i: 'monte-carlo-1',
      widgetId: 'monte-carlo',
      x: 0,
      y: 4,
      w: 6,
      h: 6
    }
  ]);

  const handleLayoutChange = useCallback((layout: Layout[]) => {
    setWidgets(prev => prev.map(widget => {
      const layoutItem = layout.find(item => item.i === widget.i);
      return layoutItem ? {
        ...widget,
        x: layoutItem.x,
        y: layoutItem.y,
        w: layoutItem.w,
        h: layoutItem.h
      } : widget;
    }));
  }, []);

  const handleAddWidget = useCallback((widgetId: string) => {
    const widgetDef = AVAILABLE_WIDGETS.find(w => w.id === widgetId);
    if (!widgetDef) return;

    const timestamp = Date.now();
    const newWidget: WidgetInstance = {
      i: `${widgetId}-${timestamp}`,
      widgetId,
      x: 0,
      y: 0,
      w: widgetDef.defaultSize.w,
      h: widgetDef.defaultSize.h
    };

    setWidgets(prev => [...prev, newWidget]);
    setShowWidgetPalette(false);
  }, []);

  const handleRemoveWidget = useCallback((widgetKey: string) => {
    setWidgets(prev => prev.filter(w => w.i !== widgetKey));
  }, []);

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true);
    // Force re-render of all widgets
    setWidgets(prev => [...prev]);
    setTimeout(() => setIsRefreshing(false), 500);
  }, []);

  const existingWidgetIds = widgets.map(w => w.widgetId);

  return (
    <div className="h-screen flex flex-col bg-background">
      <div className="p-4 border-b">
        <DashboardToolbar
          widgetCount={widgets.length}
          availableToAdd={AVAILABLE_WIDGETS.filter(w => !existingWidgetIds.includes(w.id)).length}
          onAddWidget={() => setShowWidgetPalette(!showWidgetPalette)}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />
      </div>

      {showWidgetPalette && (
        <div className="p-4 border-b bg-muted/30">
          <WidgetPalette
            onAddWidget={handleAddWidget}
            onClose={() => setShowWidgetPalette(false)}
            existingWidgets={existingWidgetIds}
          />
        </div>
      )}

      <div className="flex-1 overflow-auto p-4">
        <WidgetGrid
          widgets={widgets}
          portfolioId={portfolioId}
          onLayoutChange={handleLayoutChange}
          onRemoveWidget={handleRemoveWidget}
        />
      </div>
    </div>
  );
}