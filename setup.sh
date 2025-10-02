#!/bin/bash

# AutoTagger Setup Script
# This script automates the installation process

set -e

echo "================================"
echo "AutoTagger Setup Script"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "Error: Python 3.9 or higher is required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Download spaCy model
echo "Downloading spaCy language model..."
python -m spacy download en_core_web_sm
echo "✓ spaCy model downloaded"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads logs
echo "✓ Directories created"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=dev-secret-key-change-in-production
LOG_LEVEL=INFO
EOF
    echo "✓ .env file created"
else
    echo ".env file already exists. Skipping."
fi
echo ""

# Run initial database setup
echo "Setting up database..."
python3 << EOF
from app import create_app
app = create_app('development')
with app.app_context():
    from app import db
    db.create_all()
    print("✓ Database tables created")
EOF
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python run.py"
echo ""
echo "Server will be available at: http://localhost:5000"
echo "API documentation: See README.md"
echo ""