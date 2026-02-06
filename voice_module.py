"""
Voice Module for Ava AI Desktop Assistant
Handles voice recognition and command processing with TTS
"""

import speech_recognition as sr
import threading
import time
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass
from collections import deque
import traceback

# TTS imports
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    print("⚠️ pyttsx3 not installed. Run: pip install pyttsx3")
    TTS_AVAILABLE = False


@dataclass
class VoiceCommand:
    """Voice command result"""
    command: str
    success: bool
    response: str
    confidence: float = 0.0
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class VoiceProfile:
    """User voice profile for personalisation"""
    def __init__(self, user_name: str = "User"):
        self.user_name = user_name
        self.command_history: List[VoiceCommand] = []
        self.favorite_commands: Dict[str, int] = {}
        self.total_commands = 0
        self.successful_commands = 0

    def add_command(self, cmd: VoiceCommand):
        self.command_history.append(cmd)
        self.total_commands += 1
        if cmd.success:
            self.successful_commands += 1
            self.favorite_commands[cmd.command] = self.favorite_commands.get(cmd.command, 0) + 1

    def get_success_rate(self) -> float:
        if self.total_commands == 0:
            return 0.0
        return (self.successful_commands / self.total_commands) * 100


# Default command map template
_DEFAULT_COMMAND_MAP: Dict[str, str] = {
    # Mouse
    "click":          "MOUSE_LEFT_CLICK",
    "left click":     "MOUSE_LEFT_CLICK",
    "right click":    "MOUSE_RIGHT_CLICK",
    "double click":   "MOUSE_DOUBLE_CLICK",
    "scroll up":      "MOUSE_SCROLL_UP",
    "scroll down":    "MOUSE_SCROLL_DOWN",

    # Navigation
    "go back":        "NAVIGATE_BACK",
    "go forward":     "NAVIGATE_FORWARD",
    "refresh":        "REFRESH_PAGE",
    "new tab":        "NEW_TAB",
    "close tab":      "CLOSE_TAB",

    # Media
    "play":           "MEDIA_PLAY",
    "pause":          "MEDIA_PAUSE",
    "stop":           "MEDIA_STOP",
    "next":           "MEDIA_NEXT",
    "previous":       "MEDIA_PREVIOUS",
    "volume up":      "VOLUME_UP",
    "volume down":    "VOLUME_DOWN",
    "mute":           "VOLUME_MUTE",

    # System
    "minimize":       "WINDOW_MINIMIZE",
    "maximize":       "WINDOW_MAXIMIZE",
    "close window":   "WINDOW_CLOSE",
    "screenshot":     "TAKE_SCREENSHOT",

    # App
    "stop listening": "STOP_LISTENING",
    "exit":           "EXIT_APP",
    "help":           "SHOW_HELP",
    "reset":          "RESET_SYSTEM",
}


class VoiceAssistant:
    """
    Enhanced Voice Assistant
    - Single and continuous listening modes
    - Wake word detection
    - Command mapping and execution
    - Multi-language support
    - Text-to-Speech responses
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        duration: float = 4.0,
        energy_threshold: int = 300,
        language: str = "en-US"
    ):
        self.recognizer = sr.Recognizer()
        self.sample_rate = sample_rate
        self.microphone = sr.Microphone(sample_rate=sample_rate)

        # Configuration
        self.duration = duration
        self.language = language
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        # Each instance owns its own command map
        self.command_map: Dict[str, str] = dict(_DEFAULT_COMMAND_MAP)

        # Wake word
        self.wake_word_enabled = False
        self.wake_word = "ava"

        # Continuous listening
        self.is_listening_continuous = False
        self.continuous_thread: Optional[threading.Thread] = None
        self.continuous_callback: Optional[Callable] = None
        self.stop_listening_flag = threading.Event()

        # Profile & history
        self.profile = VoiceProfile()
        self.command_history = deque(maxlen=100)
        self.last_command_time = 0

        # ========== TEXT-TO-SPEECH INITIALIZATION ==========
        self.tts_enabled = True
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS voice properties
                self.tts_engine.setProperty('rate', 160)    # Speed (150-200 is good)
                self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
                
                # Try to set a female voice (more natural for Ava)
                voices = self.tts_engine.getProperty('voices')
                if len(voices) > 1:
                    # voices[1] is usually female on Windows
                    self.tts_engine.setProperty('voice', voices[1].id)
                    print(f"✅ TTS Voice: {voices[1].name}")
                
                print("✅ Text-to-Speech initialized")
            except Exception as e:
                print(f"⚠️ TTS initialization failed: {e}")
                self.tts_engine = None
                self.tts_enabled = False
        else:
            self.tts_engine = None
            self.tts_enabled = False

        # Calibrate mic
        self._calibrate_microphone()

        print(f"✅ Voice Assistant initialized (Language: {language})")

    # ========== TEXT-TO-SPEECH ==========

    def speak(self, text: str, force: bool = False):
        """
        Make Ava speak the given text
        
        Args:
            text: Text to speak
            force: Force speaking even if TTS is disabled
        """
        if not self.tts_enabled and not force:
            print(f"🔇 [Ava would say]: {text}")
            return
        
        if not self.tts_engine:
            print(f"🔇 [Ava]: {text}")
            return
        
        try:
            # Clean text for better speech
            clean_text = self._clean_text_for_speech(text)
            
            print(f"🗣️ Ava: {clean_text}")
            
            # Speak in a separate thread to avoid blocking
            def _speak_thread():
                try:
                    self.tts_engine.say(clean_text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    print(f"⚠️ Speech error: {e}")
            
            # Use threading for non-blocking speech
            speech_thread = threading.Thread(target=_speak_thread, daemon=True)
            speech_thread.start()
            
        except Exception as e:
            print(f"⚠️ Speech error: {e}")
            print(f"🔇 [Ava]: {text}")

    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better TTS output"""
        # Remove emojis and special characters that TTS can't pronounce
        import re
        
        # Remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        
        # Replace common symbols with words
        replacements = {
            '✅': '',
            '❌': '',
            '⚠️': 'warning',
            '🎤': '',
            '🎵': '',
            '🔊': '',
            '🔇': '',
            '💙': '',
            '❤️': '',
            '✋': '',
            '👍': '',
            '&': 'and',
            '@': 'at',
            '#': 'hashtag',
        }
        
        for symbol, replacement in replacements.items():
            text = text.replace(symbol, replacement)
        
        # Clean up extra spaces
        text = ' '.join(text.split())
        
        return text.strip()

    def set_tts_enabled(self, enabled: bool):
        """Enable or disable TTS"""
        self.tts_enabled = enabled and self.tts_engine is not None
        status = "enabled" if self.tts_enabled else "disabled"
        print(f"🔊 TTS {status}")

    def set_speech_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        if self.tts_engine:
            self.tts_engine.setProperty('rate', rate)
            print(f"🎤 Speech rate set to {rate}")

    def set_speech_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        if self.tts_engine:
            volume = max(0.0, min(1.0, volume))
            self.tts_engine.setProperty('volume', volume)
            print(f"🔊 Speech volume set to {volume:.1f}")

    # ========== CALIBRATION ==========

    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with sr.Microphone(sample_rate=self.sample_rate) as source:
                print("🎤 Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"✅ Microphone calibrated (threshold: {self.recognizer.energy_threshold:.0f})")
        except Exception as e:
            print(f"⚠️ Microphone calibration failed: {e}")

    # ========== SINGLE LISTEN ==========

    def listen_and_execute(self) -> VoiceCommand:
        """Listen for a single command and return the result."""
        try:
            # Create a new microphone instance for each listen
            with sr.Microphone(sample_rate=self.sample_rate) as source:
                print("🎤 Listening...")
                
                # Quick adjustment for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = self.recognizer.listen(
                    source,
                    timeout=self.duration,
                    phrase_time_limit=self.duration
                )

                print("🔄 Processing speech...")
                text = self.recognizer.recognize_google(audio, language=self.language)
                command_text = text.lower().strip()
                print(f"📝 Recognized: '{command_text}'")

                # Wake-word gate
                if self.wake_word_enabled:
                    if not self._check_wake_word(command_text):
                        return VoiceCommand(
                            command=command_text, success=False,
                            response=f"Wake word '{self.wake_word}' not detected",
                            confidence=0.5
                        )
                    command_text = command_text.replace(self.wake_word, "").strip()

                # Map → action
                action = self._map_command(command_text)

                if action:
                    cmd = VoiceCommand(command=command_text, success=True,
                                       response=action, confidence=1.0)
                    self.profile.add_command(cmd)
                    self.command_history.append(cmd)
                    self.last_command_time = time.time()
                    return cmd
                else:
                    return VoiceCommand(command=command_text, success=False,
                                        response="Command not recognized", confidence=0.3)

        except sr.WaitTimeoutError:
            return VoiceCommand(command="", success=False,
                                response="Listening timeout - no speech detected", confidence=0.0)
        except sr.UnknownValueError:
            return VoiceCommand(command="", success=False,
                                response="Could not understand audio", confidence=0.0)
        except sr.RequestError as e:
            return VoiceCommand(command="", success=False,
                                response=f"Speech recognition service error: {e}", confidence=0.0)
        except Exception as e:
            print(f"⚠️ Voice error: {e}")
            traceback.print_exc()
            return VoiceCommand(command="", success=False,
                                response=f"Error: {e}", confidence=0.0)

    # ========== COMMAND MAPPING ==========

    def _map_command(self, command_text: str) -> Optional[str]:
        """Map command text to action"""
        # Exact match first
        if command_text in self.command_map:
            return self.command_map[command_text]

        # Fuzzy / partial match
        for key, value in self.command_map.items():
            if key in command_text or command_text in key:
                return value

        return None

    # ========== WAKE WORD ==========

    def _check_wake_word(self, text: str) -> bool:
        """Check if wake word is in text"""
        return self.wake_word.lower() in text.lower()

    def enable_wake_word(self, wake_word: str):
        """Enable wake word detection"""
        self.wake_word = wake_word.lower()
        self.wake_word_enabled = True
        print(f"✅ Wake word enabled: '{wake_word}'")

    def disable_wake_word(self):
        """Disable wake word detection"""
        self.wake_word_enabled = False
        print("🔇 Wake word disabled")

    # ========== CONTINUOUS LISTENING ==========

    def start_continuous_listening(self, callback: Callable[[VoiceCommand], None]):
        """Start continuous listening mode"""
        if self.is_listening_continuous:
            print("⚠️ Already listening continuously")
            return

        self.continuous_callback = callback
        self.is_listening_continuous = True
        self.stop_listening_flag.clear()

        self.continuous_thread = threading.Thread(
            target=self._continuous_listen_loop, daemon=True
        )
        self.continuous_thread.start()
        print("✅ Continuous listening started")

    def stop_continuous_listening(self):
        """Stop continuous listening mode"""
        if not self.is_listening_continuous:
            return

        self.is_listening_continuous = False
        self.stop_listening_flag.set()

        if self.continuous_thread:
            self.continuous_thread.join(timeout=2.0)

        print("🔇 Continuous listening stopped")

    def _continuous_listen_loop(self):
        """Continuous listening loop"""
        print("🎤 Continuous listening loop started")

        while self.is_listening_continuous and not self.stop_listening_flag.is_set():
            try:
                # Use listen_and_execute which now creates its own microphone context
                result = self.listen_and_execute()

                if self.continuous_callback and result.success:
                    self.continuous_callback(result)

                time.sleep(0.5)  # Small delay between listens
                
            except Exception as e:
                print(f"⚠️ Continuous listening error: {e}")
                traceback.print_exc()
                time.sleep(1.0)

        print("🔇 Continuous listening loop ended")

    # ========== STATS / CONFIG ==========

    def get_statistics(self) -> dict:
        """Get voice assistant statistics"""
        return {
            'total_commands': self.profile.total_commands,
            'successful_commands': self.profile.successful_commands,
            'success_rate': self.profile.get_success_rate(),
            'favorite_commands': dict(sorted(
                self.profile.favorite_commands.items(),
                key=lambda x: x[1], reverse=True
            )[:5]),
            'language': self.language,
            'wake_word_enabled': self.wake_word_enabled,
            'tts_enabled': self.tts_enabled,
        }

    def reset(self):
        """Reset voice assistant"""
        self.command_history.clear()
        self.profile = VoiceProfile()
        self._calibrate_microphone()
        print("🔄 Voice assistant reset")

    def set_language(self, language: str):
        """Set recognition language"""
        self.language = language
        print(f"🌍 Language changed to: {language}")

    def add_custom_command(self, phrase: str, action: str):
        """Add custom command"""
        self.command_map[phrase.lower()] = action
        # Don't print for every command during bulk registration
        # print(f"✅ Custom command added: '{phrase}' -> {action}")

    def remove_custom_command(self, phrase: str):
        """Remove custom command"""
        key = phrase.lower()
        if key in self.command_map:
            del self.command_map[key]
            print(f"🗑️ Custom command removed: '{phrase}'")

    # ========== CLEANUP ==========

    def __del__(self):
        """Cleanup on deletion"""
        if self.is_listening_continuous:
            self.stop_continuous_listening()
        
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass