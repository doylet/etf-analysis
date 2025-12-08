"""Authentication and authorization patterns for widget API endpoints."""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from api.auth import get_current_user  # Existing auth system
from models.user import User

logger = logging.getLogger(__name__)

# Bearer token security scheme
security = HTTPBearer(auto_error=False)


class WidgetAuthLevel:
    """Widget authentication requirement levels."""
    
    PUBLIC = "public"           # No authentication required
    AUTHENTICATED = "authenticated"  # Requires valid user token
    PREMIUM = "premium"         # Requires premium subscription
    ADMIN = "admin"            # Requires admin privileges


class WidgetAccessControl:
    """Access control for different widget types and features."""
    
    # Widget authentication requirements
    WIDGET_AUTH_LEVELS = {
        "portfolio_summary": WidgetAuthLevel.AUTHENTICATED,
        "holdings_breakdown": WidgetAuthLevel.AUTHENTICATED, 
        "correlation_matrix": WidgetAuthLevel.PREMIUM,
        "monte_carlo": WidgetAuthLevel.PREMIUM,
        "optimization": WidgetAuthLevel.PREMIUM,
        "health": WidgetAuthLevel.PUBLIC,
        "list": WidgetAuthLevel.PUBLIC
    }
    
    # Rate limits per authentication level (requests per minute)
    RATE_LIMITS = {
        WidgetAuthLevel.PUBLIC: 10,
        WidgetAuthLevel.AUTHENTICATED: 100,
        WidgetAuthLevel.PREMIUM: 500,
        WidgetAuthLevel.ADMIN: 1000
    }
    
    @classmethod
    def get_widget_auth_level(cls, widget_name: str) -> str:
        """Get authentication level required for widget."""
        return cls.WIDGET_AUTH_LEVELS.get(widget_name, WidgetAuthLevel.AUTHENTICATED)
    
    @classmethod
    def get_rate_limit(cls, auth_level: str) -> int:
        """Get rate limit for authentication level."""
        return cls.RATE_LIMITS.get(auth_level, 10)


async def get_widget_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    widget_name: str = "unknown"
) -> Optional[User]:
    """
    Get authenticated user for widget access with flexible authentication.
    
    Args:
        credentials: Bearer token credentials (optional)
        widget_name: Name of widget being accessed
        
    Returns:
        User object if authenticated, None if public access allowed
        
    Raises:
        HTTPException: If authentication required but not provided/invalid
    """
    auth_level = WidgetAccessControl.get_widget_auth_level(widget_name)
    
    # Public access - no authentication required
    if auth_level == WidgetAuthLevel.PUBLIC:
        return None
    
    # Authentication required
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication required for {widget_name} widget",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Use existing authentication system
        user = await get_current_user(credentials.credentials)
        
        # Check authorization level
        if auth_level == WidgetAuthLevel.PREMIUM:
            if not user.has_premium_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Premium subscription required for {widget_name} widget"
                )
        
        elif auth_level == WidgetAuthLevel.ADMIN:
            if not user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Admin privileges required for {widget_name} widget"
                )
        
        logger.info(f"Widget access granted: {widget_name} for user {user.id}")
        return user
        
    except HTTPException:
        # Re-raise auth errors
        raise
    except Exception as e:
        logger.error(f"Widget authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


def create_widget_dependencies(widget_name: str):
    """
    Create dependency function for specific widget authentication.
    
    Args:
        widget_name: Name of the widget for auth level lookup
        
    Returns:
        Dependency function that can be used with FastAPI Depends()
    """
    async def widget_auth_dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[User]:
        return await get_widget_user(credentials, widget_name)
    
    return widget_auth_dependency


# Commonly used dependency functions
get_portfolio_user = create_widget_dependencies("portfolio_summary")
get_holdings_user = create_widget_dependencies("holdings_breakdown") 
get_correlation_user = create_widget_dependencies("correlation_matrix")
get_montecarlo_user = create_widget_dependencies("monte_carlo")
get_optimization_user = create_widget_dependencies("optimization")
get_public_user = create_widget_dependencies("health")


class UserContext:
    """Context information for widget execution."""
    
    def __init__(self, user: Optional[User] = None, widget_name: str = "unknown"):
        self.user = user
        self.widget_name = widget_name
        self.is_authenticated = user is not None
        self.user_id = user.id if user else None
        self.auth_level = WidgetAccessControl.get_widget_auth_level(widget_name)
        self.rate_limit = WidgetAccessControl.get_rate_limit(self.auth_level)
    
    @property
    def can_access_premium_features(self) -> bool:
        """Check if user can access premium features."""
        if not self.user:
            return False
        return hasattr(self.user, 'has_premium_access') and self.user.has_premium_access
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges.""" 
        if not self.user:
            return False
        return hasattr(self.user, 'is_admin') and self.user.is_admin
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging/metadata."""
        return {
            "user_id": self.user_id,
            "widget_name": self.widget_name,
            "is_authenticated": self.is_authenticated,
            "auth_level": self.auth_level,
            "rate_limit": self.rate_limit,
            "premium_access": self.can_access_premium_features,
            "admin_access": self.is_admin
        }