from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import uuid
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from frontend"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Send message to FastAPI backend
        response = requests.post(
            f"{FASTAPI_URL}/chat",
            json={
                "message": user_message,
                "session_id": session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            bot_response = response.json()
            return jsonify({
                'response': bot_response['response'],
                'session_id': bot_response['session_id'],
                'timestamp': bot_response['timestamp']
            })
        else:
            return jsonify({'error': 'Backend service unavailable'}), 503
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Cannot connect to chatbot service'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history/<session_id>')
def get_history(session_id):
    """Get chat history for a session"""
    try:
        response = requests.get(f"{FASTAPI_URL}/chat/history/{session_id}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Cannot retrieve history'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check if FastAPI backend is accessible
        response = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        backend_status = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        backend_status = "unreachable"
    
    return jsonify({
        'frontend': 'healthy',
        'backend': backend_status,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
