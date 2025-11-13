# Winnicki Digital - AI Intake & Intelligence System

A two-phase AI-powered system for automated sales intelligence and proposal generation.

## 🎯 Overview

This system automates the entire sales process from initial lead to proposal delivery:

**Phase 1: Pre-Call Intelligence** (Automated)
- 6 AI agents research company, contact, website, and competitors
- Generate smart discovery questions and objection handling
- Email complete brief to Shannon
- Notify Slack (#wd-leads)
- Save to Google Drive

**Phase 2: Proposal Generation** (Manual trigger after call)
- Input discovery answers from sales call
- 4 AI agents generate complete proposal with pricing and timeline
- Email proposal for review
- Notify Slack and save to Drive

## 🏗️ Architecture

### Phase 1: Research Agents (Parallel Execution)
1. **CompanyIntelligenceAgent** - Company profile and market position
2. **ContactResearchAgent** - Contact background and priorities
3. **WebsiteAnalyzerAgent** - Current website analysis
4. **CompetitiveContextAgent** - Competitive landscape
5. **RequirementsGathererAgent** - Targeted discovery questions
6. **ObjectionAnticipatorAgent** - Anticipated objections with responses

### Phase 2: Proposal Agents (Sequential Execution)
1. **TechnicalScoperAgent** - Platform and feature recommendations
2. **PricingCalculatorAgent** - Accurate pricing breakdown
3. **TimelineEstimatorAgent** - Project timeline and phases
4. **ProposalWriterAgent** - Complete professional proposal

## 📋 Prerequisites

- Python 3.11+
- Google Cloud account (project: `self-hosted-468515`)
- Google AI API key
- SendGrid API key (for email)
- Slack webhook URL (for notifications)
- Google Drive API credentials (optional)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd winnicki-intake-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GOOGLE_API_KEY=your_google_api_key
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=system@winnickidigital.com
TO_EMAIL=shannon@winnickidigital.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PORT=8000
```

### 4. Run Locally

```bash
python api.py
```

Visit:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🧪 Testing

### Test Phase 1 (Pre-Call Research)

```bash
curl -X POST http://localhost:8000/initial-lead \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "email": "john@testcorp.com",
    "phone": "555-0123",
    "company_name": "Test Corp",
    "website": "https://example.com",
    "interested_in": "Website Redesign",
    "pain_points": "Outdated website, not mobile friendly"
  }'
```

### Test Phase 2 (Proposal Generation)

```bash
curl -X POST http://localhost:8000/generate-proposal \
  -H "Content-Type: application/json" \
  -d '{
    "client_info": {
      "company_name": "Test Corp",
      "contact_name": "John Smith",
      "email": "john@testcorp.com",
      "industry": "Professional Services"
    },
    "discovery_answers": "Need 10-page website with blog, e-commerce, 6-week timeline, $3000-5000 budget"
  }'
```

### Test Integrations

```bash
curl -X POST http://localhost:8000/test-integrations
```

## 🐳 Docker

### Build

```bash
docker build -t winnicki-intake .
```

### Run

```bash
docker run -p 8000:8080 \
  -e GOOGLE_API_KEY=your_key \
  -e SENDGRID_API_KEY=your_key \
  -e SLACK_WEBHOOK_URL=your_webhook \
  winnicki-intake
```

## ☁️ Google Cloud Run Deployment

### Option 1: Simple Deployment

```bash
# Set environment variables
export GOOGLE_API_KEY=your_key
export SENDGRID_API_KEY=your_key
export SLACK_WEBHOOK_URL=your_webhook
export FROM_EMAIL=system@winnickidigital.com
export TO_EMAIL=shannon@winnickidigital.com

# Deploy
./deploy.sh
```

### Option 2: Secure Deployment (Recommended)

Uses Google Cloud Secret Manager for credentials:

```bash
# Create .env file with your credentials
cp .env.example .env
# Edit .env with actual values

# Deploy with secrets
./deploy-with-secrets.sh
```

### Manual Deployment

```bash
# Build
gcloud builds submit --tag gcr.io/self-hosted-468515/winnicki-intake

# Deploy
gcloud run deploy winnicki-intake \
  --image gcr.io/self-hosted-468515/winnicki-intake \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=xxx,SENDGRID_API_KEY=xxx,SLACK_WEBHOOK_URL=xxx
```

## 📁 Project Structure

```
winnicki-intake-system/
├── api.py                      # FastAPI application
├── config.py                   # Business configuration
├── phase1_research.py          # Phase 1: 6 research agents
├── phase2_proposal.py          # Phase 2: 4 proposal agents
├── agent_framework.py          # Custom agent framework
├── utils.py                    # Email, Slack, Drive utilities
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── deploy.sh                   # Cloud Run deployment
├── deploy-with-secrets.sh      # Secure deployment
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🔌 API Endpoints

### GET /
Health check

### GET /health
Detailed health check with configuration status

### POST /initial-lead
Phase 1: Generate pre-call intelligence brief

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john@example.com",
  "phone": "555-0123",
  "company_name": "Test Corp",
  "website": "https://example.com",
  "interested_in": "Website Redesign",
  "pain_points": "Site is outdated"
}
```

**Response:**
```json
{
  "success": true,
  "brief": "...",
  "email_sent": true,
  "slack_notified": true,
  "drive_link": "https://..."
}
```

### POST /generate-proposal
Phase 2: Generate complete proposal

**Request:**
```json
{
  "client_info": {
    "company_name": "Test Corp",
    "email": "john@testcorp.com"
  },
  "discovery_answers": "10 pages, blog, e-commerce..."
}
```

**Response:**
```json
{
  "success": true,
  "proposal": "...",
  "technical_scope": "...",
  "pricing_breakdown": "...",
  "timeline_estimate": "...",
  "email_sent": true,
  "drive_link": "https://..."
}
```

## 🔧 Configuration

### Business Configuration (config.py)

Edit `config.py` to customize:
- Website packages and pricing
- Additional services
- Company information
- Email recipients
- Slack channels

### Agent Customization

Each agent can be customized by editing:
- `phase1_research.py` - Research agent instructions
- `phase2_proposal.py` - Proposal agent instructions

## 📊 Monitoring

### View Logs (Cloud Run)

```bash
gcloud run logs read --service=winnicki-intake --limit=100
```

### View Logs (Local)

Logs are printed to console with emoji indicators:
- 📥 New lead received
- 🔍 Running agents
- 📧 Sending email
- 💬 Slack notification
- 💾 Saving to Drive
- ✅ Success
- ❌ Error

## 🔒 Security

- API keys stored in environment variables
- Google Secret Manager integration for Cloud Run
- No credentials in code
- `.gitignore` prevents credential commits
- CORS configured for production

## 🐛 Troubleshooting

### Email not sending
- Verify `SENDGRID_API_KEY` is set
- Check `FROM_EMAIL` is verified in SendGrid
- View logs for specific error

### Slack not notifying
- Verify `SLACK_WEBHOOK_URL` is correct
- Test webhook with curl
- Check Slack app permissions

### Google Drive not saving
- Ensure `credentials.json` exists
- System falls back to local storage if Drive unavailable
- Check output/ folder for local saves

### Agents not responding
- Verify `GOOGLE_API_KEY` is valid
- Check Google AI API quota
- Review logs for specific errors

## 📝 Development

### Run Tests

```bash
# Test Phase 1 agents
python phase1_research.py

# Test Phase 2 agents
python phase2_proposal.py

# Test utilities
python utils.py

# Test API
python api.py
# Then use test scripts
```

### Add New Agents

1. Create agent in appropriate phase file
2. Add to workflow (ParallelAgent or SequentialAgent)
3. Update instructions and output_key
4. Test independently before integration

## 📄 License

Proprietary - Winnicki Digital

## 👥 Contact

Shannon Winnicki - shannon@winnickidigital.com
Website: https://www.winnickidigital.com

## 🚀 Deployment Checklist

- [ ] Set all environment variables
- [ ] Test locally with `python api.py`
- [ ] Test endpoints with curl or Postman
- [ ] Verify email delivery
- [ ] Verify Slack notifications
- [ ] Test Google Drive integration
- [ ] Build Docker image
- [ ] Deploy to Cloud Run
- [ ] Test production endpoints
- [ ] Monitor logs for errors
- [ ] Set up monitoring/alerts

## 📈 Future Enhancements

- [ ] Add webhook for automatic form submission
- [ ] Implement CRM integration (HubSpot/Salesforce)
- [ ] Add proposal versioning
- [ ] Create dashboard for tracking leads
- [ ] Add analytics and reporting
- [ ] Implement A/B testing for proposals
- [ ] Add multi-language support
- [ ] Create mobile app interface
