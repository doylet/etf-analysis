# Service Layer

The service layer contains all business logic and calculations. This is the single source of truth for application logic.

## Principles

1. **Single Responsibility**: Each service handles one domain area
2. **No Duplication**: If logic exists in a service, it's not repeated elsewhere
3. **Testable**: Services are pure functions that can be tested in isolation
4. **Reusable**: Services are called by multiple endpoints/widgets

## Current Services

### `portfolio_service.py`
**Purpose:** Core portfolio calculations (cost basis, returns, positions)

**Functions:**
- `calculate_portfolio_metrics()` - Calculate total value, cost basis, and return percentage

**Used By:**
- `/api/portfolio/summary` - Main portfolio endpoint
- `/api/widgets/performance` - Performance metrics widget

**Example:**
```python
from services.portfolio_service import calculate_portfolio_metrics

total_value, cost_basis, return_pct, holdings = calculate_portfolio_metrics()
print(f"Portfolio Return: {return_pct:.2f}%")
```

## Adding New Services

When creating a new service:

1. **Create file** in `src/services/` with clear name (e.g., `risk_service.py`)
2. **Document purpose** at top of file
3. **Write pure functions** (no side effects)
4. **Add to this README** with documentation
5. **Update callers** to use the service

### Service Template

```python
"""
[Service Name] Service

Purpose:
    [What business problem this solves]

Functions:
    - function_name: [What it does]

Used By:
    - [Endpoint/widget that uses it]
"""

from typing import Dict, Tuple

def calculate_something(param1: str, param2: float) -> Dict:
    """
    [Description]
    
    Args:
        param1: [Description]
        param2: [Description]
        
    Returns:
        Dict with keys: [list keys]
        
    Example:
        >>> result = calculate_something("AAPL", 100.0)
        >>> print(result['value'])
    """
    # Implementation
    return result
```

## Service Dependencies

Services may depend on:
- ✅ Repositories (data access layer)
- ✅ Other services (composition)
- ✅ Utility functions
- ❌ API endpoints (circular dependency)
- ❌ Widgets (circular dependency)
- ❌ Frontend code (never)

## Testing Services

All services must have unit tests:

```python
# tests/services/test_portfolio_service.py

def test_calculate_portfolio_metrics():
    """Test portfolio calculation logic."""
    # Arrange
    mock_data = setup_test_data()
    
    # Act
    value, cost, return_pct, holdings = calculate_portfolio_metrics()
    
    # Assert
    assert value > 0
    assert cost > 0
    assert return_pct == expected_return
```

## Migration Checklist

When moving logic to services:

- [ ] Identify duplicated calculation code
- [ ] Create service function with clear name
- [ ] Add comprehensive documentation
- [ ] Write unit tests
- [ ] Update all callers to use service
- [ ] Remove old duplicated code
- [ ] Update this README
- [ ] Run architecture checks

## Future Services

Planned services to extract:

- [ ] `risk_service.py` - Volatility, Sharpe ratio, VaR calculations
- [ ] `performance_service.py` - Time-series performance analytics
- [ ] `optimization_service.py` - Portfolio optimization algorithms
- [ ] `dividend_service.py` - Dividend calculations and projections
- [ ] `rebalancing_service.py` - Portfolio rebalancing logic
- [ ] `tax_service.py` - Tax lot calculations and reporting

## Service Architecture

```
┌─────────────────────────────────────────┐
│         API Endpoints/Widgets           │
│  (Thin controllers - orchestrate only)  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│          Service Layer                   │
│  (Business logic - single source)       │
│                                          │
│  ├── portfolio_service.py               │
│  ├── risk_service.py                    │
│  ├── performance_service.py             │
│  └── optimization_service.py            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│          Repository Layer                │
│  (Data access - CRUD operations)        │
│                                          │
│  ├── order_repository.py                │
│  ├── instrument_repository.py           │
│  └── price_data_repository.py           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           Database                       │
│           (SQLite)                       │
└─────────────────────────────────────────┘
```

## Key Insights

**Before Services:**
- Business logic scattered across 10+ files
- Same calculation in 3 different places
- Bug fixes required updating multiple files
- Testing was difficult

**After Services:**
- Business logic in 1 place per domain
- One change updates all consumers
- Easy to test in isolation
- Clear ownership and documentation
