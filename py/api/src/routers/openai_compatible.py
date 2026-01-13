"""OpenAI-compatible API endpoints"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from loguru import logger

from ..structures.schemas import OpenAISpeechRequest, VoicesResponse, VoiceInfo
from ..services.tts_service import get_tts_service
from ..services.audio_converter import convert_audio

router = APIRouter(tags=["OpenAI Compatible"])


@router.post("/audio/speech")
async def create_speech(request: OpenAISpeechRequest, client_request: Request):
    """
    OpenAI-compatible text-to-speech endpoint.
    
    Generates audio from text input using Supertonic TTS models.
    Compatible with OpenAI's TTS API format.
    """
    try:
        # Get TTS service
        tts_service = await get_tts_service()
        
        # Validate voice exists
        available_voices = await tts_service.get_available_voices()
        if request.voice not in available_voices:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_voice",
                    "message": f"Voice '{request.voice}' not found. Available voices: {', '.join(available_voices)}",
                },
            )
        
        # Set content type based on format
        content_types = {
            "mp3": "audio/mpeg",
            "opus": "audio/opus",
            "aac": "audio/aac",
            "flac": "audio/flac",
            "wav": "audio/wav",
            "pcm": "audio/pcm",
        }
        content_type = content_types.get(request.response_format, "audio/mpeg")
        
        if request.stream:
            # Streaming response
            async def audio_stream():
                try:
                    async for chunk in tts_service.generate_audio_stream(
                        text=request.input,
                        voice=request.voice,
                        speed=request.speed,
                        lang_code=request.lang_code,
                        total_steps=request.total_steps,
                    ):
                        # Check if client disconnected
                        if await client_request.is_disconnected():
                            logger.info("Client disconnected, stopping stream")
                            break
                        
                        # Convert if not WAV
                        if request.response_format != "wav":
                            chunk = convert_audio(
                                chunk,
                                request.response_format,
                                tts_service.sample_rate,
                            )
                        
                        yield chunk
                except Exception as e:
                    logger.error(f"Streaming error: {e}")
                    raise
            
            return StreamingResponse(
                audio_stream(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f'attachment; filename="speech.{request.response_format}"',
                    "X-Accel-Buffering": "no",
                    "Cache-Control": "no-cache",
                },
            )
        else:
            # Non-streaming response
            audio_data = await tts_service.generate_audio(
                text=request.input,
                voice=request.voice,
                speed=request.speed,
                lang_code=request.lang_code,
                total_steps=request.total_steps,
            )
            
            # Convert to requested format
            if request.response_format != "wav":
                audio_data = convert_audio(
                    audio_data,
                    request.response_format,
                    tts_service.sample_rate,
                )
            
            return Response(
                content=audio_data,
                media_type=content_type,
                headers={
                    "Content-Disposition": f'attachment; filename="speech.{request.response_format}"',
                },
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating speech: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": f"Failed to generate speech: {str(e)}",
            },
        )


@router.get("/audio/voices", response_model=VoicesResponse)
async def list_voices():
    """
    List available voices.
    
    Returns a list of all available voice styles that can be used
    for text-to-speech generation.
    """
    try:
        tts_service = await get_tts_service()
        voices = await tts_service.get_available_voices()
        
        # Create voice info objects
        voice_info_list = []
        for voice_name in voices:
            # Detect language from voice name prefix
            lang = "en"  # Default
            if voice_name.startswith("M") or voice_name.startswith("F"):
                lang = "en"
            
            voice_info_list.append(
                VoiceInfo(
                    name=voice_name,
                    language=lang,
                    description=f"Supertonic voice style: {voice_name}",
                )
            )
        
        return VoicesResponse(voices=voice_info_list)
    
    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": f"Failed to list voices: {str(e)}",
            },
        )


@router.get("/models")
async def list_models():
    """
    List available models (OpenAI-compatible endpoint).
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "supertonic",
                "object": "model",
                "created": 1704067200,
                "owned_by": "supertone",
            },
            {
                "id": "tts-1",
                "object": "model",
                "created": 1704067200,
                "owned_by": "supertone",
            },
            {
                "id": "tts-1-hd",
                "object": "model",
                "created": 1704067200,
                "owned_by": "supertone",
            },
        ],
    }
