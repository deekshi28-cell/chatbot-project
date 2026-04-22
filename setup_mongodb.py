#!/usr/bin/env python3
"""
MongoDB Database Setup Script
This script connects to MongoDB and sets up the database structure for the chatbot application.
"""

import pymongo
from pymongo import MongoClient
import os
from datetime import datetime
import json

# MongoDB connection settings
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "chatbot_db"

def connect_to_mongodb():
    """Connect to MongoDB and return database instance"""
    try:
        client = MongoClient(MONGODB_URL)
        # Test connection
        client.admin.command('ping')
        print(f"✅ Successfully connected to MongoDB at {MONGODB_URL}")
        
        db = client[DB_NAME]
        print(f"✅ Using database: {DB_NAME}")
        return client, db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None, None

def show_current_structure(db):
    """Display current database structure"""
    print("\n📊 Current Database Structure:")
    print("=" * 50)
    
    collections = db.list_collection_names()
    if not collections:
        print("No collections found in database")
        return
    
    for collection_name in collections:
        collection = db[collection_name]
        count = collection.count_documents({})
        print(f"Collection: {collection_name} ({count} documents)")
        
        # Show sample document structure
        sample = collection.find_one()
        if sample:
            print(f"  Sample document structure:")
            for key, value in sample.items():
                print(f"    {key}: {type(value).__name__}")
        print()

def create_indexes(db):
    """Create indexes for better performance"""
    print("\n🔧 Creating Database Indexes:")
    print("=" * 50)
    
    # Messages collection indexes
    messages_collection = db.messages
    messages_collection.create_index([("session_id", 1), ("timestamp", -1)])
    messages_collection.create_index([("timestamp", -1)])
    print("✅ Created indexes for messages collection")
    
    # Products collection indexes
    products_collection = db.products
    products_collection.create_index([("product_name", "text"), ("description", "text")])
    products_collection.create_index([("category", 1)])
    products_collection.create_index([("price", 1)])
    print("✅ Created indexes for products collection")
    
    # Sessions collection indexes
    sessions_collection = db.sessions
    sessions_collection.create_index([("session_id", 1)])
    sessions_collection.create_index([("created_at", -1)])
    print("✅ Created indexes for sessions collection")

def setup_collections(db):
    """Set up collections with proper schema validation"""
    print("\n🏗️ Setting up Collections:")
    print("=" * 50)
    
    # Messages collection schema
    messages_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["session_id", "message", "sender", "timestamp"],
            "properties": {
                "session_id": {"bsonType": "string"},
                "message": {"bsonType": "string"},
                "sender": {"bsonType": "string", "enum": ["user", "bot"]},
                "timestamp": {"bsonType": "date"},
                "intent_name": {"bsonType": "string"},
                "confidence": {"bsonType": "number"},
                "response_source": {"bsonType": "string", "enum": ["dialogflow", "gemini", "mongodb", "fallback"]}
            }
        }
    }
    
    # Products collection schema
    products_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["product_name", "price", "category"],
            "properties": {
                "product_name": {"bsonType": "string"},
                "price": {"bsonType": "number"},
                "category": {"bsonType": "string"},
                "description": {"bsonType": "string"},
                "in_stock": {"bsonType": "bool"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"}
            }
        }
    }
    
    # Sessions collection schema
    sessions_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["session_id", "created_at"],
            "properties": {
                "session_id": {"bsonType": "string"},
                "created_at": {"bsonType": "date"},
                "last_activity": {"bsonType": "date"},
                "message_count": {"bsonType": "int"},
                "user_info": {"bsonType": "object"}
            }
        }
    }
    
    try:
        # Create or modify collections with validation
        db.create_collection("messages", validator=messages_validator)
        print("✅ Messages collection created/updated")
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️ Messages collection already exists")
        else:
            print(f"⚠️ Messages collection: {e}")
    
    try:
        db.create_collection("products", validator=products_validator)
        print("✅ Products collection created/updated")
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️ Products collection already exists")
        else:
            print(f"⚠️ Products collection: {e}")
    
    try:
        db.create_collection("sessions", validator=sessions_validator)
        print("✅ Sessions collection created/updated")
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️ Sessions collection already exists")
        else:
            print(f"⚠️ Sessions collection: {e}")

def populate_sample_data(db):
    """Populate collections with sample data if empty"""
    print("\n📝 Populating Sample Data:")
    print("=" * 50)
    
    # Sample products
    products_collection = db.products
    if products_collection.count_documents({}) == 0:
        sample_products = [
            {
                "product_name": "iPhone 15",
                "price": 999.99,
                "category": "smartphones",
                "description": "Latest iPhone with advanced camera and A17 chip",
                "in_stock": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "product_name": "MacBook Pro",
                "price": 1999.99,
                "category": "laptops",
                "description": "Powerful laptop with M3 chip for professionals",
                "in_stock": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "product_name": "AirPods Pro",
                "price": 249.99,
                "category": "audio",
                "description": "Wireless earbuds with active noise cancellation",
                "in_stock": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "product_name": "iPad Air",
                "price": 599.99,
                "category": "tablets",
                "description": "Versatile tablet for work and entertainment",
                "in_stock": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        products_collection.insert_many(sample_products)
        print(f"✅ Inserted {len(sample_products)} sample products")
    else:
        print("ℹ️ Products collection already has data")
    
    # Sample session
    sessions_collection = db.sessions
    if sessions_collection.count_documents({}) == 0:
        sample_session = {
            "session_id": "sample_session_001",
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "message_count": 0,
            "user_info": {"source": "web_interface"}
        }
        sessions_collection.insert_one(sample_session)
        print("✅ Created sample session")
    else:
        print("ℹ️ Sessions collection already has data")

def show_collection_stats(db):
    """Show statistics for each collection"""
    print("\n📈 Collection Statistics:")
    print("=" * 50)
    
    collections = ["messages", "products", "sessions"]
    
    for collection_name in collections:
        collection = db[collection_name]
        count = collection.count_documents({})
        
        if count > 0:
            # Get date range for time-based collections
            if collection_name in ["messages", "sessions"]:
                pipeline = [
                    {"$group": {
                        "_id": None,
                        "oldest": {"$min": "$created_at" if collection_name == "sessions" else "$timestamp"},
                        "newest": {"$max": "$created_at" if collection_name == "sessions" else "$timestamp"}
                    }}
                ]
                result = list(collection.aggregate(pipeline))
                if result:
                    oldest = result[0]["oldest"]
                    newest = result[0]["newest"]
                    print(f"{collection_name}: {count} documents (from {oldest} to {newest})")
                else:
                    print(f"{collection_name}: {count} documents")
            else:
                print(f"{collection_name}: {count} documents")
        else:
            print(f"{collection_name}: 0 documents")

def main():
    """Main function to set up MongoDB database"""
    print("🚀 MongoDB Database Setup for Chatbot Application")
    print("=" * 60)
    
    # Connect to MongoDB
    client, db = connect_to_mongodb()
    if db is None:
        return
    
    # Show current structure
    show_current_structure(db)
    
    # Set up collections with validation
    setup_collections(db)
    
    # Create indexes
    create_indexes(db)
    
    # Populate sample data
    populate_sample_data(db)
    
    # Show final statistics
    show_collection_stats(db)
    
    print("\n✅ Database setup completed successfully!")
    print("\n📋 Collections created:")
    print("  • messages - Store chat messages with metadata")
    print("  • products - Store product information")
    print("  • sessions - Track user sessions")
    print("\n🔍 Indexes created for optimal performance")
    print("📝 Sample data populated for testing")
    
    # Close connection
    client.close()
    print("\n🔌 MongoDB connection closed")

if __name__ == "__main__":
    main()
