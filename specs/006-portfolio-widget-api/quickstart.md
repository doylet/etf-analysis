# Quick Start: Portfolio Widget API Integration

**Feature**: Portfolio Widget API Integration  
**Date**: 2025-12-07  
**Target Audience**: Backend and frontend developers implementing widget API endpoints

## Overview

This guide helps developers implement REST API endpoints that expose existing portfolio analysis widgets to the NextJS frontend application.

## Prerequisites

- Python 3.11+ with existing ETF Analysis codebase
- FastAPI application already configured (existing `/src/api/main.py`)
- NextJS frontend application (existing `/frontend/v1/`)
- JWT authentication working (existing implementation)
- Existing portfolio widgets in `/src/widgets/`

## Implementation Steps

### Phase 1: Basic Widget APIs (Priority P1)

#### Step 1: Create Widget Adapter Base Class

Create `/src/api/widgets/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class WidgetAdapter(ABC):
    """Base class for widget API adapters"""
    
    @abstractmethod
    def get_widget_id(self) -> str:
        """Return unique widget identifier"""
        pass
    
    @abstractmethod
    def validate_parameters(self, params: Dict[str, Any]) -> BaseModel:
        """Validate and parse request parameters"""
        pass
    
    @abstractmethod
    async def execute(self, params: BaseModel, user_id: str) -> Dict[str, Any]:
        """Execute widget calculation and return JSON data"""
        pass
    
    def format_response(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format standard widget response"""
        return {
            "success": True,
            "data": data,
            "metadata": {
                "widget_id": self.get_widget_id(),
                **metadata
            },
            "warnings": [],
            "errors": []
        }
```

#### Step 2: Implement Portfolio Summary Adapter

Create `/src/api/widgets/portfolio_summary.py`:

```python
import time
from typing import Dict, Any
from pydantic import BaseModel, Field
from src.widgets.portfolio_summary_widget import PortfolioSummaryWidget
from src.storage.database_storage import DatabaseStorage
from .base import WidgetAdapter

class PortfolioSummaryParams(BaseModel):
    period_days: int = Field(default=365, ge=30, le=3650)
    benchmark_symbol: str = Field(default="SPY", pattern=r"^[A-Z]{1,5}$")
    include_risk_metrics: bool = Field(default=True)

class PortfolioSummaryAdapter(WidgetAdapter):
    def __init__(self):
        self.storage = DatabaseStorage()
        
    def get_widget_id(self) -> str:
        return "portfolio_summary"
    
    def validate_parameters(self, params: Dict[str, Any]) -> PortfolioSummaryParams:
        return PortfolioSummaryParams(**params)
    
    async def execute(self, params: PortfolioSummaryParams, user_id: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # Get user's portfolio holdings
        instruments = self.storage.get_all_instruments(active_only=True)
        holdings = [i for i in instruments if i.get('quantity', 0) > 0]
        
        # Create widget instance and calculate metrics
        widget = PortfolioSummaryWidget()
        widget.storage = self.storage
        
        # Extract calculation logic (adapt from widget's render method)
        metrics = widget._calculate_all_metrics(holdings)
        
        calculation_time = time.time() - start_time
        
        # Convert to API response format
        response_data = {
            "total_value": float(metrics.total_value),
            "total_return": float(metrics.total_return),
            "total_return_percent": float(metrics.total_return_percent),
            "day_change": float(metrics.day_change),
            "day_change_percent": float(metrics.day_change_percent),
            "positions_count": metrics.positions_count,
            "cash": float(metrics.cash),
        }
        
        if params.include_risk_metrics:
            response_data.update({
                "sharpe_ratio": float(metrics.sharpe_ratio),
                "max_drawdown": float(metrics.max_drawdown),
                "volatility": float(metrics.volatility),
            })
        
        metadata = {
            "calculation_time": calculation_time,
            "data_quality": 0.95,  # Calculate based on data availability
            "cache_status": "MISS"  # Implement caching logic
        }
        
        return self.format_response(response_data, metadata)
```

#### Step 3: Create API Router

Create `/src/api/routers/widgets.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from src.api.dependencies import get_current_user
from src.api.widgets.portfolio_summary import PortfolioSummaryAdapter

router = APIRouter(prefix="/widgets", tags=["Portfolio Widgets"])

@router.get("/portfolio/summary")
async def get_portfolio_summary(
    period_days: int = 365,
    benchmark_symbol: str = "SPY",
    include_risk_metrics: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get portfolio performance summary metrics"""
    try:
        adapter = PortfolioSummaryAdapter()
        params = adapter.validate_parameters({
            "period_days": period_days,
            "benchmark_symbol": benchmark_symbol,
            "include_risk_metrics": include_risk_metrics
        })
        
        result = await adapter.execute(params, current_user["user_id"])
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 4: Register Router

Add to `/src/api/main.py`:

```python
from api.routers.widgets import router as widgets_router

app.include_router(widgets_router)
```

### Phase 2: Frontend Integration

#### Step 5: Create Widget API Hook

Create `/frontend/v1/src/hooks/use-portfolio-widgets.ts`:

```typescript
import { useState, useEffect } from 'react';
import { portfolioApiClient } from '@/lib/api/portfolio-client';

interface PortfolioSummaryData {
  total_value: number;
  total_return: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
  positions_count: number;
  cash: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  volatility?: number;
}

interface WidgetResponse<T> {
  success: boolean;
  data: T;
  metadata: {
    widget_id: string;
    calculation_time: number;
    data_quality: number;
    cache_status: string;
  };
  warnings: string[];
  errors: Array<{code: string; message: string}>;
}

export function usePortfolioSummaryWidget(
  periodDays: number = 365,
  includeRiskMetrics: boolean = true
) {
  const [data, setData] = useState<PortfolioSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        
        const response = await portfolioApiClient.get<WidgetResponse<PortfolioSummaryData>>(
          `/widgets/portfolio/summary?period_days=${periodDays}&include_risk_metrics=${includeRiskMetrics}`
        );
        
        if (response.data.success) {
          setData(response.data.data);
        } else {
          setError(response.data.errors[0]?.message || 'Widget calculation failed');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch portfolio summary');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [periodDays, includeRiskMetrics]);

  return { data, loading, error };
}
```

#### Step 6: Update Portfolio Component

Update `/frontend/v1/src/components/PortfolioSummary.tsx`:

```typescript
import { usePortfolioSummaryWidget } from '@/hooks/use-portfolio-widgets';

export default function PortfolioSummaryComponent() {
  const { data: summary, loading, error } = usePortfolioSummaryWidget(365, true);

  // Rest of component remains the same - just using new hook
  // ... existing loading and error handling logic
  
  const metrics = [
    {
      title: 'Total Value',
      value: formatCurrency(summary?.total_value),
      variant: 'highlighted' as const,
      trend: 'neutral' as const,
    },
    {
      title: 'Total Return',
      value: formatCurrency(summary?.total_return),
      subtitle: formatPercent(summary?.total_return_percent),
      trend: determineMetricTrend(summary?.total_return),
    },
    // ... additional metrics using summary data
  ];
  
  // ... rest of component
}
```

### Phase 3: Testing

#### Step 7: Create Widget Tests

Create `/tests/unit/api/widgets/test_portfolio_summary.py`:

```python
import pytest
from unittest.mock import Mock, patch
from src.api.widgets.portfolio_summary import PortfolioSummaryAdapter

@pytest.fixture
def mock_storage():
    storage = Mock()
    storage.get_all_instruments.return_value = [
        {"symbol": "AAPL", "quantity": 100, "price": 150.0},
        {"symbol": "MSFT", "quantity": 50, "price": 200.0}
    ]
    return storage

@pytest.mark.asyncio
async def test_portfolio_summary_adapter(mock_storage):
    with patch('src.api.widgets.portfolio_summary.DatabaseStorage', return_value=mock_storage):
        adapter = PortfolioSummaryAdapter()
        params = adapter.validate_parameters({"period_days": 365})
        
        result = await adapter.execute(params, "test_user")
        
        assert result["success"] is True
        assert "total_value" in result["data"]
        assert result["metadata"]["widget_id"] == "portfolio_summary"
```

#### Step 8: Integration Testing

```bash
# Test API endpoint
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/widgets/portfolio/summary?period_days=365"

# Test frontend integration
cd frontend/v1
npm run dev
# Navigate to portfolio dashboard and verify widget data loads
```

## Development Workflow

### Adding New Widget APIs

1. **Create Adapter Class**: Follow the `WidgetAdapter` pattern
2. **Define Request/Response Models**: Use Pydantic for validation
3. **Extract Widget Logic**: Adapt existing widget calculations for JSON output
4. **Add Router Endpoint**: Create RESTful endpoint with proper error handling
5. **Create Frontend Hook**: Follow the `use-*-widget` pattern
6. **Update Components**: Integrate new hook into UI components
7. **Add Tests**: Unit tests for adapter, integration tests for API

### Performance Optimization

- **Caching**: Implement Redis caching for expensive calculations
- **Async Processing**: Use Celery for long-running calculations (Monte Carlo, Optimization)
- **Data Quality**: Include data quality metrics in responses
- **Error Handling**: Graceful degradation when data is insufficient

### Common Pitfalls

1. **Streamlit Dependencies**: Remove Streamlit-specific code from widget logic
2. **JSON Serialization**: Ensure all response data is JSON-serializable
3. **Error Propagation**: Don't let widget exceptions crash the API
4. **Authentication**: Always validate user access to portfolio data
5. **Data Freshness**: Include data quality/freshness indicators

## API Documentation

Once implemented, the full API documentation is available at:
- **Local**: http://localhost:8000/docs
- **OpenAPI Spec**: `/specs/006-portfolio-widget-api/contracts/portfolio-widgets-api.yaml`

## Next Steps

1. Start with Portfolio Summary widget (highest value)
2. Add Holdings Breakdown widget
3. Implement advanced analytics (Correlation, Monte Carlo)
4. Add comprehensive error handling and monitoring
5. Optimize performance with caching and async processing

## Support

For implementation questions or issues:
- Review existing widget code in `/src/widgets/`
- Check existing API patterns in `/src/api/routers/`
- Reference data models in `/specs/006-portfolio-widget-api/data-model.md`