"""Winnicki Digital - Multi-Agent Intake System"""

import os
import json
from typing import Dict, Any, List
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup
from config import COMPANY_INFO, WEBSITE_PACKAGES, ADDITIONAL_SERVICES

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

class IntakeAgentSystem:
    """Two-phase intake system: Pre-call intelligence and Post-call proposal"""

    def __init__(self):
        self.model = "claude-sonnet-4-5-20250929"
        self.max_tokens = 4096

    def _call_claude(self, system_prompt: str, user_message: str) -> str:
        """Helper method to call Claude API"""
        try:
            message = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error calling Claude API: {str(e)}"

    def _scrape_website(self, url: str) -> Dict[str, Any]:
        """Scrape basic information from a website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic info
            title = soup.find('title')
            title_text = title.get_text() if title else "No title found"

            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content') if meta_desc else "No description found"

            # Extract headings
            headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]

            # Extract body text (first 2000 chars)
            body_text = soup.get_text(separator=' ', strip=True)[:2000]

            return {
                "url": url,
                "title": title_text,
                "description": description,
                "headings": headings,
                "body_preview": body_text,
                "success": True
            }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

    # ============================================================================
    # PHASE 1: PRE-CALL INTELLIGENCE
    # ============================================================================

    def phase1_research_agent(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent 1: Research company/person/website"""
        print("🔍 Phase 1 - Agent 1: Researching company...")

        # Scrape website if provided
        website_data = {}
        if lead_data.get("website"):
            website_data = self._scrape_website(lead_data["website"])

        system_prompt = """You are a business research specialist for Winnicki Digital.
        Analyze the provided information about a prospect and create a comprehensive research summary.
        Focus on: business type, industry, current web presence, potential needs, and business size."""

        user_message = f"""Research this lead:

Lead Information:
- Name: {lead_data.get('name', 'Unknown')}
- Email: {lead_data.get('email', 'Unknown')}
- Phone: {lead_data.get('phone', 'Unknown')}
- Company: {lead_data.get('company', 'Unknown')}
- Website: {lead_data.get('website', 'Not provided')}

Website Data:
{json.dumps(website_data, indent=2)}

Additional Info:
{lead_data.get('additional_info', 'None provided')}

Create a research summary covering:
1. Business Overview (industry, size, type)
2. Current Web Presence Analysis
3. Potential Needs/Pain Points
4. Key Insights for Sales Call
"""

        research_summary = self._call_claude(system_prompt, user_message)

        return {
            "lead_data": lead_data,
            "website_data": website_data,
            "research_summary": research_summary
        }

    def phase1_discovery_agent(self, research_data: Dict[str, Any]) -> str:
        """Agent 2: Generate discovery questions"""
        print("❓ Phase 1 - Agent 2: Generating discovery questions...")

        system_prompt = f"""You are a sales consultant for Winnicki Digital specializing in:
        {', '.join(COMPANY_INFO['services'])}

        Generate targeted discovery questions based on the research to uncover:
        - Current pain points with their website/digital presence
        - Business goals and growth plans
        - Budget considerations
        - Timeline expectations
        - Technical requirements
        """

        user_message = f"""Based on this research, generate 10-12 discovery questions:

{research_data['research_summary']}

Format the questions in categories:
1. Current Situation (2-3 questions)
2. Goals & Objectives (2-3 questions)
3. Technical Requirements (2-3 questions)
4. Budget & Timeline (2-3 questions)
"""

        return self._call_claude(system_prompt, user_message)

    def phase1_objection_handler(self, research_data: Dict[str, Any]) -> str:
        """Agent 3: Prepare objection handling strategies"""
        print("🛡️ Phase 1 - Agent 3: Preparing objection handlers...")

        system_prompt = f"""You are a sales objection handling expert for Winnicki Digital.

        Our services: {', '.join(COMPANY_INFO['services'])}
        Our platforms: {', '.join(COMPANY_INFO['platforms'])}

        Prepare responses to common objections tailored to this specific prospect."""

        user_message = f"""Based on this research, prepare objection handlers:

{research_data['research_summary']}

Create responses for these common objections:
1. "Your prices seem high" / Budget concerns
2. "I can use a DIY website builder" / Wix/Squarespace
3. "I need to think about it" / Delaying decision
4. "I already have a website" / Current solution satisfaction
5. Any specific objections based on the research

For each objection:
- Empathize
- Provide value-focused response
- Ask a follow-up question
"""

        return self._call_claude(system_prompt, user_message)

    def phase1_generate_brief(self, lead_data: Dict[str, Any], research_summary: str,
                             discovery_questions: str, objection_handlers: str) -> str:
        """Agent 4: Compile call prep brief"""
        print("📋 Phase 1 - Agent 4: Generating call prep brief...")

        system_prompt = """You are creating a comprehensive pre-call brief for a sales executive.
        Organize all information into a clear, actionable format that can be quickly reviewed before the call."""

        user_message = f"""Create a professional call prep brief:

LEAD INFORMATION:
{json.dumps(lead_data, indent=2)}

RESEARCH SUMMARY:
{research_summary}

DISCOVERY QUESTIONS:
{discovery_questions}

OBJECTION HANDLERS:
{objection_handlers}

Format the brief with these sections:
# Call Prep Brief - {lead_data.get('company', lead_data.get('name', 'Prospect'))}

## 1. Quick Overview
[2-3 sentence summary of who they are and why they're a good fit]

## 2. Research Highlights
[Key insights from research]

## 3. Recommended Talking Points
[3-5 key points to mention]

## 4. Discovery Questions
[Organized questions from above]

## 5. Objection Handling Guide
[Prepared responses]

## 6. Pricing Guidance
[Suggested packages based on their needs]

## 7. Next Steps
[Recommended call-to-action]
"""

        return self._call_claude(system_prompt, user_message)

    def run_phase1(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Phase 1: Pre-Call Intelligence"""
        print("\n" + "="*60)
        print("PHASE 1: PRE-CALL INTELLIGENCE")
        print("="*60 + "\n")

        # Agent 1: Research
        research_data = self.phase1_research_agent(lead_data)

        # Agent 2: Discovery Questions
        discovery_questions = self.phase1_discovery_agent(research_data)

        # Agent 3: Objection Handling
        objection_handlers = self.phase1_objection_handler(research_data)

        # Agent 4: Generate Brief
        call_prep_brief = self.phase1_generate_brief(
            lead_data,
            research_data['research_summary'],
            discovery_questions,
            objection_handlers
        )

        print("\n✅ Phase 1 Complete: Call prep brief generated")

        return {
            "lead_data": lead_data,
            "research_data": research_data,
            "discovery_questions": discovery_questions,
            "objection_handlers": objection_handlers,
            "call_prep_brief": call_prep_brief
        }

    # ============================================================================
    # PHASE 2: POST-CALL PROPOSAL
    # ============================================================================

    def phase2_requirements_processor(self, call_notes: Dict[str, Any]) -> Dict[str, Any]:
        """Agent 1: Process call notes and extract requirements"""
        print("📝 Phase 2 - Agent 1: Processing requirements...")

        system_prompt = """You are a requirements analyst for Winnicki Digital.
        Extract and structure key requirements from sales call notes."""

        user_message = f"""Analyze these call notes and extract structured requirements:

{json.dumps(call_notes, indent=2)}

Extract and structure:
1. Project Type (website, SEO, AI automation, voice agent, or combination)
2. Specific Requirements
3. Must-have Features
4. Nice-to-have Features
5. Budget Range (if mentioned)
6. Timeline Expectations
7. Technical Constraints
8. Decision-making Process

Return a structured summary.
"""

        requirements = self._call_claude(system_prompt, user_message)

        return {
            "call_notes": call_notes,
            "structured_requirements": requirements
        }

    def phase2_technical_scoper(self, requirements_data: Dict[str, Any]) -> str:
        """Agent 2: Determine technical scope"""
        print("🔧 Phase 2 - Agent 2: Scoping technical requirements...")

        system_prompt = f"""You are a technical architect for Winnicki Digital.

        Available platforms: {', '.join(COMPANY_INFO['platforms'])}
        Services: {', '.join(COMPANY_INFO['services'])}

        Determine the technical scope and recommended approach."""

        user_message = f"""Based on these requirements, define technical scope:

{requirements_data['structured_requirements']}

Provide:
1. Recommended Platform (Wix/Shopify/HighLevel/Webflow)
2. Technical Approach
3. Required Features/Integrations
4. Page Count Estimate
5. Complexity Level (Simple/Moderate/Complex)
6. Any Additional Services Needed (SEO, AI, Voice Agent)
"""

        return self._call_claude(system_prompt, user_message)

    def phase2_pricing_calculator(self, technical_scope: str, requirements_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent 3: Calculate pricing"""
        print("💰 Phase 2 - Agent 3: Calculating pricing...")

        system_prompt = f"""You are a pricing specialist for Winnicki Digital.

PRICING STRUCTURE:
{json.dumps(WEBSITE_PACKAGES, indent=2)}

ADDITIONAL SERVICES:
{json.dumps(ADDITIONAL_SERVICES, indent=2)}

Calculate accurate pricing based on requirements and technical scope."""

        user_message = f"""Calculate pricing for this project:

TECHNICAL SCOPE:
{technical_scope}

REQUIREMENTS:
{requirements_data['structured_requirements']}

Provide:
1. Recommended Package (single_page, small, or large)
2. Base Price
3. Additional Pages (if any) with cost
4. Add-ons (blog, training, etc.) with costs
5. Additional Services (SEO, AI, Voice Agent) with costs
6. Total Estimated Investment
7. Payment Terms Suggestion

Format as a detailed breakdown.
"""

        pricing_breakdown = self._call_claude(system_prompt, user_message)

        return {
            "pricing_breakdown": pricing_breakdown
        }

    def phase2_timeline_estimator(self, technical_scope: str, requirements_data: Dict[str, Any]) -> str:
        """Agent 4: Estimate timeline (runs parallel with pricing)"""
        print("⏱️ Phase 2 - Agent 4: Estimating timeline...")

        system_prompt = f"""You are a project manager for Winnicki Digital.

STANDARD TIMELINES:
{json.dumps({k: v['timeline'] for k, v in WEBSITE_PACKAGES.items()}, indent=2)}

ADDITIONAL SERVICES:
{json.dumps({k: {'name': v['name'], 'timeline': v['timeline']} for k, v in ADDITIONAL_SERVICES.items()}, indent=2)}

Estimate realistic project timelines."""

        user_message = f"""Estimate timeline for this project:

TECHNICAL SCOPE:
{technical_scope}

REQUIREMENTS:
{requirements_data['structured_requirements']}

Provide:
1. Overall Timeline Estimate
2. Project Phases with durations:
   - Discovery & Planning
   - Design & Development
   - Content Creation
   - Testing & Revisions
   - Launch
3. Key Milestones
4. Factors that could affect timeline
5. Client responsibilities and timing impact
"""

        return self._call_claude(system_prompt, user_message)

    def phase2_proposal_writer(self, requirements_data: Dict[str, Any], technical_scope: str,
                               pricing_data: Dict[str, Any], timeline: str) -> str:
        """Agent 5: Generate professional proposal"""
        print("📄 Phase 2 - Agent 5: Writing proposal...")

        system_prompt = f"""You are a professional proposal writer for Winnicki Digital.

COMPANY INFO:
{json.dumps(COMPANY_INFO, indent=2)}

Create compelling, professional proposals that win business."""

        user_message = f"""Create a professional proposal:

CLIENT REQUIREMENTS:
{requirements_data['structured_requirements']}

TECHNICAL SCOPE:
{technical_scope}

PRICING:
{pricing_data['pricing_breakdown']}

TIMELINE:
{timeline}

CALL NOTES:
{json.dumps(requirements_data['call_notes'], indent=2)}

Create a complete proposal with these sections:

# Project Proposal for [Client Name]

## Executive Summary
[Compelling 2-3 paragraph overview]

## Understanding Your Needs
[Show we understood their requirements and pain points]

## Our Recommended Solution
[Technical approach and why it's the best fit]

## Scope of Work
[Detailed deliverables]

## Project Timeline
[Timeline with milestones]

## Investment
[Pricing breakdown]

## Why Winnicki Digital
[Our value proposition]

## Next Steps
[Clear call to action]

## Terms & Conditions
[Standard terms]

Make it professional, persuasive, and personalized to their specific needs.
Use the client's name and company from the call notes.
"""

        return self._call_claude(system_prompt, user_message)

    def run_phase2(self, call_notes: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Phase 2: Post-Call Proposal"""
        print("\n" + "="*60)
        print("PHASE 2: POST-CALL PROPOSAL GENERATION")
        print("="*60 + "\n")

        # Agent 1: Process Requirements
        requirements_data = self.phase2_requirements_processor(call_notes)

        # Agent 2: Technical Scoping
        technical_scope = self.phase2_technical_scoper(requirements_data)

        # Agent 3 & 4: Pricing and Timeline (can run in parallel, but we'll run sequentially for simplicity)
        pricing_data = self.phase2_pricing_calculator(technical_scope, requirements_data)
        timeline = self.phase2_timeline_estimator(technical_scope, requirements_data)

        # Agent 5: Write Proposal
        proposal = self.phase2_proposal_writer(
            requirements_data,
            technical_scope,
            pricing_data,
            timeline
        )

        print("\n✅ Phase 2 Complete: Proposal generated")

        return {
            "call_notes": call_notes,
            "requirements": requirements_data['structured_requirements'],
            "technical_scope": technical_scope,
            "pricing": pricing_data['pricing_breakdown'],
            "timeline": timeline,
            "proposal": proposal
        }


# Example usage
if __name__ == "__main__":
    system = IntakeAgentSystem()

    # Test Phase 1
    test_lead = {
        "name": "John Smith",
        "email": "john@example.com",
        "company": "Acme Plumbing",
        "website": "https://example.com",
        "phone": "555-1234",
        "additional_info": "Looking for a new website, current one is outdated"
    }

    phase1_result = system.run_phase1(test_lead)
    print("\n" + "="*60)
    print("CALL PREP BRIEF:")
    print("="*60)
    print(phase1_result['call_prep_brief'])

    # Test Phase 2
    test_call_notes = {
        "client_name": "John Smith",
        "company": "Acme Plumbing",
        "project_type": "website",
        "notes": "Needs 5-page website with service pages, wants online booking, budget around $2000-3000, needs it within 3 weeks"
    }

    phase2_result = system.run_phase2(test_call_notes)
    print("\n" + "="*60)
    print("PROPOSAL:")
    print("="*60)
    print(phase2_result['proposal'])
