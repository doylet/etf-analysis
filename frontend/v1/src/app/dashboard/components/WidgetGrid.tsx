import React, { useCallback, useMemo, useState, useEffect } from 'react';
import { Responsive, WidthProvider, Layout, Layouts } from 'react-grid-layout';
import { getWidgetComponent, getWidgetTitle } from '../widgets/widget-registry';
import { WidgetWrapper, useWidgetSpacing } from '@/components/ui/widget-wrapper';
import { WidgetCard } from '@/components/ui/widget-card';
import { generateAllLayouts } from '../services/layout-algorithm';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

export interface WidgetInstance {
  i: string;
  widgetId: string;
  x: number;
  y: number;
  w: number;
  h: number;
  isLocked?: boolean; // Track if widget position is manually set
}

interface WidgetGridProps {
  widgets: WidgetInstance[];
  portfolioId: string;
  onLayoutChange: (layout: Layout[]) => void;
  onRemoveWidget: (widgetKey: string) => void;
  onResetWidget?: (widgetKey: string) => void;
}

const WidgetGrid: React.FC<WidgetGridProps> = ({
  widgets,
  portfolioId,
  onLayoutChange,
  onRemoveWidget,
  onResetWidget,
}) => {
  const { spacing } = useWidgetSpacing();
  const [currentBreakpoint, setCurrentBreakpoint] = useState<string>('lg');
  const [isDragging, setIsDragging] = useState(false);
  const [mounted, setMounted] = useState(typeof window !== 'undefined');
  
  // Generate optimal layouts using dynamic algorithm
  // Algorithm respects locked widgets (manually positioned) and optimizes unlocked widgets
  const layouts = useMemo((): Layouts => {
    const optimizedLayouts = generateAllLayouts(widgets);
    
    // Add draggable/resizable flags
    const addInteractionFlags = (layout: Layout[]): Layout[] => {
      return layout.map(item => ({
        ...item,
        isDraggable: true,
        isResizable: true,
      }));
    };

    return {
      lg: addInteractionFlags(optimizedLayouts.lg),
      md: addInteractionFlags(optimizedLayouts.md),
      sm: addInteractionFlags(optimizedLayouts.sm),
      xs: addInteractionFlags(optimizedLayouts.xs),
      xxs: addInteractionFlags(optimizedLayouts.xxs),
    };
  }, [widgets]);

  const WidgetRenderer = useCallback(
    ({ widgetId }: { widgetId: string }) => {
      const WidgetComponent = getWidgetComponent(widgetId);
      if (!WidgetComponent) {
        return <div className="p-4 text-center text-destructive">Unknown widget type</div>;
      }
      return <WidgetComponent portfolioId={portfolioId} />;
    },
    [portfolioId]
  );

  const handleBreakpointChange = useCallback((breakpoint: string) => {
    setCurrentBreakpoint(breakpoint);
  }, []);

  const handleDrag = useCallback(
    (layout: Layout[], oldItem: Layout, newItem: Layout, placeholder: Layout) => {
      if (!isDragging) setIsDragging(true);

      // Find the widget that's being dragged
      const draggedWidget = widgets.find(w => w.i === newItem.i);
      if (!draggedWidget) return;

      // Calculate available space at the new position
      const cols = { lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }[currentBreakpoint] || 12;
      
      let maxWidth = cols - newItem.x;
      let maxHeight = 20; // reasonable max height
      
      // Find the nearest blocking widget in each direction
      layout.forEach(item => {
        if (item.i === newItem.i) return;
        
        // Check for widgets to the right that would block horizontal expansion
        if (item.x >= newItem.x && item.y < newItem.y + draggedWidget.h && item.y + item.h > newItem.y) {
          maxWidth = Math.min(maxWidth, item.x - newItem.x);
        }
        
        // Check for widgets below that would block vertical expansion
        if (item.y >= newItem.y && item.x < newItem.x + draggedWidget.w && item.x + item.w > newItem.x) {
          maxHeight = Math.min(maxHeight, item.y - newItem.y);
        }
      });
      
      // Update the placeholder to show the constrained size
      const constrainedWidth = Math.max(1, Math.min(draggedWidget.w, maxWidth));
      const constrainedHeight = Math.max(1, Math.min(draggedWidget.h, maxHeight));
      
      placeholder.w = constrainedWidth;
      placeholder.h = constrainedHeight;
    },
    [widgets, currentBreakpoint, isDragging]
  );

  const handleDragStop = useCallback(
    (layout: Layout[]) => {
      setIsDragging(false);
      onLayoutChange(layout);
    },
    [onLayoutChange]
  );

  const renderWidget = useCallback(
    (widget: WidgetInstance) => (
      <WidgetCard
        key={widget.i}
        widgetKey={widget.i}
        title={getWidgetTitle(widget.widgetId)}
        isLocked={widget.isLocked}
        onRemove={onRemoveWidget}
        onReset={onResetWidget}
      >
        <WidgetWrapper spacing={spacing}>
          <WidgetRenderer widgetId={widget.widgetId} />
        </WidgetWrapper>
      </WidgetCard>
    ),
    [WidgetRenderer, onRemoveWidget, onResetWidget, spacing]
  );

  if (widgets.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 border-2 border-dashed border-border rounded-lg">
        <div className="text-center">
          <h3 className="text-lg font-medium mb-2">No widgets added yet</h3>
          <p className="text-muted-foreground mb-4">
            Click &ldquo;Add Widget&rdquo; to start building your dashboard
          </p>
        </div>
      </div>
    );
  }

  // Prevent hydration mismatch by not rendering grid until client-side
  if (!mounted) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-muted-foreground">Loading widgets...</div>
      </div>
    );
  }

  return (
    <ResponsiveGridLayout
      layouts={layouts}
      onLayoutChange={onLayoutChange}
      onBreakpointChange={handleBreakpointChange}
      onDrag={handleDrag}
      onDragStop={handleDragStop}
      breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
      cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
      rowHeight={60}
      margin={[8, 8]}
      isDraggable={true}
      isResizable={true}
      compactType="vertical"
      preventCollision={false}
      allowOverlap={false}
      useCSSTransforms={true}
    >
      {widgets.map(widget => (
        <div key={widget.i} className="group">
          {renderWidget(widget)}
        </div>
      ))}
    </ResponsiveGridLayout>
  );
};

WidgetGrid.displayName = 'WidgetGrid';

export default React.memo(WidgetGrid);
