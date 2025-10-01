from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone
from pymongo import ReturnDocument

from app.db.mongodb import get_database
from app.models.user import UserInDB, UserCreate, UserUpdate


class UserRepository:
    def __init__(self):
        self._database = None
        self._collection = None

    @property
    def database(self):
        """Lazy loading of database"""
        if self._database is None:
            self._database = get_database()
        return self._database

    @property
    def collection(self):
        """Lazy loading of collection"""
        if self._collection is None:
            self._collection = self.database.users
        return self._collection

    async def create_user(self, user: UserInDB) -> UserInDB:
        """Create a new user"""
        user_dict = user.dict(by_alias=True, exclude_unset=True)
        user_dict["created_at"] = datetime.now(timezone.utc)
        user_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return UserInDB(**user_dict)

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        if not ObjectId.is_valid(user_id):
            return None

        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def get_user_by_verification_token(self, token: str) -> Optional[UserInDB]:
        """Get user by verification token"""
        user_doc = await self.collection.find_one({"verification_token": token})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update user"""
        if not ObjectId.is_valid(user_id):
            return None

        update_data = user_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)

            updated_user = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER
            )
            if updated_user:
                return UserInDB(**updated_user)
        return None

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login time"""
        if not ObjectId.is_valid(user_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "last_login": datetime.now(timezone.utc),
                    "login_attempts": 0
                }
            }
        )
        return result.modified_count > 0

    async def increment_login_attempts(self, email: str) -> int:
        """Increment login attempts for a user"""
        result = await self.collection.find_one_and_update(
            {"email": email},
            {"$inc": {"login_attempts": 1}},
            return_document=ReturnDocument.AFTER
        )
        if result:
            return result.get("login_attempts", 0)
        return 0

    async def reset_login_attempts(self, email: str) -> bool:
        """Reset login attempts for a user"""
        result = await self.collection.update_one(
            {"email": email},
            {"$set": {"login_attempts": 0}}
        )
        return result.modified_count > 0

    async def verify_user(self, user_id: str) -> bool:
        """Mark user as verified"""
        if not ObjectId.is_valid(user_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "is_verified": True,
                    "verification_token": None,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return result.modified_count > 0

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if not ObjectId.is_valid(user_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """List users with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
        users = []
        async for user_doc in cursor:
            users.append(UserInDB(**user_doc))
        return users

    async def count_users(self) -> int:
        """Count total users"""
        return await self.collection.count_documents({})

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        count = await self.collection.count_documents({"email": email})
        return count > 0


# Singleton instance
user_repository = UserRepository()
