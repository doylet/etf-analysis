import React, { useCallback, useMemo } from 'react';
import { Responsive, WidthProvider, Layout, Layouts } from 'react-grid-layout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import { getWidgetComponent } from '../widgets/widget-registry';
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
}

interface WidgetGridProps {
  widgets: WidgetInstance[];
  portfolioId: string;
  onLayoutChange: (layout: Layout[]) => void;
  onRemoveWidget: (widgetKey: string) => void;
}

const WidgetGrid: React.FC<WidgetGridProps> = ({
  widgets,
  portfolioId,
  onLayoutChange,
  onRemoveWidget,
}) => {
  // Convert widgets to layout format
  const layouts = useMemo((): Layouts => {
    const layout: Layout[] = widgets.map(widget => ({
      i: widget.i,
      x: widget.x,
      y: widget.y,
      w: widget.w,
      h: widget.h,
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

  const renderWidget = useCallback(
    (widget: WidgetInstance) => (
      <Card key={widget.i} className="h-full relative overflow-hidden cursor-move">
        <CardHeader className="py-2 px-3 border-b">
          <CardTitle className="text-sm font-medium flex items-center justify-between">
            <span className="truncate">Widget</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onRemoveWidget(widget.i);
              }}
              className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <X className="h-3 w-3" />
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0 h-full overflow-auto">
          <WidgetRenderer widgetId={widget.widgetId} />
        </CardContent>
      </Card>
    ),
    [WidgetRenderer, onRemoveWidget]
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

  return (
    <ResponsiveGridLayout
      layouts={layouts}
      onLayoutChange={onLayoutChange}
      breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
      cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
      rowHeight={60}
      margin={[12, 12]}
      isDraggable={true}
      isResizable={true}
      compactType="vertical"
      preventCollision={false}
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
