#!/bin/bash

# Supertonic FastAPI Server Startup Script

set -e

echo "Starting Supertonic TTS API Server..."

# Check if running in the py directory
if [ ! -f "api/src/main.py" ]; then
    echo "Error: Please run this script from the py directory"
    exit 1
fi

# Check if assets exist
if [ ! -d "../assets/onnx" ]; then
    echo "Warning: ONNX models not found in ../assets/onnx"
    echo "Please download models first:"
    echo "  git clone https://huggingface.co/Supertone/supertonic-2 ../assets"
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ONNX_DIR="${ONNX_DIR:-../assets/onnx}"
export VOICE_STYLES_DIR="${VOICE_STYLES_DIR:-../assets/voice_styles}"
export USE_GPU="${USE_GPU:-false}"
export PORT="${PORT:-8880}"

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "Starting server on port $PORT..."
python -m uvicorn api.src.main:app --host 0.0.0.0 --port "$PORT" --reload
