#!/bin/bash
# Setup script for Tipster IA Bot
# Run this script to initialize the project

set -e  # Exit on error

echo "=========================================="
echo "🤖 TIPSTER IA BOT - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials before running the bot!"
    echo "   Required variables:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_ADMIN_ID"
    echo "   - ANTHROPIC_API_KEY"
    echo ""
else
    echo "⚠️  .env file already exists. Skipping..."
    echo ""
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"
echo ""

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
    
    echo "📝 Creating initial commit..."
    git add .
    git commit -m "chore: initial project setup - Día 1 Sprint"
    echo "✅ Initial commit created"
    echo ""
else
    echo "⚠️  Git repository already initialized. Skipping..."
    echo ""
fi

echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: python main.py"
echo ""
echo "📚 Documentation: See README.md"
echo ""