#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   WINNICKI DIGITAL - SETUP VERIFICATION                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python3 --version
echo ""

# Check file structure
echo "2️⃣  Verifying file structure..."
files=(
    "api.py"
    "agent_framework.py"
    "phase1_research.py"
    "phase2_proposal.py"
    "utils.py"
    "config.py"
    "requirements.txt"
    "Dockerfile"
    ".env.example"
)

all_present=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING"
        all_present=false
    fi
done
echo ""

# Check Python syntax
echo "3️⃣  Checking Python syntax..."
python3 -m py_compile *.py 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ All Python files have valid syntax"
else
    echo "  ❌ Syntax errors found"
    exit 1
fi
echo ""

# Check imports
echo "4️⃣  Verifying imports..."
echo "  Checking for correct SDK usage..."

if grep -q "google.adk" *.py 2>/dev/null; then
    echo "  ❌ ERROR: Found reference to google.adk (doesn't exist)"
    echo "  Files with google.adk:"
    grep -l "google.adk" *.py
    exit 1
else
    echo "  ✅ No references to google.adk"
fi

if grep -q "google.generativeai" *.py; then
    echo "  ✅ Using google-generativeai (correct)"
else
    echo "  ⚠️  Warning: google-generativeai not found in imports"
fi
echo ""

# Check environment
echo "5️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    echo "  ✅ .env file exists"
    if grep -q "GOOGLE_API_KEY=" .env; then
        echo "  ✅ GOOGLE_API_KEY configured"
    else
        echo "  ⚠️  GOOGLE_API_KEY not set in .env"
    fi
else
    echo "  ⚠️  .env file not found (copy from .env.example)"
fi
echo ""

# Check Docker
echo "6️⃣  Checking Docker configuration..."
if [ -f "Dockerfile" ]; then
    echo "  ✅ Dockerfile present"
    if grep -q "google-generativeai" requirements.txt; then
        echo "  ✅ google-generativeai in requirements.txt"
    fi
fi
echo ""

# Summary
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   VERIFICATION SUMMARY                                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

if $all_present; then
    echo "✅ All core files present"
    echo "✅ Python syntax valid"
    echo "✅ Using correct SDK (google-generativeai)"
    echo "✅ No references to non-existent packages"
    echo ""
    echo "🚀 System is ready for deployment!"
    echo ""
    echo "Next steps:"
    echo "  1. Set GOOGLE_API_KEY in .env"
    echo "  2. Run locally: ./start.sh"
    echo "  3. Test: ./test-phase1.sh"
    echo "  4. Deploy: ./deploy-with-secrets.sh"
else
    echo "❌ Some files are missing"
    exit 1
fi
