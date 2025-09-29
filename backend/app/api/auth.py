from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
import logging

from app.models.user import (
    User, UserCreate, LoginRequest, LoginResponse, Token
)
from app.services.auth import auth_service, ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies.auth import get_current_user, get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate):
    """
    Register a new user

    - **email**: User's email address (must be unique)
    - **password**: User's password
    - **full_name**: User's full name
    - **role**: User role (default: user)
    """
    try:
        return await auth_service.register_user(user_create)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """
    Login with email and password

    Returns access token for authenticated requests
    """
    user = await auth_service.authenticate_user(
        login_request.email,
        login_request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    # Convert to User model for response
    user_response = User(
        _id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        is_verified=user.is_verified
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=user_response
    )


@router.get("/me", response_model=User)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """
    Get current user information

    Requires valid authentication token
    """
    return current_user


@router.post("/verify-email")
async def verify_email(token: str):
    """
    Verify user email with verification token
    """
    success = await auth_service.verify_user_email(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    return {"message": "Email verified successfully"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
        current_user: User = Depends(get_current_active_user)
):
    """
    Refresh access token

    Requires valid authentication token
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_user)
):
    """
    Logout user

    Note: Since we're using stateless JWT tokens,
    logout is handled client-side by discarding the token.
    For enhanced security, implement token blacklisting.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}
