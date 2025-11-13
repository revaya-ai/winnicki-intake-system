"""
Winnicki Digital - AI Intake & Intelligence System
FastAPI Application

Two main endpoints:
1. /initial-lead - Phase 1: Pre-call research and intelligence brief
2. /generate-proposal - Phase 2: Post-call proposal generation
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom modules
from phase1_research import run_phase1_research
from phase2_proposal import run_phase2_proposal
from utils import (
    send_email,
    send_slack_lead_notification,
    send_slack_proposal_notification,
    save_to_drive,
    compile_call_prep_brief
)
from config import COMPANY_INFO

# Initialize FastAPI
app = FastAPI(
    title="Winnicki Digital Intake API",
    description="AI-powered intake and proposal system for Winnicki Digital",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST MODELS
# ============================================================================

class LeadData(BaseModel):
    """Lead data from intake form"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    company_name: Optional[str] = None
    website: Optional[str] = None
    interested_in: str
    pain_points: Optional[str] = None
    referred_by: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "john@example.com",
                "phone": "555-0123",
                "company_name": "Test Corp",
                "website": "https://example.com",
                "interested_in": "Website Redesign",
                "pain_points": "Site is outdated and not mobile friendly",
                "referred_by": "Google Search"
            }
        }


class ProposalRequest(BaseModel):
    """Request for proposal generation"""
    client_info: dict
    discovery_answers: str

    class Config:
        json_schema_extra = {
            "example": {
                "client_info": {
                    "company_name": "Test Corp",
                    "contact_name": "John Smith",
                    "email": "john@testcorp.com",
                    "industry": "Professional Services"
                },
                "discovery_answers": """
                    Need 10-page website with blog
                    E-commerce for service bookings
                    Timeline: 6 weeks
                    Budget: $3000-5000
                """
            }
        }


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Winnicki Digital Intake System",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "company": COMPANY_INFO["name"]
    }


@app.get("/health")
def detailed_health():
    """Detailed health check with configuration status"""
    config_status = {
        "google_api_key": "configured" if os.getenv("GOOGLE_API_KEY") else "missing",
        "sendgrid_api_key": "configured" if os.getenv("SENDGRID_API_KEY") else "missing",
        "slack_webhook": "configured" if os.getenv("SLACK_WEBHOOK_URL") else "missing",
        "google_drive": "configured" if os.path.exists(os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "credentials.json")) else "missing"
    }

    all_configured = all(v == "configured" for v in config_status.values())

    return {
        "status": "healthy" if all_configured else "degraded",
        "service": "Winnicki Digital Intake System",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "configuration": config_status,
        "warnings": [] if all_configured else [
            f"{k} is {v}" for k, v in config_status.items() if v != "configured"
        ]
    }


@app.post("/initial-lead")
async def initial_lead(lead: LeadData, background_tasks: BackgroundTasks):
    """
    Phase 1: Generate pre-call intelligence brief

    This endpoint:
    1. Runs 6 research agents in parallel
    2. Generates discovery questions and objection handling
    3. Emails the complete brief to Shannon
    4. Notifies Slack
    5. Saves to Google Drive

    Returns the complete brief immediately.
    """
    try:
        print(f"📥 New lead received: {lead.company_name}")

        # Convert Pydantic model to dict
        lead_dict = lead.model_dump()

        # Run Phase 1 research agents
        print("🔍 Running research agents...")
        agent_results = run_phase1_research(lead_dict)

        # Compile the brief
        print("📝 Compiling call prep brief...")
        brief = compile_call_prep_brief(agent_results, lead_dict)

        # Background tasks for email, Slack, and Drive
        company_name = lead.company_name or "Prospect"

        # Send email
        print("📧 Sending email...")
        email_result = send_email(
            content_text=brief,
            subject=f"Call Prep Brief: {company_name}"
        )

        # Send Slack notification
        print("💬 Sending Slack notification...")
        slack_result = send_slack_lead_notification(lead_dict)

        # Save to Google Drive
        print("💾 Saving to Google Drive...")
        filename = f"CallPrep_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        drive_result = save_to_drive(brief, filename)

        print("✅ Phase 1 complete!")

        return {
            "success": True,
            "message": "Call prep brief generated successfully",
            "lead": {
                "company": company_name,
                "contact": f"{lead.first_name} {lead.last_name}",
                "email": lead.email
            },
            "brief": brief,
            "email_sent": email_result.get("success", False),
            "email_details": email_result,
            "slack_notified": slack_result.get("success", False),
            "slack_details": slack_result,
            "drive_link": drive_result.get("drive_link"),
            "drive_details": drive_result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Error in initial_lead: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "Failed to generate call prep brief"
            }
        )


@app.post("/generate-proposal")
async def generate_proposal(request: ProposalRequest, background_tasks: BackgroundTasks):
    """
    Phase 2: Generate complete project proposal

    This endpoint:
    1. Analyzes discovery call notes
    2. Creates technical scope
    3. Calculates pricing and timeline
    4. Writes professional proposal
    5. Emails proposal to Shannon
    6. Notifies Slack
    7. Saves to Google Drive

    Returns the complete proposal immediately.
    """
    try:
        company_name = request.client_info.get("company_name", "Prospect")
        print(f"📄 Generating proposal for: {company_name}")

        # Run Phase 2 proposal agents
        print("🤖 Running proposal agents...")
        agent_results = run_phase2_proposal(
            client_info=request.client_info,
            discovery_answers=request.discovery_answers
        )

        # Get the final proposal
        proposal = agent_results.get("final_proposal", "")

        if not proposal:
            raise Exception("Proposal generation failed - no output from agents")

        # Send email
        print("📧 Sending proposal email...")
        email_result = send_email(
            content_text=proposal,
            subject=f"Project Proposal: {company_name}"
        )

        # Send Slack notification
        print("💬 Sending Slack notification...")
        slack_result = send_slack_proposal_notification(request.client_info)

        # Save to Google Drive
        print("💾 Saving to Google Drive...")
        filename = f"Proposal_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        drive_result = save_to_drive(proposal, filename)

        print("✅ Phase 2 complete!")

        return {
            "success": True,
            "message": "Proposal generated successfully",
            "client": {
                "company": company_name,
                "email": request.client_info.get("email")
            },
            "proposal": proposal,
            "technical_scope": agent_results.get("technical_scope"),
            "pricing_breakdown": agent_results.get("pricing_breakdown"),
            "timeline_estimate": agent_results.get("timeline_estimate"),
            "email_sent": email_result.get("success", False),
            "email_details": email_result,
            "slack_notified": slack_result.get("success", False),
            "slack_details": slack_result,
            "drive_link": drive_result.get("drive_link"),
            "drive_details": drive_result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Error in generate_proposal: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "Failed to generate proposal"
            }
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/config")
def get_config():
    """Get public configuration information"""
    return {
        "company": COMPANY_INFO,
        "services_available": True,
        "phase1_enabled": True,
        "phase2_enabled": True
    }


@app.post("/test-integrations")
async def test_integrations():
    """Test all integrations (email, Slack, Drive)"""
    results = {}

    # Test Slack
    from utils import notify_slack
    results["slack"] = notify_slack("🧪 Test notification from Winnicki Digital API")

    # Test email
    results["email"] = send_email(
        content_text="# Test Email\n\nThis is a test email from the Winnicki Digital API.",
        subject="Test Email - Winnicki Digital API"
    )

    # Test Drive
    from utils import save_to_local
    test_content = f"# Test Document\n\nGenerated at {datetime.now().isoformat()}"
    results["drive"] = save_to_drive(test_content, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    return {
        "test_completed": True,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   WINNICKI DIGITAL - AI INTAKE & INTELLIGENCE SYSTEM     ║
    ╚═══════════════════════════════════════════════════════════╝

    🚀 Starting server on http://0.0.0.0:{port}

    📚 API Documentation: http://localhost:{port}/docs
    🏥 Health Check: http://localhost:{port}/health

    Endpoints:
    - POST /initial-lead       → Phase 1: Pre-call research
    - POST /generate-proposal  → Phase 2: Proposal generation
    - POST /test-integrations  → Test email, Slack, Drive

    Press Ctrl+C to stop
    """)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
