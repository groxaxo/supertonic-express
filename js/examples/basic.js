/**
 * Basic usage example for Supertonic TTS with Transformers.js
 */

import { SupertonicTTS } from '../index.js';

async function main() {
  console.log('=== Supertonic TTS - Basic Example ===\n');

  // Create TTS instance
  const tts = new SupertonicTTS();
  
  // Initialize (downloads model on first run)
  await tts.initialize();

  // Generate speech
  const text = 'This is really cool!';
  
  console.log('\n--- Generating speech (English, Male voice M1) ---');
  await tts.generateAndSave(text, 'output_basic.wav', {
    language: 'en',
    speaker_embeddings: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/M1.bin',
    num_inference_steps: 15,
    speed: 1.0,
  });

  console.log('\n--- Generating speech (English, Female voice F1) ---');
  await tts.generateAndSave(text, 'output_female.wav', {
    language: 'en',
    speaker_embeddings: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/F1.bin',
    num_inference_steps: 15,
    speed: 1.05,
  });

  console.log('\n✓ Done! Check output_basic.wav and output_female.wav');
}

main().catch(console.error);
