# Data Model: Portfolio Widget API Integration

**Feature**: Portfolio Widget API Integration  
**Date**: 2025-12-07  
**Purpose**: Define data structures and entities for widget API integration

## Core Entities

### Widget Instance
**Purpose**: Represents a specific portfolio analysis widget with its configuration and calculation logic  
**Attributes**:
- `widget_id`: Unique identifier for widget type (e.g., "portfolio_summary", "correlation_matrix")
- `name`: Human-readable widget name
- `description`: Widget functionality description  
- `scope`: Widget analysis scope ("portfolio", "instrument", "benchmark")
- `requires_auth`: Boolean indicating if authentication is required
- `calculation_complexity`: Enum (LOW, MEDIUM, HIGH) for performance planning
- `parameters`: Widget-specific configuration parameters schema

**Relationships**:
- Has many Analysis Requests (one widget can handle multiple analysis requests)
- Produces Widget Results when executed

**Validation Rules**:
- `widget_id` must be unique across all widgets
- `parameters` schema must be JSON-serializable
- `scope` must be valid enum value

### Analysis Request
**Purpose**: Contains user-specified parameters for running widget calculations  
**Attributes**:
- `request_id`: Unique identifier for the analysis request
- `widget_id`: Reference to target widget
- `user_id`: Authenticated user making the request
- `parameters`: Request-specific analysis parameters (JSON)
- `timestamp`: When the request was initiated
- `status`: Request status (PENDING, RUNNING, COMPLETED, FAILED)
- `priority`: Request priority for queue management

**Validation Rules**:
- `parameters` must conform to widget's parameter schema
- `timestamp` must be valid ISO datetime
- `status` transitions must follow valid state machine
- Required parameters must be present for widget type

**State Transitions**:
```
PENDING → RUNNING → COMPLETED
PENDING → RUNNING → FAILED
PENDING → FAILED (validation error)
```

### Widget Result  
**Purpose**: Structured calculation outputs including numerical results, charts data, warnings, and metadata  
**Attributes**:
- `result_id`: Unique identifier for the result
- `request_id`: Reference to originating analysis request
- `data`: Primary calculation results (JSON)
- `charts`: Chart/visualization data structures (JSON)
- `metadata`: Calculation metadata and data quality info
- `warnings`: Array of warning messages
- `calculation_time`: Time taken to compute results (seconds)
- `data_quality_score`: 0-1 score indicating data completeness
- `generated_at`: Timestamp of result generation

**Validation Rules**:
- `data` structure must match widget output schema
- `data_quality_score` must be between 0 and 1
- `calculation_time` must be positive number
- `charts` must follow supported visualization schemas

**Data Structures**:
- **Metrics**: `{"name": str, "value": float, "unit": str, "trend": enum}`
- **Time Series**: `{"dates": [datetime], "values": [float], "label": str}`
- **Allocations**: `{"category": str, "value": float, "percentage": float}`

### Portfolio Context
**Purpose**: Current portfolio state used as input for calculations  
**Attributes**:
- `portfolio_id`: Unique portfolio identifier  
- `user_id`: Portfolio owner
- `holdings`: Array of current position data
- `cash_position`: Available cash amount
- `last_updated`: Timestamp of most recent data update
- `data_freshness`: Age of price data (minutes)
- `total_value`: Current total portfolio value
- `base_currency`: Portfolio base currency (default USD)

**Holdings Structure**:
```json
{
  "symbol": "AAPL",
  "quantity": 100,
  "current_price": 150.25,
  "market_value": 15025.00,
  "cost_basis": 140.00,
  "unrealized_gain_loss": 1025.00,
  "weight": 0.15
}
```

**Validation Rules**:
- All monetary values must be non-negative
- Portfolio weights should sum to approximately 1.0
- Prices must be current (within data freshness threshold)
- Holdings array can be empty (cash-only portfolio)

## Widget-Specific Data Models

### Portfolio Summary Widget
**Request Parameters**:
- `period_days`: Historical period for calculations (default 365)
- `benchmark_symbol`: Optional benchmark comparison (default SPY)
- `include_risk_metrics`: Boolean for detailed risk analysis

**Response Data**:
- `total_value`: Current portfolio value
- `total_return`: Absolute return amount  
- `total_return_percent`: Return percentage
- `day_change`: Daily change amount
- `day_change_percent`: Daily change percentage
- `positions_count`: Number of holdings
- `sharpe_ratio`: Risk-adjusted return metric
- `max_drawdown`: Maximum historical loss
- `volatility`: Portfolio volatility (annualized)

### Holdings Breakdown Widget
**Request Parameters**:
- `breakdown_type`: Enum (SECTOR, GEOGRAPHY, ASSET_CLASS, SIZE)
- `min_allocation`: Minimum allocation to display (default 1%)

**Response Data**:
- `allocations`: Array of allocation objects
- `concentration_risk`: Boolean warning for excessive concentration
- `diversification_score`: 0-1 metric for portfolio diversification

### Correlation Matrix Widget
**Request Parameters**:
- `period_days`: Analysis period (default 252)
- `benchmark_symbols`: Array of benchmarks to include
- `correlation_threshold`: Minimum correlation to highlight

**Response Data**:
- `correlation_matrix`: 2D array of correlation values
- `symbols`: Array of symbols (holdings + benchmarks)
- `high_correlations`: Array of concerning correlation pairs

### Advanced Analytics Widgets
**Monte Carlo Parameters**:
- `iterations`: Number of simulation runs (default 1000)
- `years`: Time horizon for simulation (default 1)
- `confidence_levels`: Array of percentiles to calculate

**Optimization Parameters**:
- `target_return`: Desired portfolio return
- `risk_tolerance`: Risk constraint level  
- `candidate_symbols`: Universe of instruments for optimization
- `constraints`: Portfolio constraints (max weights, sectors, etc.)

## Error Handling Models

### Calculation Error
**Attributes**:
- `error_code`: Standardized error identifier
- `error_message`: Human-readable error description
- `details`: Technical error details
- `suggested_action`: User guidance for resolution
- `retry_possible`: Boolean indicating if retry might succeed

**Common Error Codes**:
- `INSUFFICIENT_DATA`: Not enough historical data for calculation
- `INVALID_PARAMETERS`: Request parameters fail validation
- `CALCULATION_TIMEOUT`: Widget calculation exceeded time limit
- `DATA_QUALITY_LOW`: Available data quality below minimum threshold

### Data Quality Metadata
**Attributes**:
- `data_points_available`: Count of valid data points used
- `data_points_required`: Minimum data points needed for reliable results
- `oldest_data_date`: Date of oldest data point used
- `missing_symbols`: Array of symbols with insufficient data
- `quality_warnings`: Array of data quality concerns

## Integration Considerations

### API Response Envelope
```json
{
  "success": true,
  "data": {...},
  "metadata": {
    "widget_id": "portfolio_summary",
    "calculation_time": 0.234,
    "data_quality": 0.95,
    "cache_status": "HIT"
  },
  "warnings": [],
  "errors": []
}
```

### Pagination Support
For widgets returning large datasets:
- `page`: Current page number (1-indexed)
- `page_size`: Number of items per page
- `total_items`: Total items available
- `total_pages`: Total pages available
- `has_next`: Boolean indicating more pages available

### Caching Strategy
- Cache key: `{widget_id}:{user_id}:{parameter_hash}`
- TTL varies by widget complexity and data volatility
- Cache invalidation on portfolio changes or market close