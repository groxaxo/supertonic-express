/**
 * Advanced usage example with multiple languages and voices
 */

import { SupertonicTTS } from '../index.js';

async function main() {
  console.log('=== Supertonic TTS - Advanced Example ===\n');

  const tts = new SupertonicTTS();
  await tts.initialize();

  // Available voices
  const voices = {
    M1: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/M1.bin',
    F1: 'https://huggingface.co/onnx-community/Supertonic-TTS-2-ONNX/resolve/main/voices/F1.bin',
  };

  // Examples in different languages
  const examples = [
    {
      text: 'Hello! Welcome to Supertonic text-to-speech.',
      language: 'en',
      voice: 'M1',
      steps: 15,
      speed: 1.0,
      filename: 'output_en.wav',
    },
    {
      text: '안녕하세요! 수퍼토닉 텍스트 음성 변환입니다.',
      language: 'ko',
      voice: 'F1',
      steps: 15,
      speed: 1.05,
      filename: 'output_ko.wav',
    },
    {
      text: '¡Hola! Bienvenido a la síntesis de voz Supertonic.',
      language: 'es',
      voice: 'M1',
      steps: 15,
      speed: 1.0,
      filename: 'output_es.wav',
    },
    {
      text: 'Olá! Bem-vindo à síntese de voz Supertonic.',
      language: 'pt',
      voice: 'F1',
      steps: 15,
      speed: 1.0,
      filename: 'output_pt.wav',
    },
    {
      text: 'Bonjour! Bienvenue dans la synthèse vocale Supertonic.',
      language: 'fr',
      voice: 'M1',
      steps: 15,
      speed: 0.95,
      filename: 'output_fr.wav',
    },
  ];

  console.log('\n--- Generating speech in multiple languages ---\n');

  for (const example of examples) {
    console.log(`\nLanguage: ${example.language.toUpperCase()}`);
    console.log(`Text: "${example.text}"`);
    console.log(`Voice: ${example.voice}, Steps: ${example.steps}, Speed: ${example.speed}`);
    
    await tts.generateAndSave(example.text, example.filename, {
      language: example.language,
      speaker_embeddings: voices[example.voice],
      num_inference_steps: example.steps,
      speed: example.speed,
    });
  }

  console.log('\n✓ Done! Generated audio files in 5 different languages');
}

main().catch(console.error);
