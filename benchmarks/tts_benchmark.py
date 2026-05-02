from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from profile_utils import (
    ProfilingSession,
    ResourceSampler,
    StageProfiler,
    TEST_TEXTS,
    collect_environment,
    write_json,
)


SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_REPO_ROOT = Path(os.getenv("SUPERTONIC_REPO_ROOT", str(SCRIPT_REPO_ROOT))).resolve()
PY_ROOT = TARGET_REPO_ROOT / "py"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))

from helper import load_text_to_speech  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark Supertonic TTS generation.")
    parser.add_argument("--label", required=True, help="Benchmark label, such as baseline or optimized.")
    parser.add_argument("--device", choices=["cpu", "gpu"], default="cpu")
    parser.add_argument("--onnx-dir", default=str(TARGET_REPO_ROOT / "assets"))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--profile-out", required=True)
    parser.add_argument("--voice", default="M1")
    parser.add_argument("--language", default="en")
    parser.add_argument("--steps", type=int, default=15)
    parser.add_argument("--speed", type=float, default=1.05)
    parser.add_argument("--seed", type=int, default=20260502)
    parser.add_argument("--warmup-runs", type=int, default=1)
    parser.add_argument("--require-cuda-provider", action="store_true")
    parser.add_argument("--package-manager", default="uv")
    return parser.parse_args()


def provider_names(tts: Any) -> dict[str, list[str]]:
    return {
        "text_encoder": list(tts.text_encoder.get_providers()),
        "latent_denoiser": list(tts.latent_denoiser.get_providers()),
        "voice_decoder": list(tts.voice_decoder.get_providers()),
    }


def verify_cuda(tts: Any) -> None:
    providers = provider_names(tts)
    missing = {
        name: values
        for name, values in providers.items()
        if "CUDAExecutionProvider" not in values
    }
    if missing:
        raise RuntimeError(f"CUDAExecutionProvider was required but not active: {missing}")


def save_profile(path: str | Path, aggregate: list[dict[str, Any]], records: list[dict[str, Any]]) -> None:
    lines = ["Supertonic TTS benchmark profile", "", "Aggregate component timings:"]
    for row in aggregate:
        lines.append(
            f"- {row['component']}: {row['time_seconds']:.6f}s "
            f"({row['count']} calls, avg {row['average_seconds']:.6f}s)"
        )
    lines.append("")
    lines.append("Per-sample component timings:")
    for record in records:
        lines.append(f"word_count={record['word_count']} path={record['output_path']}")
        for row in record["component_profile"]:
            lines.append(
                f"  - {row['component']}: {row['time_seconds']:.6f}s "
                f"({row['count']} calls)"
            )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    os.chdir(SCRIPT_REPO_ROOT)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    command = " ".join(sys.argv)
    environment = collect_environment(
        command=command,
        package_manager=args.package_manager,
        repo_root=TARGET_REPO_ROOT,
    )
    profiler = StageProfiler()

    model_start = time.perf_counter()
    tts = load_text_to_speech(args.onnx_dir, use_gpu=args.device == "gpu")
    model_load_time = time.perf_counter() - model_start

    if args.require_cuda_provider:
        verify_cuda(tts)

    providers = provider_names(tts)
    tts.text_encoder = ProfilingSession("text_encoder", tts.text_encoder, profiler)
    tts.latent_denoiser = ProfilingSession("latent_denoiser", tts.latent_denoiser, profiler)
    tts.voice_decoder = ProfilingSession("voice_decoder", tts.voice_decoder, profiler)

    warmup_records = []
    for warmup_index in range(args.warmup_runs):
        np.random.seed(args.seed + warmup_index)
        start = time.perf_counter()
        tts(TEST_TEXTS[0]["text"], args.language, args.voice, args.steps, args.speed)
        warmup_records.append(
            {"warmup_index": warmup_index, "wall_time_seconds": time.perf_counter() - start}
        )

    profiler.reset()
    records: list[dict[str, Any]] = []
    aggregate_profiler = StageProfiler()

    for index, sample in enumerate(TEST_TEXTS):
        np.random.seed(args.seed + 100 + index)
        profiler.reset()
        with ResourceSampler(sample_gpu=args.device == "gpu") as sampler:
            gen_start = time.perf_counter()
            wav, duration = tts(sample["text"], args.language, args.voice, args.steps, args.speed)
            generation_wall_time = time.perf_counter() - gen_start

            output_path = output_dir / f"{sample['word_count']:03d}_words.wav"
            write_start = time.perf_counter()
            sample_count = int(tts.sample_rate * float(duration[0]))
            sf.write(output_path, wav[0, :sample_count], tts.sample_rate)
            audio_write_time = time.perf_counter() - write_start
        resource_metrics = sampler.metrics()

        audio_info = sf.info(output_path)
        audio_duration = float(audio_info.duration)
        realtime_factor = audio_duration / generation_wall_time if generation_wall_time else None
        inverse_realtime_factor = generation_wall_time / audio_duration if audio_duration else None

        component_profile = profiler.summary()
        for row in component_profile:
            aggregate_profiler.totals[row["component"]] += row["time_seconds"]
            aggregate_profiler.counts[row["component"]] += row["count"]

        records.append(
            {
                "label": args.label,
                "device": args.device,
                "word_count": sample["word_count"],
                "input_text": sample["text"],
                "voice": args.voice,
                "language": args.language,
                "steps": args.steps,
                "speed": args.speed,
                "seed": args.seed + 100 + index,
                "output_path": str(output_path),
                "audio_duration_seconds": audio_duration,
                "generation_wall_time_seconds": generation_wall_time,
                "audio_write_time_seconds": audio_write_time,
                "total_end_to_end_latency_seconds": generation_wall_time + audio_write_time,
                "realtime_factor": realtime_factor,
                "inverse_realtime_factor": inverse_realtime_factor,
                "model_load_time_seconds": model_load_time,
                "first_audio_latency_seconds": None,
                "component_profile": component_profile,
                **resource_metrics,
            }
        )

    aggregate_profile = aggregate_profiler.summary()
    result = {
        "label": args.label,
        "device": args.device,
        "created_at_unix": time.time(),
        "environment": environment,
        "script_repo_root": str(SCRIPT_REPO_ROOT),
        "target_repo_root": str(TARGET_REPO_ROOT),
        "onnx_dir": args.onnx_dir,
        "providers": providers,
        "model_load_time_seconds": model_load_time,
        "warmup_records": warmup_records,
        "records": records,
        "aggregate_component_profile": aggregate_profile,
    }
    write_json(args.results, result)
    save_profile(args.profile_out, aggregate_profile, records)
    print(f"Wrote results to {args.results}")
    print(f"Wrote profile to {args.profile_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
