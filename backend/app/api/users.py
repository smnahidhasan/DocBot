from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
import logging

from app.models.user import User, UserUpdate, UserRole
from app.repositories.user import user_repository
from app.dependencies.auth import (
    get_current_verified_user,
    require_admin,
    require_admin_or_moderator
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/", response_model=List[User])
async def list_users(
        skip: int = Query(0, ge=0, description="Number of users to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
        current_user: User = Depends(require_admin_or_moderator)
):
    """
    List all users (Admin/Moderator only)

    - **skip**: Number of users to skip (pagination)
    - **limit**: Maximum number of users to return
    """
    try:
        users_in_db = await user_repository.list_users(skip=skip, limit=limit)

        # Convert to User models
        users = []
        for user_db in users_in_db:
            users.append(User(
                _id=user_db.id,
                email=user_db.email,
                full_name=user_db.full_name,
                role=user_db.role,
                status=user_db.status,
                created_at=user_db.created_at,
                updated_at=user_db.updated_at,
                last_login=user_db.last_login,
                is_verified=user_db.is_verified
            ))

        return users

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


@router.get("/count")
async def count_users(
        current_user: User = Depends(require_admin_or_moderator)
):
    """
    Get total user count (Admin/Moderator only)
    """
    try:
        count = await user_repository.count_users()
        return {"total_users": count}
    except Exception as e:
        logger.error(f"Error counting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error counting users"
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
        user_id: str,
        current_user: User = Depends(get_current_verified_user)
):
    """
    Get user by ID

    Users can only access their own data unless they are admin/moderator
    """
    # Check if user is trying to access their own data
    if str(current_user.id) == user_id:
        return current_user

    # Only admin/moderator can access other users' data
    if current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        user_db = await user_repository.get_user_by_id(user_id)
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return User(
            _id=user_db.id,
            email=user_db.email,
            full_name=user_db.full_name,
            role=user_db.role,
            status=user_db.status,
            created_at=user_db.created_at,
            updated_at=user_db.updated_at,
            last_login=user_db.last_login,
            is_verified=user_db.is_verified
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        )


@router.put("/{user_id}", response_model=User)
async def update_user(
        user_id: str,
        user_update: UserUpdate,
        current_user: User = Depends(get_current_verified_user)
):
    """
    Update user information

    Users can only update their own basic info unless they are admin
    """
    # Check if user is trying to update their own data
    if str(current_user.id) == user_id:
        # Regular users can only update email and full_name
        if current_user.role == UserRole.USER:
            if user_update.role is not None or user_update.status is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot update role or status"
                )
    else:
        # Only admin can update other users
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    try:
        updated_user = await user_repository.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return User(
            _id=updated_user.id,
            email=updated_user.email,
            full_name=updated_user.full_name,
            role=updated_user.role,
            status=updated_user.status,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            last_login=updated_user.last_login,
            is_verified=updated_user.is_verified
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )


@router.delete("/{user_id}")
async def delete_user(
        user_id: str,
        current_user: User = Depends(require_admin)
):
    """
    Delete user (Admin only)
    """
    # Prevent admin from deleting themselves
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    try:
        success = await user_repository.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"User deleted: {user_id} by {current_user.email}")
        return {"message": "User deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )
    