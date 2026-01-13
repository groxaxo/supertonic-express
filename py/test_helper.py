"""
Test script to validate the helper module structure.
This test does not require model files.
"""

import sys
import os

# Test imports
print("Testing imports...")
try:
    from helper import (
        SupertonicTTS,
        load_text_to_speech,
        load_voice_style,
        chunk_text,
        sanitize_filename,
        timer,
    )
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test utility functions
print("\nTesting utility functions...")

# Test chunk_text
text = "This is a test. This is another sentence. And one more for good measure."
chunks = chunk_text(text, max_len=30)
assert len(chunks) > 1, "chunk_text should split the text"
print(f"✓ chunk_text works: {len(chunks)} chunks")

# Test sanitize_filename
filename = sanitize_filename("Hello, World! @#$%", max_len=10)
assert filename == "Hello__Wor", f"Expected 'Hello__Wor', got '{filename}'"
print(f"✓ sanitize_filename works: '{filename}'")

# Test load_voice_style (should extract voice name from path)
voice = load_voice_style(["/path/to/M1.bin"], verbose=False)
assert voice == "M1", f"Expected 'M1', got '{voice}'"
print(f"✓ load_voice_style works: '{voice}'")

# Test SupertonicTTS class constants
print("\nTesting SupertonicTTS class constants...")
assert SupertonicTTS.SAMPLE_RATE == 44100
assert SupertonicTTS.LANGUAGES == ["en", "ko", "es", "pt", "fr"]
assert SupertonicTTS.LATENT_DIM == 24
assert SupertonicTTS.STYLE_DIM == 128
print("✓ All SupertonicTTS constants are correct")

# Test that required methods exist
print("\nTesting class structure...")
methods = ["_load_style", "generate", "__call__", "batch"]
for method in methods:
    assert hasattr(SupertonicTTS, method), f"SupertonicTTS missing method: {method}"
print(f"✓ All required methods exist: {', '.join(methods)}")

print("\n" + "="*50)
print("All tests passed! ✓")
print("="*50)
print("\nNote: To fully test the model, you need to:")
print("1. Download the model: python -c \"from huggingface_hub import snapshot_download; snapshot_download('onnx-community/Supertonic-TTS-2-ONNX', local_dir='../assets')\"")
print("2. Run example: python example_onnx.py --onnx-dir ../assets")
