/**
 * Supertonic TTS - JavaScript/Node.js Implementation
 * Using Transformers.js with Intel CPU optimizations
 * 
 * This implementation uses the @huggingface/transformers library
 * with optimizations for Intel CPUs via ONNX Runtime.
 */

import { pipeline, env } from '@huggingface/transformers';
import os from 'os';

// CPU Optimization Configuration for Intel processors
// These settings help reduce bottlenecks on Intel CPUs
const defaultThreads = Math.max(1, Math.floor(os.cpus().length * 0.75));
env.backends.onnx.wasm.numThreads = process.env.OMP_NUM_THREADS 
  ? parseInt(process.env.OMP_NUM_THREADS) 
  : defaultThreads;

// Enable ONNX Runtime optimizations
env.backends.onnx.wasm.simd = true; // SIMD instructions for Intel CPUs
env.backends.onnx.wasm.proxy = false; // Disable worker threads overhead for small models

/**
 * SupertonicTTS class for text-to-speech generation
 */
export class SupertonicTTS {
  static MODEL_ID = 'onnx-community/Supertonic-TTS-2-ONNX';
  static SAMPLE_RATE = 44100;
  static LANGUAGES = ['en', 'ko', 'es', 'pt', 'fr'];
  
  constructor() {
    this.tts = null;
    this.initialized = false;
  }

  /**
   * Initialize the TTS pipeline
   * @param {Object} options - Configuration options
   * @param {string} options.model - Model ID (default: 'onnx-community/Supertonic-TTS-2-ONNX')
   * @param {string} options.device - Device to use ('cpu' or 'gpu', default: 'cpu')
   * @returns {Promise<void>}
   */
  async initialize(options = {}) {
    if (this.initialized) {
      return;
    }

    const modelId = options.model || SupertonicTTS.MODEL_ID;
    const device = options.device || 'cpu';

    console.log(`Initializing Supertonic TTS with model: ${modelId}`);
    console.log(`Device: ${device}`);
    console.log(`CPU threads: ${env.backends.onnx.wasm.numThreads}`);

    try {
      this.tts = await pipeline('text-to-speech', modelId, {
        device: device,
        // Additional CPU optimizations
        quantized: false, // Use full precision for better quality on CPU
      });
      
      this.initialized = true;
      console.log('✓ Supertonic TTS initialized successfully');
    } catch (error) {
      throw new Error(`Failed to initialize TTS: ${error.message}`);
    }
  }

  /**
   * Generate speech from text
   * @param {string} text - Input text to synthesize
   * @param {Object} options - Generation options
   * @param {string} options.language - Language code ('en', 'ko', 'es', 'pt', 'fr')
   * @param {string} options.speaker_embeddings - URL or path to speaker voice file
   * @param {number} options.num_inference_steps - Number of denoising steps (1-50, default: 5)
   * @param {number} options.speed - Speech speed multiplier (0.8-1.2, default: 1.0)
   * @returns {Promise<Object>} Audio object with save() and toBlob() methods
   */
  async generate(text, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }

    // Validate language
    const language = options.language || 'en';
    if (!SupertonicTTS.LANGUAGES.includes(language)) {
      throw new Error(
        `Language '${language}' not supported. Choose from: ${SupertonicTTS.LANGUAGES.join(', ')}`
      );
    }

    // Wrap text with language tags
    const input_text = `<${language}>${text}</${language}>`;

    // Set default options
    const speaker_embeddings = options.speaker_embeddings || 
      'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/M1.bin';
    const num_inference_steps = options.num_inference_steps || 5;
    const speed = options.speed || 1.0;

    console.log(`Generating speech: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);
    console.log(`Options: language=${language}, steps=${num_inference_steps}, speed=${speed}`);

    try {
      const audio = await this.tts(input_text, {
        speaker_embeddings,
        num_inference_steps,
        speed,
      });

      return audio;
    } catch (error) {
      throw new Error(`Failed to generate speech: ${error.message}`);
    }
  }

  /**
   * Generate speech and save to file
   * @param {string} text - Input text
   * @param {string} outputPath - Output file path (e.g., 'output.wav')
   * @param {Object} options - Same as generate() options
   * @returns {Promise<void>}
   */
  async generateAndSave(text, outputPath, options = {}) {
    const audio = await this.generate(text, options);
    await audio.save(outputPath);
    console.log(`✓ Audio saved to: ${outputPath}`);
  }

  /**
   * Batch generate speech from multiple texts
   * @param {Array<string>} texts - Array of input texts
   * @param {Object} options - Same as generate() options (applied to all)
   * @returns {Promise<Array<Object>>} Array of audio objects
   */
  async generateBatch(texts, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }

    console.log(`Batch generating ${texts.length} audio files...`);
    
    const results = [];
    for (let i = 0; i < texts.length; i++) {
      console.log(`Processing ${i + 1}/${texts.length}...`);
      const audio = await this.generate(texts[i], options);
      results.push(audio);
    }

    return results;
  }
}

// Export helper function for quick usage
export async function createTTS(options = {}) {
  const tts = new SupertonicTTS();
  await tts.initialize(options);
  return tts;
}

// Default export
export default SupertonicTTS;
