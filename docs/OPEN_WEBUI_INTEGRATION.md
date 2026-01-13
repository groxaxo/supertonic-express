# Open-WebUI Integration Guide

This guide explains how to integrate Supertonic FastAPI server with Open-WebUI for text-to-speech functionality.

## What is Open-WebUI?

[Open-WebUI](https://github.com/open-webui/open-webui) is a user-friendly web interface for LLMs and AI services. It supports OpenAI-compatible TTS APIs, making it easy to integrate Supertonic TTS.

## Prerequisites

1. Supertonic FastAPI server running (see [API.md](API.md))
2. Open-WebUI installed and running

## Setup Instructions

### Step 1: Start Supertonic Server

Make sure your Supertonic TTS server is running:

```bash
cd py
./start_server.sh
```

Or using Docker:

```bash
cd docker/cpu
docker-compose up -d
```

The server should be accessible at `http://localhost:8880`

### Step 2: Configure Open-WebUI

#### Option A: Using Environment Variables

When starting Open-WebUI, set the following environment variables:

```bash
export OPENAI_API_BASE_URL=http://localhost:8880/v1
export OPENAI_API_KEY=not-needed
```

#### Option B: Using Docker Compose

If running Open-WebUI with Docker Compose, add these environment variables:

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_BASE_URL=http://host.docker.internal:8880/v1
      - OPENAI_API_KEY=not-needed
      # Enable TTS
      - ENABLE_OPENAI_API=true
```

**Note:** Use `host.docker.internal` instead of `localhost` when Open-WebUI is running in Docker to access services on the host machine.

#### Option C: Web UI Configuration

1. Open Open-WebUI in your browser (typically `http://localhost:3000`)
2. Go to **Settings** → **Audio**
3. Configure TTS settings:
   - **TTS Engine:** OpenAI
   - **API Base URL:** `http://localhost:8880/v1`
   - **API Key:** `not-needed` (or leave empty)
   - **Model:** `supertonic` or `tts-1`
   - **Voice:** Select from available voices (M1, F1, etc.)

### Step 3: Test the Integration

1. In Open-WebUI, type a message in the chat
2. Click the speaker icon or enable automatic TTS
3. The message should be converted to speech using Supertonic TTS

## Configuration Options

### Voice Selection

Open-WebUI allows you to select different voices. Available voices in Supertonic:

- **Male voices:** M1, M2, M3, M4, M5
- **Female voices:** F1, F2, F3, F4, F5

### Audio Format

The default format is MP3, which works well with browsers. You can configure this in the server settings if needed.

### Language Support

Supertonic automatically detects the language from the text. Supported languages:

- English (en)
- Korean (ko)
- Spanish (es)
- Portuguese (pt)
- French (fr)

## Docker Compose Example

Here's a complete docker-compose.yml that runs both Supertonic and Open-WebUI together:

```yaml
version: '3.8'

services:
  supertonic-tts:
    build:
      context: .
      dockerfile: docker/cpu/Dockerfile
    container_name: supertonic-tts
    ports:
      - "8880:8880"
    volumes:
      - ./assets:/app/assets:ro
    environment:
      - USE_GPU=false
      - PORT=8880
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    environment:
      # Point to Supertonic TTS service
      - OPENAI_API_BASE_URL=http://supertonic-tts:8880/v1
      - OPENAI_API_KEY=not-needed
      - ENABLE_OPENAI_API=true
      # Optional: Set default voice
      - TTS_VOICE=M1
      - TTS_MODEL=supertonic
    depends_on:
      - supertonic-tts
    volumes:
      - open-webui-data:/app/backend/data
    restart: unless-stopped

volumes:
  open-webui-data:
```

Save this as `docker-compose.yml` in the root directory, then run:

```bash
docker-compose up -d
```

Access Open-WebUI at `http://localhost:3000`

## Troubleshooting

### TTS Not Working

1. **Check if Supertonic server is running:**
   ```bash
   curl http://localhost:8880/health
   ```

2. **Test TTS directly:**
   ```bash
   curl -X POST http://localhost:8880/v1/audio/speech \
     -H "Content-Type: application/json" \
     -d '{"model": "supertonic", "input": "test", "voice": "M1"}' \
     --output test.mp3
   ```

3. **Check Open-WebUI logs:**
   ```bash
   docker logs open-webui
   ```

### Connection Refused

If running both services in Docker:
- Make sure you're using the service name (`supertonic-tts`) or `host.docker.internal`, not `localhost`
- Ensure both services are on the same Docker network

### Voice Not Available

1. **List available voices:**
   ```bash
   curl http://localhost:8880/v1/audio/voices
   ```

2. Make sure the voice style JSON files exist in `assets/voice_styles/`

### Slow Response

1. Reduce `total_steps` for faster generation (lower quality)
2. Use GPU version if available
3. Enable streaming in Open-WebUI settings

## Advanced Configuration

### Custom Voice Styles

To add custom voice styles:

1. Place voice style JSON files in `assets/voice_styles/`
2. Restart the Supertonic server
3. The new voices will be automatically available

### Performance Tuning

For better performance in production:

1. **Use GPU version:** Much faster for inference
   ```bash
   cd docker/gpu
   docker-compose up -d
   ```

2. **Adjust denoising steps:** Lower steps = faster but lower quality
   - Edit `py/api/src/core/config.py`
   - Change `default_total_steps` (default: 5)

3. **Enable caching:** Consider adding response caching for repeated requests

## Integration Examples

### Python Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8880/v1",
    api_key="not-needed"
)

response = client.audio.speech.create(
    model="supertonic",
    voice="M1",
    input="Hello from Open-WebUI integration!"
)

response.stream_to_file("output.mp3")
```

### JavaScript/Node.js Client

```javascript
const OpenAI = require('openai');

const client = new OpenAI({
    baseURL: 'http://localhost:8880/v1',
    apiKey: 'not-needed'
});

async function generateSpeech() {
    const response = await client.audio.speech.create({
        model: 'supertonic',
        voice: 'M1',
        input: 'Hello from Open-WebUI integration!'
    });
    
    const buffer = Buffer.from(await response.arrayBuffer());
    require('fs').writeFileSync('output.mp3', buffer);
}

generateSpeech();
```

## Support

For issues and questions:

- **Supertonic:** https://github.com/supertone-inc/supertonic
- **Open-WebUI:** https://github.com/open-webui/open-webui

## Next Steps

- Explore different voice styles and find your favorite
- Experiment with different denoising steps for quality/speed tradeoff
- Try multi-language support
- Consider GPU deployment for production use
