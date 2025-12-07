"""Unit tests for Portfolio Summary Widget Adapter."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from api.widgets.portfolio_summary import PortfolioSummaryAdapter
from api.widgets.exceptions import WidgetDataError, WidgetValidationError


class TestPortfolioSummaryAdapter:
    """Test portfolio summary widget adapter functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_storage = Mock()
        self.adapter = PortfolioSummaryAdapter(self.mock_storage)
    
    def test_widget_name(self):
        """Test widget name is correct."""
        assert self.adapter.get_widget_name() == "portfolio_summary"
    
    def test_widget_description(self):
        """Test widget description is informative."""
        description = self.adapter.get_widget_description()
        assert "portfolio" in description.lower()
        assert "performance" in description.lower()
    
    def test_validate_input_parameters_valid(self):
        """Test parameter validation with valid inputs."""
        params = self.adapter.validate_input_parameters(portfolio_id="test123")
        assert params["portfolio_id"] == "test123"
    
    def test_validate_input_parameters_none_portfolio_id(self):
        """Test parameter validation with None portfolio_id."""
        params = self.adapter.validate_input_parameters(portfolio_id=None)
        assert params["portfolio_id"] is None
    
    def test_validate_input_parameters_empty_portfolio_id(self):
        """Test parameter validation rejects empty portfolio_id."""
        with pytest.raises(WidgetValidationError) as exc_info:
            self.adapter.validate_input_parameters(portfolio_id="")
        assert "non-empty string" in str(exc_info.value)
    
    def test_extract_calculation_data_no_instruments(self):
        """Test error handling when no instruments exist."""
        self.mock_storage.get_all_instruments.return_value = []
        mock_widget = Mock()
        
        with pytest.raises(WidgetDataError) as exc_info:
            self.adapter.extract_calculation_data(mock_widget)
        
        assert "No instruments found" in str(exc_info.value)
        assert exc_info.value.code == "NO_INSTRUMENTS"
    
    def test_extract_calculation_data_no_holdings(self):
        """Test handling of portfolio with no holdings."""
        # Portfolio exists but no positions with quantity > 0
        self.mock_storage.get_all_instruments.return_value = [
            {"symbol": "AAPL", "quantity": 0, "current_price": 150.0}
        ]
        mock_widget = Mock()
        
        result = self.adapter.extract_calculation_data(mock_widget)
        
        assert result["total_value"] == 0.0
        assert result["positions"] == 0
        assert result["total_return"] == 0.0
    
    def test_extract_calculation_data_no_price_data(self):
        """Test error handling when holdings exist but no price data."""
        self.mock_storage.get_all_instruments.return_value = [
            {"symbol": "AAPL", "quantity": 100, "current_price": None}
        ]
        mock_widget = Mock()
        
        with pytest.raises(WidgetDataError) as exc_info:
            self.adapter.extract_calculation_data(mock_widget)
        
        assert "no current price data" in str(exc_info.value)
        assert exc_info.value.code == "NO_PRICE_DATA"
    
    def test_extract_calculation_data_success(self):
        """Test successful calculation data extraction."""
        # Mock instruments with valid data
        self.mock_storage.get_all_instruments.return_value = [
            {
                "symbol": "AAPL", 
                "quantity": 100, 
                "current_price": 150.0,
                "cash_allocation": 0.0
            },
            {
                "symbol": "GOOGL", 
                "quantity": 50, 
                "current_price": 120.0,
                "cash_allocation": 0.0
            }
        ]
        
        # Mock widget calculation results
        mock_metrics = Mock()
        mock_metrics.total_value = 21000.0  # 100*150 + 50*120
        mock_metrics.total_return_with_divs = 0.15  # 15% return
        
        mock_widget = Mock()
        mock_widget._calculate_all_metrics.return_value = mock_metrics
        
        result = self.adapter.extract_calculation_data(mock_widget)
        
        assert result["total_value"] == 21000.0
        assert result["total_return"] == 3150.0  # 15% of 21000
        assert result["total_return_percent"] == 15.0
        assert result["positions"] == 2
        assert isinstance(result["last_updated"], datetime)
    
    def test_execute_with_caching(self):
        """Test execute method with caching behavior."""
        with patch('api.widgets.portfolio_summary.widget_cache') as mock_cache:
            # No cache hit initially
            mock_cache.get.return_value = None
            
            # Mock successful calculation
            self.mock_storage.get_all_instruments.return_value = [
                {"symbol": "AAPL", "quantity": 100, "current_price": 150.0}
            ]
            
            mock_metrics = Mock()
            mock_metrics.total_value = 15000.0
            mock_metrics.total_return_with_divs = 0.10
            
            with patch.object(self.adapter, '_create_widget_instance') as mock_create:
                mock_widget = Mock()
                mock_widget._calculate_all_metrics.return_value = mock_metrics
                mock_create.return_value = mock_widget
                
                result = self.adapter.execute(portfolio_id=None)
                
                assert result["success"] is True
                assert result["widget_name"] == "portfolio_summary"
                assert result["data"]["total_value"] == 15000.0
                assert result["metadata"]["cache_hit"] is False
                
                # Verify caching was attempted
                mock_cache.set.assert_called_once()
    
    def test_execute_cache_hit(self):
        """Test execute method when cache hit occurs."""
        cached_data = {
            "widget_name": "portfolio_summary",
            "success": True,
            "data": {"total_value": 15000.0},
            "metadata": {"cached_at": "2025-12-07T08:00:00"}
        }
        
        with patch('api.widgets.portfolio_summary.widget_cache') as mock_cache:
            mock_cache.get.return_value = cached_data
            
            result = self.adapter.execute(portfolio_id=None)
            
            assert result["success"] is True
            assert result["data"]["total_value"] == 15000.0
            assert result["metadata"]["cache_hit"] is True
    
    def test_execute_calculation_error(self):
        """Test execute method handles calculation errors properly."""
        self.mock_storage.get_all_instruments.return_value = []
        
        with patch('api.widgets.portfolio_summary.widget_cache') as mock_cache:
            mock_cache.get.return_value = None  # No cache hit
            
            result = self.adapter.execute(portfolio_id=None)
            
            assert result["success"] is False
            assert result["error"]["code"] == "NO_INSTRUMENTS"
            assert "No instruments found" in result["error"]["message"]


if __name__ == "__main__":
    # Simple test runner for development
    adapter = PortfolioSummaryAdapter(Mock())
    print(f"Widget name: {adapter.get_widget_name()}")
    print(f"Description: {adapter.get_widget_description()}")
    print("✅ Basic adapter tests passed")