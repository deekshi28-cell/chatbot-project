#!/usr/bin/env python3
"""
Standalone Pub/Sub subscriber service
Run this separately to listen for chat events
"""
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from .pubsub_service import PubSubService, message_callback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main subscriber function"""
    # Load environment variables
    load_dotenv('.env')
    
    # Initialize Pub/Sub service
    pubsub_service = PubSubService()
    
    try:
        await pubsub_service.initialize()
        logger.info("Pub/Sub subscriber started successfully")
        
        # Start listening for messages
        pubsub_service.start_subscriber(message_callback)
        
    except KeyboardInterrupt:
        logger.info("Subscriber stopped by user")
    except Exception as e:
        logger.error(f"Error in subscriber: {e}")
    finally:
        await pubsub_service.close()

if __name__ == "__main__":
    # Add current directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run the subscriber
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSubscriber stopped")
    except Exception as e:
        print(f"Error: {e}")
