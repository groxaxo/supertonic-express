/**
 * Batch processing example for Supertonic TTS
 */

import { SupertonicTTS } from '../index.js';

async function main() {
  console.log('=== Supertonic TTS - Batch Processing Example ===\n');

  // Create and initialize TTS
  const tts = new SupertonicTTS();
  await tts.initialize();

  // Multiple prompts to generate
  const prompts = [
    "Once upon a time, there was a brave knight.",
    "Refactoring code makes it much easier to read!",
    "I love this!"
  ];

  console.log('\n--- Batch generating speech ---');
  
  // Generate all audio files
  const audioResults = await tts.generateBatch(prompts, {
    language: 'en',
    speaker_embeddings: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/M1.bin',
    num_inference_steps: 15,
    speed: 1.0,
  });

  // Save each to a file
  console.log('\n--- Saving audio files ---');
  for (let i = 0; i < audioResults.length; i++) {
    const filename = `output_batch_${i}.wav`;
    await audioResults[i].save(filename);
    console.log(`✓ Saved ${filename}: "${prompts[i].substring(0, 40)}${prompts[i].length > 40 ? '...' : ''}"`);
  }

  console.log('\n✓ Done! Generated ' + audioResults.length + ' audio files');
}

main().catch(console.error);
