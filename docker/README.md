# Docker Deployment for Supertonic TTS API

This directory contains Docker configurations for deploying the Supertonic FastAPI server.

## 📁 Directory Structure

```
docker/
├── cpu/                 # CPU-optimized deployment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
└── gpu/                 # GPU-accelerated deployment
    ├── Dockerfile
    ├── docker-compose.yml
    └── .dockerignore
```

## 🚀 Quick Start

### CPU Version (Recommended for Most Users)

```bash
cd cpu
docker-compose up -d
```

The API will be available at `http://localhost:8880`

### GPU Version (For High-Performance Deployments)

Requires:
- NVIDIA GPU
- NVIDIA Docker runtime installed
- CUDA-compatible GPU

```bash
cd gpu
docker-compose up -d
```

## 📋 Prerequisites

### For Both Versions

1. **Docker installed:**
   ```bash
   # Check Docker installation
   docker --version
   docker-compose --version
   ```

2. **Models downloaded:**
   
   The Docker containers expect models to be available in the `assets` directory at the repository root:
   
   ```bash
   # From repository root
   git clone https://huggingface.co/Supertone/supertonic-2 assets
   ```

### For GPU Version Only

3. **NVIDIA Docker Runtime:**
   
   ```bash
   # Install nvidia-docker2
   # Ubuntu/Debian
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   
   # Test NVIDIA Docker
   docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
   ```

## 🔧 Configuration

### Environment Variables

Both CPU and GPU versions support these environment variables (set in `docker-compose.yml`):

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_GPU` | `false` (CPU) / `true` (GPU) | Enable GPU acceleration |
| `ONNX_DIR` | `/app/assets/onnx` | Path to ONNX models |
| `VOICE_STYLES_DIR` | `/app/assets/voice_styles` | Path to voice styles |
| `PORT` | `8880` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Volumes

The docker-compose files mount the `assets` directory:

```yaml
volumes:
  - ../../assets:/app/assets:ro  # Read-only mount
```

This allows the container to access models without copying them into the image.

## 🎯 Usage

### Starting the Service

```bash
# CPU version
cd cpu
docker-compose up -d

# GPU version
cd gpu
docker-compose up -d
```

### Viewing Logs

```bash
docker-compose logs -f
```

### Stopping the Service

```bash
docker-compose down
```

### Rebuilding the Image

```bash
docker-compose build
docker-compose up -d
```

## 🧪 Testing the Deployment

Once the container is running, test it:

```bash
# Health check
curl http://localhost:8880/health

# List available voices
curl http://localhost:8880/v1/audio/voices

# Generate speech
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "supertonic",
    "input": "Hello from Docker!",
    "voice": "M1"
  }' \
  --output test.mp3
```

## 📊 Resource Requirements

### CPU Version

- **Memory:** 2-4 GB RAM minimum
- **Disk:** ~500 MB for image + model sizes
- **CPU:** 2+ cores recommended

### GPU Version

- **Memory:** 4-8 GB RAM minimum
- **Disk:** ~2 GB for image + model sizes
- **GPU:** NVIDIA GPU with 4GB+ VRAM
- **CUDA:** Compatible with CUDA 12.2

## 🔍 Troubleshooting

### Container Won't Start

1. **Check logs:**
   ```bash
   docker-compose logs
   ```

2. **Verify models are present:**
   ```bash
   ls -la ../../assets/onnx/
   ls -la ../../assets/voice_styles/
   ```

3. **Check port availability:**
   ```bash
   lsof -i :8880
   ```

### GPU Not Detected (GPU Version)

1. **Verify NVIDIA Docker runtime:**
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
   ```

2. **Check docker-compose GPU configuration:**
   ```bash
   docker-compose config
   ```

### Models Not Loading

1. **Verify volume mount:**
   ```bash
   docker-compose exec supertonic-tts-cpu ls -la /app/assets/
   ```

2. **Check permissions:**
   ```bash
   ls -la ../../assets/
   ```

## 🌐 Integration with Open-WebUI

To use with Open-WebUI, update your Open-WebUI docker-compose or configuration:

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - OPENAI_API_BASE_URL=http://supertonic-tts-cpu:8880/v1
      - OPENAI_API_KEY=not-needed
```

See the [Open-WebUI Integration Guide](../docs/OPEN_WEBUI_INTEGRATION.md) for detailed setup.

## 🔐 Security Considerations

1. **Network exposure:** By default, the service binds to `0.0.0.0:8880`. Consider using a reverse proxy (nginx, Traefik) for production.

2. **API authentication:** The current implementation doesn't require API keys. Add authentication middleware if needed.

3. **Resource limits:** Add resource constraints in docker-compose for production:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '4'
         memory: 4G
   ```

## 📚 Additional Documentation

- [API Documentation](../docs/API.md)
- [Open-WebUI Integration](../docs/OPEN_WEBUI_INTEGRATION.md)
- [Python README](../py/README_API.md)

## 🐛 Known Issues

1. **GPU support:** GPU mode is experimental. Report issues on GitHub.
2. **First request slow:** The first request may be slower as models load into memory.

## 📞 Support

For issues and questions:
- **Supertonic:** https://github.com/supertone-inc/supertonic
- **Docker Issues:** Open an issue on GitHub

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.
