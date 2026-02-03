FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY py/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt huggingface-hub

# Copy the application
COPY py/ ./py/
WORKDIR /app/py

# Install the package
RUN pip install -e .

# Download the ONNX model
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('onnx-community/Supertonic-TTS-2-ONNX', local_dir='../assets', repo_type='model')"

# Set environment variables
ENV ONNX_DIR=/app/assets
ENV VOICE_STYLES_DIR=/app/assets
ENV PORT=8880
ENV HOST=0.0.0.0

EXPOSE 8880

# Start the server
CMD ["python", "-m", "uvicorn", "api.src.main:app", "--host", "0.0.0.0", "--port", "8880"]
