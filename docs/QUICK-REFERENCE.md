# Quick Reference: Frontend/Backend Separation

## ✅ DO

### Frontend
```typescript
// Fetch data from API
const summary = await getPortfolioSummary();
const returnPct = summary.total_unrealized_gain_loss_pct;

// Display the data
return <div>Return: {returnPct.toFixed(2)}%</div>;
```

### Backend Service
```python
# Single source of truth for calculations
def calculate_portfolio_metrics():
    total_value = get_current_value()
    cost_basis = get_cost_basis()
    return_pct = (total_value - cost_basis) / cost_basis * 100
    return {'return_pct': return_pct}
```

### Backend Endpoint
```python
# Thin controller - delegates to service
@router.get("/portfolio/summary")
async def get_summary():
    metrics = portfolio_service.calculate_portfolio_metrics()
    return PortfolioSummaryResponse(**metrics)
```

## ❌ DON'T

### Frontend - NO Calculations
```typescript
// ❌ WRONG - calculating in frontend
const holdings = await getHoldings();
const totalValue = holdings.reduce((sum, h) => sum + h.value, 0);
const costBasis = holdings.reduce((sum, h) => sum + h.cost, 0);
const returnPct = (totalValue - costBasis) / costBasis * 100; // BAD!
```

### Backend - NO Duplication
```python
# ❌ WRONG - calculation exists in multiple places
# portfolio.py
def calc_return():
    return (value - cost) / cost * 100

# performance.py  
def calc_return():  # DUPLICATE!
    return (value - cost) / cost * 100

# ✅ RIGHT - one calculation, one place
# portfolio_service.py
def calculate_return():
    return (value - cost) / cost * 100
```

### Endpoint - NO Fat Controllers
```python
# ❌ WRONG - business logic in controller
@router.get("/portfolio")
async def get_portfolio():
    # 100 lines of calculation here... NO!
    orders = get_orders()
    for order in orders:
        # complex calculations...

# ✅ RIGHT - delegate to service
@router.get("/portfolio")
async def get_portfolio():
    result = portfolio_service.calculate_portfolio_metrics()
    return result
```

## Decision Tree

### "Where should this code go?"

```
Is it a calculation or business rule?
├─ YES → Service Layer (src/services/)
└─ NO → Is it data access?
    ├─ YES → Repository Layer (src/repositories/)
    └─ NO → Is it an API route?
        ├─ YES → Router (src/api/routers/)
        └─ NO → Is it display logic?
            ├─ YES → Frontend (frontend/v1/src/)
            └─ NO → Ask for help!
```

## Common Scenarios

### Scenario: Need to show portfolio return

❌ **WRONG:** Calculate in frontend
```typescript
const return = (currentValue - costBasis) / costBasis * 100;
```

✅ **RIGHT:** Get from API
```typescript
const { total_unrealized_gain_loss_pct } = await getPortfolioSummary();
```

### Scenario: Multiple endpoints need same calculation

❌ **WRONG:** Copy code to each endpoint
```python
# portfolio.py
return (value - cost) / cost * 100

# performance.py
return (value - cost) / cost * 100  # DUPLICATE!
```

✅ **RIGHT:** Create service function
```python
# portfolio_service.py
def calculate_return(value, cost):
    return (value - cost) / cost * 100

# Both endpoints use:
result = portfolio_service.calculate_return(value, cost)
```

### Scenario: Need to add new metric

1. Add calculation to **service** (`src/services/`)
2. Update **API schema** (`src/api/schemas/`)
3. Update **endpoint** to return new field
4. Update **frontend type** (`src/lib/api/`)
5. Display in **component**

## Validation

Before committing, run:
```bash
python3 .githooks/pre-commit-architecture
```

Or commit will automatically run validation.

## Files Structure

```
src/
├── services/              ← Business logic HERE
│   ├── portfolio_service.py
│   └── README.md
├── api/
│   ├── routers/          ← Thin controllers
│   └── schemas/          ← API contracts
└── repositories/         ← Data access

frontend/v1/src/
├── lib/api/              ← API clients ONLY
│   ├── portfolio.ts
│   └── widgets.ts
└── app/                  ← Display logic ONLY
```

## Questions?

- **"Where do I put this calculation?"** → Service layer
- **"Can I calculate this in frontend?"** → No, use API
- **"This code exists in 2 places..."** → Move to service
- **"My endpoint is 100+ lines..."** → Extract to service

## More Info

- Full principles: `docs/ARCHITECTURE-PRINCIPLES.md`
- Service layer: `src/services/README.md`
- Setup hooks: `./setup-hooks.sh`
