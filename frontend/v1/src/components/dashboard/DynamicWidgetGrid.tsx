/**
 * Dynamic Widget Container Component
 * Provides drag-and-drop grid layout for dashboard widgets
 */

'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { Responsive, WidthProvider, Layout, Layouts } from 'react-grid-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useWidgetManagement } from '@/contexts/WidgetManagementContext';
import { WidgetConfig } from '@/types/widget-config';
import { 
  X, 
  Minus, 
  Plus, 
  Settings, 
  Maximize2, 
  Minimize2,
  GripVertical 
} from 'lucide-react';

// Import all widget components
import PortfolioSummary from '@/components/PortfolioSummary';
import Holdings from '@/components/Holdings';
import CorrelationMatrix from '@/components/CorrelationMatrix';
import MonteCarloSimulation from '@/components/MonteCarloSimulation';
import BenchmarkComparison from '@/components/BenchmarkComparison';
import DividendAnalysis from '@/components/DividendAnalysis';
import PerformanceAnalysis from '@/components/PerformanceAnalysis';
import TimeseriesAnalysis from '@/components/TimeseriesAnalysis';
import PortfolioTransition from '@/components/PortfolioTransition';
import NewsEventAnalysis from '@/components/NewsEventAnalysis';
import PortfolioOptimizer from '@/components/PortfolioOptimizer';
import ConstrainedOptimization from '@/components/ConstrainedOptimization';

// Import CSS for react-grid-layout
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface DynamicWidgetGridProps {
  portfolioId?: string;
  isEditMode?: boolean;
}

export function DynamicWidgetGrid({ 
  portfolioId,
  isEditMode = false 
}: DynamicWidgetGridProps) {
  const { state, actions } = useWidgetManagement();
  
  // Convert widget configs to grid layout format
  const layouts = useMemo((): Layouts => {
    const layout: Layout[] = state.widgets
      .filter(widget => widget.isVisible)
      .map(widget => ({
        i: widget.id,
        x: widget.position.x,
        y: widget.position.y,
        w: widget.position.w,
        h: widget.position.h,
        minW: 2,
        minH: 2,
        isDraggable: isEditMode,
        isResizable: isEditMode
      }));

    return {
      lg: layout,
      md: layout,
      sm: layout,
      xs: layout,
      xxs: layout
    };
  }, [state.widgets, isEditMode]);

  // Handle layout changes (drag/resize)
  const handleLayoutChange = useCallback((layout: Layout[], layouts: Layouts) => {
    layout.forEach(item => {
      const widget = state.widgets.find(w => w.id === item.i);
      if (widget && (
        widget.position.x !== item.x ||
        widget.position.y !== item.y ||
        widget.position.w !== item.w ||
        widget.position.h !== item.h
      )) {
        actions.moveWidget(widget.id, {
          x: item.x,
          y: item.y,
          w: item.w,
          h: item.h
        });
      }
    });
  }, [state.widgets, actions]);

  // Render widget content based on type
  const renderWidgetContent = (widget: WidgetConfig) => {
    switch (widget.type) {
      case 'portfolio-summary':
        return <PortfolioSummary />;
      case 'holdings-breakdown':
        return <Holdings />;
      case 'correlation-matrix':
        return <CorrelationMatrix />;
      case 'monte-carlo':
        return <MonteCarloSimulation />;
      case 'benchmark-comparison':
        return <BenchmarkComparison />;
      case 'dividend-analysis':
        return <DividendAnalysis />;
      case 'performance-analysis':
        return <PerformanceAnalysis />;
      case 'timeseries-analysis':
        return <TimeseriesAnalysis />;
      case 'portfolio-transition':
        return <PortfolioTransition />;
      case 'news-event-analysis':
        return <NewsEventAnalysis />;
      case 'portfolio-optimizer':
        return <PortfolioOptimizer />;
      case 'constrained-optimization':
        return <ConstrainedOptimization />;
      default:
        return (
          <div className="p-4 text-center text-muted-foreground">
            Widget type "{widget.type}" not implemented
          </div>
        );
    }
  };

  // Render widget with controls
  const renderWidget = (widget: WidgetConfig) => {
    const isMinimized = widget.isMinimized;
    
    return (
      <Card 
        key={widget.id}
        className={`
          relative overflow-hidden transition-all duration-200
          ${isEditMode ? 'ring-2 ring-primary/20 hover:ring-primary/40' : ''}
          ${isMinimized ? 'h-12' : 'h-full'}
        `}
      >
        {/* Widget Header with Controls */}
        <CardHeader className="pb-2 space-y-0">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium truncate">
              {widget.title}
            </CardTitle>
            
            <div className="flex items-center gap-1">
              {isEditMode && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => actions.minimizeWidget(widget.id)}
                    className="h-6 w-6 p-0"
                  >
                    {isMinimized ? <Maximize2 className="h-3 w-3" /> : <Minimize2 className="h-3 w-3" />}
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                  >
                    <Settings className="h-3 w-3" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => actions.removeWidget(widget.id)}
                    className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </>
              )}
              
              {isEditMode && (
                <div className="h-6 w-6 flex items-center justify-center cursor-grab active:cursor-grabbing">
                  <GripVertical className="h-3 w-3 text-muted-foreground" />
                </div>
              )}
            </div>
          </div>
        </CardHeader>

        {/* Widget Content */}
        {!isMinimized && (
          <CardContent className="p-4 pt-0 h-full overflow-auto">
            {renderWidgetContent(widget)}
          </CardContent>
        )}
      </Card>
    );
  };

  return (
    <div className="p-4 w-full">
      <ResponsiveGridLayout
        layouts={layouts}
        onLayoutChange={handleLayoutChange}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={60}
        margin={[16, 16]}
        isDraggable={isEditMode}
        isResizable={isEditMode}
        compactType="vertical"
        preventCollision={false}
        useCSSTransforms={true}
        draggableHandle=".cursor-grab"
        className="min-h-[600px]"
      >
        {state.widgets
          .filter(widget => widget.isVisible)
          .map(widget => (
            <div key={widget.id}>
              {renderWidget(widget)}
            </div>
          ))}
      </ResponsiveGridLayout>
      
      {state.widgets.length === 0 && (
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
  );
}