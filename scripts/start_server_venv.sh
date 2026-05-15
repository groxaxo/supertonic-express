#!/usr/bin/env bash
set -euo pipefail
cd /home/op/supertonic-express
export ONNX_DIR=/home/op/supertonic-express/assets
export VOICE_STYLES_DIR=/home/op/supertonic-express/assets
export USE_GPU=false
export LOG_LEVEL=${LOG_LEVEL:-INFO}
exec /home/op/supertonic-express/.venv-supertonic/bin/python -m uvicorn api.src.main:app --host 0.0.0.0 --port 8880 --app-dir /home/op/supertonic-express/py
