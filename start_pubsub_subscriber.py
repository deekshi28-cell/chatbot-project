#!/usr/bin/env python3
"""
Startup script for Pub/Sub subscriber
"""
import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv('backend/.env')

if __name__ == "__main__":
    print("Starting Pub/Sub Subscriber...")
    print("This will listen for chat events from the chatbot")
    print("Press Ctrl+C to stop")
    
    try:
        # Import and run the subscriber
        import asyncio
        from backend.pubsub_service import PubSubService, message_callback
        
        async def run_subscriber():
            pubsub_service = PubSubService()
            await pubsub_service.initialize()
            print("Pub/Sub subscriber initialized successfully")
            pubsub_service.start_subscriber(message_callback)
        
        asyncio.run(run_subscriber())
    except KeyboardInterrupt:
        print("\nPub/Sub Subscriber stopped")
    except Exception as e:
        print(f"Error starting subscriber: {e}")
