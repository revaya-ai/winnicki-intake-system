# Winnicki Digital - AI Intake System

AI-powered two-phase intake system for lead qualification and proposal generation using Claude AI multi-agent workflow.

## Overview

The Winnicki Digital Intake System automates the sales process with two distinct phases:

### Phase 1: Pre-Call Intelligence
When a new lead comes in, the system automatically:
- Researches the company/person/website
- Analyzes their current digital presence
- Generates targeted discovery questions
- Prepares objection handling strategies
- Creates a comprehensive call prep brief

**Output:** Email + Slack notification + Google Drive save

### Phase 2: Post-Call Proposal
After your sales call, input the call notes and the system:
- Processes requirements from your conversation
- Scopes technical requirements
- Calculates accurate pricing
- Estimates project timeline
- Generates a professional proposal

**Output:** Email + Slack notification + Google Drive save

## Architecture

### Multi-Agent Workflow

**Phase 1 Agents:**
1. **Research Agent** - Scrapes website and analyzes company
2. **Discovery Agent** - Generates targeted questions
3. **Objection Handler** - Prepares responses to common objections
4. **Brief Generator** - Compiles comprehensive call prep

**Phase 2 Agents:**
1. **Requirements Processor** - Extracts structured requirements
2. **Technical Scoper** - Determines technical approach
3. **Pricing Calculator** - Calculates accurate pricing
4. **Timeline Estimator** - Estimates project timeline
5. **Proposal Writer** - Generates professional proposal

### Tech Stack

- **AI Engine:** Anthropic Claude (Sonnet 4.5)
- **API Framework:** FastAPI
- **Web Scraping:** BeautifulSoup4
- **Integrations:** Email (SMTP), Slack, Google Drive
- **Deployment:** Google Cloud Run (Docker)

## Project Structure

```
winnicki-intake-system/
├── agent.py              # Multi-agent system (Phase 1 & 2)
├── api.py                # FastAPI endpoints & integrations
├── config.py             # Business configuration & pricing
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container configuration
├── .env.example          # Environment variables template
├── .dockerignore         # Docker ignore rules
├── .gitignore            # Git ignore rules
├── DEPLOYMENT.md         # Deployment instructions
└── README.md             # This file
```

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd winnicki-intake-system
```

### 2. Set Up Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

Required credentials:
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/
- `SMTP_USER` and `SMTP_PASSWORD` - Gmail credentials
- `SLACK_WEBHOOK_URL` - (Optional) Slack webhook
- `GOOGLE_DRIVE_CREDENTIALS` - (Optional) Service account JSON

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Locally

```bash
python api.py
```

Or with uvicorn:
```bash
uvicorn api:app --reload --port 8080
```

### 5. Test the API

**Health Check:**
```bash
curl http://localhost:8080/health
```

**Test Phase 1:**
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

**Test Phase 2:**
```bash
curl -X POST http://localhost:8080/api/phase2/post-call-proposal \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Smith",
    "company": "Acme Plumbing",
    "project_type": "website",
    "notes": "Needs 5-page website, online booking, budget $2000-3000"
  }'
```

## API Endpoints

### GET /
Root endpoint with service info

### GET /health
Health check for monitoring

### POST /api/phase1/pre-call-intelligence
Generate pre-call intelligence brief

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "company": "Acme Plumbing",
  "website": "https://example.com",
  "phone": "555-1234",
  "additional_info": "Looking for a new website"
}
```

### POST /api/phase2/post-call-proposal
Generate post-call proposal

**Request Body:**
```json
{
  "client_name": "John Smith",
  "company": "Acme Plumbing",
  "email": "john@example.com",
  "project_type": "website",
  "notes": "Needs 5-page website with online booking",
  "budget_range": "$2000-3000",
  "timeline_expectation": "3 weeks"
}
```

### GET /api/test/integrations
Test email, Slack, and Google Drive integrations

## Deployment

The system is designed to be deployed on **Google Cloud Run**.

**Project ID:** `self-hosted-468515`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy

```bash
# Authenticate
gcloud auth login
gcloud config set project self-hosted-468515

# Build and push
docker build -t gcr.io/self-hosted-468515/winnicki-intake-system:latest .
docker push gcr.io/self-hosted-468515/winnicki-intake-system:latest

# Deploy
gcloud run deploy winnicki-intake-system \
  --image gcr.io/self-hosted-468515/winnicki-intake-system:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ANTHROPIC_API_KEY=your_key" \
  --memory 1Gi \
  --project self-hosted-468515
```

## Configuration

### Pricing Packages (config.py)

- **Single Page Website:** $700 (1-2 weeks)
- **Small Website:** $1,999 (2-3 weeks, up to 5 pages)
- **Large Website:** $3,999 (4-6 weeks, up to 15 pages)

### Additional Services

- **SEO Services:** Custom pricing (3-6 months)
- **AI Voice Agent:** $2,000-5,000 setup (2-3 weeks)
- **AI Automation:** $150/hour (varies)

### Supported Platforms

- Wix
- Shopify
- HighLevel
- Webflow

## Integration with n8n

This system is designed to integrate seamlessly with n8n workflows.

**n8n Webhook Configuration:**

1. **Phase 1 Trigger:** When new lead comes in (CRM, form, email, etc.)
   - Webhook URL: `https://your-service-url/api/phase1/pre-call-intelligence`
   - Method: POST
   - Body: Lead information (name, email, company, website, etc.)

2. **Phase 2 Trigger:** After sales call
   - Webhook URL: `https://your-service-url/api/phase2/post-call-proposal`
   - Method: POST
   - Body: Call notes and requirements

## Notifications

The system automatically sends notifications via:

1. **Email** - Detailed reports sent to shannon@winnickidigital.com
2. **Slack** - Quick notifications to #wd-leads channel
3. **Google Drive** - Documents saved to "Winnicki Digital Agent Proposals" folder

## Environment Variables

See `.env.example` for all required environment variables:

- `ANTHROPIC_API_KEY` - Claude AI API key (required)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Email config
- `SLACK_WEBHOOK_URL` - Slack webhook (optional)
- `GOOGLE_DRIVE_CREDENTIALS` - Service account JSON (optional)
- `GOOGLE_DRIVE_FOLDER_ID` - Drive folder ID (optional)
- `PORT` - API port (default: 8080)

## Monitoring

View logs on Cloud Run:
```bash
gcloud run services logs read winnicki-intake-system \
  --platform managed \
  --region us-central1 \
  --project self-hosted-468515
```

## Security

- Sensitive credentials stored in Google Secret Manager
- HTTPS enforced on Cloud Run
- API key validation
- Rate limiting recommended for production

## Support

For questions or issues:
- Email: shannon@winnickidigital.com
- Website: https://www.winnickidigital.com

## License

Proprietary - Winnicki Digital
