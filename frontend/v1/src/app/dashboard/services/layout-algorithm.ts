/**
 * Dynamic Layout Algorithm
 * Intelligently arranges dashboard widgets based on content requirements, priority, and available space
 */

import { Layout } from 'react-grid-layout';
import { getWidgetMetadata, WidgetMetadata } from '../widgets/widget-metadata';

export type Breakpoint = 'lg' | 'md' | 'sm' | 'xs' | 'xxs';

export interface ResponsiveSize {
  w: number;
  h: number;
}

interface BreakpointConfig {
  cols: number;
  strategy: LayoutStrategy;
  maxWidgetsPerRow: number;
  prioritizeFold: boolean;
}

type LayoutStrategy = 'maximize-utilization' | 'balanced-packing' | 'priority-stacking' | 'strict-priority' | 'essential-only';

const BREAKPOINT_CONFIGS: Record<Breakpoint, BreakpointConfig> = {
  lg: {
    cols: 12,
    strategy: 'maximize-utilization',
    maxWidgetsPerRow: 3,
    prioritizeFold: false,
  },
  md: {
    cols: 10,
    strategy: 'balanced-packing',
    maxWidgetsPerRow: 2,
    prioritizeFold: true,
  },
  sm: {
    cols: 6,
    strategy: 'priority-stacking',
    maxWidgetsPerRow: 1,
    prioritizeFold: true,
  },
  xs: {
    cols: 4,
    strategy: 'strict-priority',
    maxWidgetsPerRow: 1,
    prioritizeFold: true,
  },
  xxs: {
    cols: 2,
    strategy: 'essential-only',
    maxWidgetsPerRow: 1,
    prioritizeFold: true,
  },
};

interface WidgetInstance {
  i: string;
  widgetId: string;
  x?: number;
  y?: number;
  w?: number;
  h?: number;
  isLocked?: boolean;
}

/**
 * Calculate optimal size for a widget based on content type and available space
 */
function calculateOptimalSize(
  metadata: WidgetMetadata,
  breakpoint: Breakpoint
): ResponsiveSize {
  const config = BREAKPOINT_CONFIGS[breakpoint];
  
  // Rule 1: Full-width widgets always span all columns
  if (metadata.requiresFullWidth) {
    return { w: config.cols, h: metadata.minSize.h };
  }
  
  // Rule 2: Maintain aspect ratio for square widgets
  if (metadata.contentType === 'square') {
    const size = Math.min(
      Math.floor(config.cols / 2),
      metadata.minSize.w,
      8 // Cap at 8 to avoid huge squares
    );
    return { w: size, h: size };
  }
  
  // Rule 3: Width-heavy widgets get proportionally more width
  if (metadata.contentType === 'width-heavy') {
    return {
      w: Math.max(metadata.minSize.w, Math.min(Math.floor(config.cols * 0.6), config.cols)),
      h: metadata.minSize.h,
    };
  }
  
  // Rule 4: Height-heavy widgets get proportionally more height
  if (metadata.contentType === 'height-heavy') {
    return {
      w: Math.max(metadata.minSize.w, Math.floor(config.cols * 0.5)),
      h: Math.max(metadata.minSize.h, metadata.minSize.h + 1),
    };
  }
  
  // Rule 5: Compact widgets stay small
  if (metadata.contentType === 'compact') {
    return { ...metadata.minSize };
  }
  
  // Rule 6: Balanced widgets use default sizing
  return {
    w: Math.min(metadata.minSize.w, config.cols),
    h: metadata.minSize.h,
  };
}

/**
 * Check if a space in the grid is free
 */
function isSpaceFree(
  x: number,
  y: number,
  size: ResponsiveSize,
  occupied: Set<string>,
  cols: number
): boolean {
  // Check bounds
  if (x < 0 || x + size.w > cols || y < 0) {
    return false;
  }
  
  // Check if any cell is occupied
  for (let row = y; row < y + size.h; row++) {
    for (let col = x; col < x + size.w; col++) {
      if (occupied.has(`${col},${row}`)) {
        return false;
      }
    }
  }
  
  return true;
}

/**
 * Find the next available row in the grid
 */
function findNextFreeRow(occupied: Set<string>, cols: number): number {
  let row = 0;
  
  while (row <= 100) {
    let rowOccupied = false;
    for (let col = 0; col < cols; col++) {
      if (occupied.has(`${col},${row}`)) {
        rowOccupied = true;
        break;
      }
    }
    
    if (!rowOccupied && row > 0) {
      return row;
    }
    
    row++;
  }
  
  return row;
}

/**
 * Find the best position for a widget in the grid
 * Prioritizes filling horizontal space before moving to new rows
 */
function findBestPosition(
  size: ResponsiveSize,
  cols: number,
  occupied: Set<string>,
  requiresFullWidth: boolean,
  startRow: number = 0
): { x: number; y: number } {
  if (requiresFullWidth) {
    // Full-width widgets start at x=0 on new row
    let row = startRow;
    while (true) {
      if (isSpaceFree(0, row, size, occupied, cols)) {
        return { x: 0, y: row };
      }
      row++;
      
      // Safety limit
      if (row > 100) break;
    }
    return { x: 0, y: row };
  }
  
  // Prioritize horizontal packing: scan row by row, left to right
  // This ensures widgets fill horizontally before moving to next row
  for (let y = startRow; y < startRow + 50; y++) {
    for (let x = 0; x <= cols - size.w; x++) {
      if (isSpaceFree(x, y, size, occupied, cols)) {
        return { x, y };
      }
    }
  }
  
  // Fallback: bottom of grid
  return { x: 0, y: findNextFreeRow(occupied, cols) };
}

/**
 * Mark grid cells as occupied
 */
function markOccupied(
  x: number,
  y: number,
  size: ResponsiveSize,
  occupied: Set<string>
): void {
  for (let row = y; row < y + size.h; row++) {
    for (let col = x; col < x + size.w; col++) {
      occupied.add(`${col},${row}`);
    }
  }
}

/**
 * Calculate maximum size a widget can expand to without colliding
 * Now respects widget size config - no automatic expansion beyond configured size
 */
function calculateMaxExpandedSize(
  x: number,
  y: number,
  currentSize: ResponsiveSize,
  cols: number,
  occupied: Set<string>,
  metadata: WidgetMetadata
): ResponsiveSize {
  // Respect the widget's configured size - don't expand beyond it
  // The configured size (minSize) is actually the preferred/max size
  return currentSize;
}

/**
 * Generate optimal layout for widgets at a specific breakpoint
 * Respects locked widgets (manually positioned by user) and optimizes unlocked widgets
 */
export function generateOptimalLayout(
  widgets: WidgetInstance[],
  breakpoint: Breakpoint
): Layout[] {
  const config = BREAKPOINT_CONFIGS[breakpoint];
  const layout: Layout[] = [];
  const occupied = new Set<string>();
  
  // Separate locked and unlocked widgets
  const lockedWidgets = widgets.filter(w => w.isLocked);
  const unlockedWidgets = widgets.filter(w => !w.isLocked);
  
  // First, place locked widgets at their existing positions
  for (const widget of lockedWidgets) {
    if (widget.x !== undefined && widget.y !== undefined && widget.w && widget.h) {
      layout.push({
        i: widget.i,
        x: widget.x,
        y: widget.y,
        w: widget.w,
        h: widget.h,
      });
      
      // Mark their space as occupied
      markOccupied(widget.x, widget.y, { w: widget.w, h: widget.h }, occupied);
    }
  }
  
  // Sort unlocked widgets by priority (high to low)
  const sortedUnlocked = [...unlockedWidgets].sort((a, b) => {
    const metaA = getWidgetMetadata(a.widgetId);
    const metaB = getWidgetMetadata(b.widgetId);
    return metaB.priority - metaA.priority;
  });
  
  // Place unlocked widgets using algorithm
  let currentRow = 0;
  
  for (const widget of sortedUnlocked) {
    const metadata = getWidgetMetadata(widget.widgetId);
    const size = calculateOptimalSize(metadata, breakpoint);
    
    // Find best position
    const position = findBestPosition(
      size,
      config.cols,
      occupied,
      metadata.requiresFullWidth,
      currentRow
    );
    
    // Use the calculated size directly (no expansion)
    layout.push({
      i: widget.i,
      x: position.x,
      y: position.y,
      w: size.w,
      h: size.h,
    });
    
    // Mark cells as occupied using the calculated size
    markOccupied(position.x, position.y, size, occupied);
    
    // Update current row for next placement
    if (metadata.requiresFullWidth) {
      currentRow = position.y + size.h;
    } else {
      // Try to stay on same row for next widget if possible
      currentRow = position.y;
    }
  }
  
  return layout;
}

/**
 * Generate layouts for all breakpoints
 */
export function generateAllLayouts(widgets: WidgetInstance[]): Record<Breakpoint, Layout[]> {
  return {
    lg: generateOptimalLayout(widgets, 'lg'),
    md: generateOptimalLayout(widgets, 'md'),
    sm: generateOptimalLayout(widgets, 'sm'),
    xs: generateOptimalLayout(widgets, 'xs'),
    xxs: generateOptimalLayout(widgets, 'xxs'),
  };
}

/**
 * Calculate optimal size for a new widget being added
 */
export function getDefaultSizeForWidget(widgetId: string, breakpoint: Breakpoint): ResponsiveSize {
  const metadata = getWidgetMetadata(widgetId);
  return calculateOptimalSize(metadata, breakpoint);
}