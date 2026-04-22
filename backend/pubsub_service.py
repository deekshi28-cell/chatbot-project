import asyncio
import json
import os
from typing import Dict, Any, Optional
from google.cloud import pubsub_v1
from google.auth import default
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PubSubService:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.topic_name = os.getenv("PUBSUB_TOPIC_CHAT_EVENTS", "chat-events")
        self.subscription_name = os.getenv("PUBSUB_SUBSCRIPTION_CHAT_PROCESSOR", "chat-processor")
        
        # Initialize clients
        self.publisher = None
        self.subscriber = None
        self.topic_path = None
        self.subscription_path = None
        
    async def initialize(self):
        """Initialize Pub/Sub clients and create topic/subscription if needed"""
        try:
            # Set credentials path
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
            # Initialize publisher and subscriber
            self.publisher = pubsub_v1.PublisherClient()
            self.subscriber = pubsub_v1.SubscriberClient()
            
            # Create topic and subscription paths
            self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
            self.subscription_path = self.subscriber.subscription_path(
                self.project_id, self.subscription_name
            )
            
            # Create topic if it doesn't exist
            await self._create_topic_if_not_exists()
            
            # Create subscription if it doesn't exist
            await self._create_subscription_if_not_exists()
            
            logger.info(f"Pub/Sub initialized for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pub/Sub: {e}")
            raise e
    
    async def _create_topic_if_not_exists(self):
        """Create topic if it doesn't exist"""
        try:
            self.publisher.get_topic(request={"topic": self.topic_path})
            logger.info(f"Topic {self.topic_name} already exists")
        except Exception:
            try:
                self.publisher.create_topic(request={"name": self.topic_path})
                logger.info(f"Created topic: {self.topic_name}")
            except Exception as e:
                logger.error(f"Failed to create topic: {e}")
    
    async def _create_subscription_if_not_exists(self):
        """Create subscription if it doesn't exist"""
        try:
            self.subscriber.get_subscription(request={"subscription": self.subscription_path})
            logger.info(f"Subscription {self.subscription_name} already exists")
        except Exception:
            try:
                self.subscriber.create_subscription(
                    request={
                        "name": self.subscription_path,
                        "topic": self.topic_path,
                    }
                )
                logger.info(f"Created subscription: {self.subscription_name}")
            except Exception as e:
                logger.error(f"Failed to create subscription: {e}")
    
    async def publish_chat_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """Publish a chat event to Pub/Sub"""
        try:
            # Add metadata
            event_data.update({
                "timestamp": datetime.now().isoformat(),
                "event_type": "chat_message"
            })
            
            # Convert to JSON and encode
            message_data = json.dumps(event_data).encode("utf-8")
            
            # Publish message
            future = self.publisher.publish(self.topic_path, message_data)
            message_id = future.result()
            
            logger.info(f"Published message {message_id} to {self.topic_name}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return None
    
    async def publish_user_message(self, session_id: str, message: str, user_id: Optional[str] = None):
        """Publish user message event"""
        event_data = {
            "session_id": session_id,
            "message": message,
            "sender": "user",
            "user_id": user_id
        }
        return await self.publish_chat_event(event_data)
    
    async def publish_bot_response(self, session_id: str, response: str, intent: Optional[str] = None, confidence: Optional[float] = None):
        """Publish bot response event"""
        event_data = {
            "session_id": session_id,
            "message": response,
            "sender": "bot",
            "intent": intent,
            "confidence": confidence
        }
        return await self.publish_chat_event(event_data)
    
    async def publish_dialogflow_event(self, session_id: str, query_text: str, intent_name: str, confidence: float, fulfillment_text: str):
        """Publish Dialogflow webhook event"""
        event_data = {
            "session_id": session_id,
            "query_text": query_text,
            "intent_name": intent_name,
            "confidence": confidence,
            "fulfillment_text": fulfillment_text,
            "event_type": "dialogflow_webhook"
        }
        return await self.publish_chat_event(event_data)
    
    def start_subscriber(self, callback_function):
        """Start subscriber to listen for messages"""
        try:
            # Pull messages
            flow_control = pubsub_v1.types.FlowControl(max_messages=100)
            
            streaming_pull_future = self.subscriber.subscribe(
                self.subscription_path, 
                callback=callback_function,
                flow_control=flow_control
            )
            
            logger.info(f"Listening for messages on {self.subscription_path}")
            
            # Keep the main thread running
            try:
                streaming_pull_future.result()
            except KeyboardInterrupt:
                streaming_pull_future.cancel()
                
        except Exception as e:
            logger.error(f"Failed to start subscriber: {e}")
    
    async def close(self):
        """Close Pub/Sub clients"""
        try:
            if self.publisher:
                self.publisher.close()
            if self.subscriber:
                self.subscriber.close()
            logger.info("Pub/Sub clients closed")
        except Exception as e:
            logger.error(f"Error closing Pub/Sub clients: {e}")

# Message callback function for subscriber
def message_callback(message):
    """Callback function to process received messages"""
    try:
        # Decode and parse message
        message_data = json.loads(message.data.decode("utf-8"))
        
        logger.info(f"Received message: {message_data}")
        
        # Process the message based on event type
        event_type = message_data.get("event_type", "unknown")
        
        if event_type == "chat_message":
            # Process chat message
            session_id = message_data.get("session_id")
            sender = message_data.get("sender")
            msg_content = message_data.get("message")
            
            logger.info(f"Processing chat message from {sender} in session {session_id}: {msg_content}")
            
        elif event_type == "dialogflow_webhook":
            # Process Dialogflow event
            intent_name = message_data.get("intent_name")
            confidence = message_data.get("confidence")
            
            logger.info(f"Processing Dialogflow event - Intent: {intent_name}, Confidence: {confidence}")
        
        # Acknowledge the message
        message.ack()
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        message.nack()
