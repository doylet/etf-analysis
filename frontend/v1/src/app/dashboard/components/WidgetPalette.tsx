import React from 'react';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { AVAILABLE_WIDGETS, WidgetConfig } from '../widgets/widget-registry';

interface WidgetPaletteProps {
  onAddWidget: (widgetId: string) => void;
  onClose: () => void;
  existingWidgets: string[];
}

const WidgetPalette: React.FC<WidgetPaletteProps> = ({
  onAddWidget,
  existingWidgets,
}) => {
  const availableToAdd = AVAILABLE_WIDGETS.filter(
    widget => !existingWidgets.includes(widget.id)
  );

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <span className="text-sm font-medium">Add Widget:</span>
      {availableToAdd.map((widget: WidgetConfig) => (
        <Button
          key={widget.id}
          variant="outline"
          size="sm"
          onClick={() => onAddWidget(widget.id)}
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
  );
};

WidgetPalette.displayName = 'WidgetPalette';

export default React.memo(WidgetPalette);
