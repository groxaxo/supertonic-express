#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEXT="${TEXT:-Supertonic Express local benchmark. This checks CPU synthesis speed on this laptop.}"
STEPS="${STEPS:-15}"
N_TEST="${N_TEST:-3}"

cd "${ROOT_DIR}/py"

exec taskset -c "${PCORE_CPUS:-0-7}" \
  env OMP_NUM_THREADS="${OMP_NUM_THREADS:-3}" \
  ORT_INTRA_OP_NUM_THREADS="${ORT_INTRA_OP_NUM_THREADS:-3}" \
  ORT_INTER_OP_NUM_THREADS="${ORT_INTER_OP_NUM_THREADS:-1}" \
  /usr/bin/time -f 'wall_seconds=%e cpu_percent=%P max_rss_kb=%M' \
  "${ROOT_DIR}/.venv/bin/python" example_onnx.py \
    --onnx-dir "${ROOT_DIR}/assets" \
    --backend cpu \
    --text "${TEXT}" \
    --voice-style M1 \
    --lang en \
    --total-step "${STEPS}" \
    --n-test "${N_TEST}" \
    --save-dir "${ROOT_DIR}/outputs/cpu_pcores"
