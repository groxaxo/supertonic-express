# Supertonic FastAPI Server - API Documentation

This document describes the OpenAI-compatible FastAPI server for Supertonic TTS.

## Overview

The Supertonic FastAPI server provides an OpenAI-compatible API for text-to-speech generation. It supports:

- ✅ OpenAI-compatible `/v1/audio/speech` endpoint
- ✅ Streaming audio generation
- ✅ Multiple audio formats (MP3, Opus, AAC, FLAC, WAV, PCM)
- ✅ Multiple voice styles
- ✅ Multi-language support (English, Korean, Spanish, Portuguese, French)
- ✅ CPU and GPU support
- ✅ Docker deployment

## Quick Start

### Local Development

1. **Clone the repository and download models:**

```bash
git clone https://github.com/supertone-inc/supertonic.git
cd supertonic
git clone https://huggingface.co/Supertone/supertonic-2 assets
```

2. **Install dependencies:**

```bash
cd py
pip install -r requirements.txt
```

3. **Start the server:**

```bash
./start_server.sh
```

The server will start on `http://localhost:8880`

### Docker Deployment

#### CPU Version

```bash
cd docker/cpu
docker-compose up -d
```

#### GPU Version

```bash
cd docker/gpu
docker-compose up -d
```

## API Endpoints

### Text-to-Speech

**Endpoint:** `POST /v1/audio/speech`

Generate speech from text input.

**Request Body:**

```json
{
  "model": "supertonic",
  "input": "Hello, this is a test of the text to speech system.",
  "voice": "M1",
  "response_format": "mp3",
  "speed": 1.0,
  "stream": true,
  "lang_code": "en",
  "total_steps": 5
}
```

**Parameters:**

- `model` (string): Model to use. Options: `supertonic`, `tts-1`, `tts-1-hd`
- `input` (string, required): The text to convert to speech
- `voice` (string): Voice style to use (default: `M1`)
- `response_format` (string): Audio format. Options: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (default: `mp3`)
- `speed` (float): Speed multiplier, 0.25 to 4.0 (default: 1.0)
- `stream` (boolean): Enable streaming response (default: `true`)
- `lang_code` (string): Language code. Options: `en`, `ko`, `es`, `pt`, `fr` (auto-detected if not provided)
- `total_steps` (integer): Number of denoising steps, 1 to 20 (default: 5, higher = better quality but slower)

**Response:**

Audio data in the requested format.

**Example using curl:**

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

**Example using Python OpenAI client:**

```python
from openai import OpenAI

# Point to local server
client = OpenAI(
    base_url="http://localhost:8880/v1",
    api_key="not-needed"  # API key not required for local server
)

# Generate speech
response = client.audio.speech.create(
    model="supertonic",
    voice="M1",
    input="Hello, this is a test of the Supertonic text to speech system."
)

# Save to file
response.stream_to_file("output.mp3")
```

**Streaming example:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8880/v1",
    api_key="not-needed"
)

with client.audio.speech.with_streaming_response.create(
    model="supertonic",
    voice="M1",
    input="This is a streaming response example.",
    response_format="opus"
) as response:
    response.stream_to_file("output.opus")
```

### List Voices

**Endpoint:** `GET /v1/audio/voices`

Get a list of available voice styles.

**Response:**

```json
{
  "voices": [
    {
      "name": "M1",
      "language": "en",
      "description": "Supertonic voice style: M1"
    },
    {
      "name": "F1",
      "language": "en",
      "description": "Supertonic voice style: F1"
    }
  ]
}
```

**Example:**

```bash
curl http://localhost:8880/v1/audio/voices
```

### List Models

**Endpoint:** `GET /v1/models`

Get a list of available models (OpenAI-compatible).

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "supertonic",
      "object": "model",
      "created": 1704067200,
      "owned_by": "supertone"
    }
  ]
}
```

### Health Check

**Endpoint:** `GET /health`

Check the health status of the server.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

## Voice Styles

Available voice styles depend on the voice JSON files in the `assets/voice_styles` directory. Common voices include:

- `M1`, `M2`, `M3`, `M4`, `M5` - Male voices
- `F1`, `F2`, `F3`, `F4`, `F5` - Female voices

See the [Supertonic voices documentation](https://supertone-inc.github.io/supertonic-py/voices/) for more details.

## Language Support

Supported languages:

- `en` - English
- `ko` - Korean
- `es` - Spanish
- `pt` - Portuguese
- `fr` - French

The server will auto-detect the language if not specified.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ONNX_DIR` | `../assets/onnx` | Path to ONNX models directory |
| `VOICE_STYLES_DIR` | `../assets/voice_styles` | Path to voice styles directory |
| `USE_GPU` | `false` | Enable GPU acceleration |
| `PORT` | `8880` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Performance Tips

1. **Quality vs Speed:** Adjust `total_steps` parameter:
   - `total_steps=2`: Fastest, lower quality
   - `total_steps=5`: Balanced (default)
   - `total_steps=10`: High quality, slower

2. **Streaming:** Enable streaming for faster perceived response time

3. **GPU:** Use GPU version for significant performance improvement

## Interactive Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8880/docs
- **ReDoc:** http://localhost:8880/redoc

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

Error responses include details:

```json
{
  "error": "invalid_voice",
  "message": "Voice 'invalid' not found. Available voices: M1, F1, M2, F2"
}
```

## License

MIT License - See LICENSE file for details.
