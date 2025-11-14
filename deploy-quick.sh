#!/bin/bash

# Quick deployment script for Winnicki Digital
# Uses Artifact Registry

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   WINNICKI DIGITAL - QUICK DEPLOY                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ID="self-hosted-468515"
REGION="us-central1"
REPOSITORY="winnicki-repo"
IMAGE_NAME="winnicki-intake"
SERVICE_NAME="winnicki-intake"

# Full image path
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}"

echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Repository: $REPOSITORY"
echo "Image: $IMAGE_PATH"
echo ""

# Step 1: Set project
echo "Step 1: Setting project..."
gcloud config set project $PROJECT_ID
echo ""

# Step 2: Enable APIs
echo "Step 2: Enabling required APIs..."
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
echo "✅ APIs enabled"
echo ""

# Step 3: Create Artifact Registry repository (if it doesn't exist)
echo "Step 3: Checking Artifact Registry repository..."
if gcloud artifacts repositories describe $REPOSITORY \
    --location=$REGION &>/dev/null; then
    echo "✅ Repository '$REPOSITORY' already exists"
else
    echo "Creating repository '$REPOSITORY'..."
    gcloud artifacts repositories create $REPOSITORY \
        --repository-format=docker \
        --location=$REGION \
        --description="Winnicki Digital Docker images"
    echo "✅ Repository created"
fi
echo ""

# Step 4: Configure Docker authentication
echo "Step 4: Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev
echo "✅ Docker configured"
echo ""

# Step 5: Build and push image
echo "Step 5: Building and pushing Docker image..."
echo "This may take 2-5 minutes..."
echo ""

gcloud builds submit --tag $IMAGE_PATH .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Image built and pushed successfully"
else
    echo ""
    echo "❌ Build failed"
    exit 1
fi
echo ""

# Step 6: Deploy to Cloud Run
echo "Step 6: Deploying to Cloud Run..."
echo ""

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY environment variable not set"
    echo ""
    read -p "Enter your Google AI API key: " API_KEY
    export GOOGLE_API_KEY=$API_KEY
fi

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_PATH \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars "GOOGLE_API_KEY=$GOOGLE_API_KEY"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
else
    echo ""
    echo "❌ Deployment failed"
    exit 1
fi
echo ""

# Step 7: Get service URL
echo "Step 7: Getting service information..."
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
echo "📚 API Documentation: $SERVICE_URL/docs"
echo "🏥 Health Check: $SERVICE_URL/health"
echo ""
echo "Test your deployment:"
echo ""
echo "curl $SERVICE_URL/health"
echo ""
echo "View logs:"
echo "gcloud run logs read --service=$SERVICE_NAME --limit=50"
echo ""
