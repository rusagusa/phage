#!/bin/bash
# Phage OS: Automated Cloud Run Deployment Script

# 🧬 Initialization
echo "🧬 Phage Protocol: Initiating Cloud Deployment..."

# 1. Project Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="phage-gatway"
REGION="europe-west1"

# 2. Deploy to Cloud Run (Injecting Secrets)
# WARNING: Enter your keys below before running, or pass them as env vars.
# Use --set-env-vars to securely pass secrets to the Brain.

gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --timeout 300s \
    --set-env-vars="TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN,GEMINI_API_KEY=YOUR_GEMINI_API_KEY,DEVICE_ID=kigali_node_01"

echo "✅ Deployment Complete. Service URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
