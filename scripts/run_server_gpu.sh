#!/bin/bash

# Configuration
CONDA_ENV_NAME="supertonic-gpu"
CONDA_PATH="/home/op/miniconda3"
API_PORT=8880

# Source conda if not already available
if ! command -v conda &> /dev/null; then
    if [ -f "${CONDA_PATH}/etc/profile.d/conda.sh" ]; then
        source "${CONDA_PATH}/etc/profile.d/conda.sh"
    fi
fi

# Activate environment if not already active
if [ "$CONDA_DEFAULT_ENV" != "$CONDA_ENV_NAME" ]; then
    conda activate "$CONDA_ENV_NAME"
fi

# Set LD_LIBRARY_PATH for cuDNN
export LD_LIBRARY_PATH="${CONDA_PATH}/envs/${CONDA_ENV_NAME}/lib/python3.10/site-packages/nvidia/cudnn/lib/:${LD_LIBRARY_PATH}"

# Resolve absolute path to assets directory
export ONNX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../assets" && pwd)"

# Check for GPU
if ! nvidia-smi > /dev/null 2>&1; then
    echo "Error: NVIDIA GPU not found or drivers not installed."
    exit 1
fi

echo "Starting Supertonic TTS Server with GPU support..."
echo "Environment: ${CONDA_ENV_NAME}"
echo "Port: ${API_PORT}"

# Navigate to py directory
cd "$(dirname "$0")/../py" || exit

# Run server
uvicorn api.src.main:app --host 0.0.0.0 --port "${API_PORT}" --reload
