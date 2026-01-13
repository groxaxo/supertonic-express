"""Audio conversion utilities"""

import io
import subprocess
from typing import Literal

import numpy as np
import soundfile as sf
from loguru import logger


class AudioConverter:
    """Convert audio between different formats"""

    @staticmethod
    def wav_to_format(
        audio_data: bytes,
        output_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"],
        sample_rate: int = 24000,
    ) -> bytes:
        """Convert WAV audio to specified format using ffmpeg"""
        
        if output_format == "wav":
            return audio_data
        
        if output_format == "pcm":
            # Extract raw PCM data from WAV
            with io.BytesIO(audio_data) as wav_io:
                data, _ = sf.read(wav_io, dtype='int16')
                return data.tobytes()
        
        # Use ffmpeg for other formats
        try:
            # Prepare ffmpeg command
            cmd = [
                "ffmpeg",
                "-f", "wav",
                "-i", "pipe:0",  # Input from stdin
                "-f", output_format if output_format != "opus" else "opus",
            ]
            
            # Format-specific settings
            if output_format == "mp3":
                cmd.extend(["-codec:a", "libmp3lame", "-b:a", "128k"])
            elif output_format == "opus":
                cmd.extend(["-codec:a", "libopus", "-b:a", "96k"])
            elif output_format == "aac":
                cmd.extend(["-codec:a", "aac", "-b:a", "128k"])
            elif output_format == "flac":
                cmd.extend(["-codec:a", "flac"])
            
            cmd.append("pipe:1")  # Output to stdout
            
            # Run ffmpeg
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            output, error = process.communicate(input=audio_data)
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {error.decode()}")
                raise RuntimeError(f"Audio conversion failed: {error.decode()}")
            
            return output
            
        except FileNotFoundError:
            logger.error("ffmpeg not found - please install ffmpeg")
            raise RuntimeError("ffmpeg not found. Please install ffmpeg for audio format conversion.")
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            raise


def convert_audio(
    audio_data: bytes,
    output_format: str,
    sample_rate: int = 24000,
) -> bytes:
    """Convert audio to specified format"""
    return AudioConverter.wav_to_format(audio_data, output_format, sample_rate)
