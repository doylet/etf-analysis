/**
 * Widget Palette Component
 * Provides a palette for adding new widgets to the dashboard
 */

'use client';

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  WIDGET_REGISTRY, 
  WIDGET_CATEGORIES, 
  WidgetType, 
  WidgetCategory 
} from '@/types/widget-config';
import { useWidgetManagement } from '@/contexts/WidgetManagementContext';
import { Plus, Search, Grid, BarChart, TrendingUp, Target, DollarSign, Activity } from 'lucide-react';

const WIDGET_ICONS = {
  'chart-line': BarChart,
  'pie-chart': Grid,
  'grid': Grid,
  'trending-up': TrendingUp,
  'bar-chart': BarChart,
  'dollar-sign': DollarSign,
  'activity': Activity,
  'timeline': TrendingUp,
  'shuffle': Grid,
  'newspaper': Grid,
  'target': Target,
  'settings': Grid
} as const;

interface WidgetPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export function WidgetPalette({ isOpen, onClose }: WidgetPaletteProps) {
  const { actions } = useWidgetManagement();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<WidgetCategory | 'all'>('all');

  const filteredWidgets = useMemo(() => {
    const widgets = Object.values(WIDGET_REGISTRY);
    
    return widgets.filter(widget => {
      const matchesSearch = searchQuery === '' || 
        widget.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        widget.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        widget.tags?.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      
      const matchesCategory = selectedCategory === 'all' || widget.category === selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }, [searchQuery, selectedCategory]);

  const handleAddWidget = (type: WidgetType) => {
    actions.addWidget(type);
    onClose();
  };

  const getWidgetIcon = (iconName: string) => {
    const Icon = WIDGET_ICONS[iconName as keyof typeof WIDGET_ICONS] || Grid;
    return <Icon className="h-5 w-5" />;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <Card className="relative z-10 w-[800px] max-h-[80vh] overflow-hidden">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add Widget
          </CardTitle>
          <CardDescription>
            Choose from available widgets to add to your dashboard
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search widgets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Category Filter */}
          <Tabs 
            value={selectedCategory} 
            onValueChange={(value) => setSelectedCategory(value as WidgetCategory | 'all')}
          >
            <TabsList className="grid w-full grid-cols-7">
              <TabsTrigger value="all">All</TabsTrigger>
              {WIDGET_CATEGORIES.map((category) => (
                <TabsTrigger 
                  key={category.id} 
                  value={category.id}
                  className="text-xs"
                >
                  {category.name}
                </TabsTrigger>
              ))}
            </TabsList>

            <TabsContent value={selectedCategory} className="mt-4">
              <div className="grid grid-cols-2 gap-4 max-h-[400px] overflow-y-auto">
                {filteredWidgets.map((widget) => (
                  <Card 
                    key={widget.type} 
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => handleAddWidget(widget.type)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 p-2 rounded-lg bg-primary/10">
                          {getWidgetIcon(widget.icon || 'grid')}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm mb-1 truncate">
                            {widget.name}
                          </h4>
                          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                            {widget.description}
                          </p>
                          
                          <div className="flex items-center gap-2 flex-wrap">
                            <Badge 
                              variant="secondary" 
                              className="text-xs"
                              style={{ 
                                backgroundColor: WIDGET_CATEGORIES.find(c => c.id === widget.category)?.color + '20',
                                borderColor: WIDGET_CATEGORIES.find(c => c.id === widget.category)?.color
                              }}
                            >
                              {WIDGET_CATEGORIES.find(c => c.id === widget.category)?.name}
                            </Badge>
                            
                            {widget.requiresPortfolio && (
                              <Badge variant="outline" className="text-xs">
                                Portfolio
                              </Badge>
                            )}
                          </div>
                          
                          {widget.tags && (
                            <div className="flex gap-1 mt-2 flex-wrap">
                              {widget.tags.slice(0, 3).map((tag: string) => (
                                <Badge key={tag} variant="outline" className="text-xs">
                                  {tag}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>Default size: {widget.defaultSize.w}×{widget.defaultSize.h}</span>
                          <Button size="sm" variant="ghost" className="h-6 px-2">
                            <Plus className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
              
              {filteredWidgets.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-muted-foreground mb-2">No widgets found</div>
                  <p className="text-sm text-muted-foreground">
                    Try adjusting your search criteria or category filter
                  </p>
                </div>
              )}
            </TabsContent>
          </Tabs>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}