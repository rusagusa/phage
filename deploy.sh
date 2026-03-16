#!/bin/bash
# Phage OS: Automated Cloud Run Deployment Script

# 🧬 Initialization
echo "🧬 Phage Protocol: Initiating Cloud Deployment..."

# 1. Project Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="phage-gatway"
REGION="europe-west1"

# 2. Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --timeout 300s \
    --set-env-vars="PROJECT_ID=$PROJECT_ID"

echo "✅ Deployment Complete. Service URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
