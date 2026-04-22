#!/usr/bin/env python3
"""
Startup script for Flask frontend
"""
import os
from frontend.app import app

if __name__ == "__main__":
    print("Starting Flask frontend on http://localhost:5000")
    print("Make sure FastAPI backend is running on http://localhost:8000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
