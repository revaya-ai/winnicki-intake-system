#!/bin/bash

# Winnicki Digital - Cloud Run Deployment Script
# Project: self-hosted-468515

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   WINNICKI DIGITAL - CLOUD RUN DEPLOYMENT                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Configuration
PROJECT_ID="self-hosted-468515"
SERVICE_NAME="winnicki-intake"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in
echo "🔐 Checking authentication..."
gcloud auth list

# Set project
echo "📋 Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and submit container
echo "🏗️  Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "PORT=8080" \
  --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
  --set-env-vars "SENDGRID_API_KEY=${SENDGRID_API_KEY}" \
  --set-env-vars "FROM_EMAIL=${FROM_EMAIL}" \
  --set-env-vars "TO_EMAIL=${TO_EMAIL}" \
  --set-env-vars "SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}"

# Get service URL
echo ""
echo "✅ Deployment complete!"
echo ""
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "Test endpoints:"
echo "  - Health: ${SERVICE_URL}/health"
echo "  - Docs: ${SERVICE_URL}/docs"
echo ""
