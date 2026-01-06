"""
Whisper Service - Speech-to-text transcription
"""
import logging
import tempfile
import os
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class WhisperService:
    """Service for speech-to-text transcription"""
    
    def __init__(self):
        self.model = None
    
    def initialize(self, model_size: str = "large-v3", device: str = "cpu", compute_type: str = "int8"):
        """Initialize Whisper model"""
        logger.info(f"Initializing Whisper model: {model_size} on {device} with {compute_type}")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logger.info("Whisper model initialized successfully")
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio data to text"""
        if self.model is None:
            raise RuntimeError("Whisper model not initialized")
        
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(audio_data)
            temp_path = temp_audio.name
        
        try:
            # Transcribe
            segments, info = self.model.transcribe(temp_path, beam_size=5)
            transcription = " ".join([segment.text for segment in segments])
            
            logger.info(f"Transcribed audio: '{transcription[:50]}...' (lang: {info.language})")
            return transcription.strip()
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

# Global Whisper service instance
whisper_service = WhisperService()
