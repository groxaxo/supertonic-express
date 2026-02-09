# Supertonic FastAPI Server

OpenAI-compatible FastAPI server for Supertonic TTS.

## Features

- ✅ **OpenAI-Compatible API** - Drop-in replacement for OpenAI TTS API
- ✅ **Streaming Support** - Real-time audio streaming
- ✅ **Multiple Formats** - MP3, Opus, AAC, FLAC, WAV, PCM
- ✅ **Multiple Voices** - Various male and female voice styles
- ✅ **Multi-Language** - English, Korean, Spanish, Portuguese, French
- ✅ **CPU & GPU Support** - Optimized for both CPU and GPU
- ✅ **Docker Ready** - Easy deployment with Docker
- ✅ **Open-WebUI Compatible** - Works out of the box with Open-WebUI

## Quick Start

### Local Development

1. **Install dependencies:**

```bash
cd py
pip install -e .
```

2. **Download the ONNX model from Hugging Face:**

```bash
# Install huggingface-hub if not already installed
pip install huggingface-hub

# Download the model to the assets directory
cd ..
python -c "from huggingface_hub import snapshot_download; snapshot_download('onnx-community/Supertonic-TTS-2-ONNX', local_dir='assets')"
cd py
```

3. **Start the server:**

```bash
../scripts/run_server_cpu.sh
```

Or manually:

```bash
python -m uvicorn api.src.main:app --host 0.0.0.0 --port 8880 --reload
```

The server will start at `http://localhost:8880`

```bash
cd ../docker/cpu
docker-compose up -d
```

#### GPU Version (For production/high performance)

```bash
cd ../docker/gpu
docker-compose up -d
```

## Usage

### OpenAI Python Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8880/v1",
    api_key="not-needed"
)

response = client.audio.speech.create(
    model="supertonic",
    voice="M1",
    input="Hello, this is Supertonic text to speech!"
)

response.stream_to_file("output.mp3")
```

### cURL

```bash
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "supertonic",
    "input": "Hello world!",
    "voice": "M1",
    "response_format": "mp3"
  }' \
  --output speech.mp3
```

### Streaming

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8880/v1",
    api_key="not-needed"
)

with client.audio.speech.with_streaming_response.create(
    model="supertonic",
    voice="M1",
    input="This will be streamed!",
    response_format="opus"
) as response:
    response.stream_to_file("output.opus")
```

## API Endpoints

- `POST /v1/audio/speech` - Generate speech from text
- `GET /v1/audio/voices` - List available voices
- `GET /v1/models` - List available models
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ONNX_DIR` | `../assets/onnx` | Path to ONNX models |
| `VOICE_STYLES_DIR` | `../assets/voice_styles` | Path to voice styles |
| `USE_GPU` | `false` | Enable GPU acceleration |
| `PORT` | `8880` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

## Available Voices

Voice styles depend on the JSON files in `assets/voice_styles/`. Common voices:

- **Male:** M1, M2, M3, M4, M5
- **Female:** F1, F2, F3, F4, F5

List all available voices:

```bash
curl http://localhost:8880/v1/audio/voices
```

## Documentation

- [API Documentation](../../docs/API.md) - Complete API reference
- [Open-WebUI Integration](../../docs/OPEN_WEBUI_INTEGRATION.md) - Guide for Open-WebUI integration

## Performance

### Quality Settings

Adjust the `total_steps` parameter for quality vs speed:

- `total_steps=2` - Fast, lower quality
- `total_steps=5` - Quick, balanced quality
- `total_steps=15` - High quality (default)
- `total_steps=20` - Maximum quality, slower

### GPU Acceleration

For significant performance improvements, use the GPU version:

```bash
cd ../docker/gpu
docker-compose up -d
```

## Development

### Project Structure

```
py/
├── api/
│   └── src/
│       ├── core/          # Configuration
│       ├── routers/       # API endpoints
│       ├── services/      # Business logic
│       └── structures/    # Data models
├── helper.py              # ONNX inference helpers
├── example_onnx.py        # Example script
├── requirements.txt       # Dependencies
└── start_server.sh        # Startup script
```

### Running Tests

```bash
# Test TTS generation
python example_onnx.py

# Test API endpoint
curl http://localhost:8880/health
```

## Troubleshooting

### Models Not Found

Make sure you've downloaded the models:

```bash
cd ..
git clone https://huggingface.co/Supertone/supertonic-2 assets
```

### ffmpeg Not Found

Install ffmpeg for audio format conversion:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Port Already in Use

Change the port:

```bash
export PORT=8881
./start_server.sh
```

## License

MIT License - See [LICENSE](../LICENSE) for details.

## Credits

- **Supertonic Models:** [Supertone Inc.](https://huggingface.co/Supertone/supertonic-2)
- **FastAPI:** [FastAPI Framework](https://fastapi.tiangolo.com/)
