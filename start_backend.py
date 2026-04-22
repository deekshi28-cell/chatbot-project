#!/usr/bin/env python3
"""
Startup script for FastAPI backend
"""
import uvicorn
import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv('backend/.env')

if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    
    print(f"Starting FastAPI backend on {host}:{port}")
    print("Make sure MongoDB is running on localhost:27017")
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
