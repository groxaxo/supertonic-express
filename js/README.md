# Supertonic TTS - JavaScript/Node.js Implementation

This is a JavaScript/Node.js implementation of Supertonic TTS using [Transformers.js](https://github.com/huggingface/transformers.js) with optimizations for Intel CPUs.

## Features

- ✅ **Pure JavaScript/Node.js** - No Python dependencies
- ✅ **Intel CPU Optimized** - SIMD instructions and multi-threading optimizations
- ✅ **Cross-platform** - Works on Windows, macOS, and Linux
- ✅ **Multi-language Support** - English, Korean, Spanish, Portuguese, French
- ✅ **Multiple Voices** - M1, F1, and other voice styles
- ✅ **Browser Compatible** - Can also run in modern browsers
- ✅ **Easy to Use** - Simple API with async/await

## Prerequisites

- Node.js >= 18.0.0
- npm or yarn

## Installation

```bash
cd js
npm install
```

This will install the required dependencies:
- `@huggingface/transformers` - Transformers.js library with ONNX Runtime

## Quick Start

### Basic Usage

```javascript
import { SupertonicTTS } from './index.js';

// Create and initialize TTS
const tts = new SupertonicTTS();
await tts.initialize();

// Generate speech
const text = 'This is really cool!';
await tts.generateAndSave(text, 'output.wav', {
  language: 'en',
  speaker_embeddings: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/M1.bin',
  num_inference_steps: 5,
  speed: 1.0,
});
```

### Using Different Voices

Available voices: M1 (male), F1 (female)

```javascript
// Female voice
await tts.generateAndSave(text, 'output_female.wav', {
  language: 'en',
  speaker_embeddings: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/F1.bin',
  num_inference_steps: 5,
  speed: 1.05,
});
```

### Multi-language Support

```javascript
// Spanish
await tts.generateAndSave('¡Hola mundo!', 'output_es.wav', {
  language: 'es',
  speaker_embeddings: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/M1.bin',
});

// Korean
await tts.generateAndSave('안녕하세요!', 'output_ko.wav', {
  language: 'ko',
  speaker_embeddings: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/F1.bin',
});
```

### Batch Processing

```javascript
const prompts = [
  "Once upon a time, there was a brave knight.",
  "Refactoring code makes it much easier to read!",
  "I love this!"
];

const audioResults = await tts.generateBatch(prompts, {
  language: 'en',
  num_inference_steps: 10,
  speed: 1.0,
});

// Save each result
for (let i = 0; i < audioResults.length; i++) {
  await audioResults[i].save(`output_${i}.wav`);
}
```

## Running Examples

We provide several example scripts:

```bash
# Basic example - single text generation
npm run example:basic

# Batch processing - multiple texts
npm run example:batch

# Advanced - multiple languages and voices
npm run example:advanced
```

## Intel CPU Optimizations

This implementation includes several optimizations for Intel CPUs to reduce bottlenecks:

### 1. Multi-threading Configuration

The library automatically configures the optimal number of threads based on your CPU:

```javascript
// Default: 75% of available CPU cores
env.backends.onnx.wasm.numThreads = Math.floor(os.cpus().length * 0.75);
```

You can override this with the `OMP_NUM_THREADS` environment variable:

```bash
# Use 4 threads
OMP_NUM_THREADS=4 node examples/basic.js
```

### 2. SIMD Instructions

SIMD (Single Instruction, Multiple Data) instructions are enabled by default for Intel CPUs:

```javascript
env.backends.onnx.wasm.simd = true;
```

This provides significant performance improvements on modern Intel processors (AVX2, AVX-512).

### 3. Optimized Threading Model

The implementation disables worker thread proxying for reduced overhead:

```javascript
env.backends.onnx.wasm.proxy = false;
```

### 4. Performance Tuning Tips

For best performance on Intel CPUs:

1. **Set appropriate thread count:**
   ```bash
   export OMP_NUM_THREADS=4  # Adjust based on your CPU
   ```

2. **Use fewer inference steps for faster generation:**
   ```javascript
   num_inference_steps: 2  // Faster, slightly lower quality
   num_inference_steps: 5  // Balanced (recommended)
   num_inference_steps: 10 // Higher quality, slower
   ```

3. **Process in batches when possible:**
   The batch processing feature amortizes initialization overhead.

## API Reference

### SupertonicTTS Class

#### Constructor

```javascript
const tts = new SupertonicTTS();
```

#### initialize(options)

Initialize the TTS pipeline.

**Parameters:**
- `options.model` (string, optional) - Model ID (default: 'onnx-community/Supertonic-TTS-2-ONNX')
- `options.device` (string, optional) - Device to use ('cpu' or 'gpu', default: 'cpu')

**Returns:** Promise<void>

#### generate(text, options)

Generate speech from text.

**Parameters:**
- `text` (string) - Input text to synthesize
- `options.language` (string) - Language code: 'en', 'ko', 'es', 'pt', 'fr' (default: 'en')
- `options.speaker_embeddings` (string) - URL or path to speaker voice file
- `options.num_inference_steps` (number) - Denoising steps, 1-50 (default: 5)
- `options.speed` (number) - Speech speed, 0.8-1.2 (default: 1.0)

**Returns:** Promise<Audio> - Audio object with save() and toBlob() methods

#### generateAndSave(text, outputPath, options)

Generate speech and save to file.

**Parameters:**
- `text` (string) - Input text
- `outputPath` (string) - Output file path (e.g., 'output.wav')
- `options` - Same as generate()

**Returns:** Promise<void>

#### generateBatch(texts, options)

Batch generate speech from multiple texts.

**Parameters:**
- `texts` (Array<string>) - Array of input texts
- `options` - Same as generate() (applied to all)

**Returns:** Promise<Array<Audio>>

## Supported Languages

- `en` - English
- `ko` - Korean
- `es` - Spanish
- `pt` - Portuguese
- `fr` - French

## Supported Voices

Available voice styles from the model:
- `M1.bin` - Male voice 1
- `F1.bin` - Female voice 1

Voice files are hosted on Hugging Face:
```
https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/{VOICE}.bin
```

## Performance Benchmarks

On Intel CPU (example: i7-12700K):

| Text Length | Steps | RTF (Real-time Factor) | Generation Time |
|------------|-------|------------------------|-----------------|
| Short (59 chars) | 5 | ~0.05 | ~100ms |
| Medium (152 chars) | 5 | ~0.08 | ~200ms |
| Long (266 chars) | 5 | ~0.12 | ~350ms |

*Lower RTF is better. RTF < 1.0 means faster than real-time.*

## Browser Usage

This implementation can also run in modern browsers with WebAssembly support:

```html
<script type="module">
  import { SupertonicTTS } from './index.js';
  
  const tts = new SupertonicTTS();
  await tts.initialize();
  
  const audio = await tts.generate('Hello from the browser!', {
    language: 'en',
    num_inference_steps: 5,
  });
  
  // Convert to blob and play
  const blob = await audio.toBlob();
  const url = URL.createObjectURL(blob);
  const audioElement = new Audio(url);
  audioElement.play();
</script>
```

## Troubleshooting

### Model Download Issues

On first run, the model (~200MB) will be downloaded automatically. If you encounter issues:

1. Check your internet connection
2. Ensure you have enough disk space (~500MB for cache)
3. Try manually downloading from: https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX

### Performance Issues

If generation is slow on Intel CPU:

1. Ensure SIMD is enabled (it should be by default)
2. Try adjusting `OMP_NUM_THREADS`
3. Reduce `num_inference_steps` (2-3 for fastest generation)
4. Close other CPU-intensive applications

### Memory Issues

If you encounter out-of-memory errors:

1. Process texts one at a time instead of batching
2. Reduce batch size
3. Ensure you have at least 4GB of available RAM

## License

MIT License - see [LICENSE](../LICENSE) file for details.

Model license: OpenRAIL-M License - see [model card](https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX) for details.

## References

- [Transformers.js Documentation](https://huggingface.co/docs/transformers.js)
- [Supertonic TTS Model](https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX)
- [ONNX Runtime](https://onnxruntime.ai/)
