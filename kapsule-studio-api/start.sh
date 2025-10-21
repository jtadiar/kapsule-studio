#!/bin/bash

# Kapsule Studio API Startup Script

echo "🎬 Starting Kapsule Studio API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your configuration before continuing."
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg is not installed!"
    echo "Please install FFmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    exit 1
fi

# Check GCP authentication
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth application-default print-access-token &> /dev/null; then
    echo "⚠️  Warning: Not authenticated with Google Cloud!"
    echo "Please run: gcloud auth application-default login"
    exit 1
fi

echo "✅ All checks passed!"
echo ""
echo "🚀 Starting server on port 8000..."
echo "📖 API docs available at: http://localhost:8000/docs"
echo ""

# Start the server
uvicorn main:app --reload --port 8000

