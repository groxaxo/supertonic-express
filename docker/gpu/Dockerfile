FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Install Python and system dependencies
RUN apt-get update -y && \
    apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    libsndfile1 \
    ffmpeg \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

USER appuser
WORKDIR /app

# Copy requirements
COPY --chown=appuser:appuser py/requirements.txt ./requirements.txt

# Install onnxruntime-gpu instead of cpu version
RUN pip install --no-cache-dir --user -r requirements.txt && \
    pip uninstall -y onnxruntime && \
    pip install --no-cache-dir --user onnxruntime-gpu==1.23.1

# Copy application code
COPY --chown=appuser:appuser py/ ./py/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/py \
    PATH="/home/appuser/.local/bin:$PATH" \
    USE_GPU=true \
    ONNX_DIR=/app/assets/onnx \
    VOICE_STYLES_DIR=/app/assets/voice_styles \
    PORT=8880

# Create directory for assets
RUN mkdir -p /app/assets

# Expose port
EXPOSE 8880

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8880/health || exit 1

# Run the FastAPI server
CMD ["python3", "-m", "uvicorn", "py.api.src.main:app", "--host", "0.0.0.0", "--port", "8880"]
