import requests
import time
import json

URL = "http://localhost:8880/v1/audio/speech"
HEADERS = {"Content-Type": "application/json"}

def test_tts(text, voice="M1"):
    payload = {
        "model": "supertonic",
        "voice": voice,
        "input": text
    }
    
    start_time = time.time()
    try:
        response = requests.post(URL, headers=HEADERS, json=payload, stream=True)
        response.raise_for_status()
        
        # Consume the stream to ensure full processing
        size = 0
        for chunk in response.iter_content(chunk_size=8192):
            size += len(chunk)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate Audio Duration (16-bit PCM, 44.1kHz, Mono)
        # 44100 samples/s * 2 bytes/sample = 88200 bytes/s
        audio_duration_s = size / 88200
        rtf = duration / audio_duration_s if audio_duration_s > 0 else 0
        
        print(f"Generated audio for: '{text[:20]}...'")
        print(f"  - Size: {size} bytes")
        print(f"  - Gen Time: {duration:.4f}s")
        print(f"  - Audio Duration: {audio_duration_s:.4f}s")
        print(f"  - RTF: {rtf:.4f} ({1/rtf:.2f}x Real-time)")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting TTS Load Test...")
    
    test_cases = [
        "Hello world! This is a test of the Supertonic TTS system.",
        "The quick brown fox jumps over the lazy dog.",
        "Supertonic is a lightning-fast, on-device text-to-speech system designed for extreme performance.",
        "In 2026, the world saw significant advancements in AI technology.",
        "Please read this number: 123,456.78"
    ]
    
    # Run a few iterations
    for i in range(3):
        print(f"\nIteration {i+1}:")
        for text in test_cases:
            test_tts(text)
            time.sleep(1)  # Small delay between requests
            
    print("\nTest completed.")
