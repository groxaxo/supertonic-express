
import sys
import os
import time
import numpy as np

# Add py directory to path
sys.path.append(os.path.join(os.getcwd(), "py"))

from helper import SupertonicTTS

def benchmark_cpu():
    assets_dir = os.path.abspath("assets")
    print(f"Loading model from {assets_dir} (CPU)...")
    
    # Initialize with GPU=False
    try:
        tts = SupertonicTTS(assets_dir, use_gpu=False)
    except Exception as e:
        print(f"Failed to initialize TTS: {e}")
        return

    text = "The quick brown fox jumps over the lazy dog."
    
    print("Warmup...")
    tts.generate([text], steps=5)
    
    print("-" * 20)
    print(f"Benchmarking: '{text}'")
    
    steps = 15
    start_time = time.time()
    results = tts.generate([text], steps=steps)
    end_time = time.time()
    
    duration = end_time - start_time
    audio_len_s = len(results[0]) / 44100
    rtf = duration / audio_len_s
    
    print(f"Inference Time: {duration:.4f}s")
    print(f"Audio Duration: {audio_len_s:.2f}s")
    print(f"RTF: {rtf:.4f}")
    print(f"Speedup: {1/rtf:.2f}x Real-time")

if __name__ == "__main__":
    benchmark_cpu()
