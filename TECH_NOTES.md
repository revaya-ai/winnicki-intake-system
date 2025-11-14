# Technical Architecture Notes

## AI/LLM Stack

**This system uses the official Google Generative AI SDK:**

- Package: `google-generativeai` (version 0.3.2+)
- Model: `gemini-1.5-flash`
- Documentation: https://ai.google.dev/api/python/google/generativeai

**NOT using google.adk** - There is no such package. The system uses standard `google-generativeai`.

## Agent Architecture

The multi-agent system is implemented using **custom Python classes**, not an external agent framework:

### Core Classes (agent_framework.py)

```python
import google.generativeai as genai

class Agent:
    """Single AI agent using Gemini"""
    - Uses genai.GenerativeModel('gemini-1.5-flash')
    - Takes instructions, context, and shared state
    - Returns structured output with output_key

class ParallelAgent:
    """Runs multiple agents concurrently"""
    - Uses ThreadPoolExecutor for parallel execution
    - Collects and merges results

class SequentialAgent:
    """Runs agents in sequence"""
    - Passes accumulated state between agents
    - Enables multi-step workflows
```

## Phase 1: Research Agents

6 agents run in this workflow:

1. **Parallel execution** (Agents 1-4):
   - CompanyIntelligenceAgent
   - ContactResearchAgent
   - WebsiteAnalyzerAgent
   - CompetitiveContextAgent

2. **Sequential execution** (Agents 5-6):
   - RequirementsGathererAgent (uses outputs from 1-4)
   - ObjectionAnticipatorAgent (uses outputs from 1-5)

## Phase 2: Proposal Agents

4 agents run in this workflow:

1. TechnicalScoperAgent (sequential)
2. **Parallel execution**:
   - PricingCalculatorAgent
   - TimelineEstimatorAgent
3. ProposalWriterAgent (sequential, uses all previous outputs)

## Dependencies

All dependencies are standard, pip-installable packages:

```
fastapi==0.104.1              # Web framework
uvicorn[standard]==0.24.0     # ASGI server
google-generativeai==0.3.2    # Google Gemini API
pydantic==2.5.0               # Data validation
python-dotenv==1.0.0          # Environment variables
sendgrid==6.11.0              # Email
requests==2.31.0              # HTTP client
httpx==0.25.2                 # Async HTTP client
beautifulsoup4==4.12.2        # HTML parsing
google-api-python-client      # Google Drive API
google-auth-*                 # Google authentication
```

## How It Works

### Agent Execution Flow

```python
# 1. Agent receives context and instructions
context = "Lead data from form submission..."
instructions = "Analyze the company and provide insights..."

# 2. Prompt is constructed
prompt = f"{instructions}\n\nCONTEXT:\n{context}\n\nSHARED STATE:\n{json.dumps(shared_state)}"

# 3. Gemini generates response
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)

# 4. Result is stored with output_key
return {
    "company_profile": response.text,
    "agent_name": "CompanyIntelligenceAgent",
    "success": True
}
```

### Parallel Execution

```python
# Multiple agents run simultaneously using ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(agent.run, context) for agent in agents]
    results = [f.result() for f in as_completed(futures)]
```

### Sequential Execution with State Passing

```python
shared_state = {}

# Agent 1 runs first
result1 = agent1.run(context, shared_state)
shared_state.update(result1)  # {"company_profile": "..."}

# Agent 2 can now see Agent 1's output
result2 = agent2.run(context, shared_state)
shared_state.update(result2)  # {"company_profile": "...", "discovery_questions": "..."}
```

## API Structure

FastAPI application with 2 main endpoints:

```python
POST /initial-lead
→ Triggers Phase 1 (6 research agents)
→ Returns call prep brief
→ Sends email, Slack notification, saves to Drive

POST /generate-proposal
→ Triggers Phase 2 (4 proposal agents)
→ Returns complete proposal
→ Sends email, Slack notification, saves to Drive
```

## Environment Variables Required

Minimum:
```bash
GOOGLE_API_KEY=xxx  # Required for Gemini API
```

Optional (for full functionality):
```bash
SENDGRID_API_KEY=xxx        # For email sending
SLACK_WEBHOOK_URL=xxx       # For Slack notifications
FROM_EMAIL=xxx              # Email sender
TO_EMAIL=xxx                # Email recipient
GOOGLE_DRIVE_CREDENTIALS    # For Drive integration
```

## Deployment

**Docker builds correctly** because all dependencies are standard packages.

The Dockerfile:
1. Installs Python 3.11
2. Installs packages from requirements.txt
3. Copies application code
4. Exposes port 8080
5. Runs `python api.py`

**Cloud Run deployment works** because:
- Container builds successfully
- All packages are available on PyPI
- Environment variables are passed securely
- No custom or non-existent packages

## Testing

Run locally:
```bash
export GOOGLE_API_KEY=your_key
python api.py
```

Test with curl:
```bash
curl -X POST http://localhost:8000/initial-lead \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", ...}'
```

## Troubleshooting

**"Module not found: google.adk"**
- This error should NEVER occur - we don't use google.adk
- We use `google-generativeai` which is a real, pip-installable package

**"Invalid API key"**
- Get API key from https://ai.google.dev/
- Set GOOGLE_API_KEY environment variable

**"Rate limit exceeded"**
- Gemini API has rate limits
- Implement retries or request quota increase

## Summary

This is a **standard Python application** using:
- Official Google Generative AI SDK
- Custom agent orchestration (no external agent framework)
- FastAPI for REST API
- Standard Python libraries
- Docker for containerization
- Google Cloud Run for hosting

Everything is straightforward, production-ready, and uses only well-established packages.
