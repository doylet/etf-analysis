/**
 * Widget Management Context
 * Provides state management for dynamic widget management
 */

'use client';

import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { 
  WidgetConfig, 
  WidgetType, 
  WidgetAction, 
  DashboardLayout, 
  WIDGET_REGISTRY 
} from '@/types/widget-config';

interface WidgetManagementState {
  widgets: WidgetConfig[];
  selectedWidget: string | null;
  isEditMode: boolean;
  draggedWidget: string | null;
  layout: DashboardLayout | null;
  availableWidgets: WidgetType[];
}

interface WidgetManagementContext {
  state: WidgetManagementState;
  actions: {
    addWidget: (type: WidgetType, position?: { x: number; y: number }) => void;
    removeWidget: (widgetId: string) => void;
    updateWidget: (widgetId: string, config: Partial<WidgetConfig>) => void;
    moveWidget: (widgetId: string, position: { x: number; y: number; w: number; h: number }) => void;
    selectWidget: (widgetId: string | null) => void;
    toggleEditMode: () => void;
    minimizeWidget: (widgetId: string) => void;
    maximizeWidget: (widgetId: string) => void;
    setDraggedWidget: (widgetId: string | null) => void;
    saveLayout: (name: string, description?: string) => void;
    loadLayout: (layout: DashboardLayout) => void;
    resetLayout: () => void;
    exportLayout: () => string;
    importLayout: (layoutJson: string) => boolean;
  };
}

const initialState: WidgetManagementState = {
  widgets: [],
  selectedWidget: null,
  isEditMode: false,
  draggedWidget: null,
  layout: null,
  availableWidgets: Object.keys(WIDGET_REGISTRY) as WidgetType[]
};

// Default layout with core widgets
const DEFAULT_WIDGETS: WidgetConfig[] = [
  {
    id: 'portfolio-summary-1',
    type: 'portfolio-summary',
    title: 'Portfolio Summary',
    position: { x: 0, y: 0, w: 6, h: 4 },
    isVisible: true,
    isMinimized: false,
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    id: 'holdings-breakdown-1',
    type: 'holdings-breakdown',
    title: 'Holdings Breakdown',
    position: { x: 6, y: 0, w: 6, h: 5 },
    isVisible: true,
    isMinimized: false,
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    id: 'correlation-matrix-1',
    type: 'correlation-matrix',
    title: 'Correlation Matrix',
    position: { x: 0, y: 4, w: 8, h: 6 },
    isVisible: true,
    isMinimized: false,
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    id: 'monte-carlo-1',
    type: 'monte-carlo',
    title: 'Monte Carlo Simulation',
    position: { x: 8, y: 5, w: 4, h: 5 },
    isVisible: true,
    isMinimized: false,
    createdAt: new Date(),
    updatedAt: new Date()
  }
];

function widgetReducer(state: WidgetManagementState, action: WidgetAction): WidgetManagementState {
  switch (action.type) {
    case 'add': {
      if (!action.payload.widgetType) return state;
      
      const widgetDef = WIDGET_REGISTRY[action.payload.widgetType];
      const newWidget: WidgetConfig = {
        id: `${action.payload.widgetType}-${Date.now()}`,
        type: action.payload.widgetType,
        title: widgetDef.name,
        position: action.payload.position || {
          x: 0,
          y: 0,
          w: widgetDef.defaultSize.w,
          h: widgetDef.defaultSize.h
        },
        options: action.payload.options || {},
        isVisible: true,
        isMinimized: false,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      return {
        ...state,
        widgets: [...state.widgets, newWidget],
        selectedWidget: newWidget.id
      };
    }

    case 'remove': {
      if (!action.payload.widgetId) return state;
      
      return {
        ...state,
        widgets: state.widgets.filter(w => w.id !== action.payload.widgetId),
        selectedWidget: state.selectedWidget === action.payload.widgetId ? null : state.selectedWidget
      };
    }

    case 'update': {
      if (!action.payload.widgetId || !action.payload.config) return state;
      
      return {
        ...state,
        widgets: state.widgets.map(widget => 
          widget.id === action.payload.widgetId 
            ? { ...widget, ...action.payload.config, updatedAt: new Date() }
            : widget
        )
      };
    }

    case 'move': {
      if (!action.payload.widgetId || !action.payload.position) return state;
      
      return {
        ...state,
        widgets: state.widgets.map(widget => 
          widget.id === action.payload.widgetId 
            ? { ...widget, position: action.payload.position!, updatedAt: new Date() }
            : widget
        )
      };
    }

    case 'resize': {
      if (!action.payload.widgetId || !action.payload.position) return state;
      
      return {
        ...state,
        widgets: state.widgets.map(widget => 
          widget.id === action.payload.widgetId 
            ? { ...widget, position: action.payload.position!, updatedAt: new Date() }
            : widget
        )
      };
    }

    case 'minimize': {
      if (!action.payload.widgetId) return state;
      
      return {
        ...state,
        widgets: state.widgets.map(widget => 
          widget.id === action.payload.widgetId 
            ? { ...widget, isMinimized: true, updatedAt: new Date() }
            : widget
        )
      };
    }

    case 'maximize': {
      if (!action.payload.widgetId) return state;
      
      return {
        ...state,
        widgets: state.widgets.map(widget => 
          widget.id === action.payload.widgetId 
            ? { ...widget, isMinimized: false, updatedAt: new Date() }
            : widget
        )
      };
    }

    case 'configure': {
      if (!action.payload.widgetId || !action.payload.options) return state;
      
      return {
        ...state,
        widgets: state.widgets.map(widget => 
          widget.id === action.payload.widgetId 
            ? { ...widget, options: { ...widget.options, ...action.payload.options }, updatedAt: new Date() }
            : widget
        )
      };
    }

    default:
      return state;
  }
}

const WidgetManagementContext = createContext<WidgetManagementContext | null>(null);

export function WidgetManagementProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(widgetReducer, {
    ...initialState,
    widgets: DEFAULT_WIDGETS
  });

  // Actions
  const addWidget = useCallback((type: WidgetType, position?: { x: number; y: number }) => {
    dispatch({
      type: 'add',
      payload: { widgetType: type, position }
    });
  }, []);

  const removeWidget = useCallback((widgetId: string) => {
    dispatch({
      type: 'remove',
      payload: { widgetId }
    });
  }, []);

  const updateWidget = useCallback((widgetId: string, config: Partial<WidgetConfig>) => {
    dispatch({
      type: 'update',
      payload: { widgetId, config }
    });
  }, []);

  const moveWidget = useCallback((widgetId: string, position: { x: number; y: number; w: number; h: number }) => {
    dispatch({
      type: 'move',
      payload: { widgetId, position }
    });
  }, []);

  const selectWidget = useCallback((widgetId: string | null) => {
    // Note: This would normally dispatch an action, but since selectedWidget isn't in the reducer
    // we'll handle it differently in a real implementation
  }, []);

  const toggleEditMode = useCallback(() => {
    // Toggle edit mode implementation
  }, []);

  const minimizeWidget = useCallback((widgetId: string) => {
    dispatch({
      type: 'minimize',
      payload: { widgetId }
    });
  }, []);

  const maximizeWidget = useCallback((widgetId: string) => {
    dispatch({
      type: 'maximize',
      payload: { widgetId }
    });
  }, []);

  const setDraggedWidget = useCallback((widgetId: string | null) => {
    // Handle drag state
  }, []);

  const saveLayout = useCallback((name: string, description?: string) => {
    const layout: DashboardLayout = {
      id: `layout-${Date.now()}`,
      name,
      description,
      widgets: state.widgets,
      createdAt: new Date(),
      updatedAt: new Date(),
      isDefault: false
    };
    
    // Save to localStorage or backend
    localStorage.setItem(`dashboard-layout-${layout.id}`, JSON.stringify(layout));
  }, [state.widgets]);

  const loadLayout = useCallback((layout: DashboardLayout) => {
    // Load layout implementation
  }, []);

  const resetLayout = useCallback(() => {
    // Reset to default layout
  }, []);

  const exportLayout = useCallback(() => {
    return JSON.stringify({
      widgets: state.widgets,
      exportedAt: new Date().toISOString()
    });
  }, [state.widgets]);

  const importLayout = useCallback((layoutJson: string) => {
    try {
      const imported = JSON.parse(layoutJson);
      if (imported.widgets && Array.isArray(imported.widgets)) {
        // Validate and import widgets
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, []);

  // Auto-save layout changes
  useEffect(() => {
    const autoSaveTimer = setTimeout(() => {
      localStorage.setItem('dashboard-layout-autosave', JSON.stringify(state.widgets));
    }, 1000);

    return () => clearTimeout(autoSaveTimer);
  }, [state.widgets]);

  const contextValue: WidgetManagementContext = {
    state,
    actions: {
      addWidget,
      removeWidget,
      updateWidget,
      moveWidget,
      selectWidget,
      toggleEditMode,
      minimizeWidget,
      maximizeWidget,
      setDraggedWidget,
      saveLayout,
      loadLayout,
      resetLayout,
      exportLayout,
      importLayout
    }
  };

  return (
    <WidgetManagementContext.Provider value={contextValue}>
      {children}
    </WidgetManagementContext.Provider>
  );
}

export function useWidgetManagement() {
  const context = useContext(WidgetManagementContext);
  if (!context) {
    throw new Error('useWidgetManagement must be used within a WidgetManagementProvider');
  }
  return context;
}