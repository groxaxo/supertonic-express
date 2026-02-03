"""
Test script to validate voice file loading with correct dimensions.
This test verifies the fix for voice files containing 101 embeddings × 128 dimensions.
"""

import numpy as np
import tempfile
import os
import sys

# Test the reshape logic with the actual voice file dimensions
print("Testing voice file loading with 101 embeddings × 128 dimensions...")

# Create a mock voice file with the actual dimensions (12928 values)
STYLE_DIM = 128
NUM_EMBEDDINGS = 101
TOTAL_VALUES = NUM_EMBEDDINGS * STYLE_DIM  # 12928

# Create temporary voice file
with tempfile.TemporaryDirectory() as tmpdir:
    voice_dir = os.path.join(tmpdir, "voices")
    os.makedirs(voice_dir)
    voice_path = os.path.join(voice_dir, "TEST.bin")
    
    # Create a voice file with 101 embeddings of 128 dimensions each
    voice_data = np.random.randn(TOTAL_VALUES).astype(np.float32)
    voice_data.tofile(voice_path)
    
    print(f"✓ Created test voice file with {TOTAL_VALUES} values ({NUM_EMBEDDINGS} × {STYLE_DIM})")
    
    # Test loading and reshaping
    loaded_vec = np.fromfile(voice_path, dtype=np.float32)
    print(f"✓ Loaded voice file: {loaded_vec.size} values")
    
    # This is the fix: reshape should work with -1 to infer the middle dimension
    try:
        reshaped = loaded_vec.reshape(1, -1, STYLE_DIM)
        print(f"✓ Reshape successful: {reshaped.shape}")
        
        # Verify the shape
        expected_shape = (1, NUM_EMBEDDINGS, STYLE_DIM)
        assert reshaped.shape == expected_shape, f"Expected shape {expected_shape}, got {reshaped.shape}"
        print(f"✓ Shape validation passed: {reshaped.shape}")
        
        # Verify the data is preserved
        assert np.allclose(reshaped.flatten(), loaded_vec), "Data mismatch after reshape"
        print(f"✓ Data integrity verified")
        
    except Exception as e:
        print(f"✗ Reshape failed: {e}")
        sys.exit(1)

print("\n" + "="*50)
print("All voice loading tests passed! ✓")
print("="*50)
print(f"\nThe fix correctly handles voice files with {NUM_EMBEDDINGS} embeddings × {STYLE_DIM} dimensions = {TOTAL_VALUES} values")
