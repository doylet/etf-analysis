# Architecture Principles

## Separation of Concerns

### Frontend Responsibilities
**The frontend is a presentation layer only.**

✅ **ALLOWED:**
- Fetching data from backend API endpoints
- Rendering UI components
- Managing UI state (loading, errors, user interactions)
- Client-side routing
- Form validation (UX only, not security)
- Data formatting for display (dates, currency, percentages)
- Animations and visual effects

❌ **FORBIDDEN:**
- Business logic calculations (returns, cost basis, portfolio metrics)
- Direct database access
- Data transformation beyond display formatting
- Duplicating backend calculation logic
- Making assumptions about data structure beyond API schema

### Backend Responsibilities
**The backend is the single source of truth for all business logic.**

✅ **REQUIRED:**
- All business calculations (portfolio returns, cost basis, risk metrics)
- Data validation and sanitization
- Database operations
- Authentication and authorization
- API endpoint definitions
- Data aggregation and transformation
- Complex query logic

❌ **FORBIDDEN:**
- Presentation logic (how to display data)
- UI-specific state management
- Frontend component concerns

## Service Layer Pattern

### 1. Core Business Logic → Services
All reusable business logic lives in `src/services/`:

```
src/services/
├── portfolio_service.py      # Portfolio calculations (cost basis, returns, positions)
├── risk_service.py           # Risk metrics (volatility, Sharpe, VaR)
├── performance_service.py    # Performance analytics
└── optimization_service.py   # Portfolio optimization
```

**Rule:** If logic is used by >1 endpoint or widget, it MUST be in a service.

### 2. API Endpoints → Thin Controllers
Endpoints in `src/api/routers/` should be thin controllers:

```python
@router.get("/portfolio/summary")
async def get_portfolio_summary():
    """Thin controller - delegates to service layer."""
    result = portfolio_service.calculate_portfolio_metrics()
    return transform_to_response(result)
```

**Rule:** Endpoints orchestrate, they don't calculate.

### 3. Widgets → Adapters
Widget adapters in `src/api/widgets/` bridge legacy widget code to modern API:

```python
class PerformanceAdapter(BaseWidgetAdapter):
    def extract_calculation_data(self, widget_instance, validated_params):
        """Delegates to service, doesn't duplicate logic."""
        metrics = portfolio_service.calculate_portfolio_metrics()
        volatility = risk_service.calculate_volatility(...)
        return format_for_widget(metrics, volatility)
```

**Rule:** Adapters call services, never duplicate calculations.

## API Contract

### API as the Contract
The API schema (`src/api/schemas/`) is the contract between frontend and backend.

**Protocol:**
1. All data structures are defined in Pydantic schemas
2. Frontend TypeScript types are generated from schemas (or manually synced)
3. Schema changes require coordination between frontend and backend
4. Backward compatibility is maintained through versioning

**Example Schema:**
```python
# src/api/schemas/portfolio.py
class PortfolioSummaryResponse(BaseModel):
    total_value: float
    total_cost_basis: float
    total_unrealized_gain_loss_pct: float
    holdings: List[HoldingResponse]
```

### Frontend API Client
Frontend uses typed API client:

```typescript
// frontend/v1/src/lib/api/portfolio.ts
export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  const response = await fetch('/api/portfolio/summary');
  return response.json();
}
```

**Rule:** Frontend never constructs API data locally. Always fetch from backend.

## Data Flow

```
┌─────────────┐
│  Frontend   │  (Presentation Layer)
│             │  - Display data
│  React/Next │  - User interactions
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│ API Router  │  (Thin Controllers)
│             │  - Validate input
│  FastAPI    │  - Call services
└──────┬──────┘  - Format response
       │
       ▼
┌─────────────┐
│  Services   │  (Business Logic)
│             │  - Calculations
│  Python     │  - Transformations
└──────┬──────┘  - Aggregations
       │
       ▼
┌─────────────┐
│ Repositories│  (Data Access)
│             │  - CRUD operations
│  ORM/SQL    │  - Queries
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │  (Data Storage)
│   SQLite    │
└─────────────┘
```

**Critical Rules:**
- Frontend NEVER talks to Database
- Frontend NEVER talks to Repositories
- Frontend NEVER talks to Services directly
- Frontend ONLY calls API Endpoints
- API Endpoints call Services
- Services call Repositories
- Repositories access Database

## Anti-Patterns to Avoid

### ❌ Duplicated Calculations
**WRONG:**
```typescript
// Frontend calculating returns
const portfolioReturn = (currentValue - costBasis) / costBasis * 100;
```

**RIGHT:**
```typescript
// Frontend just displays what backend calculated
const { total_unrealized_gain_loss_pct } = await getPortfolioSummary();
```

### ❌ Multiple Sources of Truth
**WRONG:**
```python
# portfolio.py
def calculate_return():
    return (value - cost) / cost * 100

# performance.py  
def calculate_return():  # DUPLICATE!
    return (value - cost) / cost * 100
```

**RIGHT:**
```python
# portfolio_service.py (SINGLE source of truth)
def calculate_portfolio_metrics():
    return (value - cost) / cost * 100

# portfolio.py
result = portfolio_service.calculate_portfolio_metrics()

# performance.py
result = portfolio_service.calculate_portfolio_metrics()
```

### ❌ Fat Controllers
**WRONG:**
```python
@router.get("/portfolio/summary")
async def get_portfolio_summary():
    # 200 lines of calculation logic here... ❌
    orders = get_orders()
    for order in orders:
        # complex calculations...
```

**RIGHT:**
```python
@router.get("/portfolio/summary")
async def get_portfolio_summary():
    result = portfolio_service.calculate_portfolio_metrics()
    return PortfolioSummaryResponse(**result)
```

## Code Review Checklist

Before merging any PR, verify:

- [ ] No business logic in frontend
- [ ] No duplicated calculations between files
- [ ] All shared logic is in services
- [ ] API endpoints are thin controllers
- [ ] Widgets delegate to services
- [ ] Frontend only calls API endpoints
- [ ] Changes to calculations update ONE service file only
- [ ] API schemas are updated for data structure changes
- [ ] No direct database access from endpoints/widgets

## Migration Path

When finding violations:

1. **Identify the business logic**
2. **Extract to service layer** (`src/services/`)
3. **Update all consumers** to call service
4. **Remove duplicated code**
5. **Add tests** for service function
6. **Document** the service API

## Testing Strategy

### Backend Tests
```python
# test_portfolio_service.py
def test_calculate_portfolio_metrics():
    """Test business logic in isolation."""
    result = portfolio_service.calculate_portfolio_metrics()
    assert result['portfolio_return'] == expected_value
```

### API Tests
```python
# test_portfolio_api.py
def test_portfolio_summary_endpoint():
    """Test API contract."""
    response = client.get("/api/portfolio/summary")
    assert response.status_code == 200
    assert "total_value" in response.json()
```

### Frontend Tests
```typescript
// portfolio.test.ts
test('displays portfolio summary', async () => {
  // Mock API response
  mockFetch({ total_value: 121297.49, ... });
  
  render(<PortfolioSummary />);
  expect(screen.getByText('$121,297.49')).toBeInTheDocument();
});
```

**Rule:** Test at each layer, but business logic is ONLY tested in service tests.

## Documentation Requirements

Every service must have:

1. **Purpose:** What business problem it solves
2. **Inputs:** What parameters it needs
3. **Outputs:** What it returns
4. **Used By:** Which endpoints/widgets use it
5. **Example:** Usage example

```python
def calculate_portfolio_metrics() -> PortfolioMetrics:
    """
    Calculate core portfolio metrics.
    
    Purpose:
        Single source of truth for portfolio calculations.
        
    Returns:
        PortfolioMetrics with total_value, cost_basis, and return_pct
        
    Used By:
        - /api/portfolio/summary
        - /api/widgets/performance
        
    Example:
        >>> metrics = calculate_portfolio_metrics()
        >>> print(f"Return: {metrics.return_pct}%")
    """
```

## Enforcement

### Automated Checks
1. **Linting rules** prevent importing services in frontend
2. **Pre-commit hooks** check for calculation patterns in frontend
3. **CI/CD pipeline** runs architecture validation

### Manual Reviews
All PRs must be reviewed for:
- Adherence to separation of concerns
- No duplicated business logic
- Proper use of service layer

### Metrics
Track and report:
- Lines of business logic in frontend (goal: 0)
- Number of service functions (goal: consolidate)
- API endpoint complexity (goal: <20 lines)
- Code duplication percentage (goal: <5%)

## Summary

**Golden Rules:**

1. **Frontend displays, backend calculates**
2. **One calculation, one place, one time**
3. **Services are the source of truth**
4. **API is the contract**
5. **Never duplicate business logic**

**When in doubt:** If you're calculating something, it probably belongs in a service.
