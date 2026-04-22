#!/bin/bash

# GCP Setup Script for Chatbot Deployment
# This script sets up all necessary GCP services and configurations

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION="us-central1"
SERVICE_ACCOUNT_NAME="chatbot-service-account"
MONGODB_ATLAS_URL=${2:-"mongodb+srv://username:password@cluster.mongodb.net"}

echo "🚀 Setting up GCP environment for Chatbot deployment"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    pubsub.googleapis.com \
    dialogflow.googleapis.com \
    secretmanager.googleapis.com

# Create service account
echo "👤 Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="Chatbot Service Account" \
    --description="Service account for chatbot application"

# Grant necessary permissions
echo "🔐 Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/pubsub.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/dialogflow.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create Pub/Sub topic and subscription
echo "📢 Creating Pub/Sub resources..."
gcloud pubsub topics create chat-events || echo "Topic already exists"
gcloud pubsub subscriptions create chat-processor \
    --topic=chat-events || echo "Subscription already exists"

# Create secrets
echo "🔒 Creating secrets..."
echo -n "$MONGODB_ATLAS_URL" | gcloud secrets create chatbot-mongodb-url --data-file=-

# Grant secret access to service account
gcloud secrets add-iam-policy-binding chatbot-mongodb-url \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create Secret Manager secret for MongoDB URL
gcloud secrets create chatbot-secrets --data-file=- <<EOF
{
  "mongodb-url": "$MONGODB_ATLAS_URL"
}
EOF

echo "✅ GCP setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update your MongoDB Atlas to allow GCP IP ranges"
echo "2. Update cloudbuild.yaml with your project ID"
echo "3. Run: gcloud builds submit --config cloudbuild.yaml"
echo ""
echo "Service URLs will be:"
echo "- Backend: https://chatbot-backend-[HASH]-uc.a.run.app"
echo "- Frontend: https://chatbot-frontend-[HASH]-uc.a.run.app"
