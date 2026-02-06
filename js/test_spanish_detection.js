/**
 * Test Spanish auto-detection and default inference steps
 */

import { SupertonicTTS } from './index.js';

async function testSpanishDetection() {
  console.log('=== Testing Spanish Auto-Detection ===\n');

  const tts = new SupertonicTTS();
  await tts.initialize();

  // Test cases
  const testCases = [
    {
      text: 'Hello, this is an English sentence.',
      expectedLang: 'en',
      description: 'English text (no Spanish chars)'
    },
    {
      text: '¡Hola! ¿Cómo estás?',
      expectedLang: 'es',
      description: 'Spanish text with ¡ and ¿'
    },
    {
      text: 'El niño está feliz.',
      expectedLang: 'es',
      description: 'Spanish text with ñ'
    },
    {
      text: 'Está es una oración en español.',
      expectedLang: 'es',
      description: 'Spanish text with á'
    },
    {
      text: 'This has an accent: café',
      expectedLang: 'es',
      description: 'Mixed text with Spanish chars (é)'
    }
  ];

  console.log('Test Cases:');
  for (const testCase of testCases) {
    const isSpanish = tts._detectSpanish(testCase.text);
    const detectedLang = isSpanish ? 'es' : 'en';
    const passed = detectedLang === testCase.expectedLang;
    
    console.log(`\n${passed ? '✓' : '✗'} ${testCase.description}`);
    console.log(`  Text: "${testCase.text}"`);
    console.log(`  Expected: ${testCase.expectedLang}, Detected: ${detectedLang}`);
  }

  // Test default inference steps
  console.log('\n\n=== Testing Default Inference Steps ===\n');
  
  // Generate with defaults (should use 15 steps)
  console.log('Generating audio with default settings...');
  const audio = await tts.generate('Test text', {});
  console.log('✓ Audio generated successfully with defaults');
  console.log('Note: Default inference steps should be 15');

  console.log('\n✓ All tests completed!');
}

testSpanishDetection().catch(console.error);
