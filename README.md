# Chatbot Application

A modern chatbot application with FastAPI backend, Flask frontend, MongoDB database, and Dialogflow integration.

## Prerequisites

1. **Python 3.8+**
2. **MongoDB** - Download and install from: https://www.mongodb.com/try/download/community

## Installation

1. **Navigate to project directory**
   ```bash
   cd d:\projects\chatbot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup MongoDB database**
   ```bash
   python setup_mongodb.py
   ```

## Configuration

1. **ngrok Setup for Client PC**
   - Download ngrok from: https://ngrok.com/download
   - Extract `ngrok.exe` to the project directory
   - Get authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
   - Configure authtoken:
   ```bash
   .\ngrok.exe config add-authtoken YOUR_AUTHTOKEN_HERE
   ```

2. **Environment variables are already configured in `backend/.env`**

## Running the Application

### Step 1: Start MongoDB
```bash
mongod
```

### Step 2: Start FastAPI Backend (Terminal 1)
```bash
python start_backend.py
```
- Backend runs on: http://localhost:8000
- API docs: http://localhost:8000/docs

### Step 3: Start HTTPS Tunnel (Terminal 2)
```bash
.\ngrok.exe http 8000
```
- Copy the HTTPS URL from ngrok output (e.g., `https://abc123.ngrok-free.app`)
- Update `chatbot-event/agent.json` webhook URL:
  ```json
  "url": "https://your-ngrok-url.ngrok-free.app/webhook/dialogflow"
  ```

### Step 4: Start Flask Frontend (Terminal 3)
```bash
python start_frontend.py
```
- Frontend runs on: http://localhost:5000

### Step 5: Test Dialogflow Integration (Optional)
```bash
python test_dialogflow.py
```

## Usage

1. Open browser: http://localhost:5000
2. Start chatting with the AI chatbot
3. Messages are saved to MongoDB
4. Dialogflow handles intent recognition

## Key Features

- ✅ Modern responsive chat interface
- ✅ Dialogflow intent recognition
- ✅ MongoDB message persistence
- ✅ Google Cloud Pub/Sub integration
- ✅ Session-based conversations
- ✅ HTTPS webhook support
- ✅ Real-time messaging

## API Endpoints

- `GET /` - Root endpoint
- `POST /chat` - Send message to chatbot
- `POST /webhook/dialogflow` - Dialogflow webhook
- `GET /chat/history/{session_id}` - Get chat history
- `GET /health` - Health check

## Troubleshooting

1. **MongoDB not connecting**: Ensure MongoDB service is running
2. **Backend not starting**: Check if port 8000 is available
3. **Dialogflow webhook failing**: Verify ngrok tunnel is active and HTTPS URL is updated
4. **Frontend not loading**: Ensure backend is running on port 8000

## Project Structure

```
chatbot/
├── backend/                 # FastAPI application
├── frontend/               # Flask web interface
├── chatbot-event/          # Dialogflow agent configuration
├── start_backend.py        # Backend startup script
├── start_frontend.py       # Frontend startup script
├── test_dialogflow.py      # Test Dialogflow integration
└── setup_mongodb.py        # Database setup script
```
