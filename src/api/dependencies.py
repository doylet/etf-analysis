"""
Dependency Injection

Provides dependency injection for services and repositories used across the API.
FastAPI will use these dependency functions to inject instances into route handlers.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False


# Security scheme for JWT authentication
security = HTTPBearer()


# Celery app instance (global)
_celery_app = None


def get_celery_app():
    """
    Get Celery application instance for task management.
    
    Returns:
        Celery application instance
        
    Raises:
        HTTPException: 503 if Celery is not available
    """
    global _celery_app
    
    if not CELERY_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Celery is not available - async tasks disabled"
        )
    
    if _celery_app is None:
        # Initialize Celery with basic configuration
        _celery_app = Celery(
            'etf_analysis',
            broker='redis://localhost:6379/0',
            backend='redis://localhost:6379/0'
        )
        
        # Basic configuration
        _celery_app.conf.update(
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            result_expires=3600,
            timezone='UTC',
            enable_utc=True
        )
    
    return _celery_app


# Placeholder for service and repository dependencies
# These will be populated as services and repositories are implemented

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials (Bearer token)
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: 401 if token is invalid
        
    TODO: Implement actual JWT validation in T010
    """
    # Placeholder - will be implemented in T010 (auth.py)
    return {"username": "test_user", "user_id": 1}


# Service dependencies (to be implemented)
# async def get_monte_carlo_service() -> MonteCarloService:
#     """Get Monte Carlo simulation service instance."""
#     pass

# async def get_optimization_service() -> OptimizationService:
#     """Get portfolio optimization service instance."""
#     pass

# Repository dependencies (to be implemented)
# async def get_instrument_repository() -> InstrumentRepository:
#     """Get instrument repository instance."""
#     pass

# async def get_order_repository() -> OrderRepository:
#     """Get order repository instance."""
#     pass


__all__ = ['get_current_user', 'security', 'get_celery_app']
