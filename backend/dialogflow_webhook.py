from fastapi import HTTPException
from typing import Dict, Any
import logging
from .dialogflow_models import DialogflowWebhookRequest, DialogflowWebhookResponse
from .database import Database

logger = logging.getLogger(__name__)

class DialogflowWebhookHandler:
    def __init__(self, db: Database, pubsub_service=None):
        self.db = db
        self.pubsub_service = pubsub_service
    
    async def process_webhook(self, request: DialogflowWebhookRequest) -> DialogflowWebhookResponse:
        """
        Process Dialogflow webhook request and return appropriate response
        """
        try:
            # Extract session ID from Dialogflow session path
            session_id = self.extract_session_id(request.session)
            
            # Get query text and intent
            query_text = request.queryResult.queryText
            intent_name = request.queryResult.intent.displayName if request.queryResult.intent else "Default Fallback Intent"
            
            # Store user message in database
            user_message_doc = {
                "session_id": session_id,
                "message": query_text,
                "sender": "user",
                "intent": intent_name,
                "confidence": request.queryResult.intentDetectionConfidence,
                "timestamp": None  # Will be set in database.py
            }
            await self.db.store_message(user_message_doc)
            
            # Process the intent and generate response
            response_text = await self.handle_intent(request)
            
            # Publish Dialogflow event to Pub/Sub
            if self.pubsub_service:
                await self.pubsub_service.publish_dialogflow_event(
                    session_id=session_id,
                    query_text=query_text,
                    intent_name=intent_name,
                    confidence=request.queryResult.intentDetectionConfidence or 0.0,
                    fulfillment_text=response_text
                )
            
            # Store bot response in database
            bot_message_doc = {
                "session_id": session_id,
                "message": response_text,
                "sender": "bot",
                "intent": intent_name,
                "timestamp": None  # Will be set in database.py
            }
            await self.db.store_message(bot_message_doc)
            
            return DialogflowWebhookResponse(
                fulfillmentText=response_text
            )
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return DialogflowWebhookResponse(
                fulfillmentText="I'm sorry, I encountered an error processing your request."
            )
    
    def extract_session_id(self, session_path: str) -> str:
        """
        Extract session ID from Dialogflow session path
        Format: projects/{project-id}/agent/sessions/{session-id}
        """
        try:
            return session_path.split('/')[-1]
        except:
            return "unknown_session"
    
    async def handle_intent(self, request: DialogflowWebhookRequest) -> str:
        """
        Handle different intents and return appropriate responses
        """
        intent_name = request.queryResult.intent.displayName if request.queryResult.intent else "Default Fallback Intent"
        query_text = request.queryResult.queryText
        parameters = request.queryResult.parameters or {}
        
        # If Dialogflow already provided a fulfillment text, use it
        if request.queryResult.fulfillmentText:
            return request.queryResult.fulfillmentText
        
        # Handle product pricing intent using MongoDB + Gemini
        if intent_name == "ProductPricing" or "product" in intent_name.lower() or "price" in intent_name.lower():
            return await self.handle_product_query(query_text, parameters)
        
        # Custom intent handling
        elif intent_name == "Default Welcome Intent":
            return "Hello! Welcome to our chatbot. How can I help you today?"
        
        elif intent_name == "Default Fallback Intent":
            # Simple fallback response
            return self.generate_simple_fallback_response(query_text)
        
        elif "goodbye" in intent_name.lower() or "bye" in intent_name.lower():
            return "Goodbye! Have a great day!"
        
        elif "help" in intent_name.lower():
            return "I'm here to help! You can ask me questions about our products, services, or anything else you'd like to know."
        
        # Handle custom intents with parameters
        elif parameters:
            return await self.handle_parametric_intent(intent_name, parameters, query_text)
        
        # Simple response for unhandled intents
        else:
            return self.generate_simple_fallback_response(query_text)
    
    async def handle_parametric_intent(self, intent_name: str, parameters: Dict[str, Any], query_text: str) -> str:
        """
        Handle intents that have parameters
        """
        # Example: Handle date/time parameters
        if "date-time" in parameters:
            date_time = parameters["date-time"]
            return f"I see you mentioned a date/time: {date_time}. How can I help you with that?"
        
        # Example: Handle person names
        if "person" in parameters:
            person = parameters["person"]
            return f"You mentioned {person}. What would you like to know about them?"
        
        # Example: Handle locations
        if "location" in parameters:
            location = parameters["location"]
            return f"You're asking about {location}. What information do you need about this location?"
        
        # Simple parametric response
        return f"I understand you're asking about {intent_name.lower()}. How can I help you with that?"
    
    async def handle_product_query(self, query_text: str, parameters: Dict[str, Any]) -> str:
        """
        Handle product-related queries using MongoDB + Gemini
        """
        try:
            # Search for products in MongoDB
            products_collection = self.db.db["products"]
            
            # Extract product name from query or parameters
            product_name = None
            if "product" in parameters:
                product_name = parameters["product"]
            else:
                # Try to extract product name from query text
                words = query_text.lower().split()
                # This is a simple approach - you can enhance this with NLP
                for word in words:
                    if len(word) > 3:  # Ignore short words
                        product_name = word
                        break
            
            if product_name:
                # Search for product in MongoDB
                product_info = await products_collection.find_one({
                    "product_name": {"$regex": product_name, "$options": "i"}
                })
                
                if product_info:
                    # Generate simple product response
                    return self.generate_product_response(product_info)
                else:
                    # Product not found
                    return f"I couldn't find a product named '{product_name}' in our database. Please check the spelling or try a different product name."
            else:
                # No specific product mentioned
                return "I'd be happy to help you with product information! Could you please specify which product you're interested in?"
                
        except Exception as e:
            logger.error(f"Error handling product query: {e}")
            return "I'm sorry, there was an issue accessing our product database. Please try again later."
    
    def generate_simple_fallback_response(self, query_text: str) -> str:
        """
        Generate a simple fallback response for unhandled queries
        """
        query_lower = query_text.lower()
        
        if "hello" in query_lower or "hi" in query_lower:
            return "Hello! How can I help you today?"
        elif "how are you" in query_lower:
            return "I'm doing well, thank you for asking! How can I assist you?"
        elif "bye" in query_lower or "goodbye" in query_lower:
            return "Goodbye! Have a great day!"
        elif "help" in query_lower:
            return "I'm here to help! You can ask me questions and I'll do my best to assist you."
        elif "thank" in query_lower:
            return "You're welcome! Is there anything else I can help you with?"
        else:
            return f"I understand you said: '{query_text}'. I'm still learning, but I'm here to help! Could you please rephrase your question or ask me something else?"
    
    def generate_product_response(self, product_info: Dict[str, Any]) -> str:
        """
        Generate a simple product response based on product information
        """
        product_name = product_info.get('product_name', 'Unknown Product')
        price = product_info.get('price', 'N/A')
        description = product_info.get('description', 'No description available')
        category = product_info.get('category', 'General')
        
        response = f"Here's information about {product_name}:\n"
        response += f"• Price: ${price}\n"
        response += f"• Category: {category}\n"
        response += f"• Description: {description}\n"
        response += "Is there anything specific you'd like to know about this product?"
        
        return response
