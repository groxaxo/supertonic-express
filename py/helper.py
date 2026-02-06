"""
SupertonicTTS ONNX Runtime implementation using onnx-community/Supertonic-TTS-2-ONNX model.
Based on the official model card implementation.
"""

import os
import time
from contextlib import contextmanager
from typing import Optional
import re

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer


class SupertonicTTS:
    """SupertonicTTS class for text-to-speech generation using ONNX models."""
    
    SAMPLE_RATE = 44100
    CHUNK_COMPRESS_FACTOR = 6
    BASE_CHUNK_SIZE = 512
    LATENT_DIM = 24
    STYLE_DIM = 128
    LATENT_SIZE = BASE_CHUNK_SIZE * CHUNK_COMPRESS_FACTOR
    LANGUAGES = ["en", "ko", "es", "pt", "fr"]

    def __init__(self, model_path: str, use_gpu: bool = False):
        """
        Initialize SupertonicTTS model.
        
        Args:
            model_path: Path to the model directory containing ONNX models
            use_gpu: Whether to use GPU for inference (default: False)
        """
        self.model_path = model_path
        self.sample_rate = self.SAMPLE_RATE
        
        # Initialize tokenizer with error handling
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load tokenizer from {self.model_path}. "
                "Make sure the model files are downloaded correctly. "
                f"Original error: {e}"
            )

        # Set up ONNX Runtime providers
        if use_gpu:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            print("Using GPU for inference (if available)")
        else:
            providers = ["CPUExecutionProvider"]
            print("Using CPU for inference")

        # Load ONNX sessions
        onnx_dir = os.path.join(self.model_path, "onnx")
        self.text_encoder = ort.InferenceSession(
            os.path.join(onnx_dir, "text_encoder.onnx"),
            providers=providers
        )
        self.latent_denoiser = ort.InferenceSession(
            os.path.join(onnx_dir, "latent_denoiser.onnx"),
            providers=providers
        )
        self.voice_decoder = ort.InferenceSession(
            os.path.join(onnx_dir, "voice_decoder.onnx"),
            providers=providers
        )

    def _load_style(self, voice: str) -> np.ndarray:
        """
        Load voice style from .bin file.
        
        Args:
            voice: Voice name (e.g., 'M1', 'F1')
            
        Returns:
            Style vector as numpy array with shape (1, num_embeddings, STYLE_DIM)
        """
        voice_path = os.path.join(self.model_path, "voices", f"{voice}.bin")
        if not os.path.exists(voice_path):
            raise ValueError(f"Voice '{voice}' not found at {voice_path}.")

        style_vec = np.fromfile(voice_path, dtype=np.float32)
        
<<<<<<< HEAD
        # Reshape to (1, -1, STYLE_DIM) where -1 infers the middle dimension
=======
        # Reshape to (1, num_embeddings, STYLE_DIM)
        # The -1 allows automatic inference of the number of embeddings
>>>>>>> ab834b2912d6c9153f433e4d647f6f3388c96e6f
        return style_vec.reshape(1, -1, self.STYLE_DIM)

    def generate(
        self,
        text: list[str],
        *,
        voice: str = "M1",
        speed: float = 1.0,
        steps: int = 15,
        language: str = "en"
    ) -> list[np.ndarray]:
        """
        Generate audio from text.
        
        Args:
            text: List of text strings to synthesize
            voice: Voice style to use (default: "M1")
            speed: Speech speed multiplier (default: 1.0)
            steps: Number of inference steps (default: 15, higher = better quality)
            language: Language code (default: "en")
            
        Returns:
            List of audio arrays (one per input text)
        """
        if language not in self.LANGUAGES:
            raise ValueError(
                f"Language '{language}' not supported. Choose from {self.LANGUAGES}."
            )

        # 1. Prepare Text Inputs
        text = [f"<{language}>{t}</{language}>" for t in text]
        inputs = self.tokenizer(text, return_tensors="np", padding=True, truncation=True)
        input_ids = inputs["input_ids"]
        attn_mask = inputs["attention_mask"]
        batch_size = input_ids.shape[0]

        # 2. Prepare Style
        style = self._load_style(voice).repeat(batch_size, axis=0)

        # 3. Text Encoding
        last_hidden_state, raw_durations = self.text_encoder.run(
            None,
            {"input_ids": input_ids, "attention_mask": attn_mask, "style": style}
        )
        durations = (raw_durations / speed * self.SAMPLE_RATE).astype(np.int64)

        # 4. Latent Preparation
        latent_lengths = (durations + self.LATENT_SIZE - 1) // self.LATENT_SIZE
        max_len = latent_lengths.max()
        latent_mask = (np.arange(max_len) < latent_lengths[:, None]).astype(np.int64)
        latents = np.random.randn(
            batch_size, self.LATENT_DIM * self.CHUNK_COMPRESS_FACTOR, max_len
        ).astype(np.float32)
        latents *= latent_mask[:, None, :]

        # 5. Denoising Loop
        num_inference_steps = np.full(batch_size, steps, dtype=np.float32)
        for step in range(steps):
            timestep = np.full(batch_size, step, dtype=np.float32)
            latents = self.latent_denoiser.run(
                None,
                {
                    "noisy_latents": latents,
                    "latent_mask": latent_mask,
                    "style": style,
                    "encoder_outputs": last_hidden_state,
                    "attention_mask": attn_mask,
                    "timestep": timestep,
                    "num_inference_steps": num_inference_steps,
                },
            )[0]

        # 6. Decode Latents to Audio
        waveforms = self.voice_decoder.run(None, {"latents": latents})[0]

        # 7. Post-process: Trim padding and return list of arrays
        results = []
        for i, length in enumerate(latent_mask.sum(axis=1) * self.LATENT_SIZE):
            # Cast to int to avoid indexing issues
            length_int = int(length)
            results.append(waveforms[i, :length_int])

        return results

    def __call__(
        self,
        text: str,
        lang: str,
        voice: str,
        total_step: int,
        speed: float = 1.0,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Legacy interface for compatibility with existing API.
        
        Args:
            text: Text to synthesize
            lang: Language code
            voice: Voice name
            total_step: Number of inference steps
            speed: Speech speed multiplier
            
        Returns:
            Tuple of (waveform, duration)
        """
        # Split long text into chunks
        max_len = 120 if lang == "ko" else 300
        text_chunks = chunk_text(text, max_len=max_len)
        
        wav_list = []
        total_duration = 0.0
        
        for chunk in text_chunks:
            results = self.generate(
                [chunk],
                voice=voice,
                speed=speed,
                steps=total_step,
                language=lang
            )
            wav_list.append(results[0])
            total_duration += len(results[0]) / self.SAMPLE_RATE
            
            # Add silence between chunks
            if len(text_chunks) > 1:
                silence = np.zeros(int(0.3 * self.SAMPLE_RATE), dtype=np.float32)
                wav_list.append(silence)
                total_duration += 0.3
        
        # Concatenate all chunks
        wav_combined = np.concatenate(wav_list)
        
        # Return in format expected by API: (1, T) and duration as array
        return wav_combined.reshape(1, -1), np.array([total_duration])

    def batch(
        self,
        text_list: list[str],
        lang_list: list[str],
        voice: str,
        total_step: int,
        speed: float = 1.0,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Batch processing for multiple texts.
        
        Args:
            text_list: List of texts to synthesize
            lang_list: List of language codes (one per text)
            voice: Voice name
            total_step: Number of inference steps
            speed: Speech speed multiplier
            
        Returns:
            Tuple of (waveforms, durations)
        """
        # For simplicity, use the same language for all (first in list)
        # The new model processes batches internally
        if len(set(lang_list)) > 1:
            # If different languages, process one by one
            wavs = []
            durs = []
            for text, lang in zip(text_list, lang_list):
                wav, dur = self(text, lang, voice, total_step, speed)
                wavs.append(wav)
                durs.append(dur)
            return np.concatenate(wavs, axis=0), np.concatenate(durs, axis=0)
        
        # Same language for all - use batch generation
        results = self.generate(
            text_list,
            voice=voice,
            speed=speed,
            steps=total_step,
            language=lang_list[0]
        )
        
        # Convert to expected format
        max_len = max(len(r) for r in results)
        wavs = np.zeros((len(results), max_len), dtype=np.float32)
        durs = np.zeros(len(results), dtype=np.float32)
        
        for i, wav in enumerate(results):
            wavs[i, :len(wav)] = wav
            durs[i] = len(wav) / self.SAMPLE_RATE
            
        return wavs, durs


# Backwards compatibility functions for the API

def load_text_to_speech(model_path: str, use_gpu: bool = False) -> SupertonicTTS:
    """
    Load the text-to-speech model.
    
    Args:
        model_path: Path to model directory
        use_gpu: Whether to use GPU
        
    Returns:
        SupertonicTTS instance
    """
    return SupertonicTTS(model_path, use_gpu)


def load_voice_style(voice_paths: list[str], verbose: bool = False) -> str:
    """
    Load voice style (backwards compatibility).
    
    Args:
        voice_paths: List of paths to voice files
        verbose: Whether to print verbose output
        
    Returns:
        Voice name extracted from first path
    """
    # Extract voice name from path (e.g., "assets/voices/M1.bin" -> "M1")
    voice_name = os.path.basename(voice_paths[0]).replace(".bin", "").replace(".json", "")
    if verbose:
        print(f"Loaded voice: {voice_name}")
    return voice_name


# Utility classes for backwards compatibility

class Style:
    """Dummy Style class for backwards compatibility."""
    def __init__(self, voice_name: str):
        self.voice_name = voice_name


class TextToSpeech:
    """Wrapper class for backwards compatibility."""
    def __init__(self, model_path: str, use_gpu: bool = False):
        self.tts = SupertonicTTS(model_path, use_gpu)
        self.sample_rate = self.tts.sample_rate
    
    def __call__(self, text: str, lang: str, style, total_step: int, speed: float = 1.0):
        voice = style if isinstance(style, str) else "M1"
        return self.tts(text, lang, voice, total_step, speed)
    
    def batch(self, text_list: list[str], lang_list: list[str], style, total_step: int, speed: float = 1.0):
        voice = style if isinstance(style, str) else "M1"
        return self.tts.batch(text_list, lang_list, voice, total_step, speed)


# Utility functions

@contextmanager
def timer(name: str):
    """Context manager for timing operations."""
    start = time.time()
    print(f"{name}...")
    yield
    print(f"  -> {name} completed in {time.time() - start:.2f} sec")


def sanitize_filename(text: str, max_len: int) -> str:
    """Sanitize filename by replacing non-alphanumeric characters with underscores."""
    prefix = text[:max_len]
    return re.sub(r"[^\w]", "_", prefix, flags=re.UNICODE)


def chunk_text(text: str, max_len: int = 300) -> list[str]:
    """
    Split text into chunks by paragraphs and sentences.

    Args:
        text: Input text to chunk
        max_len: Maximum length of each chunk (default: 300)

    Returns:
        List of text chunks
    """
    # Split by paragraph (two or more newlines)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text.strip()) if p.strip()]

    chunks = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # Split by sentence boundaries
        pattern = r"(?<!Mr\.)(?<!Mrs\.)(?<!Ms\.)(?<!Dr\.)(?<!Prof\.)(?<!Sr\.)(?<!Jr\.)(?<!Ph\.D\.)(?<!etc\.)(?<!e\.g\.)(?<!i\.e\.)(?<!vs\.)(?<!Inc\.)(?<!Ltd\.)(?<!Co\.)(?<!Corp\.)(?<!St\.)(?<!Ave\.)(?<!Blvd\.)(?<!\b[A-Z]\.)(?<=[.!?])\s+"
        sentences = re.split(pattern, paragraph)

        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_len:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

    return chunks if chunks else [text]
