#!/bin/bash

# Deployment script for Chatbot to Google Cloud Platform
# Usage: ./deploy.sh [PROJECT_ID] [ENVIRONMENT]

set -e

PROJECT_ID=${1:-"corded-evening-471908-m2"}
ENVIRONMENT=${2:-"production"}
REGION="us-central1"

echo "🚀 Deploying Chatbot to Google Cloud Platform"
echo "Project: $PROJECT_ID"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Build and deploy using Cloud Build
echo "🔨 Building and deploying with Cloud Build..."
gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_ENVIRONMENT=$ENVIRONMENT

# Get service URLs
echo "📡 Getting service URLs..."
BACKEND_URL=$(gcloud run services describe chatbot-backend --region=$REGION --format="value(status.url)")
FRONTEND_URL=$(gcloud run services describe chatbot-frontend --region=$REGION --format="value(status.url)")

# Update frontend environment variable with backend URL
echo "🔗 Updating frontend with backend URL..."
gcloud run services update chatbot-frontend \
    --region=$REGION \
    --set-env-vars="FASTAPI_URL=$BACKEND_URL"

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Service URLs:"
echo "Backend API: $BACKEND_URL"
echo "Frontend App: $FRONTEND_URL"
echo ""
echo "🔍 Useful commands:"
echo "View logs: gcloud run services logs read chatbot-backend --region=$REGION"
echo "Monitor: gcloud run services describe chatbot-backend --region=$REGION"
