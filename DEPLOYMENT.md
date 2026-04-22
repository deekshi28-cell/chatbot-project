# Chatbot Deployment Guide for Google Cloud Platform

This guide provides a complete deployment structure for deploying the chatbot application to Google Cloud Platform using Cloud Run, Cloud Build, and other GCP services.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   MongoDB       │
│  (Cloud Run)    │────│  (Cloud Run)    │────│   (Atlas)       │
│   Flask App     │    │  FastAPI App    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Dialogflow    │
                    │   + Pub/Sub     │
                    └─────────────────┘
```

## 📁 Deployment Structure

```
chatbot/
├── backend/
│   └── Dockerfile              # Backend container definition
├── frontend/
│   └── Dockerfile              # Frontend container definition
├── deploy/
│   ├── setup-gcp.sh           # GCP environment setup
│   ├── deploy.sh              # Deployment script
│   ├── cloud-run-backend.yaml # Backend Cloud Run config
│   └── cloud-run-frontend.yaml# Frontend Cloud Run config
├── docker-compose.yml         # Local development
├── docker-compose.override.yml# Development overrides
├── cloudbuild.yaml            # Cloud Build configuration
├── .dockerignore              # Docker ignore rules
└── .gcloudignore             # GCloud ignore rules
```

## 🚀 Deployment Flow

### Phase 1: Prerequisites Setup

1. **Google Cloud Project Setup**
   ```bash
   # Create new project (optional)
   gcloud projects create your-project-id
   
   # Set project
   gcloud config set project your-project-id
   ```

2. **MongoDB Atlas Setup**
   - Create MongoDB Atlas cluster
   - Whitelist GCP IP ranges
   - Get connection string

### Phase 2: GCP Environment Setup

```bash
# Make setup script executable
chmod +x deploy/setup-gcp.sh

# Run setup (replace with your project ID and MongoDB URL)
./deploy/setup-gcp.sh your-project-id "mongodb+srv://user:pass@cluster.mongodb.net"
```

This script will:
- Enable required GCP APIs
- Create service accounts with proper permissions
- Set up Pub/Sub topics and subscriptions
- Create Secret Manager secrets
- Configure IAM roles

### Phase 3: Local Testing (Optional)

```bash
# Test locally with Docker Compose
docker-compose up --build

# Access services
# Frontend: http://localhost:5000
# Backend: http://localhost:8000
# MongoDB: localhost:27017
```

### Phase 4: Cloud Deployment

```bash
# Make deploy script executable
chmod +x deploy/deploy.sh

# Deploy to GCP
./deploy/deploy.sh your-project-id production
```

## 🔧 Configuration Files

### Backend Dockerfile
- Multi-stage build for optimization
- Non-root user for security
- Health checks included
- Environment variable configuration

### Frontend Dockerfile
- Lightweight Flask container
- Health monitoring
- Dynamic backend URL configuration

### Cloud Build Configuration
- Automated build and deployment
- Container image management
- Environment-specific deployments
- Rollback capabilities

## 🌐 Service Configuration

### Backend (FastAPI)
- **Resource Limits**: 1GB RAM, 1 CPU
- **Scaling**: 0-10 instances
- **Port**: 8000
- **Health Check**: `/health` endpoint

### Frontend (Flask)
- **Resource Limits**: 512MB RAM, 0.5 CPU
- **Scaling**: 0-5 instances
- **Port**: 5000
- **Health Check**: `/health` endpoint

## 🔒 Security Features

- Service accounts with minimal permissions
- Secret Manager for sensitive data
- Non-root containers
- HTTPS-only communication
- IAM-based access control

## 📊 Monitoring & Logging

```bash
# View logs
gcloud run services logs read chatbot-backend --region=us-central1

# Monitor performance
gcloud run services describe chatbot-backend --region=us-central1

# Check health
curl https://your-backend-url/health
```

## 🔄 CI/CD Pipeline

The deployment uses Cloud Build for automated CI/CD:

1. **Trigger**: Git push to main branch
2. **Build**: Docker images for backend and frontend
3. **Test**: Health checks and validation
4. **Deploy**: Rolling deployment to Cloud Run
5. **Verify**: Post-deployment health checks

## 💰 Cost Optimization

- **Auto-scaling**: Scales to zero when not in use
- **Resource limits**: Prevents over-provisioning
- **Shared VPC**: Reduces networking costs
- **Container optimization**: Multi-stage builds

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   gcloud builds log [BUILD_ID]
   ```

2. **Service Not Starting**
   ```bash
   # Check service logs
   gcloud run services logs read chatbot-backend --region=us-central1
   ```

3. **Database Connection Issues**
   - Verify MongoDB Atlas whitelist
   - Check Secret Manager configuration
   - Validate connection string

### Health Checks

```bash
# Backend health
curl https://your-backend-url/health

# Frontend health
curl https://your-frontend-url/health
```

## 📈 Scaling Considerations

- **Database**: Use MongoDB Atlas for managed scaling
- **Compute**: Cloud Run auto-scales based on traffic
- **Storage**: Use Cloud Storage for file uploads
- **CDN**: Add Cloud CDN for static assets

## 🔐 Environment Variables

### Backend
- `MONGODB_URL`: Database connection string
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `PUBSUB_TOPIC_CHAT_EVENTS`: Pub/Sub topic name

### Frontend
- `FASTAPI_URL`: Backend service URL

## 📝 Post-Deployment Steps

1. Update Dialogflow webhook URL
2. Test all endpoints
3. Configure monitoring alerts
4. Set up backup procedures
5. Document service URLs

## 🎯 Production Checklist

- [ ] MongoDB Atlas configured and accessible
- [ ] GCP services enabled and configured
- [ ] Service accounts created with proper permissions
- [ ] Secrets stored in Secret Manager
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Documentation updated

## 📞 Support

For deployment issues:
1. Check service logs
2. Verify configuration
3. Test health endpoints
4. Review GCP quotas and limits
