"""
Input Handler Module for Axon AI Assistant
Handles both voice and text input seamlessly
"""

import speech_recognition as sr
from audio_config import get_microphone, configure_recognizer

class InputHandler:
    """Manages user input from both voice and text sources"""
    
    def __init__(self, default_mode='voice'):
        """
        Initialize input handler
        
        Args:
            default_mode: 'voice', 'text', or 'auto' (asks user each time)
        """
        self.mode = default_mode
        self.recognizer = sr.Recognizer()
        self.recognizer = configure_recognizer(self.recognizer)
        self.microphone = get_microphone()
    
    def get_input(self, prompt="", timeout=5, use_voice=None):
        """
        Get input from user via voice or text
        
        Args:
            prompt: Message to display/speak to user
            timeout: Timeout for voice input (seconds)
            use_voice: Override default mode (True=voice, False=text, None=use default)
        
        Returns:
            User input as lowercase string, or "None" if failed
        """
        # Determine input method
        if use_voice is None:
            use_voice = (self.mode == 'voice')
        
        if prompt:
            print(prompt)
        
        if use_voice:
            return self._get_voice_input(timeout)
        else:
            return self._get_text_input(prompt)
    
    def _get_voice_input(self, timeout=5):
        """Get input via voice recognition"""
        with self.microphone as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print("🔄 Recognizing...")
                query = self.recognizer.recognize_google(audio, language='en-in')
                print(f"✓ You said: {query}\n")
                return query.lower()
                
            except sr.WaitTimeoutError:
                print("⏱️ Listening timed out. No speech detected.")
                return "None"
                
            except sr.UnknownValueError:
                print("❌ Sorry, I didn't catch that.")
                return "None"
                
            except sr.RequestError as e:
                print(f"🌐 Network error: {e}")
                return "None"
                
            except Exception as e:
                print(f"⚠️ Error: {e}")
                return "None"
    
    def _get_text_input(self, prompt=""):
        """Get input via keyboard typing"""
        try:
            if prompt:
                user_input = input(f"⌨️  {prompt}: ").strip()
            else:
                user_input = input("⌨️  Type your command: ").strip()
            
            if user_input:
                print(f"✓ You typed: {user_input}\n")
                return user_input.lower()
            else:
                return "None"
                
        except Exception as e:
            print(f"⚠️ Input error: {e}")
            return "None"
    
    def set_mode(self, mode):
        """
        Change input mode
        
        Args:
            mode: 'voice', 'text', or 'auto'
        """
        if mode in ['voice', 'text', 'auto']:
            self.mode = mode
            print(f"✓ Input mode set to: {mode}")
            return True
        else:
            print(f"❌ Invalid mode: {mode}. Use 'voice', 'text', or 'auto'")
            return False
    
    def get_mode(self):
        """Get current input mode"""
        return self.mode


def create_input_handler(mode='voice'):
    """
    Factory function to create an input handler
    
    Args:
        mode: 'voice', 'text', or 'auto'
    
    Returns:
        InputHandler instance
    """
    return InputHandler(mode)


if __name__ == "__main__":
    # Test the input handler
    print("Testing Input Handler\n")
    
    handler = InputHandler(default_mode='text')
    
    print("Mode: text")
    result = handler.get_input("Enter your name")
    print(f"Result: {result}\n")
    
    print("Switching to voice mode...")
    handler.set_mode('voice')
    result = handler.get_input("Say something", timeout=5)
    print(f"Result: {result}")
