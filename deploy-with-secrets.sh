#!/bin/bash

# Winnicki Digital - Cloud Run Deployment with Secret Manager
# Project: self-hosted-468515
# This script uses Google Cloud Secret Manager for secure credential storage

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   WINNICKI DIGITAL - SECURE DEPLOYMENT                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Configuration
PROJECT_ID="self-hosted-468515"
SERVICE_NAME="winnicki-intake"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Please create .env file with your credentials"
    exit 1
fi

# Load environment variables
source .env

# Set project
gcloud config set project ${PROJECT_ID}

# Enable Secret Manager API
echo "🔧 Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

# Create secrets (if they don't exist)
echo "🔐 Creating secrets..."

create_secret() {
    SECRET_NAME=$1
    SECRET_VALUE=$2

    if gcloud secrets describe ${SECRET_NAME} &>/dev/null; then
        echo "  ↻ Updating ${SECRET_NAME}..."
        echo -n "${SECRET_VALUE}" | gcloud secrets versions add ${SECRET_NAME} --data-file=-
    else
        echo "  + Creating ${SECRET_NAME}..."
        echo -n "${SECRET_VALUE}" | gcloud secrets create ${SECRET_NAME} --data-file=-
    fi
}

create_secret "winnicki-google-api-key" "${GOOGLE_API_KEY}"
create_secret "winnicki-sendgrid-api-key" "${SENDGRID_API_KEY}"
create_secret "winnicki-slack-webhook" "${SLACK_WEBHOOK_URL}"
create_secret "winnicki-from-email" "${FROM_EMAIL}"
create_secret "winnicki-to-email" "${TO_EMAIL}"

# Build container
echo "🏗️  Building container..."
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy with secrets
echo "🚀 Deploying with secrets..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-secrets "GOOGLE_API_KEY=winnicki-google-api-key:latest" \
  --set-secrets "SENDGRID_API_KEY=winnicki-sendgrid-api-key:latest" \
  --set-secrets "SLACK_WEBHOOK_URL=winnicki-slack-webhook:latest" \
  --set-secrets "FROM_EMAIL=winnicki-from-email:latest" \
  --set-secrets "TO_EMAIL=winnicki-to-email:latest" \
  --set-env-vars "PORT=8080"

# Get service URL
echo ""
echo "✅ Secure deployment complete!"
echo ""
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "Next steps:"
echo "  1. Test: curl ${SERVICE_URL}/health"
echo "  2. View logs: gcloud run logs read --service=${SERVICE_NAME}"
echo "  3. API docs: ${SERVICE_URL}/docs"
echo ""
