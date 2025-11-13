"""
Phase 1: Pre-Call Intelligence System
Six research agents that analyze company, contact, website, and competition
"""

from agent_framework import Agent, ParallelAgent, SequentialAgent, google_search, web_fetch
from typing import Dict, Any


# Agent 1: Company Intelligence
company_intelligence_agent = Agent(
    name="CompanyIntelligenceAgent",
    output_key="company_profile",
    instructions="""
You are a company research specialist. Analyze the provided company information and generate a comprehensive company profile.

Your tasks:
1. Identify the company's industry and market position
2. Determine company size indicators (if available from website/context)
3. Note any recent news, announcements, or activities mentioned
4. Assess their business model and target market
5. Identify key differentiators or unique selling points

Format your output as markdown with these sections:
## Company Overview
## Industry & Market Position
## Recent Activity & News
## Key Facts & Insights

Use the information provided in the context. Make educated inferences based on available data.
Be specific and actionable. Focus on insights that would help in a sales conversation.
"""
)


# Agent 2: Contact Research
contact_research_agent = Agent(
    name="ContactResearchAgent",
    output_key="contact_profile",
    instructions="""
You are a contact research specialist. Analyze the contact person and infer their priorities.

Your tasks:
1. Identify the person's role and seniority level
2. Based on their role, infer likely priorities:
   - CEO/Founder: Business growth, ROI, competitive advantage
   - Marketing Director/CMO: Lead generation, brand presence, conversion
   - CTO/Technical: Performance, integrations, scalability
   - Operations: Efficiency, automation, ease of management
3. Note any background information available
4. Identify potential pain points based on role

Format your output as markdown:
## Contact Information
- Name & Role
- Inferred Seniority

## Likely Priorities
(Based on role and industry)

## Potential Pain Points
(What keeps them up at night)

## Conversation Approach
(How to position our services)
"""
)


# Agent 3: Website Analyzer
website_analyzer_agent = Agent(
    name="WebsiteAnalyzerAgent",
    output_key="website_analysis",
    instructions="""
You are a website analysis specialist. Evaluate the prospect's current website and identify opportunities.

Your tasks:
1. Assess current website state (if URL provided, analyze structure and content)
2. Identify technical issues or limitations
3. Note missing features or opportunities:
   - Missing CTAs (calls-to-action)
   - Poor mobile experience indicators
   - Unclear messaging
   - Missing modern features (chat, forms, etc.)
   - SEO concerns
4. List specific improvement opportunities

Format your output as markdown:
## Current Website State
(Overall impression, platform if identifiable, design era)

## Issues Identified
- Technical problems
- UX/design issues
- Content gaps

## Improvement Opportunities
(Specific features or changes that would add value)

## Competitive Gaps
(What they're missing that competitors likely have)

If no website URL is provided, note that and provide general questions to ask about their current web presence.
"""
)


# Agent 4: Competitive Context
competitive_context_agent = Agent(
    name="CompetitiveContextAgent",
    output_key="competitive_context",
    instructions="""
You are a competitive intelligence specialist. Research the competitive landscape for this prospect.

Your tasks:
1. Identify likely competitors in their industry/market
2. Note common features or capabilities competitors typically have
3. Identify industry-standard platforms or technologies
4. Find opportunities for differentiation
5. Note competitive advantages they could gain with a strong web presence

Format your output as markdown:
## Competitive Landscape
(Who are their likely competitors)

## Industry Standards
(Common features, platforms, or capabilities in this industry)

## Opportunities to Differentiate
(How a great website could give them competitive advantage)

## Risks of Inaction
(What they lose by not improving their web presence)

Base your analysis on the industry and company information provided. Make informed inferences.
"""
)


# Agent 5: Requirements Gatherer
requirements_gatherer_agent = Agent(
    name="RequirementsGathererAgent",
    output_key="discovery_questions",
    instructions="""
You are a discovery specialist. Based on all previous research, generate targeted discovery questions.

Review the outputs from:
- company_profile
- contact_profile
- website_analysis
- competitive_context

Your tasks:
1. Generate 5-7 specific, targeted discovery questions
2. Each question should reference specific findings from the research
3. Focus areas:
   - Project scope and objectives
   - Number of pages and content structure
   - Content readiness (do they have copy, images, etc.)
   - Required integrations (CRM, payment, booking, etc.)
   - Timeline and urgency
   - Budget parameters
   - Success metrics

Format your output as a numbered list:
## Discovery Questions for [Company Name]

1. [Question with context from research]
   *Why we're asking: [Strategic reason]*

2. [Next question]
   *Why we're asking: [Strategic reason]*

Make questions conversational and consultative, not interrogative.
Reference specific findings to show you've done your homework.
"""
)


# Agent 6: Objection Anticipator
objection_anticipator_agent = Agent(
    name="ObjectionAnticipatorAgent",
    output_key="objection_handling",
    instructions="""
You are an objection handling specialist. Anticipate likely objections and prepare responses.

Review all previous outputs:
- company_profile
- contact_profile
- website_analysis
- competitive_context
- discovery_questions

Your tasks:
1. Anticipate 4-6 likely objections based on:
   - Industry (e.g., "We're in a commoditized industry")
   - Company size (e.g., budget concerns)
   - Current website state (e.g., "Our current site works fine")
   - Contact's role (e.g., technical concerns, ROI concerns)
2. Prepare strong responses with proof points

Common objection categories:
- Price/Budget ("Too expensive", "We can do it cheaper")
- DIY Options ("We can use Wix/Squarespace ourselves")
- Timeline ("We need it faster")
- Ownership ("Who owns the website?")
- Results ("How do we know it will work?")
- Urgency ("We're not ready yet")

Format your output as:
## Anticipated Objections & Responses

### Objection 1: [Likely objection]
**Your Response:**
[Prepared response with proof points, specific to their situation]

**Key Points to Emphasize:**
- [Point 1]
- [Point 2]

[Repeat for each objection]

Make responses empathetic but confident. Use their specific context to personalize responses.
"""
)


# Build the workflow structure
# Parallel research team (agents 1-4 run simultaneously)
research_team = ParallelAgent(
    name="ResearchTeam",
    sub_agents=[
        company_intelligence_agent,
        contact_research_agent,
        website_analyzer_agent,
        competitive_context_agent
    ]
)

# Sequential workflow: research → questions → objections
phase1_system = SequentialAgent(
    name="Phase1CallPrepSystem",
    sub_agents=[
        research_team,
        requirements_gatherer_agent,
        objection_anticipator_agent
    ]
)


def run_phase1_research(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for Phase 1 research
    Takes lead data and returns complete call prep brief
    """
    # Format lead context
    context = f"""
NEW LEAD SUBMISSION

Contact Information:
- Name: {lead_data.get('first_name', '')} {lead_data.get('last_name', '')}
- Email: {lead_data.get('email', '')}
- Phone: {lead_data.get('phone', 'Not provided')}

Company Information:
- Company: {lead_data.get('company_name', 'Not provided')}
- Website: {lead_data.get('website', 'Not provided')}

Lead Details:
- Interested In: {lead_data.get('interested_in', 'Not specified')}
- Pain Points: {lead_data.get('pain_points', 'Not specified')}
- Referred By: {lead_data.get('referred_by', 'Not specified')}

---

Conduct comprehensive pre-call research and generate actionable call prep brief.
"""

    # Run the agent system
    results = phase1_system.run(context)

    return results


if __name__ == "__main__":
    # Test the system
    test_lead = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@testcorp.com",
        "phone": "555-0123",
        "company_name": "Test Corp",
        "website": "https://example.com",
        "interested_in": "Website Redesign",
        "pain_points": "Outdated website, not mobile friendly"
    }

    print("Running Phase 1 Research System...")
    results = run_phase1_research(test_lead)

    print("\n" + "="*80)
    print("CALL PREP BRIEF")
    print("="*80)

    for key, value in results.items():
        if key not in ['agent_name', 'success']:
            print(f"\n{key.upper()}:")
            print("-" * 80)
            print(value)
