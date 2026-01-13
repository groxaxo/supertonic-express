"""Test OpenAI client compatibility with Supertonic API"""

import sys

try:
    # Simulated OpenAI client test (structure verification only, no actual generation)
    print("Testing OpenAI API Compatibility...")
    print()
    
    # Test 1: Check request schema structure
    from api.src.structures.schemas import OpenAISpeechRequest
    
    # Valid request
    request = OpenAISpeechRequest(
        model="supertonic",
        input="Hello world",
        voice="M1",
        response_format="mp3",
        speed=1.0,
        stream=True,
    )
    
    assert request.model == "supertonic"
    assert request.input == "Hello world"
    assert request.voice == "M1"
    assert request.response_format == "mp3"
    assert request.speed == 1.0
    assert request.stream == True
    print("✅ OpenAI request schema validation passed")
    
    # Test 2: Test with defaults
    minimal_request = OpenAISpeechRequest(input="Test")
    assert minimal_request.model == "supertonic"
    assert minimal_request.voice == "M1"
    assert minimal_request.response_format == "mp3"
    assert minimal_request.speed == 1.0
    assert minimal_request.stream == True
    print("✅ Default values test passed")
    
    # Test 3: Test speed validation
    try:
        invalid_speed = OpenAISpeechRequest(input="Test", speed=10.0)
        print("❌ Speed validation failed - should reject speed > 4.0")
        sys.exit(1)
    except Exception:
        print("✅ Speed validation test passed")
    
    # Test 4: Test required field
    try:
        no_input = OpenAISpeechRequest()
        print("❌ Required field validation failed - input should be required")
        sys.exit(1)
    except Exception:
        print("✅ Required field validation test passed")
    
    # Test 5: Check supported formats
    formats = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
    for fmt in formats:
        req = OpenAISpeechRequest(input="Test", response_format=fmt)
        assert req.response_format == fmt
    print("✅ All audio formats supported")
    
    # Test 6: Check language codes
    langs = ["en", "ko", "es", "pt", "fr"]
    for lang in langs:
        req = OpenAISpeechRequest(input="Test", lang_code=lang)
        assert req.lang_code == lang
    print("✅ All language codes supported")
    
    print()
    print("=" * 60)
    print("✅ All OpenAI compatibility tests passed!")
    print("=" * 60)
    print()
    print("Example usage with OpenAI client:")
    print()
    print("```python")
    print("from openai import OpenAI")
    print()
    print('client = OpenAI(')
    print('    base_url="http://localhost:8880/v1",')
    print('    api_key="not-needed"')
    print(')')
    print()
    print('response = client.audio.speech.create(')
    print('    model="supertonic",')
    print('    voice="M1",')
    print('    input="Hello, world!"')
    print(')')
    print()
    print('response.stream_to_file("output.mp3")')
    print("```")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
