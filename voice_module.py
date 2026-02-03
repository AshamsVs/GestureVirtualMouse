"""
Voice Module for Ava AI Desktop Assistant
Handles voice recognition and command processing
"""

import speech_recognition as sr
import threading
import time
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass, field
from collections import deque


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


# ---------------------------------------------------------------------------
# FIX 7: Default command map lives here as a module-level TEMPLATE (never mutated).
#         Each VoiceAssistant instance gets its own copy in __init__, so
#         add_custom_command / remove_custom_command are instance-safe.
# ---------------------------------------------------------------------------
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
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        duration: float = 4.0,
        energy_threshold: int = 300,
        language: str = "en-US"
    ):
        self.recognizer = sr.Recognizer()
        self.microphone  = sr.Microphone(sample_rate=sample_rate)

        # Configuration
        self.duration  = duration
        self.language  = language
        self.recognizer.energy_threshold      = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold       = 0.8

        # FIX 7: each instance owns its own command map
        self.command_map: Dict[str, str] = dict(_DEFAULT_COMMAND_MAP)

        # Wake word
        self.wake_word_enabled = False
        self.wake_word         = "ava"

        # Continuous listening
        self.is_listening_continuous = False
        self.continuous_thread: Optional[threading.Thread] = None
        self.continuous_callback: Optional[Callable] = None
        self.stop_listening_flag = threading.Event()

        # Profile & history
        self.profile         = VoiceProfile()
        self.command_history = deque(maxlen=100)
        self.last_command_time = 0

        # Calibrate mic
        self._calibrate_microphone()

        print(f"✅ Voice Assistant initialized (Language: {language})")

    # ========== CALIBRATION ==========

    def _calibrate_microphone(self):
        try:
            with self.microphone as source:
                print("🎤 Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"✅ Microphone calibrated (threshold: {self.recognizer.energy_threshold:.0f})")
        except Exception as e:
            print(f"⚠️ Microphone calibration failed: {e}")

    # ========== SINGLE LISTEN ==========

    def listen_and_execute(self) -> VoiceCommand:
        """Listen for a single command and return the result."""
        try:
            with self.microphone as source:
                print("🎤 Listening...")
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
            return VoiceCommand(command="", success=False,
                                response=f"Error: {e}", confidence=0.0)

    # ========== COMMAND MAPPING ==========

    def _map_command(self, command_text: str) -> Optional[str]:
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
        return self.wake_word.lower() in text.lower()

    def enable_wake_word(self, wake_word: str):
        self.wake_word         = wake_word.lower()
        self.wake_word_enabled = True
        print(f"✅ Wake word enabled: '{wake_word}'")

    def disable_wake_word(self):
        self.wake_word_enabled = False
        print("🔇 Wake word disabled")

    # ========== CONTINUOUS LISTENING ==========

    def start_continuous_listening(self, callback: Callable[[VoiceCommand], None]):
        if self.is_listening_continuous:
            print("⚠️ Already listening continuously")
            return

        self.continuous_callback     = callback
        self.is_listening_continuous = True
        self.stop_listening_flag.clear()

        self.continuous_thread = threading.Thread(
            target=self._continuous_listen_loop, daemon=True
        )
        self.continuous_thread.start()
        print("✅ Continuous listening started")

    def stop_continuous_listening(self):
        if not self.is_listening_continuous:
            return

        self.is_listening_continuous = False
        self.stop_listening_flag.set()

        if self.continuous_thread:
            self.continuous_thread.join(timeout=2.0)

        print("🔇 Continuous listening stopped")

    def _continuous_listen_loop(self):
        print("🎤 Continuous listening loop started")

        while self.is_listening_continuous and not self.stop_listening_flag.is_set():
            try:
                result = self.listen_and_execute()

                if self.continuous_callback and result.success:
                    self.continuous_callback(result)

                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Continuous listening error: {e}")
                time.sleep(1.0)

        print("🔇 Continuous listening loop ended")

    # ========== STATS / CONFIG ==========

    def get_statistics(self) -> dict:
        return {
            'total_commands':      self.profile.total_commands,
            'successful_commands': self.profile.successful_commands,
            'success_rate':        self.profile.get_success_rate(),
            'favorite_commands':   dict(sorted(
                self.profile.favorite_commands.items(),
                key=lambda x: x[1], reverse=True
            )[:5]),
            'language':            self.language,
            'wake_word_enabled':   self.wake_word_enabled,
        }

    def reset(self):
        self.command_history.clear()
        self.profile = VoiceProfile()
        self._calibrate_microphone()
        print("🔄 Voice assistant reset")

    def set_language(self, language: str):
        self.language = language
        print(f"🌍 Language changed to: {language}")

    # FIX 7: these now mutate self.command_map (instance dict), not the class variable
    def add_custom_command(self, phrase: str, action: str):
        self.command_map[phrase.lower()] = action
        print(f"✅ Custom command added: '{phrase}' -> {action}")

    def remove_custom_command(self, phrase: str):
        key = phrase.lower()
        if key in self.command_map:
            del self.command_map[key]
            print(f"🗑️ Custom command removed: '{phrase}'")

    # ========== CLEANUP ==========

    def __del__(self):
        if self.is_listening_continuous:
            self.stop_continuous_listening()
