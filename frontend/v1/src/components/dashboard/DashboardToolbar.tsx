/**
 * Dashboard Toolbar Component
 * Provides controls for managing the dashboard layout and widgets
 */

'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { useWidgetManagement } from '@/contexts/WidgetManagementContext';
import { 
  Plus, 
  Settings, 
  Download, 
  Upload, 
  RotateCcw, 
  Save, 
  Edit3, 
  Eye,
  Grid3x3,
  MoreHorizontal,
  RefreshCw
} from 'lucide-react';

interface DashboardToolbarProps {
  onAddWidget: () => void;
  onRefreshAll: () => void;
  portfolioId?: string;
}

export function DashboardToolbar({ 
  onAddWidget, 
  onRefreshAll,
  portfolioId 
}: DashboardToolbarProps) {
  const { state, actions } = useWidgetManagement();
  const [isEditMode, setIsEditMode] = useState(false);

  const handleToggleEditMode = () => {
    setIsEditMode(!isEditMode);
    actions.toggleEditMode();
  };

  const handleExportLayout = () => {
    const layoutData = actions.exportLayout();
    const blob = new Blob([layoutData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard-layout-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImportLayout = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const success = actions.importLayout(content);
        if (success) {
          console.log('Layout imported successfully');
        } else {
          console.error('Failed to import layout');
        }
      } catch (error) {
        console.error('Error importing layout:', error);
      }
    };
    reader.readAsText(file);
  };

  const visibleWidgets = state.widgets.filter(w => w.isVisible && !w.isMinimized);
  const totalWidgets = state.widgets.length;

  return (
    <div className="flex items-center justify-between p-4 bg-background border-b border-border">
      {/* Left side - Dashboard info and mode toggle */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Grid3x3 className="h-5 w-5 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Dashboard</h2>
          {portfolioId && (
            <Badge variant="secondary" className="text-xs">
              Portfolio: {portfolioId}
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>{visibleWidgets.length} of {totalWidgets} widgets visible</span>
        </div>
      </div>

      {/* Right side - Actions */}
      <div className="flex items-center gap-2">
        {/* Edit Mode Toggle */}
        <Button
          variant={isEditMode ? "default" : "outline"}
          size="sm"
          onClick={handleToggleEditMode}
          className="gap-2"
        >
          {isEditMode ? <Eye className="h-4 w-4" /> : <Edit3 className="h-4 w-4" />}
          {isEditMode ? 'Exit Edit' : 'Edit Layout'}
        </Button>

        {/* Add Widget */}
        <Button
          onClick={onAddWidget}
          size="sm"
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Widget
        </Button>

        {/* Refresh All */}
        <Button
          variant="outline"
          size="sm"
          onClick={onRefreshAll}
          className="gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh All
        </Button>

        {/* More Options */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          
          <DropdownMenuContent align="end" className="w-[200px]">
            <DropdownMenuItem onClick={() => actions.saveLayout('Custom Layout')}>
              <Save className="h-4 w-4 mr-2" />
              Save Layout
            </DropdownMenuItem>
            
            <DropdownMenuItem onClick={handleExportLayout}>
              <Download className="h-4 w-4 mr-2" />
              Export Layout
            </DropdownMenuItem>
            
            <DropdownMenuItem asChild>
              <label className="cursor-pointer flex items-center">
                <Upload className="h-4 w-4 mr-2" />
                Import Layout
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImportLayout}
                  className="hidden"
                />
              </label>
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem onClick={() => actions.resetLayout()}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset to Default
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem>
              <Settings className="h-4 w-4 mr-2" />
              Dashboard Settings
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}