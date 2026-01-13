# Supertonic Python Implementation

This is the Python implementation of Supertonic TTS using the [onnx-community/Supertonic-TTS-2-ONNX](https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX) model.

## Features

- **ONNX Runtime**: Fast inference using optimized ONNX models
- **Transformers Tokenizer**: Uses Hugging Face's AutoTokenizer for text processing
- **Multi-language Support**: English, Korean, Spanish, Portuguese, French
- **Multiple Voices**: Various male and female voice styles (.bin format)
- **FastAPI Server**: OpenAI-compatible REST API with streaming support
- **Batch Processing**: Efficient batch inference for multiple texts

## Installation

```bash
cd py
pip install -e .
```

## Downloading the Model

The model files need to be downloaded from Hugging Face:

```bash
# Install huggingface-hub
pip install huggingface-hub

# Download the model to the assets directory
cd ..
python -c "from huggingface_hub import snapshot_download; snapshot_download('onnx-community/Supertonic-TTS-2-ONNX', local_dir='assets')"
cd py
```

This will download:
- ONNX models (`text_encoder.onnx`, `latent_denoiser.onnx`, `voice_decoder.onnx`)
- Tokenizer files
- Voice embeddings (.bin files)

## Quick Start

### Basic Usage

```python
from helper import SupertonicTTS

# Initialize the model
tts = SupertonicTTS(model_path="../assets", use_gpu=False)

# Generate audio
prompts = ["Hello, this is a test!"]
audio_data = tts.generate(
    prompts,
    voice="M1",      # Voice style (M1, F1, etc.)
    speed=1.0,       # Speech speed
    steps=5,         # Inference steps (higher = better quality)
    language="en"    # Language code
)

# Save the audio
import soundfile as sf
sf.write("output.wav", audio_data[0], tts.SAMPLE_RATE)
```

### Command Line

```bash
# Basic usage
python example_onnx.py --onnx-dir ../assets

# Custom parameters
python example_onnx.py \
    --onnx-dir ../assets \
    --voice-style M1 \
    --text "Hello from Supertonic!" \
    --lang en \
    --speed 1.05 \
    --total-step 10
```

### FastAPI Server

Start the OpenAI-compatible API server:

```bash
./start_server.sh
```

See [README_API.md](README_API.md) for full API documentation.

## Model Architecture

The new model uses a three-stage architecture:

1. **Text Encoder** (`text_encoder.onnx`): 
   - Takes tokenized text and voice embeddings
   - Outputs text representations and duration predictions

2. **Latent Denoiser** (`latent_denoiser.onnx`):
   - Performs iterative denoising on latent representations
   - Controlled by number of inference steps (higher = better quality)

3. **Voice Decoder** (`voice_decoder.onnx`):
   - Decodes latent representations to audio waveforms
   - Outputs 44.1kHz audio

## Voice Files

Voice embeddings are stored as binary files (`.bin` format) in the `assets/voices/` directory:
- `M1.bin`, `M2.bin`, etc. - Male voices
- `F1.bin`, `F2.bin`, etc. - Female voices

Each file contains a 128-dimensional style vector.

## Migration from Old Model

This implementation replaces the previous model structure which used:
- `duration_predictor.onnx`, `text_encoder.onnx`, `vector_estimator.onnx`, `vocoder.onnx`
- JSON files for voice styles
- Custom Unicode processor for tokenization

The new model provides:
- Simpler architecture with 3 models instead of 4
- Standard Transformers tokenizer (better compatibility)
- Binary voice embeddings (more efficient)
- Improved performance and quality

## Configuration

Key parameters:
- `SAMPLE_RATE`: 44100 Hz
- `LATENT_DIM`: 24
- `STYLE_DIM`: 128
- `BASE_CHUNK_SIZE`: 512
- `CHUNK_COMPRESS_FACTOR`: 6

## Examples

See the following files for examples:
- `example_onnx.py` - Command-line TTS generation
- `test_helper.py` - Unit tests for the helper module
- `api/` - FastAPI server implementation

## Troubleshooting

### ImportError: No module named 'transformers'
Install the transformers library:
```bash
pip install transformers
```

### Voice not found error
Make sure you've downloaded the model files and the voice .bin files exist in `assets/voices/`.

### ONNX Runtime error
Ensure all three ONNX model files are present in `assets/onnx/`:
- `text_encoder.onnx`
- `latent_denoiser.onnx`
- `voice_decoder.onnx`

## Performance

The model is optimized for CPU inference but also supports GPU acceleration. Typical performance:
- RTF (Real-Time Factor): 0.01-0.02 on modern CPUs
- Supports batch processing for improved throughput
- Adjustable quality via `steps` parameter (1-50)

## License

See the main [LICENSE](../LICENSE) file for details.
