#!/bin/bash

# Quick start script for Winnicki Digital Intake System

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   WINNICKI DIGITAL - QUICK START                         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found"
    echo ""
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "✅ Created .env file"
    echo ""
    echo "📝 Please edit .env and add your API keys:"
    echo "   - GOOGLE_API_KEY (required)"
    echo "   - SENDGRID_API_KEY (for email)"
    echo "   - SLACK_WEBHOOK_URL (for notifications)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create output directory
mkdir -p output

echo "🚀 Starting Winnicki Digital Intake System..."
echo ""
echo "   API will be available at: http://localhost:8000"
echo "   Documentation: http://localhost:8000/docs"
echo "   Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server
python api.py
