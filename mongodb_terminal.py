#!/usr/bin/env python3
"""
MongoDB Terminal Interface
Interactive terminal interface for MongoDB operations
"""

import pymongo
from pymongo import MongoClient
import json
from datetime import datetime
import sys

# MongoDB connection settings
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "chatbot_db"

class MongoDBTerminal:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(MONGODB_URL)
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            print(f"✅ Connected to MongoDB: {DB_NAME}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def show_collections(self):
        """Show all collections"""
        collections = self.db.list_collection_names()
        print("\n📁 Collections:")
        for i, collection in enumerate(collections, 1):
            count = self.db[collection].count_documents({})
            print(f"  {i}. {collection} ({count} documents)")
    
    def show_messages(self, limit=10):
        """Show recent messages"""
        messages = self.db.messages.find().sort("timestamp", -1).limit(limit)
        print(f"\n💬 Recent Messages (last {limit}):")
        print("-" * 80)
        for msg in messages:
            timestamp = msg.get('timestamp', 'Unknown')
            sender = msg.get('sender', 'Unknown')
            message = msg.get('message', '')[:50] + "..." if len(msg.get('message', '')) > 50 else msg.get('message', '')
            session = msg.get('session_id', 'Unknown')[:10]
            print(f"{timestamp} | {sender:4} | {session} | {message}")
    
    def show_products(self):
        """Show all products"""
        products = self.db.products.find()
        print("\n🛍️ Products:")
        print("-" * 80)
        for product in products:
            name = product.get('product_name', 'Unknown')
            price = product.get('price', 0)
            category = product.get('category', 'Unknown')
            stock = "✅" if product.get('in_stock', False) else "❌"
            print(f"{name:20} | ${price:8.2f} | {category:15} | {stock}")
    
    def show_sessions(self):
        """Show all sessions"""
        sessions = self.db.sessions.find().sort("created_at", -1)
        print("\n🔗 Sessions:")
        print("-" * 80)
        for session in sessions:
            session_id = session.get('session_id', 'Unknown')[:20]
            created = session.get('created_at', 'Unknown')
            msg_count = session.get('message_count', 0)
            last_activity = session.get('last_activity', 'Unknown')
            print(f"{session_id:20} | Created: {created} | Messages: {msg_count:3} | Last: {last_activity}")
    
    def search_messages(self, query):
        """Search messages by text"""
        results = self.db.messages.find({"message": {"$regex": query, "$options": "i"}})
        print(f"\n🔍 Search results for '{query}':")
        print("-" * 80)
        count = 0
        for msg in results:
            timestamp = msg.get('timestamp', 'Unknown')
            sender = msg.get('sender', 'Unknown')
            message = msg.get('message', '')
            session = msg.get('session_id', 'Unknown')[:10]
            print(f"{timestamp} | {sender:4} | {session} | {message}")
            count += 1
        print(f"Found {count} messages")
    
    def add_product(self, name, price, category, description=""):
        """Add a new product"""
        product = {
            "product_name": name,
            "price": float(price),
            "category": category,
            "description": description,
            "in_stock": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = self.db.products.insert_one(product)
        print(f"✅ Added product: {name} (ID: {result.inserted_id})")
    
    def update_product_price(self, name, new_price):
        """Update product price"""
        result = self.db.products.update_one(
            {"product_name": {"$regex": name, "$options": "i"}},
            {"$set": {"price": float(new_price), "updated_at": datetime.now()}}
        )
        if result.modified_count > 0:
            print(f"✅ Updated price for {name} to ${new_price}")
        else:
            print(f"❌ Product {name} not found")
    
    def delete_old_messages(self, days=30):
        """Delete messages older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        result = self.db.messages.delete_many({"timestamp": {"$lt": cutoff_date}})
        print(f"🗑️ Deleted {result.deleted_count} messages older than {days} days")
    
    def get_stats(self):
        """Show database statistics"""
        print("\n📊 Database Statistics:")
        print("-" * 50)
        
        # Messages stats
        msg_count = self.db.messages.count_documents({})
        user_msgs = self.db.messages.count_documents({"sender": "user"})
        bot_msgs = self.db.messages.count_documents({"sender": "bot"})
        print(f"Messages: {msg_count} total ({user_msgs} user, {bot_msgs} bot)")
        
        # Products stats
        product_count = self.db.products.count_documents({})
        in_stock = self.db.products.count_documents({"in_stock": True})
        print(f"Products: {product_count} total ({in_stock} in stock)")
        
        # Sessions stats
        session_count = self.db.sessions.count_documents({})
        print(f"Sessions: {session_count} total")
        
        # Recent activity
        recent_messages = self.db.messages.count_documents({
            "timestamp": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        print(f"Today's messages: {recent_messages}")
    
    def interactive_mode(self):
        """Interactive terminal mode"""
        print("\n🖥️ MongoDB Interactive Terminal")
        print("=" * 50)
        print("Commands:")
        print("  collections - Show all collections")
        print("  messages [limit] - Show recent messages")
        print("  products - Show all products")
        print("  sessions - Show all sessions")
        print("  search <query> - Search messages")
        print("  add_product <name> <price> <category> [description]")
        print("  update_price <name> <new_price>")
        print("  delete_old <days> - Delete old messages")
        print("  stats - Show database statistics")
        print("  quit - Exit")
        print("-" * 50)
        
        while True:
            try:
                command = input("\nmongo> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    break
                elif cmd == "collections":
                    self.show_collections()
                elif cmd == "messages":
                    limit = int(command[1]) if len(command) > 1 else 10
                    self.show_messages(limit)
                elif cmd == "products":
                    self.show_products()
                elif cmd == "sessions":
                    self.show_sessions()
                elif cmd == "search":
                    if len(command) > 1:
                        query = " ".join(command[1:])
                        self.search_messages(query)
                    else:
                        print("Usage: search <query>")
                elif cmd == "add_product":
                    if len(command) >= 4:
                        name = command[1]
                        price = command[2]
                        category = command[3]
                        description = " ".join(command[4:]) if len(command) > 4 else ""
                        self.add_product(name, price, category, description)
                    else:
                        print("Usage: add_product <name> <price> <category> [description]")
                elif cmd == "update_price":
                    if len(command) >= 3:
                        name = command[1]
                        price = command[2]
                        self.update_product_price(name, price)
                    else:
                        print("Usage: update_price <name> <new_price>")
                elif cmd == "delete_old":
                    days = int(command[1]) if len(command) > 1 else 30
                    self.delete_old_messages(days)
                elif cmd == "stats":
                    self.get_stats()
                else:
                    print(f"Unknown command: {cmd}")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        self.client.close()
        print("👋 Disconnected from MongoDB")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        terminal = MongoDBTerminal()
        if not terminal.client:
            return
        
        command = sys.argv[1].lower()
        
        if command == "collections":
            terminal.show_collections()
        elif command == "messages":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            terminal.show_messages(limit)
        elif command == "products":
            terminal.show_products()
        elif command == "sessions":
            terminal.show_sessions()
        elif command == "stats":
            terminal.get_stats()
        else:
            print(f"Unknown command: {command}")
        
        terminal.client.close()
    else:
        # Interactive mode
        terminal = MongoDBTerminal()
        if terminal.client:
            terminal.interactive_mode()

if __name__ == "__main__":
    main()
