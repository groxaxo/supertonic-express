"""Configuration settings for Supertonic FastAPI server"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "Supertonic TTS API"
    api_description: str = "OpenAI-compatible Text-to-Speech API powered by Supertonic"
    api_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8880
    
    # Model Settings
    onnx_dir: str = os.getenv("ONNX_DIR", "assets")
    voice_styles_dir: str = os.getenv("VOICE_STYLES_DIR", "assets/voices")
    use_gpu: bool = os.getenv("USE_GPU", "false").lower() == "true"
    
    # TTS Settings
    default_speed: float = 1.05
    default_total_steps: int = 15
    sample_rate: int = 44100
    
    # CORS Settings
    cors_enabled: bool = True
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
