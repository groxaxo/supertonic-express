# Main vs perf-audio-benchmark-optimization CPU Benchmark

## Summary

- Date: 2026-05-03
- Main commit: 090f6574d0beb576e17864063cc37fb99524eb27
- Branch commit: 000e4cb077cae974704bf860015177e41c16e451
- Main branch field: None
- Branch field: perf-audio-benchmark-optimization
- Main Conda env: supertonic-main-bench
- Branch Conda env: supertonic-perf-bench
- Device: CPU (AVX2 host)
- Shared model assets: /home/op/supertonic-express/assets
- Main average real-time factor: 8.392x
- Branch average real-time factor: 9.774x
- Average RTF speedup: 16.475%
- Total generation time, main: 11.453s
- Total generation time, branch: 9.701s
- Total wall-time reduction: 15.297%

## Per-sample Results

| words | main gen time (s) | branch gen time (s) | main RTF | branch RTF | branch speedup |
|---:|---:|---:|---:|---:|---:|
| 10 | 0.699 | 0.667 | 7.578x | 7.934x | 1.047x |
| 20 | 1.106 | 0.915 | 7.940x | 9.594x | 1.208x |
| 30 | 1.468 | 1.258 | 8.968x | 10.465x | 1.167x |
| 50 | 2.632 | 2.189 | 8.646x | 10.393x | 1.202x |
| 100 | 5.549 | 4.671 | 8.828x | 10.486x | 1.188x |

## Aggregate Component Timings

| component | main (s) | branch (s) | improvement (s) |
|---|---:|---:|---:|
| latent_denoiser | 8.914 | 7.565 | 1.349 |
| text_encoder | 0.321 | 0.242 | 0.078 |
| voice_decoder | 2.188 | 1.868 | 0.319 |

## Notes

- Both runs used identical inputs, `M1`, `en`, `steps=15`, `speed=1.05`, `warmup-runs=1`, and the same shared local model assets.
- The benchmark harness was executed from the current branch, but `SUPERTONIC_REPO_ROOT` switched the code under test so git metadata and imported `helper.py` came from the target checkout.
- This report is performance-only. ASR validation was not rerun for this side-by-side comparison.
- GPU was not benchmarked here because the host GPU path was previously shown to be invalid for ONNX Runtime CUDA execution on this GTX 750 Ti (`cudaErrorNoKernelImageForDevice`).

