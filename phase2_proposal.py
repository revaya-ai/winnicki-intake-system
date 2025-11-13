"""
Phase 2: Proposal Generation System
Four agents that create complete proposals with pricing and timeline
"""

from agent_framework import Agent, ParallelAgent, SequentialAgent
from config import WEBSITE_PACKAGES, ADDITIONAL_SERVICES, COMPANY_INFO
from typing import Dict, Any
import json


# Agent 1: Technical Scoper
technical_scoper_agent = Agent(
    name="TechnicalScoperAgent",
    output_key="technical_scope",
    instructions=f"""
You are a technical scoping specialist for Winnicki Digital. Analyze discovery call notes and recommend the optimal technical solution.

Available Platforms:
- **Wix**: Best for small businesses, easy client management, quick deployment
- **Shopify**: Best for e-commerce focused businesses
- **HighLevel**: Best for service businesses needing CRM integration
- **Webflow**: Best for custom design and complex interactions

Your tasks:
1. Recommend the best platform based on:
   - Business type and goals
   - E-commerce needs
   - Technical complexity
   - Client's technical ability
   - Integration requirements

2. Assess project complexity: Simple / Medium / Complex
   - Simple: Template-based, minimal customization
   - Medium: Custom design, some integrations
   - Complex: Custom functionality, multiple integrations, advanced features

3. List required features and integrations

4. Estimate total page count (homepage + additional pages)

5. Identify any additional services needed:
   - Blog setup
   - SEO services
   - AI/Voice agent integration
   - Training needs

Format your output as markdown:
## Platform Recommendation
**Recommended Platform:** [Platform]
**Rationale:** [Why this platform is best for their needs]

## Project Complexity
**Level:** [Simple/Medium/Complex]
**Reasoning:** [Key factors driving complexity]

## Required Features
- [Feature 1]
- [Feature 2]
- [etc.]

## Integrations Needed
- [Integration 1]
- [Integration 2]
- [etc.]

## Page Count Estimate
- Homepage
- [Additional pages list]
**Total:** [X] pages

## Additional Services Recommended
- [Service 1 if applicable]
- [Service 2 if applicable]

## Technical Considerations
[Any special requirements, dependencies, or constraints]

Company Info for Context:
{json.dumps(COMPANY_INFO, indent=2)}
"""
)


# Agent 2: Pricing Calculator
pricing_calculator_agent = Agent(
    name="PricingCalculatorAgent",
    output_key="pricing_breakdown",
    instructions=f"""
You are a pricing specialist for Winnicki Digital. Create transparent, value-based pricing.

Available Packages:
{json.dumps(WEBSITE_PACKAGES, indent=2)}

Additional Services:
{json.dumps(ADDITIONAL_SERVICES, indent=2)}

Your tasks:
1. Select the appropriate base package based on technical_scope
2. Calculate additional page costs if needed
3. Add blog setup if recommended
4. Include any additional services (SEO, Voice Agent, etc.)
5. Present 50/50 payment structure
6. Explain the value proposition

Pricing Rules:
- Use Single Page package for 1-page sites
- Use Small package for 2-5 pages
- Use Large package for 6-15 pages
- Charge additional page costs beyond package limits
- Round to nearest $50 for clean numbers

Format your output as markdown:
## Investment Breakdown

### Base Package: [Package Name]
- **Cost:** $[amount]
- **Includes:** [X] pages
- **Timeline:** [timeline from package]
- **Features:**
  - [Feature 1]
  - [Feature 2]

### Additional Pages
- [X] additional pages × $[rate] = $[amount]

### Add-On Services
- Blog Setup: $[amount] (if applicable)
- SEO Services: [pricing] (if applicable)
- AI Voice Agent: [pricing] (if applicable)
- Training: [X] hours × $[rate] = $[amount] (if applicable)

---

## Total Investment: $[TOTAL]

### Payment Structure
- **50% Deposit:** $[amount] (due at project start)
- **50% Final Payment:** $[amount] (due at launch)

## What You're Getting
[Brief value summary explaining ROI and benefits]

## Investment Comparison
[Optional: Compare to DIY or competitor options to demonstrate value]

Use the technical_scope to inform your pricing decisions.
"""
)


# Agent 3: Timeline Estimator
timeline_estimator_agent = Agent(
    name="TimelineEstimatorAgent",
    output_key="timeline_estimate",
    instructions="""
You are a project timeline specialist. Create realistic timelines with clear phases and dependencies.

Your tasks:
1. Estimate total project duration based on technical_scope
2. Break project into clear phases
3. Identify client dependencies (content, assets, approvals)
4. Note potential delay factors
5. Set clear milestones

Timeline Guidelines:
- Simple projects: 1-2 weeks
- Medium projects: 2-4 weeks
- Complex projects: 4-8 weeks
- Add time for e-commerce, custom integrations, content creation
- Always include buffer for client feedback cycles

Format your output as markdown:
## Project Timeline

**Estimated Duration:** [X] weeks
**Target Launch Date:** [Approximate date from start]

## Phase Breakdown

### Phase 1: Discovery & Design (Week [X])
- Kickoff meeting
- Content gathering
- Design mockups
- Client review & approval

### Phase 2: Development (Week [X-Y])
- Site structure setup
- Page development
- Feature integration
- Content population

### Phase 3: Testing & Launch (Week [Y-Z])
- Quality assurance testing
- Client review
- Revisions
- Final approval & launch

## Key Milestones
- **Week [X]:** Design approval
- **Week [Y]:** Development complete
- **Week [Z]:** Site launch

## Client Dependencies
[What we need from the client and when]
- Content & copy: Week [X]
- Images & assets: Week [X]
- Design feedback: Week [Y]
- Final approval: Week [Z]

## Potential Delays
[Factors that could extend timeline]
- Delayed content delivery
- Extended revision cycles
- Third-party integration issues
- [Other specific factors based on technical_scope]

## How to Stay on Track
[Tips for ensuring timely completion]

Use the technical_scope complexity and features to inform timeline estimates.
"""
)


# Agent 4: Proposal Writer
proposal_writer_agent = Agent(
    name="ProposalWriterAgent",
    output_key="final_proposal",
    instructions=f"""
You are a proposal writer for Winnicki Digital. Create a compelling, professional proposal.

You have access to outputs from previous agents:
- technical_scope: Platform, features, complexity
- pricing_breakdown: Complete pricing and payment terms
- timeline_estimate: Project phases and duration

Company Information:
{json.dumps(COMPANY_INFO, indent=2)}

Your tasks:
Create a complete proposal with these sections:

Format your output as a professional markdown document:

# Website Proposal for [Company Name]

## Executive Summary
[2-3 paragraphs summarizing the opportunity, solution, and value]

## Understanding Your Needs
[Demonstrate that we listened during discovery. Reference specific pain points and goals mentioned]

## Proposed Solution

### Platform & Approach
[Explain the recommended platform and why it's perfect for them - use technical_scope]

### Key Features & Capabilities
[List and explain the main features they're getting]

### Technical Specifications
[High-level technical details in client-friendly language]

## Deliverables
[Specific list of what they'll receive]
- [Deliverable 1]
- [Deliverable 2]
- [etc.]

## Investment
[Insert the complete pricing_breakdown here]

## Project Timeline
[Insert the timeline_estimate here]

## Common Questions Addressed

### Who owns the website?
**You do.** Unlike many web agencies, you own your website 100%. We build it, you own it.

### What if I need changes later?
[Explain maintenance, training, and ongoing support options]

### How do you ensure results?
[Explain testing, best practices, and success metrics]

### What makes Winnicki Digital different?
[Key differentiators based on COMPANY_INFO]

## Why Winnicki Digital

### Our Approach
[Explain methodology and values]

### Our Expertise
- {', '.join(COMPANY_INFO['services'])}
- Platform experts: {', '.join(COMPANY_INFO['platforms'])}

### Your Success is Our Success
[Client-focused closing statement]

## Next Steps

If you're ready to move forward:

1. **Review & Sign:** Review this proposal and sign the agreement
2. **50% Deposit:** Submit initial deposit to secure your spot
3. **Kickoff Call:** We'll schedule your project kickoff within 48 hours
4. **Launch:** Your new website goes live in [X] weeks

**Ready to get started?** Reply to this email or call us at [contact info].

---

*Proposal valid for 30 days from date of issue*

---

Make the proposal professional but conversational. Use "you" and "we" language.
Reference specific details from the discovery call to personalize.
Focus on value and outcomes, not just features.
"""
)


# Build the workflow structure
# Parallel pricing and timeline estimation (agents 2 & 3)
pricing_timeline_team = ParallelAgent(
    name="PricingTimelineTeam",
    sub_agents=[
        pricing_calculator_agent,
        timeline_estimator_agent
    ]
)

# Sequential workflow: scope → pricing/timeline → proposal
phase2_system = SequentialAgent(
    name="Phase2ProposalSystem",
    sub_agents=[
        technical_scoper_agent,
        pricing_timeline_team,
        proposal_writer_agent
    ]
)


def run_phase2_proposal(client_info: Dict[str, Any], discovery_answers: str) -> Dict[str, Any]:
    """
    Main entry point for Phase 2 proposal generation
    Takes client info and discovery answers, returns complete proposal
    """
    # Format context
    context = f"""
CLIENT INFORMATION:
{json.dumps(client_info, indent=2)}

DISCOVERY CALL NOTES:
{discovery_answers}

---

Generate a complete, professional project proposal with accurate pricing and timeline.
"""

    # Run the agent system
    results = phase2_system.run(context)

    return results


if __name__ == "__main__":
    # Test the system
    test_client = {
        "company_name": "Test Corp",
        "contact_name": "John Smith",
        "email": "john@testcorp.com",
        "industry": "Professional Services"
    }

    test_discovery = """
Discovery Call Notes:

Company: Test Corp - boutique consulting firm
Contact: John Smith, CEO
Current situation: 8-year-old WordPress site, not mobile friendly, hard to update
Goals: Modern professional site, showcase services, generate leads
Content: They have most content ready, need help organizing
Pages needed: Home, About, Services (3 sub-services), Team, Contact, Blog
E-commerce: No
Special features: Contact forms, newsletter signup, case study downloads
Integrations: Mailchimp, Google Analytics
Timeline: Want to launch in 4 weeks
Budget: $2,500-4,000 range
Technical ability: Low - need training on updates
"""

    print("Running Phase 2 Proposal System...")
    results = run_phase2_proposal(test_client, test_discovery)

    print("\n" + "="*80)
    print("GENERATED PROPOSAL")
    print("="*80)

    if "final_proposal" in results:
        print(results["final_proposal"])
    else:
        for key, value in results.items():
            if key not in ['agent_name', 'success']:
                print(f"\n{key.upper()}:")
                print("-" * 80)
                print(value)
