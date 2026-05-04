#!/bin/bash
set -euo pipefail

API_PORT="${API_PORT:-8880}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export ONNX_DIR="${ONNX_DIR:-${ROOT_DIR}/assets}"
export SUPERTONIC_ORT_BACKEND="${SUPERTONIC_ORT_BACKEND:-openvino}"
export OPENVINO_DEVICE="${OPENVINO_DEVICE:-GPU}"
export USE_GPU=false

cd "${ROOT_DIR}/py"

cat <<'EOF'
Warning: OpenVINO is currently experimental for this model.
On this machine the iGPU runtime is visible, but text_encoder inference fails
on a dynamic Reshape node with ONNX Runtime OpenVINO EP. Use CPU mode for
reliable service until the model/export/provider issue is resolved.
EOF

echo "Starting Supertonic TTS Server (OpenVINO ${OPENVINO_DEVICE})..."
echo "ONNX_DIR=${ONNX_DIR}"
echo "Port: ${API_PORT}"

exec "${ROOT_DIR}/.venv/bin/uvicorn" api.src.main:app --host 0.0.0.0 --port "${API_PORT}"
