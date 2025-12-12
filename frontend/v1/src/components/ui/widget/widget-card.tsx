import React, { useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { Button } from '@/components/ui';
import { X, RotateCcw } from 'lucide-react';

export interface WidgetCardProps {
  widgetKey: string;
  title: string;
  isLocked?: boolean;
  onRemove?: (widgetKey: string) => void;
  onReset?: (widgetKey: string) => void;
  children: React.ReactNode;
}

export const WidgetCard: React.FC<WidgetCardProps> = ({
  widgetKey,
  title,
  isLocked,
  onRemove,
  onReset,
  children,
}) => {
  const handleRemove = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      onRemove?.(widgetKey);
    },
    [onRemove, widgetKey]
  );

  const handleReset = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      onReset?.(widgetKey);
    },
    [onReset, widgetKey]
  );

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
  }, []);

  return (
    <Card className="h-full relative overflow-hidden cursor-move flex flex-col">
      <CardHeader className="py-2 px-3 border-b flex-shrink-0 cursor-move">
        <CardTitle className="text-sm font-medium flex items-center justify-between">
          <span className="truncate">{title}</span>
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {isLocked && onReset && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleReset}
                onMouseDown={handleMouseDown}
                title="Reset to optimal position"
                className="h-6 w-6 p-0 hover:bg-primary/10 hover:text-primary cursor-pointer"
              >
                <RotateCcw className="h-3 w-3" />
              </Button>
            )}
            {onRemove && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRemove}
                onMouseDown={handleMouseDown}
                className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive cursor-pointer"
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto min-h-0 p-0 cursor-auto">
        {children}
      </CardContent>
    </Card>
  );
};

WidgetCard.displayName = 'WidgetCard';
