"""Integration test framework for widget API endpoints."""

import pytest
import asyncio
from typing import Dict, Any
from httpx import AsyncClient
import json

from src.api.main import app


class WidgetAPITestClient:
    """Test client for widget API integration tests."""
    
    def __init__(self):
        self.base_url = "http://test"
        self.client = None
        
    async def __aenter__(self):
        self.client = AsyncClient(app=app, base_url=self.base_url)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            
    async def get_widget_list(self):
        """Get list of available widgets."""
        response = await self.client.get("/api/widgets/")
        return response.status_code, response.json()
        
    async def get_portfolio_summary(self, portfolio_id: str = None):
        """Get portfolio summary widget data."""
        params = {"portfolio_id": portfolio_id} if portfolio_id else {}
        response = await self.client.get("/api/widgets/portfolio/summary", params=params)
        return response.status_code, response.json()
        
    async def get_holdings_breakdown(self, portfolio_id: str = None):
        """Get holdings breakdown widget data.""" 
        params = {"portfolio_id": portfolio_id} if portfolio_id else {}
        response = await self.client.get("/api/widgets/portfolio/holdings", params=params)
        return response.status_code, response.json()
        
    async def get_correlation_matrix(self, portfolio_id: str = None, lookback_days: int = 252):
        """Get correlation matrix widget data."""
        params = {
            "lookback_days": lookback_days
        }
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
        response = await self.client.get("/api/widgets/portfolio/correlation", params=params)
        return response.status_code, response.json()
        
    async def get_monte_carlo(self, portfolio_id: str = None, num_simulations: int = 1000):
        """Get Monte Carlo simulation widget data."""
        params = {
            "num_simulations": num_simulations,
            "time_horizon_days": 252,
            "confidence_level": 0.95
        }
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
        response = await self.client.get("/api/widgets/portfolio/monte-carlo", params=params)
        return response.status_code, response.json()
        
    async def health_check(self):
        """Check widget service health."""
        response = await self.client.get("/api/widgets/health")
        return response.status_code, response.json()


@pytest.fixture
async def widget_client():
    """Pytest fixture for widget API test client."""
    async with WidgetAPITestClient() as client:
        yield client


def assert_widget_response_format(response_data: Dict[str, Any], should_succeed: bool = True):
    """Assert that API response follows widget response format."""
    # Check required fields
    assert "widget_name" in response_data
    assert "success" in response_data  
    assert "metadata" in response_data
    
    # Check data types
    assert isinstance(response_data["success"], bool)
    assert isinstance(response_data["metadata"], dict)
    
    # Check success/failure structure
    if should_succeed:
        assert response_data["success"] == True
        assert "data" in response_data
        assert response_data["data"] is not None
        assert response_data.get("error") is None
    else:
        assert response_data["success"] == False
        assert "error" in response_data
        assert response_data["error"] is not None
        assert "code" in response_data["error"]
        assert "message" in response_data["error"]


def assert_portfolio_summary_data(data: Dict[str, Any]):
    """Assert portfolio summary data structure."""
    required_fields = [
        "total_value", "total_return", "total_return_percent",
        "day_change", "day_change_percent", "positions", 
        "allocated_cash", "last_updated"
    ]
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
        
    # Check numeric fields
    numeric_fields = [
        "total_value", "total_return", "total_return_percent", 
        "day_change", "day_change_percent", "allocated_cash"
    ]
    for field in numeric_fields:
        assert isinstance(data[field], (int, float)), f"{field} should be numeric"
        
    # Check integer fields
    assert isinstance(data["positions"], int), "positions should be integer"


def assert_holdings_breakdown_data(data: Dict[str, Any]):
    """Assert holdings breakdown data structure."""
    assert "positions" in data
    assert "total_value" in data
    assert "cash_position" in data
    assert "last_updated" in data
    
    assert isinstance(data["positions"], list)
    assert isinstance(data["total_value"], (int, float))
    assert isinstance(data["cash_position"], (int, float))
    
    # Check position structure
    for position in data["positions"]:
        position_fields = [
            "symbol", "name", "quantity", "current_price",
            "market_value", "weight", "day_change", "day_change_percent",
            "total_return", "total_return_percent"
        ]
        for field in position_fields:
            assert field in position, f"Position missing field: {field}"


def assert_correlation_matrix_data(data: Dict[str, Any]):
    """Assert correlation matrix data structure."""
    assert "correlation_matrix" in data
    assert "symbols" in data
    assert "time_period" in data
    assert "calculation_date" in data
    assert "data_quality_score" in data
    
    assert isinstance(data["correlation_matrix"], dict)
    assert isinstance(data["symbols"], list)
    assert isinstance(data["data_quality_score"], (int, float))
    assert 0 <= data["data_quality_score"] <= 1


def assert_monte_carlo_data(data: Dict[str, Any]):
    """Assert Monte Carlo simulation data structure."""
    assert "scenarios" in data
    assert "statistics" in data
    assert "percentiles" in data
    assert "var_95" in data
    assert "var_99" in data
    assert "simulation_params" in data
    assert "execution_time_seconds" in data
    
    assert isinstance(data["scenarios"], list)
    assert isinstance(data["statistics"], dict)
    assert isinstance(data["percentiles"], dict)
    assert isinstance(data["var_95"], (int, float))
    assert isinstance(data["var_99"], (int, float))


# Test scenarios for integration tests
TEST_SCENARIOS = {
    "portfolio_summary": {
        "description": "Test portfolio summary widget endpoint",
        "endpoint": "/api/widgets/portfolio/summary",
        "method": "GET",
        "expected_status": 501,  # Will be 200 when implemented
        "data_validator": assert_portfolio_summary_data
    },
    "holdings_breakdown": {
        "description": "Test holdings breakdown widget endpoint",  
        "endpoint": "/api/widgets/portfolio/holdings",
        "method": "GET", 
        "expected_status": 501,  # Will be 200 when implemented
        "data_validator": assert_holdings_breakdown_data
    },
    "correlation_matrix": {
        "description": "Test correlation matrix widget endpoint",
        "endpoint": "/api/widgets/portfolio/correlation", 
        "method": "GET",
        "expected_status": 501,  # Will be 200 when implemented
        "data_validator": assert_correlation_matrix_data
    },
    "monte_carlo": {
        "description": "Test Monte Carlo simulation widget endpoint",
        "endpoint": "/api/widgets/portfolio/monte-carlo",
        "method": "GET", 
        "expected_status": 501,  # Will be 200 when implemented
        "data_validator": assert_monte_carlo_data
    }
}