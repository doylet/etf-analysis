# ETF Analysis - Coding Standards

**Version**: 1.0  
**Last Updated**: December 9, 2025  
**Status**: Active

## Overview

This document establishes coding standards and architectural patterns for the ETF Analysis project. Following these standards ensures maintainability, testability, and consistency across the codebase.

## Architecture Layers

Our application follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────┐
│   Presentation Layer                │
│   (Streamlit widgets, Next.js UI)  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   API Layer (FastAPI routes)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Service Layer (Business Logic)    │
│   - Framework-agnostic               │
│   - Pure business logic              │
│   - Returns domain models            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Repository Layer (Data Access)    │
│   - Abstract interfaces              │
│   - Domain-focused methods           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Infrastructure (Database, APIs)   │
└─────────────────────────────────────┘
```

### 1. Service Layer (`src/services/`)

**Purpose**: Contains all business logic

**Rules**:
- ✅ **DO**: Write pure business logic with no framework dependencies
- ✅ **DO**: Use repositories for data access
- ✅ **DO**: Accept and return domain models
- ✅ **DO**: Raise domain exceptions for business rule violations
- ❌ **DON'T**: Import Streamlit, FastAPI, or any UI framework
- ❌ **DON'T**: Access database directly (use repositories)
- ❌ **DON'T**: Handle HTTP requests or responses

**Example**:
```python
# ✅ GOOD: Framework-agnostic service
class MonteCarloService:
    """Pure business logic for Monte Carlo simulation."""
    
    def __init__(self, price_repo: PriceDataRepository):
        self.price_repo = price_repo
    
    def run_simulation(self, params: SimulationParameters) -> SimulationResults:
        """Execute Monte Carlo simulation."""
        # Fetch data through repository
        price_data = self.price_repo.get_price_history(
            params.symbols, params.start_date, params.end_date
        )
        
        # Business logic
        returns = self._calculate_returns(price_data)
        paths = self._simulate_paths(returns, params)
        
        # Return domain model
        return SimulationResults(
            paths=paths,
            percentiles=self._calculate_percentiles(paths),
            risk_metrics=self._calculate_risk_metrics(paths)
        )
```

```python
# ❌ BAD: Framework coupling
class MonteCarloWidget:
    def render(self):
        st.header("Monte Carlo")  # UI code mixed with logic
        data = self.storage.get_price_data(...)  # Direct storage access
        # Business logic here
        st.plotly_chart(fig)  # More UI code
```

### 2. Repository Layer (`src/repositories/`)

**Purpose**: Provides data access abstraction

**Rules**:
- ✅ **DO**: Define abstract interfaces for data operations
- ✅ **DO**: Return domain models, not database models
- ✅ **DO**: Use domain-focused method names (e.g., `find_by_symbol`, not `query`)
- ✅ **DO**: Handle database-specific exceptions and convert to domain exceptions
- ❌ **DON'T**: Include business logic
- ❌ **DON'T**: Return SQLAlchemy or database-specific objects
- ❌ **DON'T**: Know about services or presentation layers

**Example**:
```python
# ✅ GOOD: Clean repository interface
class InstrumentRepository:
    """Repository for instrument domain objects."""
    
    def find_by_symbol(self, symbol: str) -> Optional[Instrument]:
        """Find instrument by ticker symbol."""
        db_instrument = self._db_query(symbol)
        return self._to_domain_model(db_instrument) if db_instrument else None
    
    def find_all_active(self) -> List[Instrument]:
        """Get all active instruments."""
        db_instruments = self._db_query_active()
        return [self._to_domain_model(i) for i in db_instruments]
```

### 3. Presentation Layer (Widgets & Frontend)

**Purpose**: Handles user interface and interaction

**Rules**:
- ✅ **DO**: Keep render methods small (<150 lines)
- ✅ **DO**: Call services for business logic
- ✅ **DO**: Handle user input validation
- ✅ **DO**: Display results and errors appropriately
- ❌ **DON'T**: Implement business logic
- ❌ **DON'T**: Access repositories or database directly
- ❌ **DON'T**: Duplicate logic from services

**Example**:
```python
# ✅ GOOD: Thin presentation layer
class MonteCarloWidget:
    """Monte Carlo simulation widget."""
    
    def __init__(self, service: MonteCarloService):
        self.service = service
    
    def render(self, instruments: List[Instrument]) -> None:
        """Render Monte Carlo widget."""
        # UI: Collect parameters
        params = self._collect_parameters(instruments)
        
        # Call service for logic
        try:
            results = self.service.run_simulation(params)
            self._display_results(results)
        except InsufficientDataError as e:
            st.warning(f"Not enough data: {e}")
        except Exception as e:
            st.error("An error occurred")
            logger.exception("Monte Carlo widget error")
```

### 4. API Layer (`src/api/`)

**Purpose**: Exposes functionality via REST endpoints

**Rules**:
- ✅ **DO**: Use dependency injection for services
- ✅ **DO**: Validate request data with Pydantic
- ✅ **DO**: Translate domain exceptions to HTTP status codes
- ✅ **DO**: Document endpoints with docstrings
- ❌ **DON'T**: Implement business logic
- ❌ **DON'T**: Access repositories directly

**Example**:
```python
# ✅ GOOD: Clean API endpoint
@router.post("/monte-carlo", response_model=SimulationResults)
async def run_monte_carlo(
    params: SimulationParameters,
    service: MonteCarloService = Depends(get_monte_carlo_service)
) -> SimulationResults:
    """Execute Monte Carlo simulation."""
    try:
        return service.run_simulation(params)
    except InvalidParameterError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InsufficientDataError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in Monte Carlo endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## File Organization

### Directory Structure

```
src/
├── domain/              # Domain models (Pydantic)
│   ├── __init__.py
│   ├── models.py        # Core domain models
│   └── exceptions.py    # Domain exceptions
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── monte_carlo_service.py
│   ├── optimization_service.py
│   └── correlation_service.py
├── repositories/        # Data access layer
│   ├── __init__.py
│   ├── base.py          # Base repository interface
│   ├── instrument_repository.py
│   └── price_data_repository.py
├── api/                 # FastAPI routes
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   │   ├── simulation.py
│   │   └── portfolio.py
│   └── dependencies.py  # Dependency injection
├── widgets/             # Streamlit presentation
│   ├── __init__.py
│   ├── monte_carlo_widget.py
│   └── portfolio_widget.py
└── infrastructure/      # External integrations
    ├── database/
    └── external_apis/
```

### Model Organization

- **Domain Models** (`src/domain/models.py`): Pydantic models for business entities
- **Database Models** (`src/infrastructure/database/models.py`): SQLAlchemy ORM models
- **API Schemas** (`src/api/schemas/`): Request/response models for API contracts

## Naming Conventions

### Classes
- Services: `*Service` (e.g., `MonteCarloService`, `OptimizationService`)
- Repositories: `*Repository` (e.g., `InstrumentRepository`, `PriceDataRepository`)
- Exceptions: `*Error` (e.g., `InsufficientDataError`, `InvalidParameterError`)
- Domain models: Descriptive names (e.g., `SimulationParameters`, `PortfolioSummary`)
- Widgets: `*Widget` (e.g., `MonteCarloWidget`, `CorrelationMatrixWidget`)

### Methods
- Repository queries: `find_*`, `get_*`, `save_*`, `delete_*`
- Service operations: Verb-based (e.g., `run_simulation`, `optimize_portfolio`, `calculate_correlation`)
- Widget methods: `render`, `_collect_parameters`, `_display_results`

### Files
- Use snake_case: `monte_carlo_service.py`, `price_data_repository.py`
- One primary class per file
- Group related utilities in appropriately named modules

## Error Handling

### Domain Exceptions

Define custom exceptions for domain-specific errors:

```python
# src/domain/exceptions.py

class DomainException(Exception):
    """Base exception for domain errors."""
    pass

class InsufficientDataError(DomainException):
    """Raised when insufficient data for calculation."""
    pass

class InvalidParameterError(DomainException):
    """Raised when parameters fail validation."""
    pass

class OptimizationFailedError(DomainException):
    """Raised when optimization cannot converge."""
    pass
```

### Error Handling Pattern

**Services**: Raise domain exceptions
```python
def calculate_correlation(self, symbols: List[str]) -> pd.DataFrame:
    if len(symbols) < 2:
        raise InvalidParameterError("Need at least 2 symbols")
    
    data = self.price_repo.get_price_history(symbols)
    if len(data) < 30:
        raise InsufficientDataError(f"Need 30+ data points, got {len(data)}")
    
    return self._compute_correlation(data)
```

**API Layer**: Translate to HTTP status codes
```python
try:
    result = service.calculate_correlation(symbols)
    return result
except InvalidParameterError as e:
    raise HTTPException(status_code=400, detail=str(e))
except InsufficientDataError as e:
    raise HTTPException(status_code=422, detail=str(e))
except Exception as e:
    logger.exception("Unexpected error")
    raise HTTPException(status_code=500, detail="Internal error")
```

**Widgets**: Display user-friendly messages
```python
try:
    result = self.service.calculate_correlation(symbols)
    self._display_results(result)
except InvalidParameterError as e:
    st.error(f"Invalid input: {e}")
except InsufficientDataError as e:
    st.warning(f"Not enough data: {e}")
except Exception as e:
    st.error("An unexpected error occurred")
    logger.exception("Widget error")
```

## Dependency Injection

### Service Dependencies

Use constructor injection for dependencies:

```python
# ✅ GOOD: Dependencies injected
class PortfolioService:
    def __init__(
        self,
        price_repo: PriceDataRepository,
        instrument_repo: InstrumentRepository
    ):
        self.price_repo = price_repo
        self.instrument_repo = instrument_repo
```

```python
# ❌ BAD: Direct instantiation
class PortfolioService:
    def __init__(self):
        self.price_repo = PriceDataRepository()  # Hard to test
        self.instrument_repo = InstrumentRepository()
```

### FastAPI Dependencies

Use FastAPI's dependency injection:

```python
# src/api/dependencies.py

def get_price_repository() -> PriceDataRepository:
    storage = get_storage_adapter()
    return PriceDataRepository(storage)

def get_monte_carlo_service(
    price_repo: PriceDataRepository = Depends(get_price_repository)
) -> MonteCarloService:
    return MonteCarloService(price_repo)
```

```python
# src/api/routers/simulation.py

@router.post("/monte-carlo")
async def run_simulation(
    params: SimulationParameters,
    service: MonteCarloService = Depends(get_monte_carlo_service)
):
    return service.run_simulation(params)
```

## Testing Standards

### Test Coverage Targets
- Service layer: **90%+** coverage
- Repository layer: **80%+** coverage
- API endpoints: **70%+** coverage
- Domain models: **80%+** coverage

### Test Organization

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── services/              # Service layer tests
│   ├── domain/                # Domain model tests
│   └── repositories/          # Repository tests (mocked storage)
├── integration/               # Tests with real database
│   └── repositories/          # Repository integration tests
└── api/                       # API contract tests
    └── test_simulation_endpoints.py
```

### Testing Guidelines

**Services**: Test without framework dependencies
```python
def test_monte_carlo_simulation():
    # Arrange: Mock repository
    price_repo = Mock(spec=PriceDataRepository)
    price_repo.get_price_history.return_value = sample_price_data
    service = MonteCarloService(price_repo)
    
    # Act
    result = service.run_simulation(params)
    
    # Assert
    assert len(result.paths) == params.num_simulations
    assert result.percentiles.p50 > 0
```

**Repositories**: Test with test database
```python
@pytest.fixture
def test_db():
    """Create test database."""
    db = create_test_database()
    yield db
    db.cleanup()

def test_find_by_symbol(test_db):
    repo = InstrumentRepository(test_db)
    instrument = repo.find_by_symbol("AAPL")
    assert instrument.symbol == "AAPL"
```

## Code Quality

### Size Limits
- Widget render methods: **<150 lines**
- Service methods: **<50 lines**
- Total file size: **<500 lines** (prefer smaller)
- Cyclomatic complexity: **<10 per method**

### Documentation
- All public classes and methods must have docstrings
- Use type hints for all function signatures
- Document complex algorithms with inline comments
- Update README.md when adding new features

### Code Review Checklist
- [ ] Business logic is in service layer
- [ ] No framework dependencies in services
- [ ] Proper error handling with domain exceptions
- [ ] Dependencies are injected, not instantiated
- [ ] Tests are written and passing
- [ ] Type hints are used
- [ ] Docstrings are present
- [ ] File size is reasonable (<500 lines)

## Migration Guidelines

### Refactoring Existing Widgets

When refactoring a widget to follow these standards:

1. **Extract service** - Move business logic to a new service class
2. **Create domain models** - Define Pydantic models for inputs/outputs
3. **Update widget** - Make widget thin, calling service
4. **Add tests** - Unit test the service
5. **Update API** - Create/update API endpoint using the service
6. **Document** - Update documentation

**Example Refactoring**:
```python
# BEFORE: 500-line widget with mixed concerns
class CorrelationMatrixWidget(BaseWidget):
    def render(self, instruments, selected_symbols):
        # 500 lines of mixed UI, data access, and calculations
        pass

# AFTER: Clean separation
class CorrelationService:
    """Business logic for correlation analysis."""
    def calculate_correlation_matrix(
        self, 
        price_data: pd.DataFrame
    ) -> CorrelationResults:
        # Pure business logic
        pass

class CorrelationMatrixWidget:
    """Presentation layer for correlation analysis."""
    def __init__(self, service: CorrelationService):
        self.service = service
    
    def render(self, instruments: List[Instrument]) -> None:
        # <150 lines of UI code only
        params = self._collect_parameters(instruments)
        results = self.service.calculate_correlation_matrix(params)
        self._display_results(results)
```

## Common Pitfalls

### ❌ Don't Mix Concerns
```python
# BAD: Business logic in API endpoint
@router.post("/correlation")
async def calculate_correlation(symbols: List[str]):
    # Fetching data
    data = fetch_price_data(symbols)
    # Business logic
    correlation = data.corr()
    # More calculations
    significant_pairs = find_significant(correlation)
    return {"correlation": correlation}
```

### ✅ Do Separate Concerns
```python
# GOOD: Delegate to service
@router.post("/correlation")
async def calculate_correlation(
    params: CorrelationParameters,
    service: CorrelationService = Depends(get_correlation_service)
):
    return service.calculate_correlation(params)
```

### ❌ Don't Return Database Objects
```python
# BAD: Exposing SQLAlchemy models
def get_instrument(symbol: str) -> InstrumentModel:
    return session.query(InstrumentModel).filter_by(symbol=symbol).first()
```

### ✅ Do Return Domain Models
```python
# GOOD: Domain model abstraction
def find_by_symbol(self, symbol: str) -> Optional[Instrument]:
    db_instrument = self._query(symbol)
    return Instrument.from_db(db_instrument) if db_instrument else None
```

## Resources

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Questions?

For questions about these standards or help with refactoring, contact the development team or refer to:
- [Architecture Review](./ARCHITECTURE_REVIEW.md) - Detailed analysis
- [Action Plan](./ARCHITECTURE_ACTION_PLAN.md) - Implementation roadmap

---

**Remember**: These standards exist to make the codebase maintainable and extensible. When in doubt, favor simplicity and separation of concerns.
