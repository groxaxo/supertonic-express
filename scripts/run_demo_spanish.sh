#!/bin/bash

# Configuration
CONDA_ENV_NAME="base" # Or "chatterbox"
CONDA_PATH="/home/op/miniconda3"

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

echo "Running Spanish Detection Demo..."
echo "Environment: ${CONDA_ENV_NAME}"

# Navigate to scripts directory
cd "$(dirname "$0")" || exit

# Run demo
python demo_spanish_detection.py
