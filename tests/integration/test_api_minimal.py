"""
Minimal API integration tests to verify endpoints work before widget testing.
Quick validation of core functionality - focused on speed over comprehensiveness.
"""
import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.main import app

client = TestClient(app)

class TestAPIMinimal:
    """Quick smoke tests for API endpoints"""
    
    def test_api_health(self):
        """Verify API is running"""
        response = client.get("/api/docs")
        assert response.status_code == 200
    
    def test_portfolio_summary(self):
        """Quick test of portfolio endpoint"""
        response = client.get("/api/portfolio/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_value" in data
        assert "positions" in data
    
    def test_portfolio_holdings(self):
        """Quick test of holdings endpoint"""
        response = client.get("/api/portfolio/holdings")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_simulation_sync(self):
        """Quick simulation test (synchronous)"""
        payload = {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "weights": [0.4, 0.3, 0.3],
            "initial_investment": 10000,
            "years": 1,
            "iterations": 100  # Small number for speed
        }
        response = client.post("/api/simulation/monte-carlo", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "percentiles" in data
        assert "final_values" in data
    
    def test_optimization_max_sharpe(self):
        """Quick optimization test"""
        payload = {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "lookback_days": 60  # Short period for speed
        }
        response = client.post("/api/optimization/max-sharpe", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "optimal_weights" in data
        assert len(data["optimal_weights"]) == 3
    
    def test_instruments_list(self):
        """Quick instruments test"""
        response = client.get("/api/instruments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_auth_endpoints_exist(self):
        """Verify auth endpoints are accessible (don't test auth flow for speed)"""
        # Just check they exist and don't 404
        response = client.post("/api/auth/login", json={"username": "test", "password": "test"})
        # Expect 401/422, not 404
        assert response.status_code in [401, 422]
        
        response = client.get("/api/auth/me")
        # Expect 401, not 404
        assert response.status_code == 401

if __name__ == "__main__":
    # Quick manual run
    test = TestAPIMinimal()
    
    print("Running minimal API tests...")
    test.test_api_health()
    print("✓ API health check")
    
    test.test_portfolio_summary()
    print("✓ Portfolio summary")
    
    test.test_portfolio_holdings()
    print("✓ Portfolio holdings")
    
    test.test_simulation_sync()
    print("✓ Monte Carlo simulation")
    
    test.test_optimization_max_sharpe()
    print("✓ Portfolio optimization")
    
    test.test_instruments_list()
    print("✓ Instruments list")
    
    test.test_auth_endpoints_exist()
    print("✓ Auth endpoints exist")
    
    print("\n✅ All minimal API tests passed!")