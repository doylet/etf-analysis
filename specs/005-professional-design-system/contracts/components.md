# Component API Contracts

**Version**: 1.0.0  
**Purpose**: Define React component interfaces for financial UI components  
**Dependencies**: React 19.2+, design-tokens.md

## Core Financial Components

### MetricCard

**Purpose**: Display financial metrics with consistent formatting and visual hierarchy

```typescript
export interface MetricCardProps {
  // Content (Required)
  title: string;
  value: string | number;
  
  // Optional Content
  subtitle?: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string }>;
  
  // Trend Indicators
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: string | number;
    label?: string;
    period?: string; // e.g., "vs yesterday", "YTD"
  };
  
  // Visual Variants
  variant?: 'default' | 'highlighted' | 'compact' | 'minimal';
  size?: 'sm' | 'base' | 'lg';
  colorScheme?: 'auto' | 'positive' | 'negative' | 'neutral';
  
  // Layout
  orientation?: 'vertical' | 'horizontal';
  iconPosition?: 'top' | 'left' | 'right';
  
  // Formatting
  formatValue?: (value: string | number) => string;
  currency?: string;
  precision?: number;
  
  // Interactions
  onClick?: () => void;
  href?: string;
  loading?: boolean;
  
  // Accessibility
  'aria-label'?: string;
  'aria-describedby'?: string;
  'data-testid'?: string;
  
  // Custom Styling
  className?: string;
  contentClassName?: string;
  iconClassName?: string;
}

// Usage Example:
<MetricCard 
  title="Portfolio Value"
  value={121297.49}
  currency="USD"
  trend={{ direction: 'up', value: '+2.34%', label: 'vs yesterday' }}
  variant="highlighted"
  icon={DollarSign}
  aria-label="Current portfolio value with daily change"
/>
```

### DataTable

**Purpose**: Display tabular financial data with sorting and accessibility features

```typescript
export interface DataTableProps<T = any> {
  // Data (Required)
  data: T[];
  columns: ColumnDefinition<T>[];
  
  // Core Features
  sortable?: boolean;
  selectable?: boolean;
  pagination?: boolean | PaginationConfig;
  
  // Default States
  defaultSort?: {
    columnKey: keyof T;
    direction: 'asc' | 'desc';
  };
  defaultPageSize?: number;
  
  // Visual Options
  variant?: 'default' | 'compact' | 'spacious' | 'bordered';
  striped?: boolean;
  showHeader?: boolean;
  
  // Loading & Empty States
  loading?: boolean;
  loadingRows?: number;
  emptyMessage?: string;
  emptyIcon?: React.ComponentType;
  
  // Event Handlers
  onSort?: (columnKey: keyof T, direction: 'asc' | 'desc') => void;
  onRowClick?: (row: T, index: number) => void;
  onSelectionChange?: (selectedRows: T[]) => void;
  
  // Accessibility
  'aria-label'?: string;
  caption?: string;
  'data-testid'?: string;
  
  // Custom Styling
  className?: string;
  headerClassName?: string;
  bodyClassName?: string;
  rowClassName?: (row: T, index: number) => string;
}

export interface ColumnDefinition<T> {
  // Identity (Required)
  key: keyof T;
  label: string;
  
  // Display Options
  align?: 'left' | 'center' | 'right';
  width?: string | number;
  minWidth?: string | number;
  
  // Functionality
  sortable?: boolean;
  searchable?: boolean;
  
  // Formatting
  formatter?: (value: any, row: T) => React.ReactNode;
  dataType?: 'text' | 'number' | 'currency' | 'percentage' | 'date';
  currency?: string;
  precision?: number;
  
  // Custom Rendering
  render?: (value: any, row: T, index: number) => React.ReactNode;
  headerRender?: (column: ColumnDefinition<T>) => React.ReactNode;
  
  // Styling
  className?: string;
  headerClassName?: string;
  cellClassName?: string;
  
  // Accessibility
  'aria-label'?: string;
  'aria-sort'?: 'ascending' | 'descending' | 'none';
}

export interface PaginationConfig {
  pageSize: number;
  showPageSizeOptions?: boolean;
  pageSizeOptions?: number[];
  showQuickJumper?: boolean;
  showTotal?: boolean | ((total: number, range: [number, number]) => string);
}

// Usage Example:
<DataTable
  data={holdings}
  columns={[
    { 
      key: 'symbol', 
      label: 'Symbol', 
      align: 'left',
      sortable: true 
    },
    { 
      key: 'currentValue', 
      label: 'Market Value', 
      align: 'right',
      dataType: 'currency',
      currency: 'USD',
      sortable: true 
    },
    { 
      key: 'unrealizedPnL', 
      label: 'Unrealized P&L', 
      align: 'right',
      dataType: 'percentage',
      precision: 2,
      formatter: (value) => <PercentageChange value={value} />
    }
  ]}
  sortable
  striped
  aria-label="Portfolio holdings data"
/>
```

### FinancialAmount

**Purpose**: Consistent display of currency amounts with proper formatting

```typescript
export interface FinancialAmountProps {
  // Value (Required)
  value: number | string;
  
  // Formatting
  currency?: string;
  locale?: string;
  precision?: number;
  showCurrency?: boolean;
  showSign?: boolean;
  abbreviated?: boolean; // 1K, 1M, 1B format
  
  // Visual Options
  size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl';
  weight?: 'normal' | 'medium' | 'semibold' | 'bold';
  color?: 'auto' | 'positive' | 'negative' | 'neutral' | 'inherit';
  
  // Behavior
  animate?: boolean; // Animate value changes
  highlightChange?: boolean;
  
  // Custom Formatting
  formatter?: (value: number, currency: string) => string;
  
  // Accessibility
  'aria-label'?: string;
  'data-testid'?: string;
  
  // Custom Styling
  className?: string;
  currencyClassName?: string;
  valueClassName?: string;
}

// Usage Example:
<FinancialAmount 
  value={121297.49}
  currency="USD"
  size="lg"
  color="auto"
  showSign
  animate
  aria-label="Current portfolio value"
/>
```

### PercentageChange

**Purpose**: Display percentage changes with appropriate color coding

```typescript
export interface PercentageChangeProps {
  // Value (Required)
  value: number;
  
  // Display Options
  showSign?: boolean;
  showIcon?: boolean;
  precision?: number;
  
  // Visual Variants
  size?: 'xs' | 'sm' | 'base' | 'lg';
  variant?: 'inline' | 'badge' | 'minimal' | 'prominent';
  
  // Icon Options
  iconPosition?: 'left' | 'right';
  customIcons?: {
    positive?: React.ComponentType;
    negative?: React.ComponentType;
    neutral?: React.ComponentType;
  };
  
  // Behavior
  animate?: boolean;
  threshold?: number; // Minimum change to show color
  
  // Accessibility
  'aria-label'?: string;
  'data-testid'?: string;
  
  // Custom Styling
  className?: string;
  iconClassName?: string;
}

// Usage Example:
<PercentageChange 
  value={2.34}
  showSign
  showIcon
  variant="badge"
  precision={2}
  aria-label="Daily change percentage"
/>
```

### StatusIndicator

**Purpose**: Visual status indicators for financial states

```typescript
export interface StatusIndicatorProps {
  // Status (Required)
  status: 'positive' | 'negative' | 'neutral' | 'warning' | 'info' | 'error';
  
  // Display Options
  variant?: 'dot' | 'badge' | 'pill' | 'outline';
  size?: 'xs' | 'sm' | 'base' | 'lg';
  
  // Content
  label?: string;
  icon?: React.ComponentType;
  
  // Accessibility
  'aria-label'?: string;
  'data-testid'?: string;
  
  // Custom Styling
  className?: string;
}

// Usage Example:
<StatusIndicator 
  status="positive"
  variant="dot"
  label="Profitable"
  aria-label="Position is currently profitable"
/>
```

## Layout Components

### GridLayout

**Purpose**: Responsive grid layout for financial dashboards

```typescript
export interface GridLayoutProps {
  // Layout Configuration
  columns?: number | { sm?: number; md?: number; lg?: number; xl?: number };
  gap?: 'xs' | 'sm' | 'base' | 'lg' | 'xl';
  
  // Responsive Behavior
  breakpoints?: {
    sm?: number;
    md?: number; 
    lg?: number;
    xl?: number;
  };
  
  // Content
  children: React.ReactNode;
  
  // Accessibility
  'aria-label'?: string;
  'data-testid'?: string;
  
  // Custom Styling
  className?: string;
}

// Usage Example:
<GridLayout 
  columns={{ sm: 1, md: 2, lg: 4 }}
  gap="lg"
  aria-label="Portfolio metrics grid"
>
  <MetricCard title="Total Value" value={121297} />
  <MetricCard title="Day Change" value={1250} />
</GridLayout>
```

## Compound Components

### MetricGroup

**Purpose**: Group related metrics with consistent spacing

```typescript
export interface MetricGroupProps {
  // Content
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  
  // Layout
  orientation?: 'vertical' | 'horizontal';
  spacing?: 'xs' | 'sm' | 'base' | 'lg';
  
  // Visual Options
  bordered?: boolean;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  
  // Accessibility
  'aria-label'?: string;
  'data-testid'?: string;
  
  // Custom Styling
  className?: string;
  headerClassName?: string;
  contentClassName?: string;
}

// Usage Example:
<MetricGroup 
  title="Portfolio Performance"
  orientation="horizontal"
  spacing="lg"
  bordered
>
  <MetricCard title="Total Return" value="12.5%" />
  <MetricCard title="YTD Return" value="8.2%" />
</MetricGroup>
```

## Error Boundaries & Loading States

### LoadingState

**Purpose**: Consistent loading indicators for financial components

```typescript
export interface LoadingStateProps {
  // Display Options
  variant?: 'spinner' | 'skeleton' | 'pulse' | 'dots';
  size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl';
  
  // Content
  message?: string;
  overlay?: boolean;
  
  // Accessibility
  'aria-label'?: string;
  
  // Custom Styling
  className?: string;
}
```

## Component Composition Rules

### Inheritance Hierarchy
```typescript
interface BaseFinancialComponentProps {
  'data-testid'?: string;
  className?: string;
  'aria-label'?: string;
}

// All financial components extend this base
interface MetricCardProps extends BaseFinancialComponentProps { /* ... */ }
interface DataTableProps extends BaseFinancialComponentProps { /* ... */ }
```

### Theme Integration
All components MUST accept theme context through:
```typescript
const theme = useDesignTokens();
const className = cn(baseClassName, themeClassName, props.className);
```

### Accessibility Requirements
1. All interactive components MUST support keyboard navigation
2. All data displays MUST provide appropriate ARIA labels
3. All color-coded information MUST include alternative indicators
4. All form components MUST support screen readers

### Performance Requirements
1. Component rendering MUST complete within 16ms (60fps)
2. Large tables MUST implement virtualization for >100 rows
3. Animation duration MUST not exceed 300ms
4. Bundle size per component MUST not exceed 10KB