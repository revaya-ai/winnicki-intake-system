#!/bin/bash

# Test all endpoints

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   WINNICKI DIGITAL - COMPLETE SYSTEM TEST                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Server is not running!"
    echo "Start the server with: python api.py"
    exit 1
fi

# Test 1: Health check
echo "1️⃣  Testing Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s http://localhost:8000/health | python -m json.tool
echo ""
echo ""

# Test 2: Configuration
echo "2️⃣  Testing Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s http://localhost:8000/config | python -m json.tool
echo ""
echo ""

# Test 3: Integration test
echo "3️⃣  Testing Integrations (Email, Slack, Drive)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s -X POST http://localhost:8000/test-integrations | python -m json.tool
echo ""
echo ""

# Test 4: Phase 1
echo "4️⃣  Testing Phase 1: Pre-Call Intelligence"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./test-phase1.sh
echo ""

# Test 5: Phase 2
echo "5️⃣  Testing Phase 2: Proposal Generation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./test-phase2.sh
echo ""

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   ALL TESTS COMPLETE                                      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Review the output above to verify:"
echo "  ✓ Health check passed"
echo "  ✓ Configuration loaded"
echo "  ✓ Integrations working"
echo "  ✓ Phase 1 completed"
echo "  ✓ Phase 2 completed"
echo ""
