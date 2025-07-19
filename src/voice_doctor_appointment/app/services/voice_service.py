"""Voice service for handling voice input and output operations."""
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from typing import Optional
import sys
from pathlib import Path

"""Voice service for handling voice input and output operations."""
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from typing import Optional
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from elevenlabs import ElevenLabs, play
import openai
import os
from dotenv import load_dotenv

# Load environment variables
env_path = project_root / '.env'

# Load environment variables
load_dotenv(env_path, override=True)

class VoiceService:
    """Service for handling voice input and output."""
    
    def __init__(self):
        """Initialize the voice service with API keys."""
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
            
        self.elevenlabs = ElevenLabs(api_key=elevenlabs_api_key)
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def record_audio(self, duration: int, sample_rate: int = 44100) -> np.ndarray:
        """Record audio from the microphone.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate in Hz
            
        Returns:
            NumPy array containing the audio data
        """
        print(f"🎤 Recording for {duration} seconds...")
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16'
        )
        sd.wait()  # Wait until recording is finished
        return audio
    
    def save_audio(self, audio: np.ndarray, filename: str, sample_rate: int = 44100) -> None:
        """Save audio data to a WAV file.
        
        Args:
            audio: NumPy array containing audio data
            filename: Output filename
            sample_rate: Audio sample rate in Hz
        """
        write(filename, sample_rate, audio)
    
    def text_to_speech(self, text: str) -> None:
        """Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
        """
        audio = self.elevenlabs.text_to_speech.convert(
            voice_id=self.voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        play(audio)
    
    def speech_to_text(self, audio_file: str) -> Optional[str]:
        """Convert speech to text.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Transcribed text or None if an error occurs
        """
        try:
            with open(audio_file, "rb") as f:
                transcript = self.elevenlabs.speech_to_text.convert(
                    file=f,
                    model_id="scribe_v1",
                    diarize=False
                )
                return transcript.text.strip()
        except Exception as e:
            print(f"Error in speech-to-text: {e}")
            return None
    
    def ask_voice(self, prompt: str, duration: int = 5) -> Optional[str]:
        """Ask a question and get a voice response.
        
        Args:
            prompt: Question to ask
            duration: Maximum recording duration in seconds
            
        Returns:
            Transcribed response or None if an error occurs
        """
        # Speak the prompt
        self.text_to_speech(prompt)
        
        # Record the response
        audio = self.record_audio(duration)
        
        # Save to a temporary file
        temp_file = "temp_response.wav"
        self.save_audio(audio, temp_file)
        
        # Convert to text
        return self.speech_to_text(temp_file)
