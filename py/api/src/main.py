"""
Supertonic FastAPI Server - OpenAI Compatible TTS API
"""

import sys
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .core.config import settings
from .routers.openai_compatible import router as openai_router
from .structures.schemas import HealthResponse


def setup_logger():
    """Configure loguru logger"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=os.getenv("LOG_LEVEL", "INFO"),
        colorize=True,
    )


# Configure logger
setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup/shutdown"""
    from .services.tts_service import get_tts_service
    
    logger.info("Starting Supertonic TTS API server...")
    logger.info(f"ONNX directory: {settings.onnx_dir}")
    logger.info(f"Voice styles directory: {settings.voice_styles_dir}")
    logger.info(f"Using GPU: {settings.use_gpu}")
    
    # Initialize TTS service
    try:
        tts_service = await get_tts_service()
        voices = await tts_service.get_available_voices()
        logger.info(f"Loaded {len(voices)} voice styles")
        logger.info(f"Available voices: {', '.join(voices)}")
    except Exception as e:
        logger.error(f"Failed to initialize TTS service: {e}")
        raise
    
    logger.success("=" * 60)
    logger.success("Supertonic TTS API Server Ready!")
    logger.success(f"Server running at http://{settings.host}:{settings.port}")
    logger.success(f"OpenAPI docs: http://{settings.host}:{settings.port}/docs")
    logger.success(f"Sample rate: {settings.sample_rate} Hz")
    logger.success("=" * 60)
    
    yield
    
    logger.info("Shutting down Supertonic TTS API server...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(openai_router, prefix="/v1")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from .services.tts_service import get_tts_service
    
    try:
        tts_service = await get_tts_service()
        model_loaded = tts_service._initialized
    except Exception:
        model_loaded = False
    
    return HealthResponse(
        status="healthy" if model_loaded else "initializing",
        model_loaded=model_loaded,
        version=settings.api_version,
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Supertonic TTS API",
        "version": settings.api_version,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.src.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info",
    )
