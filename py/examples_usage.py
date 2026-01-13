"""
Example usage of Supertonic FastAPI Server with OpenAI client
This example demonstrates how to use the OpenAI Python client
to interact with the Supertonic TTS API.
"""

def example_basic():
    """Basic usage example"""
    print("Example 1: Basic Text-to-Speech")
    print("-" * 60)
    print()
    print("from openai import OpenAI")
    print()
    print("client = OpenAI(")
    print("    base_url='http://localhost:8880/v1',")
    print("    api_key='not-needed'")
    print(")")
    print()
    print("response = client.audio.speech.create(")
    print("    model='supertonic',")
    print("    voice='M1',")
    print("    input='Hello, this is Supertonic text to speech!'")
    print(")")
    print()
    print("response.stream_to_file('output.mp3')")
    print()


def example_streaming():
    """Streaming example"""
    print("Example 2: Streaming Response")
    print("-" * 60)
    print()
    print("from openai import OpenAI")
    print()
    print("client = OpenAI(")
    print("    base_url='http://localhost:8880/v1',")
    print("    api_key='not-needed'")
    print(")")
    print()
    print("with client.audio.speech.with_streaming_response.create(")
    print("    model='supertonic',")
    print("    voice='M1',")
    print("    input='This is a streaming example',")
    print("    response_format='opus'")
    print(") as response:")
    print("    response.stream_to_file('output.opus')")
    print()


def example_curl():
    """cURL example"""
    print("Example 3: Using cURL")
    print("-" * 60)
    print()
    print("curl -X POST http://localhost:8880/v1/audio/speech \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print("    \"model\": \"supertonic\",")
    print("    \"input\": \"Hello world!\",")
    print("    \"voice\": \"M1\",")
    print("    \"response_format\": \"mp3\",")
    print("    \"speed\": 1.0")
    print("  }' \\")
    print("  --output speech.mp3")
    print()


def example_custom_settings():
    """Custom settings example"""
    print("Example 4: Custom Settings")
    print("-" * 60)
    print()
    print("from openai import OpenAI")
    print()
    print("client = OpenAI(")
    print("    base_url='http://localhost:8880/v1',")
    print("    api_key='not-needed'")
    print(")")
    print()
    print("response = client.audio.speech.create(")
    print("    model='supertonic',")
    print("    voice='F1',              # Female voice")
    print("    input='Custom quality settings example',")
    print("    response_format='opus',  # High-quality Opus format")
    print("    speed=1.1                # Slightly faster")
    print(")")
    print()
    print("response.stream_to_file('output.opus')")
    print()


def example_list_voices():
    """List voices example"""
    print("Example 5: List Available Voices")
    print("-" * 60)
    print()
    print("import requests")
    print()
    print("response = requests.get('http://localhost:8880/v1/audio/voices')")
    print("voices = response.json()")
    print("print(voices)")
    print()


def main():
    """Show all examples"""
    print()
    print("=" * 60)
    print("Supertonic FastAPI Server - Usage Examples")
    print("=" * 60)
    print()
    print("Before running these examples, make sure:")
    print("1. The server is running: ./start_server.sh")
    print("2. Models are downloaded: git clone https://huggingface.co/Supertone/supertonic-2 ../assets")
    print("3. OpenAI Python client is installed: pip install openai")
    print()
    print("=" * 60)
    print()
    
    example_basic()
    example_streaming()
    example_curl()
    example_custom_settings()
    example_list_voices()
    
    print("=" * 60)
    print()
    print("For more examples and documentation:")
    print("- API Docs: http://localhost:8880/docs")
    print("- README: ../docs/API.md")
    print("- Open-WebUI Integration: ../docs/OPEN_WEBUI_INTEGRATION.md")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
