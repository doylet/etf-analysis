/**
 * Dashboard Page with Drag-and-Drop Widget Management
 */

'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { Responsive, WidthProvider, Layout, Layouts } from 'react-grid-layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

// Import working widget components  
import { PortfolioSummary } from '@/components/PortfolioSummary';
import { Holdings } from '@/components/Holdings';
import { CorrelationMatrix } from '@/components/CorrelationMatrix';
import { MonteCarloSimulation } from '@/components/MonteCarloSimulation';

import { useAllWidgets } from '@/hooks/use-portfolio-widgets';
import { RefreshCw, Grid, Plus, X } from 'lucide-react';

// Import CSS for react-grid-layout
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface WidgetInstance {
  id: string;
  type: string;
  name: string;
  component: React.ComponentType<{ portfolioId?: string }>;
  position: {
    i: string;
    x: number;
    y: number;
    w: number;
    h: number;
  };
}

const AVAILABLE_WIDGETS = [
  {
    type: 'portfolio-summary',
    name: 'Portfolio Summary',
    component: PortfolioSummary,
    defaultSize: { w: 6, h: 4 }
  },
  {
    type: 'holdings-breakdown', 
    name: 'Holdings Breakdown',
    component: Holdings,
    defaultSize: { w: 6, h: 5 }
  },
  {
    type: 'correlation-matrix',
    name: 'Correlation Matrix',
    component: CorrelationMatrix,
    defaultSize: { w: 12, h: 6 }
  },
  {
    type: 'monte-carlo',
    name: 'Monte Carlo Simulation',
    component: MonteCarloSimulation,
    defaultSize: { w: 6, h: 6 }
  }
];

export default function DashboardPage() {
  const [portfolioId, setPortfolioId] = useState<string | undefined>();
  const [showWidgetPalette, setShowWidgetPalette] = useState(false);
  
  // Initialize with default widgets
  const [widgets, setWidgets] = useState<WidgetInstance[]>([
    {
      id: 'portfolio-summary-1',
      type: 'portfolio-summary',
      name: 'Portfolio Summary',
      component: PortfolioSummary,
      position: { i: 'portfolio-summary-1', x: 0, y: 0, w: 6, h: 4 }
    },
    {
      id: 'holdings-breakdown-1', 
      type: 'holdings-breakdown',
      name: 'Holdings Breakdown',
      component: Holdings,
      position: { i: 'holdings-breakdown-1', x: 6, y: 0, w: 6, h: 5 }
    },
    {
      id: 'correlation-matrix-1',
      type: 'correlation-matrix',
      name: 'Correlation Matrix',
      component: CorrelationMatrix,
      position: { i: 'correlation-matrix-1', x: 0, y: 5, w: 12, h: 6 }
    },
    {
      id: 'monte-carlo-1',
      type: 'monte-carlo',
      name: 'Monte Carlo Simulation', 
      component: MonteCarloSimulation,
      position: { i: 'monte-carlo-1', x: 0, y: 11, w: 6, h: 6 }
    }
  ]);

  const { refetchAll } = useAllWidgets(portfolioId);

  // Convert widgets to grid layout format
  const layouts = useMemo((): Layouts => {
    const layout: Layout[] = widgets.map(widget => ({
      ...widget.position,
      isDraggable: true,
      isResizable: true
    }));

    return {
      lg: layout,
      md: layout,
      sm: layout,
      xs: layout.map(item => ({ ...item, w: Math.min(item.w, 4) })),
      xxs: layout.map(item => ({ ...item, w: 2 }))
    };
  }, [widgets]);

  // Handle layout changes from drag/resize
  const handleLayoutChange = useCallback((layout: Layout[]) => {
    setWidgets(prev => prev.map(widget => {
      const layoutItem = layout.find(item => item.i === widget.id);
      return layoutItem ? {
        ...widget,
        position: {
          i: widget.id,
          x: layoutItem.x,
          y: layoutItem.y,
          w: layoutItem.w,
          h: layoutItem.h
        }
      } : widget;
    }));
  }, []);

  const addWidget = (type: string) => {
    const widgetDef = AVAILABLE_WIDGETS.find(w => w.type === type);
    if (!widgetDef) return;

    const newWidget: WidgetInstance = {
      id: `${type}-${Date.now()}`,
      type,
      name: widgetDef.name,
      component: widgetDef.component,
      position: {
        i: `${type}-${Date.now()}`,
        x: 0,
        y: 0,
        w: widgetDef.defaultSize.w,
        h: widgetDef.defaultSize.h
      }
    };

    setWidgets(prev => [...prev, newWidget]);
    setShowWidgetPalette(false);
  };

  const removeWidget = (widgetId: string) => {
    setWidgets(prev => prev.filter(w => w.id !== widgetId));
  };

  const handleRefreshAll = async () => {
    try {
      await refetchAll();
    } catch (error) {
      console.error('Failed to refresh widgets:', error);
    }
  };

  // Render individual widget with remove button
  const renderWidget = (widget: WidgetInstance) => (
    <Card key={widget.id} className="h-full relative overflow-hidden cursor-move">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center justify-between">
          <span className="truncate">{widget.name}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              removeWidget(widget.id);
            }}
            className="h-6 w-6 p-0 text-destructive hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <X className="h-3 w-3" />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0 h-full overflow-auto">
        <widget.component portfolioId={portfolioId} />
      </CardContent>
    </Card>
  );

  const availableToAdd = AVAILABLE_WIDGETS.filter(
    available => !widgets.some(widget => widget.type === available.type)
  );

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-4">
          <Grid className="h-5 w-5" />
          <div>
            <h1 className="text-xl font-semibold">Portfolio Dashboard</h1>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>{widgets.length} widgets</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            onClick={() => setShowWidgetPalette(!showWidgetPalette)}
            className="gap-2"
            disabled={availableToAdd.length === 0}
          >
            <Plus className="h-4 w-4" />
            Add Widget
          </Button>
          
          <Button variant="outline" onClick={handleRefreshAll} className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Widget Palette */}
      {showWidgetPalette && (
        <div className="p-4 border-b bg-muted/30">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium">Add Widget:</span>
            {availableToAdd.map(widget => (
              <Button
                key={widget.type}
                variant="outline"
                size="sm"
                onClick={() => addWidget(widget.type)}
                className="gap-2"
              >
                <Plus className="h-3 w-3" />
                {widget.name}
              </Button>
            ))}
            {availableToAdd.length === 0 && (
              <span className="text-sm text-muted-foreground">All widgets already added</span>
            )}
          </div>
        </div>
      )}

      {/* Main Dashboard Grid */}
      <div className="flex-1 overflow-auto p-4">
        <ResponsiveGridLayout
          layouts={layouts}
          onLayoutChange={handleLayoutChange}
          breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
          cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
          rowHeight={60}
          margin={[16, 16]}
          isDraggable={true}
          isResizable={true}
          compactType="vertical"
          preventCollision={false}
          useCSSTransforms={true}
        >
          {widgets.map(widget => (
            <div key={widget.id} className="group">
              {renderWidget(widget)}
            </div>
          ))}
        </ResponsiveGridLayout>
        
        {widgets.length === 0 && (
          <div className="flex items-center justify-center h-96 border-2 border-dashed border-border rounded-lg">
            <div className="text-center">
              <h3 className="text-lg font-medium mb-2">No widgets added yet</h3>
              <p className="text-muted-foreground mb-4">
                Click "Add Widget" to start building your dashboard
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}