from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import requests

from profile_utils import read_json, text_metrics, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated audio with Parakeet ASR.")
    parser.add_argument("--baseline-results", required=True)
    parser.add_argument("--optimized-results", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout", type=float, default=180.0)
    return parser.parse_args()


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def detect_endpoint(explicit: str | None) -> tuple[str, str]:
    if explicit:
        return normalize_endpoint(explicit), "cli"
    env_keys = [
        "PARAKEET_ASR_BASE_URL",
        "PARAKEET_BASE_URL",
        "ASR_BASE_URL",
        "OPENAI_BASE_URL",
        "OPENAI_API_BASE",
        "SERVER_URL",
    ]
    for key in env_keys:
        value = os.getenv(key)
        if value:
            return normalize_endpoint(value), f"env:{key}"
    for env_file in [Path(".env"), Path("py/.env")]:
        values = read_env_file(env_file)
        for key in env_keys:
            if values.get(key):
                return normalize_endpoint(values[key]), f"file:{env_file}:{key}"
    return "http://127.0.0.1:5092/v1", "user_required_default"


def normalize_endpoint(value: str) -> str:
    endpoint = value.rstrip("/")
    suffix = "/audio/transcriptions"
    if endpoint.endswith(suffix):
        endpoint = endpoint[: -len(suffix)]
    return endpoint.rstrip("/")


def get_models(endpoint: str, timeout: float) -> tuple[list[str], dict[str, Any] | None, str | None]:
    url = f"{endpoint}/models"
    try:
        response = requests.get(url, timeout=timeout)
    except requests.RequestException as exc:
        return [], None, str(exc)
    if response.status_code >= 400:
        return [], None, f"HTTP {response.status_code}: {response.text[:500]}"
    try:
        payload = response.json()
    except ValueError:
        return [], None, f"Non-JSON /models response: {response.text[:500]}"
    models = []
    for item in payload.get("data", []):
        if isinstance(item, dict) and item.get("id"):
            models.append(str(item["id"]))
    return models, payload, None


def choose_model(cli_model: str | None, models: list[str]) -> str:
    if cli_model:
        return cli_model
    for model in models:
        if "parakeet" in model.lower():
            return model
    return models[0] if models else "parakeet"


def transcribe(endpoint: str, model: str, audio_path: str, timeout: float) -> tuple[str | None, str | None]:
    url = f"{endpoint}/audio/transcriptions"
    try:
        with open(audio_path, "rb") as audio_file:
            response = requests.post(
                url,
                data={"model": model, "response_format": "json"},
                files={"file": (Path(audio_path).name, audio_file, "audio/wav")},
                timeout=timeout,
            )
    except requests.RequestException as exc:
        return None, str(exc)
    if response.status_code >= 400:
        return None, f"HTTP {response.status_code}: {response.text[:1000]}"
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip(), None
    for key in ["text", "transcript", "transcription"]:
        if key in payload and payload[key] is not None:
            return str(payload[key]), None
    return None, f"No transcript field in response: {payload}"


def validate_set(label: str, results: dict[str, Any], endpoint: str, model: str, timeout: float) -> list[dict[str, Any]]:
    rows = []
    for record in results.get("records", []):
        transcript, error = transcribe(endpoint, model, record["output_path"], timeout)
        metric_values = text_metrics(record["input_text"], transcript or "") if transcript else None
        rows.append(
            {
                "label": label,
                "word_count": record["word_count"],
                "audio_path": record["output_path"],
                "input_text": record["input_text"],
                "transcript": transcript,
                "error": error,
                "metrics": metric_values,
            }
        )
    return rows


def main() -> int:
    args = parse_args()
    endpoint, endpoint_source = detect_endpoint(args.endpoint)
    baseline = read_json(args.baseline_results)
    optimized = read_json(args.optimized_results)
    models, models_payload, models_error = get_models(endpoint, args.timeout)
    model = choose_model(args.model, models)

    baseline_rows = validate_set("baseline", baseline, endpoint, model, args.timeout)
    optimized_rows = validate_set("optimized", optimized, endpoint, model, args.timeout)
    output = {
        "endpoint": endpoint,
        "endpoint_source": endpoint_source,
        "models_endpoint_payload": models_payload,
        "models_endpoint_error": models_error,
        "model_used": model,
        "baseline": baseline_rows,
        "optimized": optimized_rows,
    }
    write_json(args.output, output)
    print(f"ASR endpoint used: {endpoint} ({endpoint_source})")
    print(f"ASR model used: {model}")
    print(f"Wrote ASR validation to {args.output}")
    errors = [row for row in baseline_rows + optimized_rows if row["error"]]
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
