#!/bin/bash

# Test Phase 2: Proposal Generation

echo "🧪 Testing Phase 2: Proposal Generation"
echo "========================================"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Server is not running!"
    echo "Start the server with: python api.py"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Test data
echo "📄 Generating test proposal..."
echo ""

curl -X POST http://localhost:8000/generate-proposal \
  -H "Content-Type: application/json" \
  -d '{
    "client_info": {
      "company_name": "Test Corp",
      "contact_name": "John Smith",
      "email": "john@testcorp.com",
      "industry": "Professional Services"
    },
    "discovery_answers": "Company is a boutique consulting firm. Need professional website with 8 pages: Home, About, Services, Team, Case Studies, Blog, Resources, Contact. Want e-commerce for booking consultations. Need blog for thought leadership. Mailchimp integration required. Timeline: 4-6 weeks. Budget: $3000-4000 range. Low technical ability, need training."
  }' | python -m json.tool

echo ""
echo "✅ Phase 2 test complete!"
echo ""
echo "Check:"
echo "  - Email sent to shannon@winnickidigital.com"
echo "  - Slack notification"
echo "  - Proposal saved in output/ folder or Google Drive"
echo ""
