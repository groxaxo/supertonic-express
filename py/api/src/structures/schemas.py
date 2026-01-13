"""Pydantic schemas for API requests and responses"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class OpenAISpeechRequest(BaseModel):
    """OpenAI-compatible TTS request schema"""
    
    model: str = Field(
        default="supertonic",
        description="TTS model to use"
    )
    
    input: str = Field(
        ...,
        description="The text to generate audio for",
        min_length=1
    )
    
    voice: str = Field(
        default="M1",
        description="Voice style to use (e.g., M1, F1, M2, F2)"
    )
    
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = Field(
        default="mp3",
        description="Audio format"
    )
    
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="Speed of generated audio (0.25 to 4.0)"
    )
    
    stream: bool = Field(
        default=True,
        description="Whether to stream the audio"
    )
    
    lang_code: Optional[str] = Field(
        default=None,
        description="Language code (en, ko, es, pt, fr). Auto-detected if not provided"
    )
    
    total_steps: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Number of denoising steps (higher = better quality, slower)"
    )


class VoiceInfo(BaseModel):
    """Voice information"""
    
    name: str
    language: str
    description: Optional[str] = None


class VoicesResponse(BaseModel):
    """Response containing available voices"""
    
    voices: list[VoiceInfo]


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    model_loaded: bool
    version: str
