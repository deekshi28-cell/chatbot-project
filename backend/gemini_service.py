import os
import logging
from typing import Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
    async def initialize(self):
        """Initialize Gemini API client"""
        try:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            
            # Initialize the model - try gemini-1.5-flash first, fallback to gemini-pro
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini API initialized successfully with gemini-1.5-flash")
            except:
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini API initialized successfully with gemini-pro")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            raise e
    
    async def generate_response(self, user_message: str, context: Optional[str] = None) -> str:
        """
        Generate response using Gemini API
        """
        try:
            if not self.model:
                logger.info("Model not initialized, initializing now...")
                await self.initialize()
            
            # Prepare the prompt
            if context:
                prompt = f"Context: {context}\n\nUser: {user_message}\n\nPlease provide a helpful response:"
            else:
                prompt = f"User: {user_message}\n\nPlease provide a helpful response as a chatbot assistant:"
            
            logger.info(f"Sending prompt to Gemini: {prompt[:100]}...")
            
            # Generate response - this is a synchronous call, not async
            response = self.model.generate_content(prompt)
            
            logger.info(f"Gemini response received: {response}")
            
            if response and hasattr(response, 'text') and response.text:
                logger.info(f"Gemini response text: {response.text[:100]}...")
                return response.text.strip()
            else:
                logger.warning("No response text from Gemini")
                return "I'm sorry, I couldn't generate a response at the moment. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "I'm experiencing some technical difficulties. Please try again later."
    
    async def generate_product_response(self, user_message: str, product_data: dict) -> str:
        """
        Generate response about a specific product using Gemini
        """
        try:
            context = f"""
            Product Information:
            - Name: {product_data.get('product_name', 'Unknown')}
            - Price: ${product_data.get('price', 'N/A')}
            - Description: {product_data.get('description', 'No description available')}
            - Category: {product_data.get('category', 'General')}
            """
            
            prompt = f"""
            {context}
            
            User Question: {user_message}
            
            Please provide a helpful response about this product based on the user's question.
            Be conversational and helpful.
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return f"Here's what I know about {product_data.get('product_name', 'this product')}: it's priced at ${product_data.get('price', 'N/A')}."
                
        except Exception as e:
            logger.error(f"Error generating product response: {e}")
            return f"I found information about {product_data.get('product_name', 'this product')} - it's priced at ${product_data.get('price', 'N/A')}."
    
    async def generate_fallback_response(self, user_message: str, intent_name: str) -> str:
        """
        Generate fallback response when no specific intent handler exists
        """
        try:
            prompt = f"""
            You are a helpful chatbot assistant. A user has sent a message that was classified as "{intent_name}" intent.
            
            User Message: {user_message}
            
            Please provide a helpful, conversational response. If you're not sure about something specific, 
            acknowledge that and offer to help in other ways.
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I understand you're asking about something, but I'm not sure how to help with that specific request. Could you please rephrase your question?"
                
        except Exception as e:
            logger.error(f"Error generating fallback response: {e}")
            return "I'm here to help! Could you please tell me more about what you're looking for?"
