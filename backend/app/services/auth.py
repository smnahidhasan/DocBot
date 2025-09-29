import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
import logging

from app.models.user import UserInDB, UserCreate, User, TokenData
from app.repositories.user import user_repository

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify JWT token and return token data"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return TokenData(user_id=user_id)
        except JWTError:
            return None

    @staticmethod
    def generate_verification_token() -> str:
        """Generate verification token"""
        return secrets.token_urlsafe(32)

    async def register_user(self, user_create: UserCreate) -> User:
        """Register a new user"""
        # Check if email already exists
        if await user_repository.email_exists(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = self.get_password_hash(user_create.password)

        # Generate verification token
        verification_token = self.generate_verification_token()

        # Create user in database
        user_in_db = UserInDB(
            **user_create.dict(exclude={"password"}),
            hashed_password=hashed_password,
            verification_token=verification_token
        )

        try:
            created_user = await user_repository.create_user(user_in_db)
            logger.info(f"User registered: {created_user.email}")

            # Convert to User model (without sensitive data)
            return User(
                _id=created_user.id,
                email=created_user.email,
                full_name=created_user.full_name,
                role=created_user.role,
                status=created_user.status,
                created_at=created_user.created_at,
                updated_at=created_user.updated_at,
                last_login=created_user.last_login,
                is_verified=created_user.is_verified
            )
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user"
            )

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        user = await user_repository.get_user_by_email(email)
        if not user:
            return None

        # Check if user is suspended or has too many login attempts
        if user.status == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account suspended"
            )

        if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )

        if not self.verify_password(password, user.hashed_password):
            # Increment login attempts
            await user_repository.increment_login_attempts(email)
            return None

        # Reset login attempts and update last login
        await user_repository.reset_login_attempts(email)
        await user_repository.update_last_login(str(user.id))

        logger.info(f"User authenticated: {user.email}")
        return user

    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token_data = self.verify_token(token)
        if token_data is None or token_data.user_id is None:
            raise credentials_exception

        user = await user_repository.get_user_by_id(token_data.user_id)
        if user is None:
            raise credentials_exception

        # Check if user is active
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        return User(
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

    async def verify_user_email(self, token: str) -> bool:
        """Verify user email with verification token"""
        user = await user_repository.get_user_by_verification_token(token)
        if not user:
            return False

        success = await user_repository.verify_user(str(user.id))
        if success:
            logger.info(f"User email verified: {user.email}")
        return success

    def require_roles(self, required_roles: list):
        """Decorator to check user roles"""

        def role_checker(current_user: User):
            if current_user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user

        return role_checker


# Singleton instance
auth_service = AuthService()
