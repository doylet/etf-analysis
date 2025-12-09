/**
 * Widget configuration interface following Interface Segregation Principle
 * Provides type-safe configuration for different widget types
 * 
 * Note: Holding interface is defined in data-model.md to avoid duplication
 */
export interface IWidgetConfiguration {
  /** Unique widget identifier */
  id: string;
  
  /** Widget type identifier */
  type: WidgetType;
  
  /** Human-readable widget title */
  title: string;
  
  /** Widget size configuration */
  size: WidgetSize;
  
  /** Auto-refresh interval in milliseconds (0 = disabled) */
  refreshInterval: number;
  
  /** Widget position in grid layout */
  position: GridPosition;
  
  /** Visibility and access settings */
  settings: WidgetSettings;
  
  /** Widget-specific configuration data */
  data: WidgetConfigData;
}

/**
 * Supported widget types
 */
export enum WidgetType {
  HOLDINGS = 'holdings',
  PORTFOLIO_SUMMARY = 'portfolio-summary',
  CORRELATION_MATRIX = 'correlation-matrix',
  MONTE_CARLO = 'monte-carlo'
}

/**
 * Widget size configuration
 */
export interface WidgetSize {
  /** Width in grid units */
  width: number;
  
  /** Height in grid units */
  height: number;
  
  /** Minimum width constraint */
  minWidth?: number;
  
  /** Minimum height constraint */
  minHeight?: number;
  
  /** Maximum width constraint */
  maxWidth?: number;
  
  /** Maximum height constraint */
  maxHeight?: number;
  
  /** Whether widget can be resized */
  resizable: boolean;
}

/**
 * Widget position in grid layout
 */
export interface GridPosition {
  /** X coordinate (column) */
  x: number;
  
  /** Y coordinate (row) */
  y: number;
  
  /** Z-index for layering */
  z?: number;
  
  /** Whether position is fixed */
  static?: boolean;
}

/**
 * Widget settings and permissions
 */
export interface WidgetSettings {
  /** Widget visibility */
  visible: boolean;
  
  /** Whether widget can be moved */
  draggable: boolean;
  
  /** Whether widget can be removed */
  removable: boolean;
  
  /** Access control level */
  accessLevel: AccessLevel;
  
  /** Theme override for widget */
  theme?: WidgetTheme;
  
  /** Custom CSS classes */
  cssClasses?: string[];
}

/**
 * Access control levels
 */
export enum AccessLevel {
  READ_ONLY = 'read-only',
  INTERACTIVE = 'interactive',
  CONFIGURABLE = 'configurable',
  ADMIN = 'admin'
}

/**
 * Widget theme configuration
 */
export interface WidgetTheme {
  /** Color scheme */
  colorScheme: 'light' | 'dark' | 'auto';
  
  /** Primary color */
  primaryColor?: string;
  
  /** Secondary color */
  secondaryColor?: string;
  
  /** Background color override */
  backgroundColor?: string;
  
  /** Border style */
  borderStyle?: BorderStyle;
  
  /** Font settings */
  typography?: TypographySettings;
}

/**
 * Border style configuration
 */
export interface BorderStyle {
  /** Border width in pixels */
  width: number;
  
  /** Border style */
  style: 'solid' | 'dashed' | 'dotted' | 'none';
  
  /** Border color */
  color: string;
  
  /** Border radius in pixels */
  radius: number;
}

/**
 * Typography settings
 */
export interface TypographySettings {
  /** Font family */
  fontFamily?: string;
  
  /** Base font size */
  fontSize?: number;
  
  /** Font weight */
  fontWeight?: number | string;
  
  /** Line height multiplier */
  lineHeight?: number;
  
  /** Letter spacing */
  letterSpacing?: number;
}

/**
 * Widget-specific configuration data (discriminated union)
 */
export type WidgetConfigData = 
  | HoldingsConfigData
  | PortfolioSummaryConfigData  
  | CorrelationMatrixConfigData
  | MonteCarloConfigData;

/**
 * Holdings widget configuration
 */
export interface HoldingsConfigData {
  type: WidgetType.HOLDINGS;
  
  /** Portfolio ID to display */
  portfolioId: string;
  
  /** Columns to show */
  columns: HoldingsColumn[];
  
  /** Sorting configuration */
  sorting: SortingConfig;
  
  /** Number of holdings to display */
  limit?: number;
  
  /** Grouping options */
  groupBy?: 'sector' | 'region' | 'assetClass';
}

/**
 * Portfolio Summary widget configuration  
 */
export interface PortfolioSummaryConfigData {
  type: WidgetType.PORTFOLIO_SUMMARY;
  
  /** Portfolio ID to display */
  portfolioId: string;
  
  /** Metrics to display */
  metrics: SummaryMetric[];
  
  /** Chart configuration */
  charts: ChartConfig[];
  
  /** Time period for calculations */
  timePeriod: TimePeriod;
}

/**
 * Correlation Matrix widget configuration
 */
export interface CorrelationMatrixConfigData {
  type: WidgetType.CORRELATION_MATRIX;
  
  /** Asset symbols to include */
  symbols: string[];
  
  /** Time period for correlation calculation */
  timePeriod: TimePeriod;
  
  /** Matrix display options */
  display: MatrixDisplayOptions;
  
  /** Color scheme for correlation values */
  colorScheme: CorrelationColorScheme;
}

/**
 * Monte Carlo simulation widget configuration
 */
export interface MonteCarloConfigData {
  type: WidgetType.MONTE_CARLO;
  
  /** Portfolio ID for simulation */
  portfolioId: string;
  
  /** Simulation parameters */
  parameters: SimulationParameters;
  
  /** Chart and display options */
  display: SimulationDisplayOptions;
  
  /** Number of scenarios to show */
  scenarioCount: number;
}

export interface HoldingsColumn {
  key: string;
  label: string;
  visible: boolean;
  width?: number;
  sortable: boolean;
  format?: 'currency' | 'percentage' | 'number' | 'text';
}

export interface SortingConfig {
  column: string;
  direction: 'asc' | 'desc';
  secondarySort?: {
    column: string;
    direction: 'asc' | 'desc';
  };
}

export interface SummaryMetric {
  key: string;
  label: string;
  visible: boolean;
  format: 'currency' | 'percentage' | 'number';
  precision?: number;
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'area';
  dataKey: string;
  visible: boolean;
  color?: string;
}

export interface TimePeriod {
  value: number;
  unit: 'days' | 'weeks' | 'months' | 'years';
}

export interface MatrixDisplayOptions {
  showValues: boolean;
  showColorBar: boolean;
  precision: number;
  fontSize: number;
}

export interface CorrelationColorScheme {
  positive: string;
  negative: string;
  neutral: string;
  highCorrelation: string;
}

export interface SimulationParameters {
  timeHorizon: number;
  iterations: number;
  confidenceLevel: number;
  volatilityModel: 'historical' | 'garch' | 'constant';
  rebalancingFrequency: 'never' | 'monthly' | 'quarterly' | 'annually';
}

export interface SimulationDisplayOptions {
  showDistribution: boolean;
  showPercentiles: boolean;
  showVaR: boolean;
  chartType: 'histogram' | 'density' | 'both';
}