"""
Custom API Exception Handlers

Standardized error handling and validation for all API endpoints.
Provides consistent error responses across the application.
"""

import logging
from typing import Any, Dict, List, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from datetime import datetime


logger = logging.getLogger(__name__)


class BusinessLogicError(HTTPException):
    """Custom exception for business logic validation errors."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class ResourceNotFoundError(HTTPException):
    """Custom exception for missing resources."""
    
    def __init__(self, resource_type: str, identifier: str):
        detail = f"{resource_type} with identifier '{identifier}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InsufficientDataError(BusinessLogicError):
    """Exception for insufficient historical data."""
    
    def __init__(self, symbols: List[str], required_days: int, available_days: int):
        detail = f"Insufficient data for symbols {symbols}. Required: {required_days} days, Available: {available_days} days"
        super().__init__(detail=detail)


class InvalidConstraintsError(BusinessLogicError):
    """Exception for invalid optimization constraints."""
    
    def __init__(self, message: str):
        detail = f"Invalid optimization constraints: {message}"
        super().__init__(detail=detail)


class SimulationError(HTTPException):
    """Exception for Monte Carlo simulation errors."""
    
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Simulation failed: {detail}")


def create_error_response(
    error_type: str,
    message: str,
    details: Union[Dict[str, Any], List[Dict[str, Any]], None] = None,
    status_code: int = 500
) -> Dict[str, Any]:
    """
    Create standardized error response format.
    
    Args:
        error_type: Type of error (validation, business_logic, not_found, internal)
        message: Main error message
        details: Additional error details or validation errors
        status_code: HTTP status code
        
    Returns:
        Standardized error response dictionary
    """
    response = {
        "error": {
            "type": error_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors (422 Unprocessable Entity).
    
    Returns detailed validation error information for debugging.
    """
    validation_errors = []
    
    for error in exc.errors():
        validation_errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input_value": error.get("input")
        })
    
    logger.warning(f"Validation error on {request.method} {request.url}: {validation_errors}")
    
    response_content = create_error_response(
        error_type="validation",
        message="Request validation failed",
        details=validation_errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_content
    )


async def business_logic_exception_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
    """
    Handle business logic validation errors (400 Bad Request).
    
    These are domain-specific validation errors like insufficient data,
    invalid constraints, or business rule violations.
    """
    logger.info(f"Business logic error on {request.method} {request.url}: {exc.detail}")
    
    response_content = create_error_response(
        error_type="business_logic",
        message=exc.detail,
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    )


async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """
    Handle resource not found errors (404 Not Found).
    
    For missing instruments, portfolios, tasks, or other resources.
    """
    logger.info(f"Resource not found on {request.method} {request.url}: {exc.detail}")
    
    response_content = create_error_response(
        error_type="not_found",
        message=exc.detail,
        status_code=status.HTTP_404_NOT_FOUND
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response_content
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle general HTTP exceptions with standardized format.
    
    Catches HTTPException instances and formats them consistently.
    """
    # Log based on severity
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code} error on {request.method} {request.url}: {exc.detail}")
    elif exc.status_code >= 400:
        logger.warning(f"HTTP {exc.status_code} error on {request.method} {request.url}: {exc.detail}")
    
    # Determine error type based on status code
    if exc.status_code == 401:
        error_type = "authentication"
    elif exc.status_code == 403:
        error_type = "authorization"
    elif exc.status_code == 404:
        error_type = "not_found"
    elif exc.status_code >= 500:
        error_type = "internal"
    else:
        error_type = "client_error"
    
    response_content = create_error_response(
        error_type=error_type,
        message=exc.detail,
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    )


async def internal_server_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected server errors (500 Internal Server Error).
    
    Logs full stack trace while returning safe error message to client.
    """
    logger.error(
        f"Internal server error on {request.method} {request.url}: {str(exc)}",
        exc_info=True
    )
    
    response_content = create_error_response(
        error_type="internal",
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content
    )


async def simulation_exception_handler(request: Request, exc: SimulationError) -> JSONResponse:
    """
    Handle Monte Carlo simulation specific errors.
    
    These are typically computational errors or data-related issues.
    """
    logger.error(f"Simulation error on {request.method} {request.url}: {exc.detail}")
    
    response_content = create_error_response(
        error_type="simulation",
        message=exc.detail,
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    )


# Exception handler mapping for FastAPI app registration
exception_handlers = {
    RequestValidationError: validation_exception_handler,
    BusinessLogicError: business_logic_exception_handler,
    ResourceNotFoundError: resource_not_found_exception_handler,
    SimulationError: simulation_exception_handler,
    HTTPException: http_exception_handler,
    Exception: internal_server_exception_handler,
}