# Widget Architecture Migration Guide

## Quick Start: Refactoring to Layered Architecture

This guide shows how to migrate widgets from monolithic `render()` methods to the layered architecture pattern.

## Before & After Comparison

### Original Architecture (Monolithic)
- **500+ lines** in single `render()` method
- UI, data fetching, and calculations mixed together
- Hard to test (requires Streamlit runtime)
- Difficult to debug (need to step through UI code)
- Changes risk breaking multiple concerns

### New Architecture (Layered)
- **<300 total lines** split across focused methods
- UI Layer: <100 lines (rendering only)
- Data Layer: ~100 lines (fetching & validation)
- Logic Layer: ~100 lines (pure calculations)
- **Easy to test**: Business logic is pure functions
- **Easy to debug**: Test calculations with sample data
- **Safe to change**: Layers are independent

## Architecture Layers

### Layer 1: UI Layer (`_render_*` methods)
**Purpose**: Streamlit component rendering and user interaction

**Rules**:
- ✅ Call `st.*` functions
- ✅ Read/write session state
- ✅ Call data/logic layers
- ❌ NO `self.storage` calls
- ❌ NO business calculations

**Example**:
```python
def _render_period_selector(self) -> Tuple[int, datetime, datetime]:
    """Render time period selection - returns user choice."""
    period = st.selectbox(
        "Time Period:",
        options=['1 Month', '3 Months', '6 Months'],
        key=self._get_session_key("period")
    )
    days = self.PERIOD_DAYS_MAP[period]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return days, start_date, end_date
```

### Layer 2: Data Layer (`_fetch_*`, `_prepare_*` methods)
**Purpose**: Data retrieval, validation, and preparation

**Rules**:
- ✅ Call `self.storage`
- ✅ Validate data quality
- ✅ Return typed structures
- ❌ NO `st.*` calls
- ❌ NO business calculations

**Example**:
```python
def _fetch_returns_data(
    self, symbols: List[str], start_date: datetime, end_date: datetime
) -> Dict:
    """Fetch price data and calculate returns - returns dict with status."""
    returns_data = {}
    missing_data = []
    
    for symbol in symbols:
        price_df = self.storage.get_price_data(symbol, start_date, end_date)
        
        if price_df is None or price_df.empty:
            missing_data.append(symbol)
            continue
        
        returns_data[symbol] = calculate_returns(price_df['close'])
    
    if not returns_data:
        return {'status': 'error', 'message': 'No data available'}
    
    return {
        'status': 'success',
        'returns_df': pd.DataFrame(returns_data),
        'missing_data': missing_data
    }
```

### Layer 3: Logic Layer (`_calculate_*`, `_analyze_*` static methods)
**Purpose**: Pure business logic and calculations

**Rules**:
- ✅ Pure functions (no side effects)
- ✅ Take data structures as input
- ✅ Return calculation results
- ✅ Use `@staticmethod` when possible
- ❌ NO `st.*` calls
- ❌ NO `self.storage` calls
- ✅ **MUST BE UNIT TESTABLE**

**Example**:
```python
@staticmethod
def _calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate correlation matrix from returns DataFrame."""
    return returns_df.corr()

@staticmethod
def _analyze_diversification(correlation_matrix: pd.DataFrame) -> Dict:
    """Analyze diversification from correlation matrix."""
    corr_values = []
    for i in range(len(correlation_matrix)):
        for j in range(i + 1, len(correlation_matrix)):
            corr_values.append(correlation_matrix.iloc[i, j])
    
    return {
        'avg_correlation': float(np.mean(corr_values)),
        'max_correlation': float(np.max(corr_values)),
        'min_correlation': float(np.min(corr_values))
    }
```

## Migration Checklist

### Step 1: Setup
- [ ] Create backup: `cp widget.py widget.py.original`
- [ ] Change import: `from .layered_base_widget import LayeredBaseWidget`
- [ ] Change class: `class MyWidget(LayeredBaseWidget):`

### Step 2: Identify Boundaries
Read through current `render()` method and mark sections:
- [ ] Mark all `st.*` calls → UI Layer
- [ ] Mark all `self.storage.*` calls → Data Layer
- [ ] Mark all calculations/transformations → Logic Layer

### Step 3: Extract Logic Layer (Do This First!)
- [ ] Find all calculation logic
- [ ] Extract to `@staticmethod _calculate_*()` methods
- [ ] Ensure pure functions (no st.*, no self.storage)
- [ ] Add type hints and docstrings
- [ ] Test with sample data in Python REPL

### Step 4: Extract Data Layer
- [ ] Find all `self.storage.*` calls
- [ ] Extract to `_fetch_*()` and `_prepare_*()` methods
- [ ] Return dicts with `{'status': 'success', 'data': ...}` pattern
- [ ] Add validation and error handling
- [ ] Use helper: `self._handle_data_error()`

### Step 5: Refactor UI Layer
- [ ] Keep only `st.*` calls in `_render_*()` methods
- [ ] Use `self._get_session_key()` for session state
- [ ] Break into small focused methods (<50 lines)
- [ ] Call data layer to get data
- [ ] Call logic layer to calculate
- [ ] Display results

### Step 6: Simplify Main `render()`
Transform main render() into orchestration:

```python
def render(self, instruments, selected_symbols):
    """Main render - orchestration only."""
    with st.container(border=True):
        # 1. UI: Get inputs
        period, start, end = self._render_controls()
        selections = self._render_selections()
        
        # 2. Data: Fetch
        data_result = self._fetch_data(selections, start, end)
        if data_result['status'] == 'error':
            st.error(data_result['message'])
            return
        
        # 3. Logic: Calculate
        results = self._calculate_metrics(data_result['data'])
        
        # 4. UI: Display
        self._render_results(results)
```

### Step 7: Test & Verify
- [ ] Run widget in Streamlit app
- [ ] Test all UI interactions
- [ ] Verify calculations match original
- [ ] Check error handling
- [ ] Test edge cases
- [ ] Verify session state persistence

## Line Count Targets

| Component | Target | Good | Needs Work |
|-----------|--------|------|------------|
| `render()` method | <100 lines | <80 lines | >120 lines |
| Helper methods | <50 lines | <40 lines | >60 lines |
| Total widget | <300 lines | <250 lines | >350 lines |

## Common Patterns

### Pattern: Error Result Dictionary
```python
# Data layer returns status dict
def _fetch_data(self):
    try:
        data = self.storage.get_data()
        if not data:
            return {'status': 'error', 'message': 'No data found'}
        return {'status': 'success', 'data': data}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# UI layer checks status
result = self._fetch_data()
if result['status'] == 'error':
    st.error(result['message'])
    return
```

### Pattern: Session State Helper
```python
# Old way
key = f"{self.widget_id}_selections"
if key not in st.session_state:
    st.session_state[key] = []

# New way (using helper)
key = self._get_session_key("selections")
self._init_session_state(key, [])
```

### Pattern: Pure Calculation with Dataclass
```python
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    """Type-safe result container."""
    correlation_matrix: pd.DataFrame
    avg_correlation: float
    insights: Dict

@staticmethod
def _calculate_analysis(returns_df: pd.DataFrame) -> AnalysisResult:
    """Pure calculation returning typed result."""
    corr_matrix = returns_df.corr()
    avg = float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean())
    
    return AnalysisResult(
        correlation_matrix=corr_matrix,
        avg_correlation=avg,
        insights={'diversified': avg < 0.5}
    )
```

## Testing Your Refactored Widget

### Unit Test Logic Layer (NEW!)
```python
# tests/widgets/test_calculations.py
import pandas as pd
import numpy as np
from src.widgets.my_widget import MyWidget

def test_calculate_correlation():
    # Arrange: Create sample data
    returns = pd.DataFrame({
        'A': [0.01, 0.02, -0.01],
        'B': [0.02, 0.03, -0.02]
    })
    
    # Act: Call pure function
    result = MyWidget._calculate_correlation_matrix(returns)
    
    # Assert: Verify result
    assert result.shape == (2, 2)
    assert result.loc['A', 'A'] == 1.0
    assert 0.99 < result.loc['A', 'B'] < 1.0  # Highly correlated
```

### Manual UI Test
1. Run Streamlit app
2. Test each UI control
3. Verify calculations match original
4. Test error conditions
5. Check session state persistence

## Anti-Patterns to Avoid

❌ **Don't mix layers**:
```python
def _render_results(self):
    st.subheader("Results")
    # ❌ BAD: Calculation in UI method
    correlation = returns_df.corr()
    st.dataframe(correlation)
```

✅ **Do separate layers**:
```python
def _render_results(self, correlation_matrix):
    st.subheader("Results")
    # ✅ GOOD: Just display pre-calculated data
    st.dataframe(correlation_matrix)
```

❌ **Don't call storage from logic**:
```python
@staticmethod
def _calculate_metrics(symbol):
    # ❌ BAD: Can't be static if calling storage
    data = self.storage.get_data(symbol)  # Error!
```

✅ **Do fetch first, then calculate**:
```python
def render(self):
    # ✅ GOOD: Data layer fetches, logic layer calculates
    data = self._fetch_data(symbol)
    metrics = self._calculate_metrics(data)
```

## Benefits After Migration

1. **Testability**: Business logic can be unit tested
2. **Debuggability**: Test calculations with sample data in REPL
3. **Maintainability**: Clear responsibilities, easy to modify
4. **Reusability**: Logic functions can be shared
5. **Readability**: Small focused methods, clear flow
6. **Safety**: Changes to UI don't affect calculations

## Example: Before & After

See `correlation_matrix_widget.py.original` (500+ lines) vs `correlation_matrix_widget_refactored.py` (450 lines with full docstrings) for complete example.

Key improvements:
- Render method: 350 lines → 45 lines
- Logic extracted to 12 pure functions
- All business logic is unit testable
- Error handling centralized
- Session state consistent pattern
