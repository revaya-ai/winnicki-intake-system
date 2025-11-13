"""
Utility functions for email, Slack, and Google Drive integration
"""

import os
import json
from typing import Optional
from datetime import datetime
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
from config import EMAIL_CONFIG, SLACK_CONFIG, GOOGLE_DRIVE_CONFIG


# ============================================================================
# EMAIL FUNCTIONS (SendGrid)
# ============================================================================

def send_email(
    content_text: str,
    subject: str,
    recipient: Optional[str] = None,
    content_type: str = "text/html"
) -> dict:
    """
    Send email via SendGrid

    Args:
        content_text: Email body (supports HTML)
        subject: Email subject line
        recipient: Email recipient (defaults to config)
        content_type: "text/plain" or "text/html"

    Returns:
        dict with success status and details
    """
    try:
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "SENDGRID_API_KEY not configured",
                "message": "Email not sent - API key missing"
            }

        from_email = os.getenv("FROM_EMAIL", EMAIL_CONFIG["from_email"])
        to_email = recipient or os.getenv("TO_EMAIL", EMAIL_CONFIG["recipient"])

        # Convert markdown to HTML if needed
        if content_type == "text/html":
            html_content = markdown_to_html(content_text)
        else:
            html_content = content_text

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        return {
            "success": True,
            "status_code": response.status_code,
            "message": f"Email sent to {to_email}",
            "recipient": to_email
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to send email: {str(e)}"
        }


def markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown to HTML for email
    Basic conversion - wraps in HTML template
    """
    # Simple HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-bottom: 1px solid #ecf0f1;
                padding-bottom: 5px;
            }}
            h3 {{
                color: #555;
            }}
            ul, ol {{
                padding-left: 25px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            strong {{
                color: #2c3e50;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
                font-size: 0.9em;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <div style="white-space: pre-wrap;">{markdown_text}</div>
        <div class="footer">
            <p>
                <strong>Winnicki Digital</strong><br>
                Email: shannon@winnickidigital.com<br>
                Web: <a href="https://www.winnickidigital.com">www.winnickidigital.com</a>
            </p>
        </div>
    </body>
    </html>
    """
    return html


# ============================================================================
# SLACK FUNCTIONS
# ============================================================================

def notify_slack(message: str, channel: Optional[str] = None) -> dict:
    """
    Send notification to Slack via webhook

    Args:
        message: Message to send
        channel: Optional channel override

    Returns:
        dict with success status
    """
    try:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url or webhook_url == "ENV_VAR":
            return {
                "success": False,
                "error": "SLACK_WEBHOOK_URL not configured",
                "message": "Slack notification skipped - webhook not configured"
            }

        payload = {
            "text": message,
            "username": "Winnicki Digital Bot",
            "icon_emoji": ":globe_with_meridians:"
        }

        if channel:
            payload["channel"] = channel

        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            return {
                "success": True,
                "message": "Slack notification sent"
            }
        else:
            return {
                "success": False,
                "error": f"Slack API returned {response.status_code}",
                "message": f"Failed to send Slack notification: {response.text}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to send Slack notification: {str(e)}"
        }


def send_slack_lead_notification(lead_data: dict) -> dict:
    """
    Send formatted lead notification to Slack
    """
    company = lead_data.get("company_name", "Unknown Company")
    name = f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip()
    interested_in = lead_data.get("interested_in", "General Inquiry")

    message = f"""
🎯 *New Lead: {company}*

*Contact:* {name}
*Email:* {lead_data.get('email', 'N/A')}
*Interested In:* {interested_in}
*Pain Points:* {lead_data.get('pain_points', 'Not specified')}

Call prep brief has been generated and emailed!
"""

    return notify_slack(message)


def send_slack_proposal_notification(client_info: dict) -> dict:
    """
    Send formatted proposal notification to Slack
    """
    company = client_info.get("company_name", "Unknown Company")

    message = f"""
📄 *Proposal Generated: {company}*

A new proposal has been created and sent for review.
Check your email for the complete proposal.
"""

    return notify_slack(message)


# ============================================================================
# GOOGLE DRIVE FUNCTIONS
# ============================================================================

def save_to_drive(content: str, filename: str) -> dict:
    """
    Save content to Google Drive

    Args:
        content: File content (text/markdown)
        filename: Name of file to create

    Returns:
        dict with success status and drive link
    """
    try:
        from google.oauth2.credentials import Credentials
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        import io
        from googleapiclient.http import MediaIoBaseUpload

        # Check for credentials
        creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "credentials.json")

        if not os.path.exists(creds_path):
            # Return success but note that Drive save was skipped
            return {
                "success": True,
                "drive_link": None,
                "message": "Google Drive credentials not configured - file not saved to Drive",
                "local_fallback": save_to_local(content, filename)
            }

        # Load service account credentials
        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )

        service = build('drive', 'v3', credentials=creds)

        # Get or create folder
        folder_name = os.getenv("GOOGLE_DRIVE_FOLDER_NAME", GOOGLE_DRIVE_CONFIG["folder_name"])
        folder_id = get_or_create_folder(service, folder_name)

        # Create file metadata
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else [],
            'mimeType': 'text/markdown'
        }

        # Upload file
        media = MediaIoBaseUpload(
            io.BytesIO(content.encode('utf-8')),
            mimetype='text/markdown',
            resumable=True
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        # Make file shareable
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=file.get('id'),
            body=permission
        ).execute()

        return {
            "success": True,
            "drive_link": file.get('webViewLink'),
            "file_id": file.get('id'),
            "message": f"File saved to Google Drive: {filename}"
        }

    except Exception as e:
        # Fallback to local storage
        local_path = save_to_local(content, filename)
        return {
            "success": True,
            "drive_link": None,
            "error": str(e),
            "message": f"Could not save to Drive, saved locally: {local_path}",
            "local_path": local_path
        }


def get_or_create_folder(service, folder_name: str) -> Optional[str]:
    """
    Get existing folder or create new one in Google Drive
    Returns folder ID
    """
    try:
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])

        if folders:
            return folders[0]['id']

        # Create new folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

    except Exception as e:
        print(f"Error with folder: {e}")
        return None


def save_to_local(content: str, filename: str) -> str:
    """
    Fallback: Save file locally if Drive is not available
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(filename)
    filename_with_timestamp = f"{base}_{timestamp}{ext}"

    filepath = os.path.join(output_dir, filename_with_timestamp)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


# ============================================================================
# CALL PREP BRIEF COMPILER
# ============================================================================

def compile_call_prep_brief(agent_results: dict, lead_data: dict) -> str:
    """
    Compile all Phase 1 research into a formatted call prep brief
    """
    company = lead_data.get("company_name", "Prospect")
    contact = f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip()

    brief = f"""
# CALL PREP BRIEF: {company}

**Contact:** {contact}
**Email:** {lead_data.get('email', 'N/A')}
**Phone:** {lead_data.get('phone', 'N/A')}
**Interested In:** {lead_data.get('interested_in', 'N/A')}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

"""

    # Add each section from agent results
    sections = [
        ("company_profile", "COMPANY RESEARCH"),
        ("contact_profile", "CONTACT RESEARCH"),
        ("website_analysis", "WEBSITE ANALYSIS"),
        ("competitive_context", "COMPETITIVE INTELLIGENCE"),
        ("discovery_questions", "DISCOVERY QUESTIONS"),
        ("objection_handling", "OBJECTION HANDLING")
    ]

    for key, title in sections:
        if key in agent_results:
            brief += f"""
## {title}

{agent_results[key]}

---

"""

    brief += f"""
## CALL PREPARATION CHECKLIST

- [ ] Review company background and recent news
- [ ] Understand contact's role and priorities
- [ ] Note current website issues and opportunities
- [ ] Prepare discovery questions with context
- [ ] Review objection responses
- [ ] Have pricing packages ready to discuss
- [ ] Confirm calendar availability for follow-up

---

*Prepared by Winnicki Digital AI System*
*Contact: shannon@winnickidigital.com*
"""

    return brief


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")

    # Test Slack
    result = notify_slack("Test message from Winnicki Digital system")
    print(f"Slack test: {result}")

    # Test local file save
    test_content = "# Test Document\n\nThis is a test."
    result = save_to_local(test_content, "test.md")
    print(f"Local save test: {result}")

    print("\nUtilities loaded successfully!")
