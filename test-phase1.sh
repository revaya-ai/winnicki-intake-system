#!/bin/bash

# Test Phase 1: Initial Lead Research

echo "🧪 Testing Phase 1: Pre-Call Intelligence"
echo "=========================================="
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
echo "📥 Submitting test lead..."
echo ""

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
    "pain_points": "Outdated website, not mobile friendly, no lead generation"
  }' | python -m json.tool

echo ""
echo "✅ Phase 1 test complete!"
echo ""
echo "Check:"
echo "  - Email sent to shannon@winnickidigital.com"
echo "  - Slack notification in #wd-leads"
echo "  - Document saved in output/ folder or Google Drive"
echo ""
