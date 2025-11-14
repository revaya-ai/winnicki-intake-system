#!/bin/bash

# Winnicki Digital - Deployment Guide
# This script provides step-by-step deployment instructions

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   WINNICKI DIGITAL - DEPLOYMENT GUIDE                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check prerequisites
echo "STEP 1: Checking Prerequisites"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check gcloud
if command -v gcloud &> /dev/null; then
    echo "✅ gcloud CLI installed"
    gcloud --version | head -1
else
    echo "❌ gcloud CLI not found"
    echo ""
    echo "Install gcloud CLI:"
    echo "  macOS:   brew install google-cloud-sdk"
    echo "  Linux:   https://cloud.google.com/sdk/docs/install"
    echo "  Windows: https://cloud.google.com/sdk/docs/install"
    echo ""
    exit 1
fi

echo ""

# Check if logged in
echo "STEP 2: Checking Authentication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)
    echo "✅ Authenticated as: $ACCOUNT"
else
    echo "⚠️  Not authenticated"
    echo "Run: gcloud auth login"
    echo ""
    read -p "Run gcloud auth login now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud auth login
    else
        exit 1
    fi
fi

echo ""

# Check project
echo "STEP 3: Setting Project"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PROJECT_ID="self-hosted-468515"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "Setting project to: $PROJECT_ID"
    gcloud config set project $PROJECT_ID
else
    echo "✅ Project already set to: $PROJECT_ID"
fi

echo ""

# Check .env file
echo "STEP 4: Checking Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo ""
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - GOOGLE_API_KEY (REQUIRED)"
    echo "   - SENDGRID_API_KEY (optional)"
    echo "   - SLACK_WEBHOOK_URL (optional)"
    echo ""
    echo "Get Google AI API key: https://ai.google.dev/"
    echo ""
    read -p "Press Enter after you've added your GOOGLE_API_KEY to .env..."
fi

# Check if GOOGLE_API_KEY is set
if grep -q "^GOOGLE_API_KEY=your_" .env || ! grep -q "^GOOGLE_API_KEY=..*" .env; then
    echo "❌ GOOGLE_API_KEY not set in .env"
    echo ""
    echo "Please edit .env and add your Google AI API key"
    echo "Get it from: https://ai.google.dev/"
    exit 1
else
    echo "✅ GOOGLE_API_KEY is set"
fi

echo ""

# Enable APIs
echo "STEP 5: Enabling Required APIs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Enabling Cloud Build API..."
gcloud services enable cloudbuild.googleapis.com

echo "Enabling Cloud Run API..."
gcloud services enable run.googleapis.com

echo "Enabling Container Registry API..."
gcloud services enable containerregistry.googleapis.com

echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

echo "✅ APIs enabled"
echo ""

# Create secrets
echo "STEP 6: Creating Secrets in Secret Manager"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Load .env
source .env

# Function to create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2

    if [ -z "$secret_value" ] || [ "$secret_value" == "your_"* ]; then
        echo "⏭️  Skipping $secret_name (not set)"
        return
    fi

    if gcloud secrets describe $secret_name &>/dev/null; then
        echo "Updating $secret_name..."
        echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=-
    else
        echo "Creating $secret_name..."
        echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=-
    fi
}

create_or_update_secret "winnicki-google-api-key" "$GOOGLE_API_KEY"
create_or_update_secret "winnicki-sendgrid-api-key" "$SENDGRID_API_KEY"
create_or_update_secret "winnicki-slack-webhook" "$SLACK_WEBHOOK_URL"
create_or_update_secret "winnicki-from-email" "$FROM_EMAIL"
create_or_update_secret "winnicki-to-email" "$TO_EMAIL"

echo "✅ Secrets configured"
echo ""

# Build container
echo "STEP 7: Building Container Image"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

IMAGE_NAME="gcr.io/${PROJECT_ID}/winnicki-intake"

echo "Building and pushing to: $IMAGE_NAME"
echo "This may take 2-5 minutes..."
echo ""

gcloud builds submit --tag $IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "✅ Container built successfully"
else
    echo "❌ Build failed"
    exit 1
fi

echo ""

# Deploy to Cloud Run
echo "STEP 8: Deploying to Cloud Run"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SERVICE_NAME="winnicki-intake"
REGION="us-central1"

echo "Deploying $SERVICE_NAME to $REGION..."
echo ""

# Build secret flags
SECRET_FLAGS=""
if gcloud secrets describe winnicki-google-api-key &>/dev/null; then
    SECRET_FLAGS="$SECRET_FLAGS --set-secrets=GOOGLE_API_KEY=winnicki-google-api-key:latest"
fi
if gcloud secrets describe winnicki-sendgrid-api-key &>/dev/null; then
    SECRET_FLAGS="$SECRET_FLAGS,SENDGRID_API_KEY=winnicki-sendgrid-api-key:latest"
fi
if gcloud secrets describe winnicki-slack-webhook &>/dev/null; then
    SECRET_FLAGS="$SECRET_FLAGS,SLACK_WEBHOOK_URL=winnicki-slack-webhook:latest"
fi
if gcloud secrets describe winnicki-from-email &>/dev/null; then
    SECRET_FLAGS="$SECRET_FLAGS,FROM_EMAIL=winnicki-from-email:latest"
fi
if gcloud secrets describe winnicki-to-email &>/dev/null; then
    SECRET_FLAGS="$SECRET_FLAGS,TO_EMAIL=winnicki-to-email:latest"
fi

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  $SECRET_FLAGS

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
else
    echo ""
    echo "❌ Deployment failed"
    exit 1
fi

echo ""

# Get service URL
echo "STEP 9: Service Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   DEPLOYMENT COMPLETE!                                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "Test your deployment:"
echo "  Health check:  curl $SERVICE_URL/health"
echo "  API docs:      $SERVICE_URL/docs"
echo ""
echo "Test Phase 1 (Pre-call research):"
echo "  curl -X POST $SERVICE_URL/initial-lead \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"first_name\":\"John\",\"last_name\":\"Doe\",\"email\":\"john@test.com\",\"company_name\":\"Test Corp\",\"interested_in\":\"Website\"}'"
echo ""
echo "View logs:"
echo "  gcloud run logs read --service=$SERVICE_NAME --limit=50"
echo ""
echo "Manage service:"
echo "  gcloud run services list"
echo "  gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""
