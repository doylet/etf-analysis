"""
Authentication and Authorization

JWT-based authentication for API endpoints.
Handles token generation, validation, and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm


# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str


class LoginRequest(BaseModel):
    """Request model for user login."""
    username: str
    password: str


class TokenData(BaseModel):
    """Data encoded in JWT token."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    token_type: Optional[str] = "access"  # "access" or "refresh"


class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plaintext password against hashed password.
    
    Args:
        plain_password: Password to verify
        hashed_password: Bcrypt hashed password
        
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password: Plaintext password
        
    Returns:
        Bcrypt hashed password
    """
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Dictionary of claims to encode in token
        expires_delta: Token expiration time (default: 30 minutes)
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Dictionary of claims to encode in token
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("token_type", "access")
        
        if username is None:
            return None
        
        return TokenData(username=username, user_id=user_id, token_type=token_type)
    
    except JWTError:
        return None


# Fake user database for testing (TODO: Replace with real user repository)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret" hash
        "disabled": False,
    }
}


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate user with username and password.
    
    Args:
        username: Username
        password: Plaintext password
        
    Returns:
        UserInDB if authenticated, None if invalid credentials
    """
    user_dict = fake_users_db.get(username)
    
    if not user_dict:
        return None
    
    user = UserInDB(**user_dict)
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials (Bearer token)
        
    Returns:
        User information
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = decode_access_token(token)
        
        if token_data is None or token_data.username is None:
            raise credentials_exception
            
        # Check if it's a refresh token (should not be used for regular access)
        if token_data.token_type == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token cannot be used for API access"
            )
        
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user_dict = fake_users_db.get(token_data.username)
    if user_dict is None:
        raise credentials_exception
    
    user = User(**user_dict)
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


# Create authentication router
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest) -> Token:
    """
    Authenticate user and return JWT tokens.
    
    Args:
        login_data: Username and password
        
    Returns:
        JWT access and refresh tokens
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user = authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": 1}, 
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": 1}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshTokenRequest) -> Token:
    """
    Refresh JWT access token using refresh token.
    
    Args:
        refresh_data: Refresh token
        
    Returns:
        New JWT access and refresh tokens
        
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = decode_access_token(refresh_data.refresh_token)
        
        if token_data is None or token_data.username is None:
            raise credentials_exception
            
        # Check if it's actually a refresh token
        if token_data.token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for refresh"
            )
        
    except JWTError:
        raise credentials_exception
    
    # Verify user still exists and is active
    user_dict = fake_users_db.get(token_data.username)
    if user_dict is None:
        raise credentials_exception
    
    user = User(**user_dict)
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": token_data.user_id}, 
        expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": token_data.user_id}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return current_user


__all__ = [
    'Token',
    'TokenData',
    'User',
    'UserInDB',
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'decode_access_token',
    'authenticate_user',
]
