/**
 * Dashboard Page - Clean Modular Architecture
 * Orchestrates dashboard layout and widget management
 */

'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Layout } from 'react-grid-layout';
import DashboardToolbar from './components/DashboardToolbar';
import WidgetPalette from './components/WidgetPalette';
import WidgetGrid, { type WidgetInstance } from './components/WidgetGrid';
import { AVAILABLE_WIDGETS } from './widgets/widget-registry';
import { WidgetSpacingProvider } from '@/components/ui/widget-wrapper';
import { getDefaultSizeForWidget } from './services/layout-algorithm';

const STORAGE_KEY = 'dashboard-widgets';
const STORAGE_VERSION = '1.0';

// Default widgets configuration
const DEFAULT_WIDGETS: WidgetInstance[] = [
  {
    i: 'portfolio-summary-1',
    widgetId: 'portfolio-summary',
    x: 0,
    y: 0,
    w: 3,
    h: 2,
    isLocked: false
  },
  {
    i: 'holdings-1',
    widgetId: 'holdings',
    x: 0,
    y: 0,
    w: 6,
    h: 4,
    isLocked: false
  },
  {
    i: 'correlation-matrix-1',
    widgetId: 'correlation-matrix',
    x: 0,
    y: 0,
    w: 8,
    h: 8,
    isLocked: false
  },
  {
    i: 'monte-carlo-1',
    widgetId: 'monte-carlo',
    x: 0,
    y: 0,
    w: 6,
    h: 6,
    isLocked: false
  }
];

// Load dashboard state from localStorage
function loadDashboardState(): WidgetInstance[] | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return null;
    
    const parsed = JSON.parse(saved);
    if (parsed.version !== STORAGE_VERSION) {
      console.log('Dashboard state version mismatch, using defaults');
      return null;
    }
    
    return parsed.widgets || null;
  } catch (error) {
    console.error('Failed to load dashboard state:', error);
    return null;
  }
}

// Save dashboard state to localStorage
function saveDashboardState(widgets: WidgetInstance[]) {
  if (typeof window === 'undefined') return;
  
  try {
    const state = {
      version: STORAGE_VERSION,
      widgets,
      lastSaved: new Date().toISOString()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    console.error('Failed to save dashboard state:', error);
  }
}

export default function DashboardPage() {
  const [portfolioId] = useState<string>('default');
  const [showWidgetPalette, setShowWidgetPalette] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Initialize with saved state or defaults using lazy initializer
  const [widgets, setWidgets] = useState<WidgetInstance[]>(() => {
    return loadDashboardState() || DEFAULT_WIDGETS;
  });

  // Save state to localStorage whenever widgets change
  useEffect(() => {
    saveDashboardState(widgets);
  }, [widgets]);

  const handleLayoutChange = useCallback((layout: Layout[]) => {
    setWidgets(prev => {
      // First, update all widgets with new layout positions
      const updated = prev.map(widget => {
        const layoutItem = layout.find(item => item.i === widget.i);
        if (!layoutItem) return widget;
        
        // Check if widget was manually moved or resized by user
        const wasModified = 
          layoutItem.x !== widget.x ||
          layoutItem.y !== widget.y ||
          layoutItem.w !== widget.w ||
          layoutItem.h !== widget.h;
        
        return {
          ...widget,
          x: layoutItem.x,
          y: layoutItem.y,
          w: layoutItem.w,
          h: layoutItem.h,
          // Lock widget if it was manually modified by user drag/resize
          isLocked: wasModified ? true : widget.isLocked
        };
      });
      
      return updated;
    });
  }, []);

  const handleAddWidget = useCallback((widgetId: string) => {
    const widgetDef = AVAILABLE_WIDGETS.find(w => w.id === widgetId);
    if (!widgetDef) return;

    const timestamp = Date.now();
    const defaultSize = getDefaultSizeForWidget(widgetId, 'lg');
    
    const newWidget: WidgetInstance = {
      i: `${widgetId}-${timestamp}`,
      widgetId,
      x: 0,
      y: 0,
      w: defaultSize.w,
      h: defaultSize.h,
      isLocked: false // New widgets start unlocked (algorithm optimizes)
    };

    setWidgets(prev => [...prev, newWidget]);
    setShowWidgetPalette(false);
  }, []);

  const handleRemoveWidget = useCallback((widgetKey: string) => {
    setWidgets(prev => prev.filter(w => w.i !== widgetKey));
  }, []);

  const handleResetWidget = useCallback((widgetKey: string) => {
    // Unlock widget and clear position so algorithm will reposition it optimally
    setWidgets(prev => prev.map(widget => 
      widget.i === widgetKey 
        ? { ...widget, isLocked: false, x: 0, y: 0 }
        : widget
    ));
  }, []);

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true);
    // Force re-render of all widgets
    setWidgets(prev => [...prev]);
    setTimeout(() => setIsRefreshing(false), 500);
  }, []);

  const handleReset = useCallback(() => {
    if (typeof window === 'undefined') return;
    
    const confirmed = window.confirm(
      'Are you sure you want to reset the dashboard to default layout? This will clear all saved positions and widget configurations.'
    );
    
    if (confirmed) {
      // Clear localStorage
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (error) {
        console.error('Failed to clear dashboard state:', error);
      }
      
      // Reset to default widgets
      setWidgets(DEFAULT_WIDGETS);
    }
  }, []);

  const existingWidgetIds = widgets.map(w => w.widgetId);

  return (
    <WidgetSpacingProvider defaultSpacing="compact">
      <div className="h-screen flex flex-col bg-background">
        <div className="p-2 border-b">
          <DashboardToolbar
            widgetCount={widgets.length}
            availableToAdd={AVAILABLE_WIDGETS.filter(w => !existingWidgetIds.includes(w.id)).length}
            onAddWidget={() => setShowWidgetPalette(!showWidgetPalette)}
            onRefresh={handleRefresh}
            onReset={handleReset}
            isRefreshing={isRefreshing}
          />
        </div>

        {showWidgetPalette && (
          <div className="p-2 border-b bg-muted/30">
            <WidgetPalette
              onAddWidget={handleAddWidget}
              onClose={() => setShowWidgetPalette(false)}
              existingWidgets={existingWidgetIds}
            />
          </div>
        )}

        <div className="flex-1 overflow-auto p-2">
          <WidgetGrid
            widgets={widgets}
            portfolioId={portfolioId}
            onLayoutChange={handleLayoutChange}
            onRemoveWidget={handleRemoveWidget}
            onResetWidget={handleResetWidget}
          />
        </div>
      </div>
    </WidgetSpacingProvider>
  );
}