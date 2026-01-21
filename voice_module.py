import speech_recognition as sr
import sounddevice as sd
import numpy as np
import webbrowser
import os
import datetime
import threading
import queue
import time
from typing import Optional, Callable, Dict, List, Tuple
from dataclasses import dataclass
import json


@dataclass
class VoiceCommand:
    """Data class for voice command results"""
    success: bool
    command: str
    response: str
    confidence: float
    timestamp: datetime.datetime


class VoiceAssistant:
    """
    Advanced voice assistant with continuous listening, custom commands,
    noise suppression, and multi-threaded processing
    """
    
    def __init__(self, 
                 sample_rate: int = 16000, 
                 duration: float = 4.0,
                 energy_threshold: int = 300,
                 pause_threshold: float = 0.8):
        
        # --- Core components ---
        self.recognizer = sr.Recognizer()
        self.sample_rate = sample_rate
        self.duration = duration
        
        # --- Advanced recognition settings ---
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
        # --- Continuous listening ---
        self.listening = False
        self.listen_thread = None
        self.command_queue = queue.Queue()
        self.callback_function = None
        
        # --- Command history ---
        self.command_history: List[VoiceCommand] = []
        self.max_history = 50
        
        # --- Custom commands registry ---
        self.custom_commands: Dict[str, Callable] = {}
        self._register_default_commands()
        
        # --- Performance tracking ---
        self.total_commands = 0
        self.successful_commands = 0
        self.response_times = []
        
        # --- Wake word detection ---
        self.wake_word = None
        self.wake_word_active = False
        
        # --- Audio preprocessing ---
        self.noise_reduce = True
        self.auto_gain = True
        
    def _register_default_commands(self):
        """Register built-in command handlers"""
        
        # Web commands
        self.register_command(["google", "search google"], self._open_google)
        self.register_command(["youtube", "open youtube"], self._open_youtube)
        self.register_command(["gmail", "email", "open gmail"], self._open_gmail)
        
        # Application commands
        self.register_command(["notepad", "open notepad"], self._open_notepad)
        self.register_command(["calculator", "calc"], self._open_calculator)
        
        # System commands
        self.register_command(["time", "what time"], self._get_time)
        self.register_command(["date", "what date"], self._get_date)
        
        # Mouse control commands
        self.register_command(["left click", "click"], self._trigger_left_click)
        self.register_command(["right click"], self._trigger_right_click)
        self.register_command(["double click"], self._trigger_double_click)
        self.register_command(["scroll up"], self._scroll_up)
        self.register_command(["scroll down"], self._scroll_down)
        
    def register_command(self, keywords: List[str], handler: Callable):
        """Register a custom command handler"""
        for keyword in keywords:
            self.custom_commands[keyword.lower()] = handler
    
    def listen_and_execute(self) -> VoiceCommand:
        """Single-shot voice command recognition and execution"""
        start_time = time.time()
        
        try:
            print("🎤 Listening...")
            recording = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="int16"
            )
            sd.wait()
            
            audio = sr.AudioData(
                recording.tobytes(),
                self.sample_rate,
                2
            )
            
            print("🔍 Recognizing...")
            command = self.recognizer.recognize_google(audio).lower()
            
            result = self._execute_command(command)
            
            voice_cmd = VoiceCommand(
                success=True,
                command=command,
                response=result,
                confidence=0.85,
                timestamp=datetime.datetime.now()
            )
            
            self.total_commands += 1
            self.successful_commands += 1
            self._add_to_history(voice_cmd)
            
            print(f"✅ {result}")
            return voice_cmd
            
        except sr.UnknownValueError:
            voice_cmd = VoiceCommand(
                success=False,
                command="",
                response="Could not understand audio",
                confidence=0.0,
                timestamp=datetime.datetime.now()
            )
            self.total_commands += 1
            return voice_cmd
            
        except sr.RequestError as e:
            voice_cmd = VoiceCommand(
                success=False,
                command="",
                response=f"Speech service error: {e}",
                confidence=0.0,
                timestamp=datetime.datetime.now()
            )
            return voice_cmd
            
        except Exception as e:
            voice_cmd = VoiceCommand(
                success=False,
                command="",
                response=f"Error: {e}",
                confidence=0.0,
                timestamp=datetime.datetime.now()
            )
            return voice_cmd
    
    def _execute_command(self, command: str) -> str:
        """Execute recognized command"""
        
        if command in self.custom_commands:
            return self.custom_commands[command]()
        
        for keyword, handler in self.custom_commands.items():
            if keyword in command:
                return handler()
        
        if "search for" in command or "google" in command:
            query = command.replace("search for", "").replace("google", "").strip()
            return self._search_web(query)
        
        return f"Recognized: '{command}' (no handler found)"
    
    def start_continuous_listening(self, callback: Optional[Callable] = None):
        """Start continuous background listening"""
        if self.listening:
            return
        
        self.listening = True
        self.callback_function = callback
        self.listen_thread = threading.Thread(target=self._continuous_listen_loop, daemon=True)
        self.listen_thread.start()
        print("🎤 Continuous listening started")
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self.listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2.0)
        print("🔇 Continuous listening stopped")
    
    def _continuous_listen_loop(self):
        """Background thread for continuous listening"""
        with sr.Microphone(sample_rate=self.sample_rate) as source:
            print("🎧 Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    command = self.recognizer.recognize_google(audio).lower()
                    
                    if self.wake_word_active and self.wake_word not in command:
                        continue
                    
                    result = self._execute_command(command)
                    
                    voice_cmd = VoiceCommand(
                        success=True,
                        command=command,
                        response=result,
                        confidence=0.85,
                        timestamp=datetime.datetime.now()
                    )
                    
                    self._add_to_history(voice_cmd)
                    
                    if self.callback_function:
                        self.callback_function(voice_cmd)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception:
                    time.sleep(0.1)
    
    def _add_to_history(self, cmd: VoiceCommand):
        """Add command to history"""
        self.command_history.append(cmd)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
    
    # Command Handlers
    def _open_google(self) -> str:
        webbrowser.open("https://www.google.com")
        return "✅ Opened Google"
    
    def _open_youtube(self) -> str:
        webbrowser.open("https://www.youtube.com")
        return "✅ Opened YouTube"
    
    def _open_gmail(self) -> str:
        webbrowser.open("https://mail.google.com")
        return "✅ Opened Gmail"
    
    def _open_notepad(self) -> str:
        try:
            os.system("notepad" if os.name == 'nt' else "gedit &")
            return "✅ Opened Notepad"
        except:
            return "❌ Could not open text editor"
    
    def _open_calculator(self) -> str:
        try:
            os.system("calc" if os.name == 'nt' else "gnome-calculator &")
            return "✅ Opened Calculator"
        except:
            return "❌ Could not open calculator"
    
    def _get_time(self) -> str:
        now = datetime.datetime.now()
        return f"🕐 Current time: {now.strftime('%I:%M %p')}"
    
    def _get_date(self) -> str:
        today = datetime.date.today()
        return f"📅 Today's date: {today.strftime('%B %d, %Y')}"
    
    def _trigger_left_click(self) -> str:
        return "MOUSE_LEFT_CLICK"
    
    def _trigger_right_click(self) -> str:
        return "MOUSE_RIGHT_CLICK"
    
    def _trigger_double_click(self) -> str:
        return "MOUSE_DOUBLE_CLICK"
    
    def _scroll_up(self) -> str:
        return "MOUSE_SCROLL_UP"
    
    def _scroll_down(self) -> str:
        return "MOUSE_SCROLL_DOWN"
    
    def _search_web(self, query: str) -> str:
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            return f"🔍 Searching for: {query}"
        return "❌ No search query provided"
    
    def get_statistics(self) -> Dict:
        """Get performance statistics"""
        return {
            "total_commands": self.total_commands,
            "successful_commands": self.successful_commands,
            "success_rate": (self.successful_commands / self.total_commands * 100) 
                           if self.total_commands > 0 else 0,
        }