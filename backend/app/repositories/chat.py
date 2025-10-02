from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone
from pymongo import ReturnDocument

from app.db.mongodb import get_database
from app.models.user import ChatSessionInDB, ChatSessionUpdate


class ChatRepository:
    def __init__(self):
        self._database = None
        self._collection = None

    @property
    def database(self):
        if self._database is None:
            self._database = get_database()
        return self._database

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.database.chat_sessions
        return self._collection

    async def create_session(self, session: ChatSessionInDB) -> ChatSessionInDB:
        session_dict = session.dict(by_alias=True, exclude_unset=True)
        session_dict["created_at"] = datetime.now(timezone.utc)
        session_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.insert_one(session_dict)
        session_dict["_id"] = result.inserted_id
        return ChatSessionInDB(**session_dict)

    async def get_session_by_id(self, session_id: str, user_id: str) -> Optional[ChatSessionInDB]:
        if not ObjectId.is_valid(session_id):
            return None

        session_doc = await self.collection.find_one({
            "_id": ObjectId(session_id),
            "user_id": user_id
        })
        if session_doc:
            return ChatSessionInDB(**session_doc)
        return None

    async def get_user_sessions(self, user_id: str, skip: int = 0, limit: int = 50) -> List[ChatSessionInDB]:
        cursor = self.collection.find({"user_id": user_id}).sort("updated_at", -1).skip(skip).limit(limit)
        sessions = []
        async for session_doc in cursor:
            sessions.append(ChatSessionInDB(**session_doc))
        return sessions

    async def update_session(self, session_id: str, user_id: str, session_update: ChatSessionUpdate) -> Optional[ChatSessionInDB]:
        if not ObjectId.is_valid(session_id):
            return None

        update_data = session_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)

            updated_session = await self.collection.find_one_and_update(
                {"_id": ObjectId(session_id), "user_id": user_id},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER
            )
            if updated_session:
                return ChatSessionInDB(**updated_session)
        return None

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        if not ObjectId.is_valid(session_id):
            return False

        result = await self.collection.delete_one({
            "_id": ObjectId(session_id),
            "user_id": user_id
        })
        return result.deleted_count > 0

    async def count_user_sessions(self, user_id: str) -> int:
        return await self.collection.count_documents({"user_id": user_id})


chat_repository = ChatRepository()

