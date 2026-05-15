# Cross-Host CPU Benchmark Comparison

## A. Executive Summary

- **Host A (local):** Intel Core i5-7500T @ 2.70GHz (4C/4T, 35W TDP, Kaby Lake)
- **Host B (remote):** Intel Core i7-4790 @ 3.60GHz (4C/8T, 84W TDP, Haswell)
- Both CPUs support AVX2. Both run ONNX Runtime 1.23.1, CPU-only execution.
- Host B is **5.29x faster** overall (total component time).
- Host A average RTF: **1.97x** | Host B average RTF: **10.42x**
- Biggest bottleneck on both hosts: `latent_denoiser` (~75% of total time).
- `text_encoder` shows the largest per-call gap: 9.10x slower on Host A.

## B. Environment

| | Host A (i5-7500T) | Host B (i7-4790) |
|---|---|---|
| CPU | Intel Core i5-7500T @ 2.70GHz | Intel Core i7-4790 @ 3.60GHz |
| Cores/Threads | 4C/4T | 4C/8T |
| TDP | 35W | 84W |
| AVX2 | Yes | Yes |
| RAM | 32 GB | 32 GB |
| GPU | None | NVIDIA GeForce GTX 750 Ti (unused) |
| Python | 3.12.3 | 3.11.15 |
| ONNX Runtime | 1.23.1 | 1.23.1 |
| Providers | CPUExecutionProvider | CPUExecutionProvider |
| Model load time | 1.561s | 0.323s |

## C. Benchmark Parameters

- **Steps:** 15 (default_total_steps)
- **Voice:** M1
- **Speed:** 1.05
- **Seed:** 20260502
- **Warmup runs:** 1
- **Script:** `benchmarks/tts_benchmark.py` (optimized path)

## D. Performance Table

| Words | Host A Gen(s) | Host A Audio(s) | Host A RTF | Host B Gen(s) | Host B Audio(s) | Host B RTF | Speedup |
|------:|------:|------:|------:|------:|------:|------:|------:|
| 10 | 3.190s | 5.29s | 1.66x | 0.589s | 5.29s | 8.99x | 5.42x |
| 20 | 4.766s | 8.78s | 1.84x | 0.888s | 8.78s | 9.89x | 5.37x |
| 30 | 6.006s | 13.17s | 2.19x | 1.173s | 13.17s | 11.22x | 5.12x |
| 50 | 11.242s | 22.75s | 2.02x | 2.094s | 22.75s | 10.87x | 5.37x |
| 100 | 23.151s | 48.99s | 2.12x | 4.404s | 48.99s | 11.12x | 5.26x |
| **AVG** | | | **1.97x** | | | **10.42x** | **5.29x** |

## E. Component Breakdown

| Component | Host A Total | Host A Avg/Call | Host B Total | Host B Avg/Call | Speedup | Calls |
|---|---:|---:|---:|---:|---:|---:|
| latent_denoiser | 36.334s | 269.14ms | 7.071s | 52.38ms | 5.14x | 135 |
| text_encoder | 2.184s | 242.66ms | 0.240s | 26.68ms | 9.10x | 9 |
| voice_decoder | 9.731s | 1081.22ms | 1.809s | 201.01ms | 5.38x | 9 |
| **TOTAL** | **48.249s** | | **9.121s** | | **5.29x** | |

### Observations

1. **latent_denoiser** dominates runtime (75% on both hosts). Each of the 15 denoising steps costs ~269ms on Host A vs ~52ms on Host B. The 5.14x gap reflects the combined advantage of higher clock (3.6 vs 2.7 GHz) and double threads (8 vs 4) for ONNX parallel ops.

2. **text_encoder** shows the widest gap at 9.10x. It runs once per sample (9 calls total: 1 warmup + 5 benchmark + 3 from chunking). The encoder is more sequential and benefits disproportionately from raw clock speed and cache architecture.

3. **voice_decoder** is 5.38x faster on Host B, consistent with the denoiser ratio. Each call is heavy (1.08s vs 201ms) and benefits from both clock and parallelism.

4. **Model load time** is 4.8x faster on Host B (0.323s vs 1.561s), likely due to faster disk I/O and CPU-bound ONNX graph parsing.

## F. Analysis: Why 5.3x and Not More

The i7-4790 has:
- 33% higher base clock (3.6 vs 2.7 GHz)
- 84W vs 35W TDP (sustained turbo without throttling)
- 8 threads vs 4 (SMT)
- 8MB L3 cache vs 6MB

The 5.3x overall speedup exceeds what clock alone would explain (~1.33x). The extra threads contribute significantly to ONNX Runtime's intra-op parallelism, especially in the denoiser loop where matrix multiplications can split across cores. The larger L3 cache also reduces memory pressure for the 66M-parameter model.

## G. Reproduction

```bash
# On any host with the repo:
python benchmarks/tts_benchmark.py \
  --label <hostname>-optimized --device cpu \
  --output-dir benchmarks/<hostname>-optimized \
  --results benchmarks/<hostname>-results/results_optimized.json \
  --profile-out benchmarks/<hostname>-results/profile_optimized.txt \
  --warmup-runs 1 --steps 15 --speed 1.05 --voice M1 --seed 20260502
```

## H. Artifacts

- `benchmarks/local-optimized/*.wav` — Host A generated audio
- `benchmarks/local-results/results_optimized.json` — Host A full results
- `benchmarks/local-results/profile_optimized.txt` — Host A component profile
- Remote results are on Host B at `benchmarks/fresh-results/`

---
*Generated: 2026-05-15*
