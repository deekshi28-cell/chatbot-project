from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import os
from .database import Database
from .models import ChatMessage, ChatResponse
from .dialogflow_models import DialogflowWebhookRequest, DialogflowWebhookResponse
from .dialogflow_webhook import DialogflowWebhookHandler
from .dialogflow_client import DialogflowClient
from .pubsub_service import PubSubService

app = FastAPI(title="Chatbot API", version="1.0.0")

# CORS middleware to allow Flask frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database, webhook handler, Pub/Sub service, and Dialogflow client
db = Database()
pubsub_service = PubSubService()
dialogflow_client = DialogflowClient()
webhook_handler = DialogflowWebhookHandler(db, pubsub_service)

@app.on_event("startup")
async def startup_event():
    try:
        await db.connect()
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
    
    try:
        await pubsub_service.initialize()
        print("✅ Pub/Sub initialized successfully")
    except Exception as e:
        print(f"⚠️ Pub/Sub initialization failed: {e}")
    
    try:
        await dialogflow_client.initialize()
        print("✅ Dialogflow client initialized successfully")
    except Exception as e:
        print(f"⚠️ Dialogflow initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await db.close()
    await pubsub_service.close()

@app.get("/")
async def root():
    return {"message": "Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        # Try to publish user message to Pub/Sub (optional)
        try:
            await pubsub_service.publish_user_message(
                session_id=message.session_id,
                message=message.message,
                user_id=message.user_id
            )
        except Exception as e:
            print(f"Pub/Sub publish failed: {e}")
        
        # Try to store user message in database (optional)
        try:
            user_message_doc = {
                "session_id": message.session_id,
                "message": message.message,
                "sender": "user",
                "timestamp": datetime.now()
            }
            await db.store_message(user_message_doc)
        except Exception as e:
            print(f"Database store failed: {e}")
        
        # Try Dialogflow first, fallback to simple response
        bot_response = None
        try:
            dialogflow_result = await dialogflow_client.detect_intent(message.session_id, message.message)
            if dialogflow_result and dialogflow_result.get('fulfillment_text'):
                bot_response = dialogflow_result['fulfillment_text']
        except Exception as e:
            print(f"Dialogflow failed: {e}")
        
        # Fallback to simple response if Dialogflow fails
        if not bot_response:
            bot_response = await generate_response(message.message)
        
        # Try to publish bot response to Pub/Sub (optional)
        try:
            await pubsub_service.publish_bot_response(
                session_id=message.session_id,
                response=bot_response
            )
        except Exception as e:
            print(f"Pub/Sub publish failed: {e}")
        
        # Try to store bot response in database (optional)
        try:
            bot_message_doc = {
                "session_id": message.session_id,
                "message": bot_response,
                "sender": "bot",
                "timestamp": datetime.now()
            }
            await db.store_message(bot_message_doc)
        except Exception as e:
            print(f"Database store failed: {e}")
        
        return ChatResponse(
            response=bot_response,
            session_id=message.session_id,
            timestamp=datetime.now()
        )
    except Exception as e:
        # Return a basic response even if everything fails
        return ChatResponse(
            response="I'm having some technical difficulties, but I'm here to help! Please try again.",
            session_id=message.session_id,
            timestamp=datetime.now()
        )

@app.post("/webhook/dialogflow", response_model=DialogflowWebhookResponse)
async def dialogflow_webhook(request: DialogflowWebhookRequest):
    """
    Dialogflow webhook endpoint for processing intents
    """
    try:
        response = await webhook_handler.process_webhook(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        messages = await db.get_chat_history(session_id)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pubsub/test")
async def test_pubsub():
    """Test endpoint to verify Pub/Sub integration"""
    try:
        test_message_id = await pubsub_service.publish_chat_event({
            "test": True,
            "message": "Test Pub/Sub integration",
            "session_id": "test_session"
        })
        
        return {
            "status": "success",
            "message": "Test message published to Pub/Sub",
            "message_id": test_message_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pub/Sub test failed: {str(e)}")


async def generate_response(user_message: str) -> str:
    """
    Simple response generator - will be replaced with Dialogflow integration
    """
    user_message_lower = user_message.lower()
    
    if "hello" in user_message_lower or "hi" in user_message_lower:
        return "Hello! How can I help you today?"
    elif "how are you" in user_message_lower:
        return "I'm doing well, thank you for asking! How can I assist you?"
    elif "bye" in user_message_lower or "goodbye" in user_message_lower:
        return "Goodbye! Have a great day!"
    elif "help" in user_message_lower:
        return "I'm here to help! You can ask me questions and I'll do my best to assist you."
    else:
        return f"I understand you said: '{user_message}'. I'm still learning, but I'm here to help!"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
