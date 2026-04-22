from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.messages_collection = None
        
    async def connect(self):
        """Connect to MongoDB local instance"""
        try:
            # MongoDB connection string for local instance
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            self.client = AsyncIOMotorClient(mongodb_url)
            
            # Database name
            db_name = os.getenv("DB_NAME", "chatbot_db")
            self.db = self.client[db_name]
            
            # Collections
            self.messages_collection = self.db["messages"]
            
            # Test connection
            await self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise e
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    async def store_message(self, message_doc: Dict[str, Any]) -> str:
        """Store a chat message in the database"""
        try:
            result = await self.messages_collection.insert_one(message_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing message: {e}")
            raise e
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve chat history for a session"""
        try:
            cursor = self.messages_collection.find(
                {"session_id": session_id}
            ).sort("timestamp", 1).limit(limit)
            
            messages = []
            async for message in cursor:
                # Convert ObjectId to string for JSON serialization
                message["_id"] = str(message["_id"])
                messages.append(message)
            
            return messages
        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            raise e
    
    async def get_all_sessions(self) -> List[str]:
        """Get all unique session IDs"""
        try:
            sessions = await self.messages_collection.distinct("session_id")
            return sessions
        except Exception as e:
            print(f"Error retrieving sessions: {e}")
            raise e
