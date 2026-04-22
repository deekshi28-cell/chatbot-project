from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class DialogflowIntent(BaseModel):
    name: str
    displayName: str

class DialogflowQueryResult(BaseModel):
    queryText: str
    languageCode: str
    speechRecognitionConfidence: Optional[float] = None
    action: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    allRequiredParamsPresent: Optional[bool] = None
    fulfillmentText: Optional[str] = None
    fulfillmentMessages: Optional[List[Dict[str, Any]]] = None
    outputContexts: Optional[List[Dict[str, Any]]] = None
    intent: Optional[DialogflowIntent] = None
    intentDetectionConfidence: Optional[float] = None
    diagnosticInfo: Optional[Dict[str, Any]] = None

class DialogflowWebhookRequest(BaseModel):
    responseId: str
    queryResult: DialogflowQueryResult
    session: str

class DialogflowWebhookResponse(BaseModel):
    fulfillmentText: str
    fulfillmentMessages: Optional[List[Dict[str, Any]]] = None
    outputContexts: Optional[List[Dict[str, Any]]] = None
