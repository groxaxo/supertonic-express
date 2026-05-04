# Local Install And Performance Notes

Date: 2026-05-04
Host: Dynabook PORTEGE X30W-K, Intel Core i5-1240P, Intel Iris Xe iGPU, 16 GB RAM
Checkout: `/home/op/supertonic-express-fresh`

## Install

The fresh checkout was cloned from:

```bash
git clone https://github.com/groxaxo/supertonic-express /home/op/supertonic-express-fresh
```

Python environment:

```bash
cd /home/op/supertonic-express-fresh
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -e py
uv pip install --python .venv/bin/python onnxruntime
```

JavaScript dependencies:

```bash
cd /home/op/supertonic-express-fresh/js
npm install
```

Model assets:

```bash
cd /home/op/supertonic-express-fresh
.venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("onnx-community/Supertonic-TTS-2-ONNX", local_dir="assets")
PY
```

OpenVINO/iGPU packages:

```bash
cd /home/op/supertonic-express-fresh
uv pip install --python .venv/bin/python openvino onnxruntime-openvino
sudo apt-get update
sudo apt-get install -y intel-opencl-icd libze-intel-gpu1
```

## Hardware Discovery

P-cores are logical CPUs `0-7`:

```bash
lscpu --all --extended=CPU,CORE,SOCKET,NODE,ONLINE,MAXMHZ,MINMHZ,MHZ
```

The E-cores are logical CPUs `8-15`.

OpenVINO/iGPU discovery after installing the Intel compute runtime:

```text
clinfo -l
Platform #0: Intel(R) OpenCL Graphics
 `-- Device #0: Intel(R) Iris(R) Xe Graphics

openvino 2026.1.0
devices ['CPU', 'GPU']
GPU Intel(R) Iris(R) Xe Graphics (iGPU)

onnxruntime 1.24.1
providers ['OpenVINOExecutionProvider', 'CPUExecutionProvider']
```

## CPU Benchmarks

Prompt:

```text
Supertonic Express local benchmark. This checks CPU synthesis speed on this laptop.
```

Settings: `M1`, English, 15 denoising steps.

Unpinned CPU:

```bash
cd /home/op/supertonic-express-fresh/py
/usr/bin/time -f 'wall_seconds=%e cpu_percent=%P max_rss_kb=%M' \
  env OMP_NUM_THREADS=4 ORT_INTRA_OP_NUM_THREADS=4 ORT_INTER_OP_NUM_THREADS=1 \
  ../.venv/bin/python example_onnx.py \
  --onnx-dir ../assets \
  --backend cpu \
  --text 'Supertonic Express local benchmark. This checks CPU synthesis speed on this laptop.' \
  --voice-style M1 --lang en --total-step 15 --n-test 3 \
  --save-dir ../outputs/cpu_unpinned
```

Result:

```text
1.19 sec, 1.19 sec, 1.24 sec
wall_seconds=4.93 cpu_percent=596% max_rss_kb=403964
```

P-core pinned CPU:

```bash
cd /home/op/supertonic-express-fresh/py
/usr/bin/time -f 'wall_seconds=%e cpu_percent=%P max_rss_kb=%M' \
  taskset -c 0-7 \
  env OMP_NUM_THREADS=4 ORT_INTRA_OP_NUM_THREADS=4 ORT_INTER_OP_NUM_THREADS=1 \
  ../.venv/bin/python example_onnx.py \
  --onnx-dir ../assets \
  --backend cpu \
  --text 'Supertonic Express local benchmark. This checks CPU synthesis speed on this laptop.' \
  --voice-style M1 --lang en --total-step 15 --n-test 3 \
  --save-dir ../outputs/cpu_pcores
```

Best result observed:

```text
1.11 sec, 0.99 sec, 0.97 sec
wall_seconds=4.55 cpu_percent=561% max_rss_kb=404948
```

Retest after adding backend selection:

```text
1.16 sec, 1.32 sec, 0.97 sec
wall_seconds=5.66 cpu_percent=472% max_rss_kb=403604
```

Final thread sweep with the API server stopped showed that more threads do not help
this model. Best reliable setting was 3 ORT/OMP threads pinned to the 4 P-cores:

```bash
cd /home/op/supertonic-express-fresh/py
/usr/bin/time -f 'wall_seconds=%e cpu_percent=%P max_rss_kb=%M' \
  taskset -c 0-7 \
  env OMP_NUM_THREADS=3 ORT_INTRA_OP_NUM_THREADS=3 ORT_INTER_OP_NUM_THREADS=1 \
  ../.venv/bin/python example_onnx.py \
  --onnx-dir ../assets \
  --backend cpu \
  --text 'Supertonic Express local benchmark. This checks CPU synthesis speed on this laptop.' \
  --voice-style M1 --lang en --total-step 15 --n-test 5 \
  --save-dir ../outputs/final_sweep_pcores_t3
```

Result:

```text
0.83 sec, 0.69 sec, 0.69 sec, 0.70 sec, 0.70 sec
wall_seconds=4.84 cpu_percent=540% max_rss_kb=403336
```

Slower thread settings from the same sweep:

```text
P-cores, 4 threads: 0.97, 0.98, 0.94, 0.85, 0.88 sec
P-cores, 5 threads: 1.22, 1.19, 1.31, 1.15, 1.17 sec
All cores, 3 threads: 0.83, 0.88, 0.83, 0.79, 0.74 sec
All cores, 4 threads: 0.82, 1.12, 1.26, 1.29, 1.22 sec
All cores, 5 threads: 1.13, 1.24, 1.27, 1.14, 1.15 sec
```

Use the helper script for repeatable P-core CPU tests:

```bash
cd /home/op/supertonic-express-fresh
scripts/benchmark_pcores.sh
```

## OpenVINO/iGPU Status

OpenVINO can see the iGPU and ONNX Runtime can create all three model sessions with:

```python
providers = [
    ("OpenVINOExecutionProvider", {"device_type": "GPU"}),
    "CPUExecutionProvider",
]
```

Actual synthesis currently fails in the text encoder on both OpenVINO GPU and OpenVINO CPU:

```text
OpenVINO-EP-subgraph_1
Reshape node /text_encoder/attn_encoder/attn_layers.0/Reshape_10
Shape inference input shapes {[1,4,183],[4]}
Requested output shape [1,4,93,183] is incompatible with input shape
```

Conclusion: the iGPU stack is now installed and visible, but this ONNX model/export is not currently compatible with ONNX Runtime OpenVINO EP for synthesis. CPU with P-core pinning is the reliable fast path for now.

## Running The Service

Reliable CPU service:

```bash
cd /home/op/supertonic-express-fresh
export ONNX_DIR=/home/op/supertonic-express-fresh/assets
export SUPERTONIC_ORT_BACKEND=cpu
export OMP_NUM_THREADS=3
export ORT_INTRA_OP_NUM_THREADS=3
export ORT_INTER_OP_NUM_THREADS=1
taskset -c 0-7 .venv/bin/uvicorn api.src.main:app --app-dir py --host 0.0.0.0 --port 8880
```

Experimental OpenVINO service:

```bash
cd /home/op/supertonic-express-fresh
scripts/run_server_igpu.sh
```

The experimental OpenVINO service is expected to fail on first synthesis until the reshape/provider compatibility issue is fixed.
