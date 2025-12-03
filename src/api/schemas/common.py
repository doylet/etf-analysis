"""
Common API Schemas

Shared request/response models used across multiple API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional, Any
from datetime import datetime


# Generic type for paginated data
T = TypeVar('T')


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Any] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input parameters",
                "details": {"field": "weights", "issue": "must sum to 1.0"},
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response format."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response wrapper.
    
    Used for endpoints that return lists with pagination support.
    """
    
    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": ["item1", "item2", "item3"],
                "total": 50,
                "page": 1,
                "page_size": 10,
                "pages": 5
            }
        }


class TaskStatusResponse(BaseModel):
    """
    Async task status response.
    
    Used to track progress of long-running operations.
    """
    
    task_id: str = Field(..., description="Celery task ID")
    state: str = Field(..., description="Task state (PENDING, STARTED, SUCCESS, FAILURE)")
    status: str = Field(..., description="Human-readable status message")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage (0-100)")
    result: Optional[Any] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc-123-def-456",
                "state": "PROGRESS",
                "status": "Running simulation...",
                "progress": 45.0,
                "result": None,
                "error": None
            }
        }


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")


__all__ = [
    'ErrorResponse',
    'SuccessResponse',
    'PaginatedResponse',
    'TaskStatusResponse',
    'PaginationParams',
]
