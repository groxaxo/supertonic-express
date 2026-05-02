# Supertonic Express Performance Report

## A. Executive summary

- Baseline average realtime factor: 8.441x
- Optimized average realtime factor: 9.527x
- Speedup percentage: 12.867%
- Quality/accuracy preserved: yes
- Biggest bottleneck found: latent_denoiser
- Biggest optimization win: latent_denoiser
- Notes: CPU/AVX2 optimization succeeded. NVIDIA GPU was detected, but ONNX Runtime CUDA execution failed on GTX 750 Ti with cudaErrorNoKernelImageForDevice, so GPU benchmarking was not valid on this hardware. Parakeet ASR endpoint was detected from SERVER_URL as http://100.85.200.51:5092/v1; /models returned 404 but /audio/transcriptions succeeded.

## B. Environment

- OS: Linux-6.8.0-110-generic-x86_64-with-glibc2.39
- Python: 3.11.15
- Package manager: uv
- GPU: NVIDIA GeForce GTX 750 Ti, 535.288.01, 2048 MiB
- CUDA: 12.2
- PyTorch: None
- ONNX Runtime: 1.23.1
- CPU: Intel(R) Core(TM) i7-4790 CPU @ 3.60GHz
- AVX2 available: True
- Repo commit hash: 090f6574d0beb576e17864063cc37fb99524eb27
- Baseline command: benchmarks/tts_benchmark.py --label baseline --device cpu --output-dir benchmarks/baseline --results benchmarks/results_baseline.json --profile-out benchmarks/profile_baseline.txt --warmup-runs 1 --steps 15 --speed 1.05 --voice M1 --seed 20260502
- Optimized command: benchmarks/tts_benchmark.py --label optimized --device cpu --output-dir benchmarks/optimized --results benchmarks/results_optimized.json --profile-out benchmarks/profile_optimized.txt --warmup-runs 1 --steps 15 --speed 1.05 --voice M1 --seed 20260502
- Baseline providers: latent_denoiser: CPUExecutionProvider; text_encoder: CPUExecutionProvider; voice_decoder: CPUExecutionProvider
- Optimized providers: latent_denoiser: CPUExecutionProvider; text_encoder: CPUExecutionProvider; voice_decoder: CPUExecutionProvider
- ASR endpoint used: http://100.85.200.51:5092/v1 (env:SERVER_URL)
- ASR model used: parakeet

## C. Bottleneck table

| component | baseline time | optimized time | improvement | evidence/profiler source | changed files |
|---|---:|---:|---:|---|---|
| latent_denoiser | 8.836s | 7.605s | 1.231s | benchmarks/profile_baseline.txt, benchmarks/profile_optimized.txt | py/helper.py, benchmarks/*.py |
| text_encoder | 0.312s | 0.264s | 0.048s | benchmarks/profile_baseline.txt, benchmarks/profile_optimized.txt | py/helper.py, benchmarks/*.py |
| voice_decoder | 2.196s | 2.100s | 0.096s | benchmarks/profile_baseline.txt, benchmarks/profile_optimized.txt | py/helper.py, benchmarks/*.py |

## D. Performance table

| word count | baseline generation time | baseline audio duration | baseline realtime factor | optimized generation time | optimized audio duration | optimized realtime factor | speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0.718s | 5.294s | 7.370x | 0.667s | 5.294s | 7.935x | 1.077x |
| 20 | 1.036s | 8.777s | 8.469x | 0.927s | 8.777s | 9.472x | 1.118x |
| 30 | 1.494s | 13.166s | 8.810x | 1.279s | 13.166s | 10.291x | 1.168x |
| 50 | 2.636s | 22.752s | 8.630x | 2.353s | 22.752s | 9.668x | 1.120x |
| 100 | 5.488s | 48.987s | 8.927x | 4.769s | 48.987s | 10.271x | 1.151x |

## E. Accuracy table

| word count | baseline WER | optimized WER | baseline CER | optimized CER | ASR transcript baseline | ASR transcript optimized | pass/fail |
|---:|---:|---:|---:|---:|---|---|---|
| 10 | 0.000 | 0.000 | 0.000 | 0.000 | Fast speech generation must stay clear, natural, stable, and measurable. | Fast speech generation must stay clear, natural, stable, and measurable. | PASS |
| 20 | 0.000 | 0.000 | 0.000 | 0.000 | This benchmark checks whether the audio model can generate short responses quickly while preserving pronunciation, rhythm, and clarity. | This benchmark checks whether the audio model can generate short responses quickly while preserving pronunciation, rhythm, and clarity. | PASS |
| 30 | 0.125 | 0.125 | 0.022 | 0.022 | A real-time voice agent needs low latency, consistent audio quality, accurate pronunciation, and predictable performance across short and medium length replies during no normal conversation. | A real-time voice agent needs low latency, consistent audio quality, accurate pronunciation, and predictable performance across short and medium length replies during no normal conversation. | PASS |
| 50 | 0.000 | 0.000 | 0.000 | 0.000 | This test measures whether the text-to-speech system can generate a useful spoken response fast enough for an interactive voice agent. The output should sound natural, remain intelligible, avoid skipped words, and maintain stable pacing whi | This test measures whether the text-to-speech system can generate a useful spoken response fast enough for an interactive voice agent. The output should sound natural, remain intelligible, avoid skipped words, and maintain stable pacing whi | PASS |
| 100 | 0.073 | 0.042 | 0.027 | 0.012 | This longer benchmark chec whether the optimized generation path remains stable when the ascent produces a complete spoken answer. The system should keep the model loaded, avoid unnecessary transferen and GPU, reduce repeated preprocessing  | This longer benchmark chec whether the optimized generation path remains stable when the ascent produces a complete spoken answer. The system should keep the model loaded, avoid unnecessary transfers between CPU and GPU, reduce repeated pre | PASS |

## F. Code changes

- benchmarks/profile_utils.py: shared benchmark text set, component timers, environment capture, resource sampling, and text accuracy metrics.
- benchmarks/tts_benchmark.py: reproducible baseline and optimized TTS benchmark runner that saves WAV and JSON artifacts.
- benchmarks/asr_validate.py: OpenAI-compatible Parakeet transcription and WER/CER validation.
- benchmarks/report.py: report generator for the required performance, bottleneck, accuracy, reproduction, and artifact sections.
- py/helper.py: CPU ONNX Runtime now defaults to detected physical cores instead of SMT-heavy logical-core use, and voice style tensors are cached per loaded model instance.
- Performance rationale: the profiler showed `latent_denoiser` dominated runtime, and the thread sweep measured physical-core execution as the fastest AVX2 path on this host.
- Risk: physical-core detection is Linux-specific with the previous 75% logical-core heuristic retained as fallback; environment variables still override the default.

## G. Reproduction commands

```bash
uv venv .venv-bench-cpu --python python3.11
. .venv-bench-cpu/bin/activate
uv pip install -r py/requirements.txt -e py
python benchmarks/tts_benchmark.py --label baseline --device cpu --output-dir benchmarks/baseline --results benchmarks/results_baseline.json --profile-out benchmarks/profile_baseline.txt
python benchmarks/tts_benchmark.py --label optimized --device cpu --output-dir benchmarks/optimized --results benchmarks/results_optimized.json --profile-out benchmarks/profile_optimized.txt
SERVER_URL=http://100.85.200.51:5092/v1/audio/transcriptions python benchmarks/asr_validate.py --baseline-results benchmarks/results_baseline.json --optimized-results benchmarks/results_optimized.json --output benchmarks/asr_validation.json
python benchmarks/report.py --baseline-results benchmarks/results_baseline.json --optimized-results benchmarks/results_optimized.json --asr-results benchmarks/asr_validation.json --output benchmarks/comparison.md
```

## H. Artifacts

- benchmarks/baseline/*.wav
- benchmarks/optimized/*.wav
- benchmarks/results_baseline.json
- benchmarks/results_optimized.json
- benchmarks/asr_validation.json
- benchmarks/comparison.md
- benchmarks/profile_baseline.txt
- benchmarks/profile_optimized.txt

## Verdict: PASS
