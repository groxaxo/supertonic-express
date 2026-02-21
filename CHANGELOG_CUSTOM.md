# Changelog - Custom Enhancements

## [Unreleased] - 2026-02-22

### Added
- **Smart Text Chunking**: Implemented automatic text splitting in `tts_service.py`. Long texts are now broken into sentence-based chunks (max ~300 chars) to prevent Out-Of-Memory (OOM) errors and allow unlimited audio generation length.
- **Improved Streaming**: 
  - Updated `openai_compatible.py` to stream audio chunk-by-chunk.
  - Reduced time-to-first-byte (latency) for long texts.
  - Properly handles format conversion and concatenation for streamed chunks.

### Changed
- **Default Audio Format**: Changed default output format from `mp3` to `opus` in `schemas.py`.
- **Audio Conversion**: 
  - Updated `audio_converter.py` to use optimized FFmpeg settings for streaming.
  - **Opus**: Now uses Ogg container with 64k bitrate (WhatsApp compatible).
  - **AAC**: Now uses ADTS container for streaming support.
  - **MP3**: Standardized to 128k bitrate.

### Fixed
- **WAV Streaming**: Fixed issue where concatenated WAV chunks would produce invalid files. Now correctly strips headers from subsequent chunks (though Opus/AAC is recommended for streaming).

### Usage
- To use the new streaming capability, simply send long text to the `/v1/audio/speech` endpoint with `"stream": true`.
- Recommended format for WhatsApp/Messaging apps: `"response_format": "opus"` (default) or `"aac"`.
