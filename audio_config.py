"""
Audio Configuration Module for Axon AI Assistant
Handles platform detection, TTS engine selection, and microphone configuration
"""

import platform
import pyttsx3
import speech_recognition as sr
from typing import Optional, Dict, List, Tuple

class AudioConfig:
    """Manages audio system configuration for the AI assistant"""
    
    def __init__(self):
        self.platform = platform.system()
        self.platform_version = platform.version()
        self.machine = platform.machine()
        self.tts_engine_type = self._detect_tts_engine()
        self.microphone_index = None
        self.microphone_name = None
        
    def _detect_tts_engine(self) -> str:
        """Detect the best TTS engine for the current platform"""
        if self.platform == 'Windows':
            return 'sapi5'
        elif self.platform == 'Darwin':  # macOS
            return 'nsss'
        elif self.platform == 'Linux':
            return 'espeak'
        else:
            return 'sapi5'  # Default fallback
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get platform information"""
        return {
            'platform': self.platform,
            'version': self.platform_version,
            'machine': self.machine,
            'tts_engine': self.tts_engine_type
        }
    
    def list_microphones(self) -> List[Tuple[int, str]]:
        """List all available microphone devices"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            return [(i, name) for i, name in enumerate(mic_list)]
        except Exception as e:
            print(f"Error listing microphones: {e}")
            return []
    
    def get_best_microphone(self) -> Optional[Tuple[int, str]]:
        """
        Auto-select the best microphone device
        Prioritizes: Microphone Array > Microphone > Default
        """
        microphones = self.list_microphones()
        
        if not microphones:
            return None
        
        # Priority order for microphone selection
        priority_keywords = [
            'microphone array',
            'microphone',
            'mic',
            'input',
            'capture'
        ]
        
        # Filter out output devices
        input_devices = [
            (idx, name) for idx, name in microphones
            if not any(keyword in name.lower() for keyword in ['output', 'speaker', 'headphone'])
        ]
        
        # Try to find best match based on priority
        for keyword in priority_keywords:
            for idx, name in input_devices:
                if keyword in name.lower():
                    # Prefer Realtek or system default devices
                    if 'realtek' in name.lower() or 'microsoft' in name.lower():
                        self.microphone_index = idx
                        self.microphone_name = name
                        return (idx, name)
        
        # Fallback to first input device
        if input_devices:
            self.microphone_index = input_devices[0][0]
            self.microphone_name = input_devices[0][1]
            return input_devices[0]
        
        # Last resort: use default (None)
        return None
    
    def create_tts_engine(self, rate: int = 194, voice_index: int = 0) -> pyttsx3.Engine:
        """
        Create a fresh TTS engine with platform-appropriate settings
        
        Args:
            rate: Speech rate (words per minute)
            voice_index: Index of voice to use (0 for default)
        
        Returns:
            Configured pyttsx3 engine
        """
        try:
            engine = pyttsx3.init(self.tts_engine_type)
            voices = engine.getProperty('voices')
            
            # Set voice (use index if available, otherwise first voice)
            if voices and len(voices) > voice_index:
                engine.setProperty('voice', voices[voice_index].id)
            elif voices:
                engine.setProperty('voice', voices[0].id)
            
            # Set speech rate
            engine.setProperty('rate', rate)
            
            # Platform-specific volume settings
            if self.platform == 'Windows':
                engine.setProperty('volume', 1.0)  # Max volume on Windows
            
            return engine
            
        except Exception as e:
            print(f"Error creating TTS engine: {e}")
            # Fallback to default engine
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', rate)
                return engine
            except:
                raise RuntimeError("Failed to initialize any TTS engine")
    
    def configure_recognizer(self, recognizer: sr.Recognizer) -> sr.Recognizer:
        """
        Configure speech recognizer with optimized settings
        
        Args:
            recognizer: SpeechRecognition Recognizer object
        
        Returns:
            Configured recognizer
        """
        # Energy threshold for detecting speech
        # Lower = more sensitive, Higher = less sensitive to noise
        recognizer.energy_threshold = 4000
        
        # Minimum silence duration to consider phrase complete (seconds)
        recognizer.pause_threshold = 1.0
        
        # Minimum audio energy to consider for recording
        recognizer.dynamic_energy_threshold = True
        
        # Adjust for ambient noise dynamically
        recognizer.dynamic_energy_adjustment_damping = 0.15
        recognizer.dynamic_energy_ratio = 1.5
        
        return recognizer
    
    def get_microphone(self, device_index: Optional[int] = None) -> sr.Microphone:
        """
        Get configured microphone object
        
        Args:
            device_index: Specific device index to use (None for auto-select)
        
        Returns:
            Configured Microphone object
        """
        if device_index is None:
            # Auto-select best microphone
            best_mic = self.get_best_microphone()
            if best_mic:
                device_index = best_mic[0]
        
        try:
            if device_index is not None:
                return sr.Microphone(device_index=device_index)
            else:
                return sr.Microphone()  # Use system default
        except Exception as e:
            print(f"Error initializing microphone: {e}")
            return sr.Microphone()  # Fallback to default
    
    def print_audio_config(self):
        """Print current audio configuration"""
        print("\n" + "="*60)
        print("AUDIO SYSTEM CONFIGURATION")
        print("="*60)
        
        # Platform info
        info = self.get_platform_info()
        print(f"Platform: {info['platform']} {info['version']}")
        print(f"Machine: {info['machine']}")
        print(f"TTS Engine: {info['tts_engine']}")
        
        # Microphone info
        best_mic = self.get_best_microphone()
        if best_mic:
            print(f"\nSelected Microphone:")
            print(f"  Index: {best_mic[0]}")
            print(f"  Name: {best_mic[1]}")
        else:
            print("\nMicrophone: Using system default")
        
        print("="*60 + "\n")


# Global audio configuration instance
audio_config = AudioConfig()


# Convenience functions for easy import
def get_platform_info() -> Dict[str, str]:
    """Get platform information"""
    return audio_config.get_platform_info()


def get_best_microphone() -> Optional[Tuple[int, str]]:
    """Get the best microphone device"""
    return audio_config.get_best_microphone()


def create_tts_engine(rate: int = 194, voice_index: int = 0) -> pyttsx3.Engine:
    """Create a configured TTS engine"""
    return audio_config.create_tts_engine(rate, voice_index)


def configure_recognizer(recognizer: sr.Recognizer) -> sr.Recognizer:
    """Configure speech recognizer"""
    return audio_config.configure_recognizer(recognizer)


def get_microphone(device_index: Optional[int] = None) -> sr.Microphone:
    """Get configured microphone"""
    return audio_config.get_microphone(device_index)


def print_audio_config():
    """Print audio configuration"""
    audio_config.print_audio_config()


if __name__ == "__main__":
    # Test the audio configuration
    print_audio_config()
    
    print("\nAll Available Microphones:")
    print("-" * 60)
    for idx, name in audio_config.list_microphones():
        print(f"{idx:2d}: {name}")
