# 🚀 Deploy Right Now

You already have your API key, so let's deploy!

## Option 1: Automated (Recommended)

Run this single script that does everything:

```bash
export GOOGLE_API_KEY="AIzaSyCV3KmTvk2lv64eaDIcno11xXyxs2CbnWA"
./deploy-quick.sh
```

This will:
1. Enable required APIs
2. Create Artifact Registry repository
3. Build your Docker image
4. Push to Artifact Registry
5. Deploy to Cloud Run
6. Give you the service URL

**Time:** About 3-5 minutes

---

## Option 2: Manual Steps

### Step 1: Enable APIs
```bash
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### Step 2: Create Artifact Registry Repository
```bash
gcloud artifacts repositories create winnicki-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Winnicki Digital Docker images"
```

### Step 3: Configure Docker Authentication
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Step 4: Build and Push Image
```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/self-hosted-468515/winnicki-repo/winnicki-intake
```

This takes 2-5 minutes and builds your Docker container.

### Step 5: Deploy to Cloud Run
```bash
gcloud run deploy winnicki-intake \
  --image us-central1-docker.pkg.dev/self-hosted-468515/winnicki-repo/winnicki-intake \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars GOOGLE_API_KEY="AIzaSyCV3KmTvk2lv64eaDIcno11xXyxs2CbnWA"
```

### Step 6: Get Service URL
```bash
gcloud run services describe winnicki-intake \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## After Deployment

### Test Health Check
```bash
SERVICE_URL=$(gcloud run services describe winnicki-intake \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

curl $SERVICE_URL/health
```

### Test Phase 1 (Pre-Call Intelligence)
```bash
curl -X POST $SERVICE_URL/initial-lead \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "email": "john@testcorp.com",
    "company_name": "Test Corp",
    "website": "https://example.com",
    "interested_in": "Website Redesign",
    "pain_points": "Outdated website"
  }'
```

### View API Documentation
Open in browser:
```bash
echo "$SERVICE_URL/docs"
```

### View Logs
```bash
gcloud run logs read --service=winnicki-intake --limit=50
```

---

## Quick Reference

**Your Configuration:**
- Project: `self-hosted-468515`
- Region: `us-central1`
- Repository: `winnicki-repo`
- Service: `winnicki-intake`
- Port: `8080`
- Image: `us-central1-docker.pkg.dev/self-hosted-468515/winnicki-repo/winnicki-intake`

**Update Deployment:**
```bash
# Rebuild and redeploy
gcloud builds submit --tag us-central1-docker.pkg.dev/self-hosted-468515/winnicki-repo/winnicki-intake

gcloud run deploy winnicki-intake \
  --image us-central1-docker.pkg.dev/self-hosted-468515/winnicki-repo/winnicki-intake \
  --region us-central1
```

---

## Troubleshooting

**"Repository not found"**
```bash
gcloud artifacts repositories create winnicki-repo \
  --repository-format=docker \
  --location=us-central1
```

**"Permission denied"**
```bash
gcloud auth login
gcloud config set project self-hosted-468515
```

**"Build failed"**
```bash
# Check logs
gcloud builds list
```

**"Service not responding"**
```bash
# Check logs
gcloud run logs read --service=winnicki-intake --limit=100

# Check environment variables
gcloud run services describe winnicki-intake --region=us-central1
```

---

## Security Note

Your API key is currently passed as an environment variable. For production, consider using Secret Manager:

```bash
# Store in Secret Manager
echo -n "AIzaSyCV3KmTvk2lv64eaDIcno11xXyxs2CbnWA" | \
  gcloud secrets create winnicki-google-api-key --data-file=-

# Update deployment to use secret
gcloud run services update winnicki-intake \
  --region us-central1 \
  --set-secrets GOOGLE_API_KEY=winnicki-google-api-key:latest
```

---

**Ready to deploy?** Run: `./deploy-quick.sh`
