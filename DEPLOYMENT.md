# Winnicki Digital Intake System - Deployment Guide

## Overview

This guide covers deploying the Winnicki Digital Intake System to Google Cloud Run.

**Project ID:** `self-hosted-468515`

## Prerequisites

1. **Google Cloud CLI** installed and configured
   ```bash
   gcloud --version
   ```

2. **Docker** installed (for local testing)
   ```bash
   docker --version
   ```

3. **API Keys and Credentials**
   - Anthropic API key
   - SMTP credentials (Gmail)
   - Slack webhook URL (optional)
   - Google Drive service account (optional)

## Step 1: Local Testing

### 1.1 Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add your actual credentials:
- `ANTHROPIC_API_KEY`
- `SMTP_USER` and `SMTP_PASSWORD`
- `SLACK_WEBHOOK_URL` (optional)
- `GOOGLE_DRIVE_CREDENTIALS` (optional)

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Run Locally

```bash
python api.py
```

Or with uvicorn:
```bash
uvicorn api:app --reload --port 8080
```

### 1.4 Test Endpoints

**Health Check:**
```bash
curl http://localhost:8080/health
```

**Test Integrations:**
```bash
curl http://localhost:8080/api/test/integrations
```

**Test Phase 1 (Pre-Call Intelligence):**
```bash
curl -X POST http://localhost:8080/api/phase1/pre-call-intelligence \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "email": "john@example.com",
    "company": "Acme Plumbing",
    "website": "https://acmeplumbing.com",
    "phone": "555-1234",
    "additional_info": "Looking for a new website"
  }'
```

**Test Phase 2 (Post-Call Proposal):**
```bash
curl -X POST http://localhost:8080/api/phase2/post-call-proposal \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Smith",
    "company": "Acme Plumbing",
    "email": "john@example.com",
    "project_type": "website",
    "notes": "Needs 5-page website with service pages, wants online booking, budget around $2000-3000",
    "budget_range": "$2000-3000",
    "timeline_expectation": "3 weeks"
  }'
```

## Step 2: Google Cloud Setup

### 2.1 Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project self-hosted-468515
```

### 2.2 Enable Required APIs

```bash
# Enable Cloud Run
gcloud services enable run.googleapis.com

# Enable Container Registry
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com
```

### 2.3 Configure Docker for GCR

```bash
gcloud auth configure-docker
```

## Step 3: Build and Push Docker Image

### 3.1 Build the Docker Image

```bash
docker build -t gcr.io/self-hosted-468515/winnicki-intake-system:latest .
```

### 3.2 Test Docker Image Locally (Optional)

```bash
docker run -p 8080:8080 \
  -e ANTHROPIC_API_KEY="your_key" \
  -e SMTP_USER="your_email" \
  -e SMTP_PASSWORD="your_password" \
  gcr.io/self-hosted-468515/winnicki-intake-system:latest
```

### 3.3 Push to Google Container Registry

```bash
docker push gcr.io/self-hosted-468515/winnicki-intake-system:latest
```

## Step 4: Deploy to Cloud Run

### 4.1 Deploy with Environment Variables

```bash
gcloud run deploy winnicki-intake-system \
  --image gcr.io/self-hosted-468515/winnicki-intake-system:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ANTHROPIC_API_KEY=your_anthropic_key" \
  --set-env-vars "SMTP_HOST=smtp.gmail.com" \
  --set-env-vars "SMTP_PORT=587" \
  --set-env-vars "SMTP_USER=your_email@gmail.com" \
  --set-env-vars "SMTP_PASSWORD=your_app_password" \
  --set-env-vars "SLACK_WEBHOOK_URL=your_slack_webhook" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --project self-hosted-468515
```

### 4.2 Alternative: Using Secrets Manager (Recommended for Production)

Store sensitive data in Google Secret Manager:

```bash
# Create secrets
echo -n "your_anthropic_key" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "your_smtp_password" | gcloud secrets create smtp-password --data-file=-
echo -n "your_slack_webhook" | gcloud secrets create slack-webhook --data-file=-

# Deploy with secrets
gcloud run deploy winnicki-intake-system \
  --image gcr.io/self-hosted-468515/winnicki-intake-system:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --set-secrets "SMTP_PASSWORD=smtp-password:latest" \
  --set-secrets "SLACK_WEBHOOK_URL=slack-webhook:latest" \
  --set-env-vars "SMTP_HOST=smtp.gmail.com,SMTP_PORT=587,SMTP_USER=shannon@winnickidigital.com" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --project self-hosted-468515
```

## Step 5: Get Service URL

After deployment, get your service URL:

```bash
gcloud run services describe winnicki-intake-system \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)' \
  --project self-hosted-468515
```

Example output: `https://winnicki-intake-system-abc123-uc.a.run.app`

## Step 6: Configure n8n Webhooks

Use these endpoints in your n8n workflows:

**Phase 1 Endpoint:**
```
POST https://your-service-url/api/phase1/pre-call-intelligence
```

**Phase 2 Endpoint:**
```
POST https://your-service-url/api/phase2/post-call-proposal
```

## Step 7: Verify Deployment

Test the deployed service:

```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe winnicki-intake-system \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)' \
  --project self-hosted-468515)

# Test health check
curl $SERVICE_URL/health

# Test integrations
curl $SERVICE_URL/api/test/integrations

# Test Phase 1
curl -X POST $SERVICE_URL/api/phase1/pre-call-intelligence \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Lead",
    "email": "test@example.com",
    "company": "Test Company",
    "website": "https://example.com"
  }'
```

## Updating the Service

When you make code changes:

```bash
# 1. Build new image
docker build -t gcr.io/self-hosted-468515/winnicki-intake-system:latest .

# 2. Push to GCR
docker push gcr.io/self-hosted-468515/winnicki-intake-system:latest

# 3. Deploy update
gcloud run deploy winnicki-intake-system \
  --image gcr.io/self-hosted-468515/winnicki-intake-system:latest \
  --platform managed \
  --region us-central1 \
  --project self-hosted-468515
```

## Monitoring and Logs

### View Logs
```bash
gcloud run services logs read winnicki-intake-system \
  --platform managed \
  --region us-central1 \
  --project self-hosted-468515
```

### View Service Details
```bash
gcloud run services describe winnicki-intake-system \
  --platform managed \
  --region us-central1 \
  --project self-hosted-468515
```

## Troubleshooting

### Check Container Logs
```bash
gcloud run services logs tail winnicki-intake-system \
  --platform managed \
  --region us-central1 \
  --project self-hosted-468515
```

### Common Issues

1. **503 Service Unavailable**
   - Check if the container is starting properly
   - Verify environment variables are set
   - Check memory/CPU limits

2. **API Errors**
   - Verify ANTHROPIC_API_KEY is correct
   - Check API key has sufficient credits

3. **Email Not Sending**
   - Verify SMTP credentials
   - For Gmail: Use App Password, not regular password
   - Enable "Less secure app access" if needed

4. **Slack Notifications Failing**
   - Verify webhook URL is correct
   - Check webhook is active in Slack

## Security Best Practices

1. **Use Secret Manager** for sensitive data (recommended)
2. **Restrict service access** if needed:
   ```bash
   gcloud run services remove-iam-policy-binding winnicki-intake-system \
     --member="allUsers" \
     --role="roles/run.invoker" \
     --region us-central1 \
     --project self-hosted-468515
   ```
3. **Monitor costs** in Google Cloud Console
4. **Set up billing alerts**

## Cost Optimization

Cloud Run pricing is based on:
- Request duration
- CPU/Memory usage
- Number of requests

Tips:
- Use `--max-instances` to limit scale
- Use `--cpu 1` for cost-effective setup
- Use `--memory 1Gi` (minimum needed)
- Monitor usage in Cloud Console

## Support

For issues or questions:
- Check logs: `gcloud run services logs read winnicki-intake-system`
- Review API documentation: `https://your-service-url/docs`
- Contact: shannon@winnickidigital.com
