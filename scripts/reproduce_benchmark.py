
import os
import time
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
import logging

# Configure logging to capture ONNX Runtime warnings
logging.basicConfig(level=logging.WARNING)

class BenchmarkTTS:
    SAMPLE_RATE = 44100
    CHUNK_COMPRESS_FACTOR = 6
    BASE_CHUNK_SIZE = 512
    LATENT_DIM = 24
    STYLE_DIM = 128
    LATENT_SIZE = BASE_CHUNK_SIZE * CHUNK_COMPRESS_FACTOR

    def __init__(self, model_path: str, use_gpu: bool = True):
        self.model_path = model_path
        print(f"Loading models from {model_path} with use_gpu={use_gpu}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        except Exception as e:
            print(f"Error loading tokenizer: {e}")
            return

        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if use_gpu else ["CPUExecutionProvider"]
        print(f"Providers: {providers}")

        sess_options = ort.SessionOptions()
        # sess_options.log_severity_level = 0 # Verbose

        onnx_dir = os.path.join(self.model_path, "onnx")
        self.text_encoder = ort.InferenceSession(
            os.path.join(onnx_dir, "text_encoder.onnx"),
            sess_options=sess_options,
            providers=providers
        )
        self.latent_denoiser = ort.InferenceSession(
            os.path.join(onnx_dir, "latent_denoiser.onnx"),
            sess_options=sess_options,
            providers=providers
        )
        self.voice_decoder = ort.InferenceSession(
            os.path.join(onnx_dir, "voice_decoder.onnx"),
            sess_options=sess_options,
            providers=providers
        )
        print("Models loaded.")

    def _load_style(self, voice: str) -> np.ndarray:
        voice_path = os.path.join(self.model_path, "voices", f"{voice}.bin")
        if not os.path.exists(voice_path):
             # Fallback to check if .json exists or just random
             print(f"Voice {voice} not found, using random style.")
             return np.random.randn(1, 1, self.STYLE_DIM).astype(np.float32)
             
        style_vec = np.fromfile(voice_path, dtype=np.float32)
        return style_vec.reshape(1, -1, self.STYLE_DIM)

    def benchmark(self, text: str, steps: int = 10):
        print(f"Benchmarking with text: '{text}' (steps={steps})")
        
        start_total = time.time()
        
        # 1. Prepare Inputs
        language = "en"
        text_input = [f"<{language}>{text}</{language}>"]
        inputs = self.tokenizer(text_input, return_tensors="np", padding=True, truncation=True)
        input_ids = inputs["input_ids"]
        attn_mask = inputs["attention_mask"]
        batch_size = input_ids.shape[0]
        style = self._load_style("M1").repeat(batch_size, axis=0)

        # 2. Encoder
        t0 = time.time()
        last_hidden_state, raw_durations = self.text_encoder.run(
            None,
            {"input_ids": input_ids, "attention_mask": attn_mask, "style": style}
        )
        t_encoder = time.time() - t0
        print(f"Encoder time: {t_encoder*1000:.2f} ms")

        durations = (raw_durations * self.SAMPLE_RATE).astype(np.int64) # Ignoring speed for benchmark
        
        # 3. Latent Prep
        latent_lengths = (durations + self.LATENT_SIZE - 1) // self.LATENT_SIZE
        max_len = latent_lengths.max()
        latent_mask = (np.arange(max_len) < latent_lengths[:, None]).astype(np.int64)
        latents = np.random.randn(
            batch_size, self.LATENT_DIM * self.CHUNK_COMPRESS_FACTOR, max_len
        ).astype(np.float32)
        latents *= latent_mask[:, None, :]

        # 4. Denoiser Loop
        t0 = time.time()
        num_inference_steps = np.full(batch_size, steps, dtype=np.float32)
        
        for step in range(steps):
            t_step_start = time.time()
            timestep = np.full(batch_size, step, dtype=np.float32)
            latents = self.latent_denoiser.run(
                None,
                {
                    "noisy_latents": latents,
                    "latent_mask": latent_mask,
                    "style": style,
                    "encoder_outputs": last_hidden_state,
                    "attention_mask": attn_mask,
                    "timestep": timestep,
                    "num_inference_steps": num_inference_steps,
                },
            )[0]
            # print(f"  Step {step}: {(time.time() - t_step_start)*1000:.2f} ms")
            
        t_denoiser = time.time() - t0
        print(f"Denoiser time ({steps} steps): {t_denoiser*1000:.2f} ms (Avg {(t_denoiser/steps)*1000:.2f} ms/step)")

        # 5. Decoder
        t0 = time.time()
        waveforms = self.voice_decoder.run(None, {"latents": latents})[0]
        t_decoder = time.time() - t0
        print(f"Decoder time: {t_decoder*1000:.2f} ms")
        
        total_time = time.time() - start_total
        print(f"Total Inference Time: {total_time:.4f} s")
        
if __name__ == "__main__":
    # Point to the assets logic in the repo
    # Assuming we run this from repo root
    assets_dir = os.path.abspath("assets") 
    
    # First warmup
    tts = BenchmarkTTS(assets_dir, use_gpu=True)
    tts.benchmark("Warmup text", steps=5)
    
    print("-" * 20)
    # Real run
    tts.benchmark("The quick brown fox jumps over the lazy dog.", steps=15)
