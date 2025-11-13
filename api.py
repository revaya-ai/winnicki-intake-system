"""Winnicki Digital - FastAPI Integration for n8n"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
import requests
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from agent import IntakeAgentSystem
from config import EMAIL_CONFIG, SLACK_CONFIG, GOOGLE_DRIVE_CONFIG

# Initialize FastAPI
app = FastAPI(
    title="Winnicki Digital Intake System",
    description="Two-phase AI-powered intake system for lead qualification and proposal generation",
    version="1.0.0"
)

# Initialize agent system
agent_system = IntakeAgentSystem()

# ============================================================================
# REQUEST MODELS
# ============================================================================

class Phase1Request(BaseModel):
    """Phase 1: Pre-Call Intelligence Request"""
    name: str
    email: EmailStr
    company: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    additional_info: Optional[str] = None

class Phase2Request(BaseModel):
    """Phase 2: Post-Call Proposal Request"""
    client_name: str
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    project_type: str
    notes: str
    budget_range: Optional[str] = None
    timeline_expectation: Optional[str] = None

# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def send_email(subject: str, body: str, recipient: str = None) -> bool:
    """Send email via SMTP"""
    try:
        recipient = recipient or EMAIL_CONFIG["recipient"]
        from_email = EMAIL_CONFIG["from_email"]

        # Get SMTP settings from environment
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not smtp_user or not smtp_password:
            print("⚠️ SMTP credentials not configured, skipping email")
            return False

        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send via SMTP
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print(f"✅ Email sent to {recipient}")
        return True

    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return False

def send_slack_notification(message: str, channel: str = None) -> bool:
    """Send Slack notification"""
    try:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")

        if not webhook_url or webhook_url == "ENV_VAR":
            print("⚠️ Slack webhook not configured, skipping notification")
            return False

        channel = channel or SLACK_CONFIG["channel"]

        payload = {
            "channel": f"#{channel}",
            "text": message,
            "username": "Winnicki Digital Bot",
            "icon_emoji": ":robot_face:"
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()

        print(f"✅ Slack notification sent to #{channel}")
        return True

    except Exception as e:
        print(f"❌ Slack error: {str(e)}")
        return False

def save_to_google_drive(filename: str, content: str, mime_type: str = "text/plain") -> Optional[str]:
    """Save file to Google Drive"""
    try:
        # Get credentials from environment
        creds_json = os.getenv("GOOGLE_DRIVE_CREDENTIALS")

        if not creds_json:
            print("⚠️ Google Drive credentials not configured, skipping upload")
            return None

        # Parse credentials
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )

        # Build Drive service
        service = build('drive', 'v3', credentials=credentials)

        # Get or create folder
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

        if not folder_id:
            # Search for folder
            folder_name = GOOGLE_DRIVE_CONFIG["folder_name"]
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            folders = results.get('files', [])

            if folders:
                folder_id = folders[0]['id']
            else:
                # Create folder
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = service.files().create(body=folder_metadata, fields='id').execute()
                folder_id = folder.get('id')
                print(f"✅ Created Google Drive folder: {folder_name}")

        # Upload file
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }

        media = MediaIoBaseUpload(
            io.BytesIO(content.encode('utf-8')),
            mimetype=mime_type,
            resumable=True
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        file_id = file.get('id')
        file_link = file.get('webViewLink')

        print(f"✅ Saved to Google Drive: {filename}")
        return file_link

    except Exception as e:
        print(f"❌ Google Drive error: {str(e)}")
        return None

# ============================================================================
# NOTIFICATION HANDLERS
# ============================================================================

def send_phase1_notifications(lead_data: Dict[str, Any], brief: str):
    """Send notifications for Phase 1 completion"""
    client_name = lead_data.get('company') or lead_data.get('name')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Email
    email_subject = f"📞 Call Prep Brief Ready: {client_name}"
    email_body = f"""Hi Shannon,

A new lead has come in and the AI system has prepared your call prep brief.

LEAD DETAILS:
• Name: {lead_data.get('name')}
• Company: {lead_data.get('company', 'N/A')}
• Email: {lead_data.get('email')}
• Phone: {lead_data.get('phone', 'N/A')}
• Website: {lead_data.get('website', 'N/A')}

---

{brief}

---

Generated at {timestamp}
Winnicki Digital AI Intake System
"""
    send_email(email_subject, email_body)

    # Slack
    slack_message = f"""🎯 *New Lead - Call Prep Ready*

*{client_name}*
• Email: {lead_data.get('email')}
• Phone: {lead_data.get('phone', 'N/A')}
• Website: {lead_data.get('website', 'N/A')}

Call prep brief has been emailed to Shannon.
"""
    send_slack_notification(slack_message)

    # Google Drive
    filename = f"CallPrep_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    save_to_google_drive(filename, brief)

def send_phase2_notifications(call_notes: Dict[str, Any], proposal: str):
    """Send notifications for Phase 2 completion"""
    client_name = call_notes.get('company') or call_notes.get('client_name')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Email
    email_subject = f"📄 Proposal Ready: {client_name}"
    email_body = f"""Hi Shannon,

The AI system has generated a proposal based on your call notes.

CLIENT: {client_name}
PROJECT TYPE: {call_notes.get('project_type')}

---

{proposal}

---

Generated at {timestamp}
Winnicki Digital AI Intake System
"""
    send_email(email_subject, email_body)

    # Slack
    slack_message = f"""📄 *Proposal Generated*

*{client_name}*
• Project: {call_notes.get('project_type')}
• Budget Range: {call_notes.get('budget_range', 'TBD')}

Proposal has been emailed to Shannon and saved to Google Drive.
"""
    send_slack_notification(slack_message)

    # Google Drive
    filename = f"Proposal_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    save_to_google_drive(filename, proposal)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Winnicki Digital Intake System",
        "version": "1.0.0",
        "endpoints": {
            "phase1": "/api/phase1/pre-call-intelligence",
            "phase2": "/api/phase2/post-call-proposal"
        }
    }

@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/phase1/pre-call-intelligence")
async def phase1_pre_call_intelligence(
    request: Phase1Request,
    background_tasks: BackgroundTasks
):
    """
    Phase 1: Generate pre-call intelligence brief

    This endpoint:
    1. Researches the company/website
    2. Generates discovery questions
    3. Prepares objection handlers
    4. Creates comprehensive call prep brief
    5. Sends email, Slack notification, and saves to Google Drive
    """
    try:
        # Convert request to dict
        lead_data = request.dict()

        # Run Phase 1 agents
        result = agent_system.run_phase1(lead_data)

        # Send notifications in background
        background_tasks.add_task(
            send_phase1_notifications,
            lead_data,
            result['call_prep_brief']
        )

        return {
            "success": True,
            "phase": 1,
            "message": "Pre-call intelligence brief generated successfully",
            "lead": {
                "name": request.name,
                "company": request.company,
                "email": request.email
            },
            "brief": result['call_prep_brief'],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phase 1 error: {str(e)}")

@app.post("/api/phase2/post-call-proposal")
async def phase2_post_call_proposal(
    request: Phase2Request,
    background_tasks: BackgroundTasks
):
    """
    Phase 2: Generate post-call proposal

    This endpoint:
    1. Processes call notes and requirements
    2. Scopes technical requirements
    3. Calculates pricing
    4. Estimates timeline
    5. Generates professional proposal
    6. Sends email, Slack notification, and saves to Google Drive
    """
    try:
        # Convert request to dict
        call_notes = request.dict()

        # Run Phase 2 agents
        result = agent_system.run_phase2(call_notes)

        # Send notifications in background
        background_tasks.add_task(
            send_phase2_notifications,
            call_notes,
            result['proposal']
        )

        return {
            "success": True,
            "phase": 2,
            "message": "Proposal generated successfully",
            "client": {
                "name": request.client_name,
                "company": request.company,
                "project_type": request.project_type
            },
            "proposal": result['proposal'],
            "pricing": result['pricing'],
            "timeline": result['timeline'],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phase 2 error: {str(e)}")

@app.get("/api/test/integrations")
async def test_integrations():
    """Test endpoint to verify integrations are working"""
    results = {}

    # Test email
    try:
        email_sent = send_email(
            "Test Email - Winnicki Digital Intake System",
            "This is a test email to verify SMTP configuration."
        )
        results["email"] = "configured" if email_sent else "not configured"
    except Exception as e:
        results["email"] = f"error: {str(e)}"

    # Test Slack
    try:
        slack_sent = send_slack_notification(
            "🧪 Test notification from Winnicki Digital Intake System"
        )
        results["slack"] = "configured" if slack_sent else "not configured"
    except Exception as e:
        results["slack"] = f"error: {str(e)}"

    # Test Google Drive
    try:
        drive_link = save_to_google_drive(
            f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Test file from Winnicki Digital Intake System"
        )
        results["google_drive"] = "configured" if drive_link else "not configured"
        if drive_link:
            results["google_drive_link"] = drive_link
    except Exception as e:
        results["google_drive"] = f"error: {str(e)}"

    return {
        "status": "Integration test completed",
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
