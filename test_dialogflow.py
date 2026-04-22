#!/usr/bin/env python3
"""
Test script to verify Dialogflow integration
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv('backend/.env')

async def test_dialogflow():
    """Test Dialogflow client integration"""
    try:
        from backend.dialogflow_client import DialogflowClient
        
        print("🤖 Testing Dialogflow Integration")
        print("=" * 50)
        
        # Initialize client
        client = DialogflowClient()
        await client.initialize()
        print("✅ Dialogflow client initialized successfully")
        
        # Test cases
        test_cases = [
            "Hello",
            "What is the price of iPhone?",
            "I need help with my account",
            "Tell me about your products",
            "Thank you",
            "Goodbye"
        ]
        
        session_id = "test_session_123"
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: '{test_input}'")
            print("-" * 30)
            
            result = await client.detect_intent(session_id, test_input)
            
            if result:
                print(f"Intent: {result['intent_name']}")
                print(f"Confidence: {result['confidence']:.2f}")
                print(f"Response: {result['fulfillment_text']}")
                if result['parameters']:
                    print(f"Parameters: {result['parameters']}")
            else:
                print("❌ Failed to detect intent")
        
        await client.close()
        print("\n✅ Dialogflow test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Dialogflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dialogflow())
