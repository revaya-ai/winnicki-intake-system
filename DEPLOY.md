# 🚀 Deployment Instructions

## Quick Deploy (Recommended)

### Prerequisites
1. **Google Cloud SDK** installed
   - macOS: `brew install google-cloud-sdk`
   - Linux/Windows: https://cloud.google.com/sdk/docs/install

2. **Google AI API Key**
   - Get it from: https://ai.google.dev/
   - Click "Get API Key" → Create new key

### Deploy in 3 Steps

**1. Clone the repository to your local machine:**
```bash
git clone https://github.com/revaya-ai/winnicki-intake-system.git
cd winnicki-intake-system
```

**2. Set your API key:**
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your Google AI API key:
```env
GOOGLE_API_KEY=your_actual_api_key_here
```

**3. Run the deployment script:**
```bash
./deploy-interactive.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Authenticate with Google Cloud
- ✅ Enable required APIs
- ✅ Store secrets securely
- ✅ Build Docker container
- ✅ Deploy to Cloud Run
- ✅ Give you the service URL

**That's it!** Your service will be live at:
```
https://winnicki-intake-xxxxxxxxxx-uc.a.run.app
```

---

## Manual Deployment

If you prefer to run commands manually:

### 1. Authenticate
```bash
gcloud auth login
gcloud config set project self-hosted-468515
```

### 2. Enable APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 3. Create Secret
```bash
echo -n "your_google_api_key" | gcloud secrets create winnicki-google-api-key --data-file=-
```

### 4. Build Container
```bash
gcloud builds submit --tag gcr.io/self-hosted-468515/winnicki-intake
```

### 5. Deploy to Cloud Run
```bash
gcloud run deploy winnicki-intake \
  --image gcr.io/self-hosted-468515/winnicki-intake \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets GOOGLE_API_KEY=winnicki-google-api-key:latest
```

### 6. Get Service URL
```bash
gcloud run services describe winnicki-intake \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## Test Your Deployment

### Health Check
```bash
curl https://your-service-url.run.app/health
```

### Test Phase 1 (Pre-call Research)
```bash
curl -X POST https://your-service-url.run.app/initial-lead \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@testcorp.com",
    "company_name": "Test Corp",
    "interested_in": "Website Redesign",
    "pain_points": "Outdated site"
  }'
```

### Test Phase 2 (Proposal Generation)
```bash
curl -X POST https://your-service-url.run.app/generate-proposal \
  -H "Content-Type: application/json" \
  -d '{
    "client_info": {
      "company_name": "Test Corp",
      "email": "john@testcorp.com"
    },
    "discovery_answers": "Need 10 pages, blog, e-commerce, 6 weeks"
  }'
```

### View API Documentation
Open in browser:
```
https://your-service-url.run.app/docs
```

---

## View Logs

```bash
# View recent logs
gcloud run logs read --service=winnicki-intake --limit=50

# Follow logs in real-time
gcloud run logs tail --service=winnicki-intake

# Filter for errors
gcloud run logs read --service=winnicki-intake | grep ERROR
```

---

## Update Deployment

When you make code changes:

```bash
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/self-hosted-468515/winnicki-intake

gcloud run deploy winnicki-intake \
  --image gcr.io/self-hosted-468515/winnicki-intake \
  --region us-central1
```

Or simply run:
```bash
./deploy-interactive.sh
```

---

## Manage Secrets

### Update API Key
```bash
echo -n "new_api_key" | gcloud secrets versions add winnicki-google-api-key --data-file=-

# Redeploy to use new secret
gcloud run services update winnicki-intake --region=us-central1
```

### List Secrets
```bash
gcloud secrets list
```

### View Secret Versions
```bash
gcloud secrets versions list winnicki-google-api-key
```

---

## Cost Management

### View Current Usage
```bash
gcloud run services describe winnicki-intake \
  --region=us-central1 \
  --format="value(status.traffic)"
```

### Set Budget Alert
Go to: https://console.cloud.google.com/billing/budgets

Recommended: Set alert at $10/month

---

## Troubleshooting

### Build Fails
```bash
# Check build logs
gcloud builds list
gcloud builds log [BUILD_ID]

# Test Dockerfile locally (requires Docker)
docker build -t test .
docker run -p 8000:8080 -e GOOGLE_API_KEY=xxx test
```

### Deployment Fails
```bash
# Check quotas
gcloud compute project-info describe --project=self-hosted-468515

# Check service status
gcloud run services list
gcloud run services describe winnicki-intake --region=us-central1
```

### Service Returns Errors
```bash
# View detailed logs
gcloud run logs read --service=winnicki-intake --limit=100

# Check environment variables
gcloud run services describe winnicki-intake \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### API Key Issues
```bash
# Verify secret exists
gcloud secrets describe winnicki-google-api-key

# Check secret value (first 10 chars)
gcloud secrets versions access latest --secret=winnicki-google-api-key | head -c 10

# Update if needed
echo -n "correct_api_key" | gcloud secrets versions add winnicki-google-api-key --data-file=-
```

---

## Delete Service (if needed)

```bash
# Delete Cloud Run service
gcloud run services delete winnicki-intake --region=us-central1

# Delete container image
gcloud container images delete gcr.io/self-hosted-468515/winnicki-intake

# Delete secrets
gcloud secrets delete winnicki-google-api-key
```

---

## Support

- Google Cloud Run Docs: https://cloud.google.com/run/docs
- Google AI API Docs: https://ai.google.dev/docs
- Project Issues: https://github.com/revaya-ai/winnicki-intake-system/issues

---

## Next Steps After Deployment

1. ✅ Test all endpoints
2. ✅ Set up monitoring/alerts
3. ✅ Configure custom domain (optional)
4. ✅ Set up CI/CD (optional)
5. ✅ Configure rate limiting (optional)
6. ✅ Add authentication (if needed)

**Your AI intake system is now live!** 🎉
