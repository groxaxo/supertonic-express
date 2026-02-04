"""TTS Service wrapper for Supertonic ONNX models"""

import asyncio
import io
import json
import os
from typing import AsyncGenerator, Optional

import numpy as np
import soundfile as sf
from loguru import logger

# Import from parent package helper
from pathlib import Path
import importlib.util

# Load helper module from the parent py directory
_helper_path = Path(__file__).parent.parent.parent.parent / "helper.py"
spec = importlib.util.spec_from_file_location("helper", _helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

# Import needed functions from helper
load_text_to_speech = helper.load_text_to_speech
load_voice_style = helper.load_voice_style
Style = helper.Style
TextToSpeech = helper.TextToSpeech
chunk_text = helper.chunk_text

from ..core.config import settings


class TTSService:
    """Service for text-to-speech generation"""

    def __init__(self):
        self.tts_model: Optional[TextToSpeech] = None
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self):
        """Initialize the TTS model"""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            logger.info(f"Loading TTS model from {settings.onnx_dir}")
            await asyncio.to_thread(self._load_model)
            self._initialized = True
            logger.info("TTS model loaded successfully")

    def _load_model(self):
        """Load the ONNX model (sync)"""
        self.tts_model = load_text_to_speech(settings.onnx_dir, settings.use_gpu)

    async def get_available_voices(self) -> list[str]:
        """Get list of available voice styles"""
        voices = []
        voices_dir = os.path.join(settings.onnx_dir, "voices")
        if os.path.exists(voices_dir):
            for file in os.listdir(voices_dir):
                if file.endswith(".bin"):
                    voices.append(file.replace(".bin", ""))
        # Fallback to old location for backwards compatibility
        elif os.path.exists(settings.voice_styles_dir):
            for file in os.listdir(settings.voice_styles_dir):
                if file.endswith(".json") or file.endswith(".bin"):
                    voices.append(file.replace(".json", "").replace(".bin", ""))
        return sorted(voices)

    def _get_voice_path(self, voice_name: str) -> str:
        """Get the full path to a voice style file"""
        # Try new location first (.bin files in model voices directory)
        voice_path = os.path.join(settings.onnx_dir, "voices", f"{voice_name}.bin")
        if os.path.exists(voice_path):
            return voice_path
        # Fall back to old location (.json files)
        return os.path.join(settings.voice_styles_dir, f"{voice_name}.json")

    def _detect_language(self, text: str, lang_code: Optional[str] = None) -> str:
        """Detect or validate language code"""
        if lang_code and lang_code in ["en", "ko", "es", "pt", "fr"]:
            return lang_code
        
        # Auto-detect Spanish if text contains Spanish characters
        # Spanish-specific characters: á, é, í, ó, ú, ñ, ü, ¿, ¡
        import re
        spanish_chars = re.compile(r'[áéíóúñüÁÉÍÓÚÑÜ¿¡]')
        if spanish_chars.search(text):
            logger.info("Auto-detected Spanish language based on text characters")
            return "es"
        
        # Default to English
        return "en"

    async def generate_audio(
        self,
        text: str,
        voice: str = "M1",
        speed: float = 1.0,
        lang_code: Optional[str] = None,
        total_steps: Optional[int] = None,
    ) -> bytes:
        """Generate complete audio file"""
        if not self._initialized:
            await self.initialize()

        # Get language
        lang = self._detect_language(text, lang_code)

        # Use configured default if not specified
        steps = total_steps or settings.default_total_steps
        actual_speed = speed * settings.default_speed

        # Generate audio (voice is passed directly as string in new model)
        wav, duration = await asyncio.to_thread(
            self.tts_model,
            text,
            lang,
            voice,
            steps,
            actual_speed,
        )

        # Trim to actual duration
        sample_count = int(self.tts_model.sample_rate * duration[0].item())
        wav_trimmed = wav[0, :sample_count]

        # Convert to bytes
        buffer = io.BytesIO()
        sf.write(buffer, wav_trimmed, self.tts_model.sample_rate, format="WAV")
        return buffer.getvalue()

    async def generate_audio_stream(
        self,
        text: str,
        voice: str = "M1",
        speed: float = 1.0,
        lang_code: Optional[str] = None,
        total_steps: Optional[int] = None,
        chunk_size: int = 8192,
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate audio in streaming chunks.
        
        Note: This implementation generates complete audio and streams it in chunks.
        For very long texts, consider using the chunk_text functionality to split
        text into smaller segments and generate them sequentially.
        """
        # Generate complete audio
        audio_data = await self.generate_audio(
            text, voice, speed, lang_code, total_steps
        )

        # Stream the audio in chunks
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i : i + chunk_size]
            # Small delay to simulate streaming and allow event loop to process
            await asyncio.sleep(0.001)

    @property
    def sample_rate(self) -> int:
        """Get the model's sample rate"""
        return self.tts_model.sample_rate if self.tts_model else settings.sample_rate


# Global service instance
_tts_service: Optional[TTSService] = None


async def get_tts_service() -> TTSService:
    """Get or create global TTS service instance"""
    global _tts_service

    if _tts_service is None:
        _tts_service = TTSService()
        await _tts_service.initialize()

    return _tts_service
