import os
import logging
from google.cloud import dialogflow
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DialogflowClient:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.session_client = None
        self.language_code = "en"
        
    async def initialize(self):
        """Initialize Dialogflow client"""
        try:
            # Set credentials path
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
            # Initialize session client
            self.session_client = dialogflow.SessionsClient()
            logger.info(f"Dialogflow client initialized for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Dialogflow client: {e}")
            raise e
    
    async def detect_intent(self, session_id: str, text_input: str) -> Optional[Dict[str, Any]]:
        """
        Detect intent from user input using Dialogflow
        """
        try:
            if not self.session_client:
                await self.initialize()
            
            # Create session path
            session_path = self.session_client.session_path(self.project_id, session_id)
            
            # Create text input
            text_input_obj = dialogflow.TextInput(text=text_input, language_code=self.language_code)
            query_input = dialogflow.QueryInput(text=text_input_obj)
            
            # Detect intent
            response = self.session_client.detect_intent(
                request={"session": session_path, "query_input": query_input}
            )
            
            # Extract relevant information
            result = {
                "query_text": response.query_result.query_text,
                "intent_name": response.query_result.intent.display_name if response.query_result.intent else "Default Fallback Intent",
                "confidence": response.query_result.intent_detection_confidence,
                "fulfillment_text": response.query_result.fulfillment_text,
                "parameters": dict(response.query_result.parameters) if response.query_result.parameters else {},
                "action": response.query_result.action,
                "all_required_params_present": response.query_result.all_required_params_present
            }
            
            logger.info(f"Intent detected: {result['intent_name']} (confidence: {result['confidence']})")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            return None
    
    async def close(self):
        """Close Dialogflow client"""
        try:
            if self.session_client:
                # Dialogflow client doesn't need explicit closing
                pass
            logger.info("Dialogflow client closed")
        except Exception as e:
            logger.error(f"Error closing Dialogflow client: {e}")
