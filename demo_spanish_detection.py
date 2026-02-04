#!/usr/bin/env python3
"""
Demo script showing Spanish auto-detection and new default inference steps
This script doesn't require the full model to be downloaded - it just demonstrates
the language detection logic.
"""

import re


class MockTTSService:
    """Mock TTS service to demonstrate auto-detection logic"""
    
    def _detect_language(self, text: str, lang_code=None):
        """Detect or validate language code"""
        if lang_code and lang_code in ["en", "ko", "es", "pt", "fr"]:
            return lang_code
        
        # Auto-detect Spanish if text contains Spanish characters
        # Spanish-specific characters: á, é, í, ó, ú, ñ, ü, ¿, ¡
        spanish_chars = re.compile(r'[áéíóúñüÁÉÍÓÚÑÜ¿¡]')
        if spanish_chars.search(text):
            print("  → Auto-detected Spanish language based on text characters")
            return "es"
        
        # Default to English
        return "en"
    
    def generate_audio(self, text, voice="M1", speed=1.0, lang_code=None, total_steps=None):
        """Mock audio generation to demonstrate the flow"""
        # Get language
        lang = self._detect_language(text, lang_code)
        
        # Use default 15 if not specified
        steps = total_steps if total_steps is not None else 15
        
        print(f"  Language: {lang}")
        print(f"  Inference steps: {steps}")
        print(f"  Voice: {voice}, Speed: {speed}")
        print(f"  → Would generate audio here")
        
        return f"mock_audio_{lang}_{steps}steps.wav"


def demo():
    """Demonstrate the auto-detection and default settings"""
    
    print("=" * 70)
    print("Spanish Auto-Detection and Default Inference Steps Demo")
    print("=" * 70)
    
    tts = MockTTSService()
    
    test_cases = [
        {
            "text": "Hello! This is a test in English.",
            "lang_code": None,
            "description": "English text (auto-detect)"
        },
        {
            "text": "¡Hola! Esta es una prueba en español.",
            "lang_code": None,
            "description": "Spanish text with ¡ (auto-detect)"
        },
        {
            "text": "El niño come una manzana.",
            "lang_code": None,
            "description": "Spanish text with ñ (auto-detect)"
        },
        {
            "text": "Café, résumé, naïve",
            "lang_code": None,
            "description": "Text with accents (auto-detect as Spanish)"
        },
        {
            "text": "Plain English text",
            "lang_code": "fr",
            "description": "English text with explicit French override"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"  Input: \"{test['text']}\"")
        
        result = tts.generate_audio(
            text=test["text"],
            lang_code=test["lang_code"]
        )
        
        print(f"  Output: {result}")
    
    print("\n" + "=" * 70)
    print("Key Features Demonstrated:")
    print("=" * 70)
    print("✓ Default inference steps changed from 5 to 15")
    print("✓ Spanish characters (á, é, í, ó, ú, ñ, ü, ¿, ¡) trigger auto-detection")
    print("✓ Automatic language detection to 'es' for Spanish text")
    print("✓ Falls back to 'en' for English text")
    print("✓ Explicit language parameter still overrides auto-detection")
    print("=" * 70)


if __name__ == "__main__":
    demo()
