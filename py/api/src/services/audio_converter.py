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
        sample_rate: int = 44100,
    ) -> bytes:
        """Convert WAV audio to specified format using ffmpeg

        Args:
            audio_data: Raw WAV bytes
            output_format: Target format (mp3, opus, aac, flac, wav, pcm)
            sample_rate: Sample rate for the audio

        Returns:
            Converted audio bytes

        Note:
            - Opus: Best for streaming, excellent quality/size ratio, WhatsApp compatible
            - AAC: Good for streaming, widely compatible (WhatsApp, iMessage, etc.)
            - MP3: Universal compatibility, larger file size
        """

        if output_format == "wav":
            return audio_data

        if output_format == "pcm":
            # Extract raw PCM data from WAV
            with io.BytesIO(audio_data) as wav_io:
                data, _ = sf.read(wav_io, dtype="int16")
                return data.tobytes()

        # Use ffmpeg for other formats
        try:
            # Prepare ffmpeg command
            cmd = [
                "ffmpeg",
                "-f",
                "wav",
                "-i",
                "pipe:0",  # Input from stdin
                "-y",  # Overwrite output
            ]

            # Format-specific settings optimized for streaming and compatibility
            if output_format == "mp3":
                cmd.extend(
                    [
                        "-f",
                        "mp3",
                        "-codec:a",
                        "libmp3lame",
                        "-b:a",
                        "128k",
                        "-q:a",
                        "2",
                    ]
                )
            elif output_format == "opus":
                # Opus in OGG container - best for streaming, WhatsApp compatible
                cmd.extend(
                    [
                        "-f",
                        "ogg",
                        "-codec:a",
                        "libopus",
                        "-b:a",
                        "64k",  # Opus is efficient, 64k is good quality
                        "-vbr",
                        "on",
                        "-compression_level",
                        "10",
                    ]
                )
            elif output_format == "aac":
                # AAC in ADTS container for streaming compatibility
                cmd.extend(
                    [
                        "-f",
                        "adts",  # ADTS format for streaming (no seek needed)
                        "-codec:a",
                        "aac",
                        "-b:a",
                        "128k",
                        "-vbr",
                        "5",
                    ]
                )
            elif output_format == "flac":
                cmd.extend(
                    [
                        "-f",
                        "flac",
                        "-codec:a",
                        "flac",
                    ]
                )

            cmd.extend(["-hide_banner", "-loglevel", "error", "pipe:1"])

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
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg for audio format conversion."
            )
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            raise


def convert_audio(
    audio_data: bytes,
    output_format: str,
    sample_rate: int = 44100,
) -> bytes:
    """Convert audio to specified format"""
    return AudioConverter.wav_to_format(audio_data, output_format, sample_rate)
