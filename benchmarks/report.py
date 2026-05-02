from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from profile_utils import read_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write benchmark comparison report.")
    parser.add_argument("--baseline-results", required=True)
    parser.add_argument("--optimized-results", required=True)
    parser.add_argument("--asr-results", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--verdict", default="PARTIAL PASS")
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def average(records: list[dict[str, Any]], key: str) -> float | None:
    values = [record.get(key) for record in records if isinstance(record.get(key), (int, float))]
    return sum(values) / len(values) if values else None


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def by_word(records: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(record["word_count"]): record for record in records}


def asr_by_label_word(asr: dict[str, Any], label: str) -> dict[int, dict[str, Any]]:
    return {int(row["word_count"]): row for row in asr.get(label, [])}


def aggregate_profile(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["component"]: row for row in result.get("aggregate_component_profile", [])}


def provider_summary(result: dict[str, Any]) -> str:
    providers = result.get("providers", {})
    return "; ".join(f"{name}: {', '.join(values)}" for name, values in providers.items())


def main() -> int:
    args = parse_args()
    baseline = read_json(args.baseline_results)
    optimized = read_json(args.optimized_results)
    asr = read_json(args.asr_results)

    baseline_records = baseline.get("records", [])
    optimized_records = optimized.get("records", [])
    baseline_avg = average(baseline_records, "realtime_factor")
    optimized_avg = average(optimized_records, "realtime_factor")
    speedup_pct = None
    if baseline_avg and optimized_avg:
        speedup_pct = (optimized_avg / baseline_avg - 1.0) * 100.0

    base_profile = aggregate_profile(baseline)
    opt_profile = aggregate_profile(optimized)
    all_components = sorted(set(base_profile) | set(opt_profile))

    base_by_word = by_word(baseline_records)
    opt_by_word = by_word(optimized_records)
    asr_base = asr_by_label_word(asr, "baseline")
    asr_opt = asr_by_label_word(asr, "optimized")

    biggest_bottleneck = "n/a"
    if baseline.get("aggregate_component_profile"):
        biggest_bottleneck = baseline["aggregate_component_profile"][0]["component"]
    biggest_win = "n/a"
    wins = []
    for component in all_components:
        base_time = base_profile.get(component, {}).get("time_seconds")
        opt_time = opt_profile.get(component, {}).get("time_seconds")
        if isinstance(base_time, (int, float)) and isinstance(opt_time, (int, float)):
            wins.append((base_time - opt_time, component))
    if wins:
        biggest_win = max(wins)[1]

    lines = []
    lines.append("# Supertonic Express Performance Report")
    lines.append("")
    lines.append("## A. Executive summary")
    lines.append("")
    lines.append(f"- Baseline average realtime factor: {fmt(baseline_avg)}x")
    lines.append(f"- Optimized average realtime factor: {fmt(optimized_avg)}x")
    lines.append(f"- Speedup percentage: {fmt(speedup_pct)}%")
    lines.append(f"- Quality/accuracy preserved: {_accuracy_preserved(asr)}")
    lines.append(f"- Biggest bottleneck found: {biggest_bottleneck}")
    lines.append(f"- Biggest optimization win: {biggest_win}")
    if args.notes:
        lines.append(f"- Notes: {args.notes}")
    lines.append("")
    lines.append("## B. Environment")
    lines.append("")
    env = optimized.get("environment") or baseline.get("environment") or {}
    lines.append(f"- OS: {env.get('os')}")
    lines.append(f"- Python: {env.get('python')}")
    lines.append(f"- Package manager: {env.get('package_manager')}")
    lines.append(f"- GPU: {env.get('gpu_query')}")
    lines.append(f"- CUDA: {env.get('cuda_version_from_nvidia_smi')}")
    lines.append(f"- PyTorch: {env.get('pytorch_version')}")
    lines.append(f"- ONNX Runtime: {env.get('onnxruntime_version')}")
    lines.append(f"- CPU: {env.get('cpu_model')}")
    lines.append(f"- AVX2 available: {env.get('cpu_flags_contains_avx2')}")
    lines.append(f"- Repo commit hash: {env.get('commit_hash')}")
    lines.append(f"- Baseline command: {baseline.get('environment', {}).get('command')}")
    lines.append(f"- Optimized command: {optimized.get('environment', {}).get('command')}")
    lines.append(f"- Baseline providers: {provider_summary(baseline)}")
    lines.append(f"- Optimized providers: {provider_summary(optimized)}")
    lines.append(f"- ASR endpoint used: {asr.get('endpoint')} ({asr.get('endpoint_source')})")
    lines.append(f"- ASR model used: {asr.get('model_used')}")
    lines.append("")
    lines.append("## C. Bottleneck table")
    lines.append("")
    lines.append("| component | baseline time | optimized time | improvement | evidence/profiler source | changed files |")
    lines.append("|---|---:|---:|---:|---|---|")
    for component in all_components:
        base_time = base_profile.get(component, {}).get("time_seconds")
        opt_time = opt_profile.get(component, {}).get("time_seconds")
        improvement = None
        if isinstance(base_time, (int, float)) and isinstance(opt_time, (int, float)):
            improvement = base_time - opt_time
        lines.append(
            f"| {component} | {fmt(base_time)}s | {fmt(opt_time)}s | {fmt(improvement)}s | benchmarks/profile_baseline.txt, benchmarks/profile_optimized.txt | py/helper.py, benchmarks/*.py |"
        )
    lines.append("")
    lines.append("## D. Performance table")
    lines.append("")
    lines.append("| word count | baseline generation time | baseline audio duration | baseline realtime factor | optimized generation time | optimized audio duration | optimized realtime factor | speedup |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for word_count in sorted(set(base_by_word) | set(opt_by_word)):
        base = base_by_word.get(word_count, {})
        opt = opt_by_word.get(word_count, {})
        speedup = None
        if base.get("generation_wall_time_seconds") and opt.get("generation_wall_time_seconds"):
            speedup = base["generation_wall_time_seconds"] / opt["generation_wall_time_seconds"]
        lines.append(
            f"| {word_count} | {fmt(base.get('generation_wall_time_seconds'))}s | {fmt(base.get('audio_duration_seconds'))}s | {fmt(base.get('realtime_factor'))}x | "
            f"{fmt(opt.get('generation_wall_time_seconds'))}s | {fmt(opt.get('audio_duration_seconds'))}s | {fmt(opt.get('realtime_factor'))}x | {fmt(speedup)}x |"
        )
    lines.append("")
    lines.append("## E. Accuracy table")
    lines.append("")
    lines.append("| word count | baseline WER | optimized WER | baseline CER | optimized CER | ASR transcript baseline | ASR transcript optimized | pass/fail |")
    lines.append("|---:|---:|---:|---:|---:|---|---|---|")
    for word_count in sorted(set(asr_base) | set(asr_opt)):
        base = asr_base.get(word_count, {})
        opt = asr_opt.get(word_count, {})
        base_metrics = base.get("metrics") or {}
        opt_metrics = opt.get("metrics") or {}
        passed = bool(base_metrics.get("pass")) and bool(opt_metrics.get("pass")) and not base.get("error") and not opt.get("error")
        lines.append(
            f"| {word_count} | {fmt(base_metrics.get('wer'))} | {fmt(opt_metrics.get('wer'))} | {fmt(base_metrics.get('cer'))} | {fmt(opt_metrics.get('cer'))} | "
            f"{_cell(base.get('transcript') or base.get('error'))} | {_cell(opt.get('transcript') or opt.get('error'))} | {'PASS' if passed else 'FAIL'} |"
        )
    lines.append("")
    lines.append("## F. Code changes")
    lines.append("")
    lines.append("- benchmarks/profile_utils.py: shared benchmark text set, component timers, environment capture, resource sampling, and text accuracy metrics.")
    lines.append("- benchmarks/tts_benchmark.py: reproducible baseline and optimized TTS benchmark runner that saves WAV and JSON artifacts.")
    lines.append("- benchmarks/asr_validate.py: OpenAI-compatible Parakeet transcription and WER/CER validation.")
    lines.append("- benchmarks/report.py: report generator for the required performance, bottleneck, accuracy, reproduction, and artifact sections.")
    lines.append("- py/helper.py: CPU ONNX Runtime now defaults to detected physical cores instead of SMT-heavy logical-core use, and voice style tensors are cached per loaded model instance.")
    lines.append("- Performance rationale: the profiler showed `latent_denoiser` dominated runtime, and the thread sweep measured physical-core execution as the fastest AVX2 path on this host.")
    lines.append("- Risk: physical-core detection is Linux-specific with the previous 75% logical-core heuristic retained as fallback; environment variables still override the default.")
    lines.append("")
    lines.append("## G. Reproduction commands")
    lines.append("")
    lines.append("```bash")
    lines.append("uv venv .venv-bench-cpu --python python3.11")
    lines.append(". .venv-bench-cpu/bin/activate")
    lines.append("uv pip install -r py/requirements.txt -e py")
    lines.append("python benchmarks/tts_benchmark.py --label baseline --device cpu --output-dir benchmarks/baseline --results benchmarks/results_baseline.json --profile-out benchmarks/profile_baseline.txt")
    lines.append("python benchmarks/tts_benchmark.py --label optimized --device cpu --output-dir benchmarks/optimized --results benchmarks/results_optimized.json --profile-out benchmarks/profile_optimized.txt")
    lines.append("SERVER_URL=http://100.85.200.51:5092/v1/audio/transcriptions python benchmarks/asr_validate.py --baseline-results benchmarks/results_baseline.json --optimized-results benchmarks/results_optimized.json --output benchmarks/asr_validation.json")
    lines.append("python benchmarks/report.py --baseline-results benchmarks/results_baseline.json --optimized-results benchmarks/results_optimized.json --asr-results benchmarks/asr_validation.json --output benchmarks/comparison.md")
    lines.append("```")
    lines.append("")
    lines.append("## H. Artifacts")
    lines.append("")
    lines.append("- benchmarks/baseline/*.wav")
    lines.append("- benchmarks/optimized/*.wav")
    lines.append("- benchmarks/results_baseline.json")
    lines.append("- benchmarks/results_optimized.json")
    lines.append("- benchmarks/asr_validation.json")
    lines.append("- benchmarks/comparison.md")
    lines.append("- benchmarks/profile_baseline.txt")
    lines.append("- benchmarks/profile_optimized.txt")
    lines.append("")
    lines.append(f"## Verdict: {args.verdict}")
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote report to {args.output}")
    return 0


def _accuracy_preserved(asr: dict[str, Any]) -> str:
    base_rows = asr.get("baseline", [])
    opt_rows = asr.get("optimized", [])
    if not base_rows or not opt_rows:
        return "not validated"
    for base, opt in zip(base_rows, opt_rows):
        if base.get("error") or opt.get("error"):
            return "no, ASR error present"
        base_metrics = base.get("metrics") or {}
        opt_metrics = opt.get("metrics") or {}
        if opt_metrics.get("wer", 1.0) > 0.25:
            return "no, optimized WER exceeded 0.25"
        if opt_metrics.get("wer", 1.0) - base_metrics.get("wer", 1.0) > 0.10:
            return "no, optimized WER worsened by more than 0.10"
    return "yes"


def _cell(value: Any) -> str:
    text = str(value or "")
    return text.replace("|", "\\|").replace("\n", " ")[:240]


if __name__ == "__main__":
    raise SystemExit(main())
