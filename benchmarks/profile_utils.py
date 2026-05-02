from __future__ import annotations

import contextlib
import importlib.metadata
import json
import os
import platform
import re
import resource
import shutil
import statistics
import subprocess
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator


TEST_TEXTS: list[dict[str, Any]] = [
    {
        "word_count": 10,
        "text": "Fast speech generation must stay clear, natural, stable, and measurable.",
    },
    {
        "word_count": 20,
        "text": "This benchmark checks whether the audio model can generate short responses quickly while preserving pronunciation, rhythm, and clarity.",
    },
    {
        "word_count": 30,
        "text": "A realtime voice agent needs low latency, consistent audio quality, accurate pronunciation, and predictable performance across short and medium length replies during normal conversation.",
    },
    {
        "word_count": 50,
        "text": "This test measures whether the text to speech system can generate a useful spoken response fast enough for an interactive voice agent. The output should sound natural, remain intelligible, avoid skipped words, and maintain stable pacing while the benchmark records latency, throughput, memory usage, and transcription accuracy.",
    },
    {
        "word_count": 100,
        "text": "This longer benchmark checks whether the optimized generation path remains stable when the assistant produces a complete spoken answer. The system should keep the model loaded, avoid unnecessary transfers between CPU and GPU, reduce repeated preprocessing work, and generate audio faster than the original implementation without damaging intelligibility. The output should preserve the meaning of the prompt, pronounce the words clearly, avoid hallucinated phrases, avoid missing clauses, and maintain a natural speaking rhythm. The final report must compare baseline and optimized generation times, realtime factors, memory usage, bottlenecks, code changes, and transcription accuracy measured with Parakeet.",
    },
]


def write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_text(command: list[str], timeout: float = 5.0) -> str | None:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (completed.stdout or completed.stderr).strip()
    return output or None


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def collect_environment(
    command: str,
    package_manager: str,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    repo_root_path = Path(repo_root).resolve() if repo_root is not None else None

    nvidia_csv = run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total",
            "--format=csv,noheader",
        ]
    )
    nvidia_full = run_text(["nvidia-smi"], timeout=10.0)
    cpu_model = None
    cpu_flags = None
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(errors="ignore").splitlines():
            if line.startswith("model name") and cpu_model is None:
                cpu_model = line.split(":", 1)[1].strip()
            elif line.startswith("flags") and cpu_flags is None:
                cpu_flags = line.split(":", 1)[1].strip()
            if cpu_model and cpu_flags:
                break

    return {
        "command": command,
        "package_manager": package_manager,
        "python": platform.python_version(),
        "python_executable": shutil.which("python"),
        "os": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": cpu_model,
        "cpu_count": os.cpu_count(),
        "cpu_flags_contains_avx2": bool(cpu_flags and "avx2" in cpu_flags.split()),
        "ram": run_text(["free", "-h"]),
        "gpu_query": nvidia_csv,
        "nvidia_smi": nvidia_full,
        "cuda_version_from_nvidia_smi": _extract_cuda_version(nvidia_full),
        "driver_version_from_nvidia_smi": _extract_driver_version(nvidia_full),
        "pytorch_version": package_version("torch"),
        "onnxruntime_version": package_version("onnxruntime") or package_version("onnxruntime-gpu"),
        "transformers_version": package_version("transformers"),
        "soundfile_version": package_version("soundfile"),
        "librosa_version": package_version("librosa"),
        "commit_hash": _git_text(repo_root_path, ["rev-parse", "HEAD"]),
        "branch": _git_text(repo_root_path, ["branch", "--show-current"]),
        "repo_root": str(repo_root_path) if repo_root_path is not None else None,
    }


def _git_text(repo_root: Path | None, args: list[str]) -> str | None:
    command = ["git"]
    if repo_root is not None:
        command.extend(["-C", str(repo_root)])
    command.extend(args)
    return run_text(command)


def _extract_cuda_version(nvidia_smi_output: str | None) -> str | None:
    if not nvidia_smi_output:
        return None
    match = re.search(r"CUDA Version:\s*([^\s|]+)", nvidia_smi_output)
    return match.group(1) if match else None


def _extract_driver_version(nvidia_smi_output: str | None) -> str | None:
    if not nvidia_smi_output:
        return None
    match = re.search(r"Driver Version:\s*([^\s|]+)", nvidia_smi_output)
    return match.group(1) if match else None


@dataclass
class StageProfiler:
    totals: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    @contextlib.contextmanager
    def time(self, name: str) -> Iterator[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.totals[name] += elapsed
            self.counts[name] += 1

    def reset(self) -> None:
        self.totals.clear()
        self.counts.clear()

    def summary(self) -> list[dict[str, Any]]:
        return [
            {
                "component": name,
                "time_seconds": seconds,
                "count": self.counts[name],
                "average_seconds": seconds / self.counts[name] if self.counts[name] else 0.0,
            }
            for name, seconds in sorted(self.totals.items(), key=lambda item: item[1], reverse=True)
        ]


class ProfilingSession:
    def __init__(self, name: str, session: Any, profiler: StageProfiler):
        self._name = name
        self._session = session
        self._profiler = profiler

    def run(self, *args: Any, **kwargs: Any) -> Any:
        with self._profiler.time(self._name):
            return self._session.run(*args, **kwargs)

    def run_with_iobinding(self, *args: Any, **kwargs: Any) -> Any:
        with self._profiler.time(self._name):
            return self._session.run_with_iobinding(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._session, name)


class ResourceSampler:
    def __init__(self, interval_seconds: float = 0.2, sample_gpu: bool = True):
        self.interval_seconds = interval_seconds
        self.sample_gpu = sample_gpu and shutil.which("nvidia-smi") is not None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.samples: list[dict[str, float]] = []
        self._start_process_time = 0.0
        self._start_wall_time = 0.0
        self._start_maxrss_kb = 0

    def __enter__(self) -> "ResourceSampler":
        self._start_process_time = time.process_time()
        self._start_wall_time = time.perf_counter()
        self._start_maxrss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if self.sample_gpu:
            self._thread = threading.Thread(target=self._poll_gpu, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _poll_gpu(self) -> None:
        while not self._stop.is_set():
            output = run_text(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used",
                    "--format=csv,noheader,nounits",
                ],
                timeout=2.0,
            )
            if output:
                first = output.splitlines()[0]
                parts = [part.strip() for part in first.split(",")]
                if len(parts) >= 2:
                    try:
                        self.samples.append(
                            {
                                "gpu_utilization_percent": float(parts[0]),
                                "vram_used_mb": float(parts[1]),
                            }
                        )
                    except ValueError:
                        pass
            self._stop.wait(self.interval_seconds)

    def metrics(self) -> dict[str, Any]:
        wall = time.perf_counter() - self._start_wall_time
        process_time = time.process_time() - self._start_process_time
        cpu_count = os.cpu_count() or 1
        cpu_util = (process_time / wall / cpu_count * 100.0) if wall > 0 else None
        maxrss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        vram_values = [sample["vram_used_mb"] for sample in self.samples]
        util_values = [sample["gpu_utilization_percent"] for sample in self.samples]
        return {
            "cpu_utilization_percent_estimate": cpu_util,
            "process_cpu_time_seconds": process_time,
            "process_maxrss_mb": maxrss_kb / 1024.0,
            "process_maxrss_delta_mb": max(0.0, (maxrss_kb - self._start_maxrss_kb) / 1024.0),
            "average_gpu_utilization_percent": statistics.mean(util_values) if util_values else None,
            "peak_vram_mb": max(vram_values) if vram_values else None,
            "gpu_sample_count": len(self.samples),
        }


def normalize_text(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def levenshtein(a: list[str] | str, b: list[str] | str) -> int:
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for index_a, token_a in enumerate(a, start=1):
        current = [index_a]
        for index_b, token_b in enumerate(b, start=1):
            insert_cost = current[index_b - 1] + 1
            delete_cost = previous[index_b] + 1
            replace_cost = previous[index_b - 1] + (token_a != token_b)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


def text_metrics(reference: str, hypothesis: str) -> dict[str, Any]:
    ref_norm = normalize_text(reference)
    hyp_norm = normalize_text(hypothesis)
    ref_tokens = ref_norm.split()
    hyp_tokens = hyp_norm.split()
    word_distance = levenshtein(ref_tokens, hyp_tokens)
    char_distance = levenshtein(ref_norm, hyp_norm)
    wer = word_distance / max(1, len(ref_tokens))
    cer = char_distance / max(1, len(ref_norm))
    token_similarity = 1.0 - word_distance / max(1, max(len(ref_tokens), len(hyp_tokens)))
    char_similarity = 1.0 - char_distance / max(1, max(len(ref_norm), len(hyp_norm)))
    return {
        "reference_normalized": ref_norm,
        "hypothesis_normalized": hyp_norm,
        "wer": wer,
        "cer": cer,
        "token_level_similarity": max(0.0, token_similarity),
        "character_level_similarity": max(0.0, char_similarity),
        "pass": wer <= 0.15,
        "flag": "likely_degradation_or_asr_mismatch" if wer > 0.25 else None,
    }
