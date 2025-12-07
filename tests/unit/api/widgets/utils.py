"""Test utilities for widget unit tests."""

from typing import Dict, Any, Optional
from datetime import datetime
import pytest
from unittest.mock import Mock, MagicMock

from src.api.schemas.widgets import WidgetResponse, PortfolioSummaryData
from src.api.widgets.base import BaseWidgetAdapter


class MockWidgetAdapter(BaseWidgetAdapter):
    """Mock widget adapter for testing."""
    
    def __init__(self, storage, widget_class=None):
        super().__init__(storage, widget_class or Mock())
        self.test_data = {}
        self.should_fail = False
        self.failure_type = None
        
    def get_widget_name(self) -> str:
        return "test_widget"
        
    def get_widget_description(self) -> str:
        return "Test widget for unit tests"
        
    def extract_calculation_data(self, widget_instance) -> Dict[str, Any]:
        if self.should_fail:
            if self.failure_type == "calculation_error":
                raise Exception("Test calculation error")
            elif self.failure_type == "data_error":
                raise ValueError("Test data error")
                
        return self.test_data
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        if self.should_fail and self.failure_type == "validation_error":
            from src.api.widgets.exceptions import WidgetValidationError
            raise WidgetValidationError("Test validation error")
            
        return kwargs


def create_mock_storage():
    """Create mock database storage for tests."""
    storage = Mock()
    storage.get_portfolio_summary.return_value = {
        'total_value': 100000.0,
        'total_return': 5000.0,
        'total_return_percent': 5.0,
        'day_change': 250.0,
        'day_change_percent': 0.25,
        'positions': 10,
        'allocated_cash': 5000.0,
        'last_updated': datetime.utcnow()
    }
    return storage


def create_mock_portfolio_data():
    """Create mock portfolio data for tests."""
    return {
        'total_value': 100000.0,
        'cash': 5000.0,
        'last_updated': datetime.utcnow().isoformat(),
        'positions': [
            {
                'symbol': 'AAPL',
                'quantity': 100,
                'current_price': 150.0,
                'market_value': 15000.0
            },
            {
                'symbol': 'GOOGL', 
                'quantity': 50,
                'current_price': 2500.0,
                'market_value': 125000.0
            }
        ]
    }


def create_sample_widget_response(success: bool = True) -> WidgetResponse:
    """Create sample widget response for tests."""
    if success:
        return WidgetResponse(
            widget_name="test_widget",
            success=True,
            data={
                "total_value": 100000.0,
                "positions": 10,
                "last_updated": datetime.utcnow().isoformat()
            },
            metadata={
                "execution_time": datetime.utcnow().isoformat(),
                "parameters": {},
                "widget_description": "Test widget"
            },
            error=None
        )
    else:
        from src.api.schemas.widgets import WidgetError
        return WidgetResponse(
            widget_name="test_widget",
            success=False,
            data=None,
            metadata={
                "execution_time": datetime.utcnow().isoformat(),
                "parameters": {},
                "widget_description": "Test widget"
            },
            error=WidgetError(
                code="TEST_ERROR",
                message="Test error message",
                details={"test": "details"}
            )
        )


def assert_widget_response_structure(response: WidgetResponse):
    """Assert that a widget response has the correct structure."""
    assert hasattr(response, 'widget_name')
    assert hasattr(response, 'success')
    assert hasattr(response, 'data')
    assert hasattr(response, 'metadata')
    assert hasattr(response, 'error')
    
    assert isinstance(response.success, bool)
    assert isinstance(response.metadata, dict)
    
    if response.success:
        assert response.data is not None
        assert response.error is None
    else:
        assert response.error is not None
        assert hasattr(response.error, 'code')
        assert hasattr(response.error, 'message')


@pytest.fixture
def mock_storage():
    """Pytest fixture for mock storage."""
    return create_mock_storage()


@pytest.fixture
def mock_widget_adapter(mock_storage):
    """Pytest fixture for mock widget adapter."""
    adapter = MockWidgetAdapter(mock_storage)
    adapter.test_data = {
        "test_result": "success",
        "calculation_time": datetime.utcnow().isoformat()
    }
    return adapter


@pytest.fixture
def sample_portfolio_data():
    """Pytest fixture for sample portfolio data."""
    return create_mock_portfolio_data()