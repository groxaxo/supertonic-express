"""
Focused tests for CPU-oriented ONNX Runtime optimizations.
"""

import os
import sys
import tempfile
from unittest import mock

import onnxruntime as ort

sys.path.insert(0, os.path.dirname(__file__))

from helper import SupertonicTTS


def test_create_session_options_prefers_cpu_tuning_env_vars():
    with mock.patch.dict(
        os.environ,
        {
            "OMP_NUM_THREADS": "7",
            "ORT_INTER_OP_NUM_THREADS": "3",
            "ORT_EXECUTION_MODE": "1",
        },
        clear=False,
    ):
        sess_options = SupertonicTTS._create_session_options(use_gpu=False)

    assert sess_options.graph_optimization_level == ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    assert sess_options.intra_op_num_threads == 7
    assert sess_options.inter_op_num_threads == 3
    assert sess_options.execution_mode == ort.ExecutionMode.ORT_PARALLEL


def test_init_passes_optimized_session_options_to_all_cpu_sessions():
    with tempfile.TemporaryDirectory() as model_dir:
        onnx_dir = os.path.join(model_dir, "onnx")
        os.makedirs(onnx_dir)
        for filename in ("text_encoder.onnx", "latent_denoiser.onnx", "voice_decoder.onnx"):
            with open(os.path.join(onnx_dir, filename), "wb"):
                pass

        created_sessions = []

        def capture_session(path, sess_options=None, providers=None):
            created_sessions.append(
                {
                    "path": path,
                    "sess_options": sess_options,
                    "providers": providers,
                }
            )
            return object()

        with mock.patch("helper.AutoTokenizer.from_pretrained", return_value=object()), mock.patch(
            "helper.ort.InferenceSession", side_effect=capture_session
        ), mock.patch.dict(os.environ, {"OMP_NUM_THREADS": "5"}, clear=False):
            SupertonicTTS(model_dir, use_gpu=False)

    assert len(created_sessions) == 3
    assert {tuple(session["providers"]) for session in created_sessions} == {
        ("CPUExecutionProvider",)
    }
    for session in created_sessions:
        assert session["sess_options"] is not None
        assert session["sess_options"].graph_optimization_level == (
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )
        assert session["sess_options"].intra_op_num_threads == 5
