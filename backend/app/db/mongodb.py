import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Create database connection"""
    try:
        # mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongodb_url = 'mongodb+srv://smhasanruetece17_db_user:docDB#$12@cluster0.c7nkpux.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
        database_name = os.getenv("DATABASE_NAME", "docbot")

        logger.info(f"Connecting to mongodb database: {mongodb_url}")

        mongodb.client = AsyncIOMotorClient(mongodb_url)
        mongodb.database = mongodb.client[database_name]

        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")

        # Create indexes
        await create_indexes()

    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


async def create_indexes():
    """Create database indexes for better performance"""
    try:
        users_collection = mongodb.database.users

        # Create unique index on email
        await users_collection.create_index("email", unique=True)

        # Create index on verification_token
        await users_collection.create_index("verification_token", sparse=True)

        # Create index on created_at for sorting
        await users_collection.create_index("created_at")

        logger.info("Database indexes created successfully")

    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")


def get_database():
    """Get database instance"""
    return mongodb.database
