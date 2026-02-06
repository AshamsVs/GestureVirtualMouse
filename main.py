"""
Ava - AI Desktop Assistant
Professional gesture and voice controlled virtual mouse system
Powered by Ava's intelligent brain with enhanced features
Created by Ashams
"""

import customtkinter as ctk
import cv2
import pyautogui
import numpy as np
from typing import Optional, Tuple, List
import time
from collections import deque
import threading
import traceback

# Import UI components
try:
    from ui.main_window import MainWindow
    from ui.sidebar import Sidebar
    from ui.status_panel import StatusPanel
    from ui.dialogs import HelpDialog, SettingsDialog, AlertDialog
except ImportError:
    print("⚠️ Warning: UI components not found. Using fallback minimal UI.")
    MainWindow = Sidebar = StatusPanel = None
    HelpDialog = SettingsDialog = AlertDialog = None

# Import core systems
from voice_module import VoiceAssistant, VoiceCommand
from gestures import AdvancedHandTracker

# Import Ava's brain (FIXED: correct import path)
try:
    from ui.assistant import create_assistant, AvaCore, AssistantState
    ASSISTANT_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: Ava assistant module not found. Using basic mode.")
    ASSISTANT_AVAILABLE = False


class FallbackAssistant:
    """Fallback assistant when Ava module is not available"""
    def __init__(self, name="Ava"):
        self.name = name
        self.personality = _Personality(name)

    def initialize(self): return f"{self.name} initialized"
    def process_gesture(self, g): return f"Gesture: {g}"
    def process_voice_command(self, c): return f"Command: {c}"
    def handle_error(self, t, m): return f"Error: {m}"
    def start_listening(self): return "Listening..."
    def voice_not_understood(self): return "Could not understand"
    def toggle_mouse(self, s): return f"Mouse {'enabled' if s else 'disabled'}"
    def change_mode(self, m): return f"Mode changed to {m}"
    def set_voice_active(self, s): return f"Voice {'active' if s else 'inactive'}"
    def reset(self): return "System reset"
    def shutdown(self): return f"{self.name} shutting down"
    def get_tip(self): return "💡 Tip: Use gestures for hands-free control!"
    def get_statistics(self): return "Stats not available"
    def get_status_report(self): return {"commands_executed": 0, "gestures_detected": 0, "session_duration": 0}
    def update_context(self, **kwargs): pass


class _Personality:
    """Helper so personality attributes are real methods, not broken lambdas"""
    def __init__(self, name):
        self.assistant_name = name

    def system_ready(self):
        return f"{self.assistant_name} is ready!"

    def greeting(self):
        return f"Hello! I'm {self.assistant_name}, your AI assistant."


class AvaDesktopAssistant(ctk.CTk):
    """
    Ava - AI Desktop Assistant
    Integrates advanced gesture control, voice commands, and AI intelligence
    """

    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("🤖 Ava - AI Desktop Assistant Pro")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Initialize Ava's Brain FIRST ---
        if ASSISTANT_AVAILABLE:
            try:
                self.ava = create_assistant("Ava")
            except Exception as e:
                print(f"⚠️ Failed to create Ava assistant: {e}")
                self.ava = FallbackAssistant("Ava")
        else:
            self.ava = FallbackAssistant("Ava")

        # --- Initialize Core Systems ---
        self._init_core_systems()

        # --- Initialize State ---
        self._init_state()

        # --- Log startup ---
        self._log_startup()

        # --- Build UI ---
        self._build_ui()

        # --- Camera Check ---
        if not self.cap or not self.cap.isOpened():
            error_msg = self.ava.handle_error("camera", "Camera not found or unavailable")
            self._show_error(error_msg)
            if self.status_panel:
                self.status_panel.log(error_msg, "ERROR")

        # --- Start Application ---
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self.start_systems)

    # ========== INIT ==========

    def _init_core_systems(self):
        """Initialize core systems with error handling"""

        # Voice Assistant
        try:
            self.voice = VoiceAssistant(
                sample_rate=16000,
                duration=4.0,
                energy_threshold=300,
                language="en-US"
            )
            print("✅ Voice Assistant initialized")
            
            # EXPANDED: Register ALL commands in voice module
            all_commands = []
            
            # Web commands - Social Media & Streaming
            web_commands = [
                "google", "open google", "search google",
                "youtube", "open youtube", "yt",
                "gmail", "email", "open gmail", "mail",
                "github", "open github",
                "facebook", "open facebook", "fb",
                "twitter", "open twitter", "x",
                "instagram", "open instagram", "insta",
                "linkedin", "open linkedin",
                "reddit", "open reddit",
                "tiktok", "open tiktok",
                "pinterest", "open pinterest",
                "snapchat", "open snapchat",
                "netflix", "open netflix",
                "spotify", "open spotify",
                "amazon prime", "prime video",
                "disney plus", "disney",
                "hulu", "open hulu",
                "twitch", "open twitch",
                "amazon", "open amazon",
                "ebay", "open ebay",
                "wikipedia", "wiki",
                "stackoverflow", "stack overflow",
                "coursera", "open coursera",
                "udemy", "open udemy",
                "chatgpt", "chat gpt",
                "google drive", "drive", "gdrive",
                "dropbox", "open dropbox",
                "onedrive", "one drive",
                "whatsapp", "open whatsapp",
                "discord", "open discord",
                "slack", "open slack",
                "zoom", "open zoom",
                "teams", "microsoft teams"
            ]
            all_commands.extend(web_commands)
            
            # Application commands
            app_commands = [
                "notepad", "open notepad", "text editor",
                "calculator", "calc", "open calculator",
                "explorer", "file explorer", "open explorer", "files",
                "browser", "open browser", "chrome",
                "paint", "open paint", "draw",
                "word", "open word", "microsoft word",
                "excel", "open excel", "spreadsheet",
                "powerpoint", "open powerpoint", "ppt",
                "outlook", "open outlook",
                "task manager", "open task manager",
                "control panel", "settings",
                "command prompt", "cmd", "terminal",
                "powershell",
                "photos", "pictures",
                "camera", "webcam",
                "video player", "vlc",
                "vscode", "visual studio code", "code",
                "pycharm", "open pycharm"
            ]
            all_commands.extend(app_commands)
            
            # Media commands
            media_commands = [
                "play music", "music", "play song", "play songs",
                "pause", "pause music", "stop music",
                "next", "next song", "skip",
                "previous", "previous song", "back",
                "volume up", "increase volume", "louder",
                "volume down", "decrease volume", "quieter",
                "mute", "unmute",
                "volume max", "maximum volume"
            ]
            all_commands.extend(media_commands)
            
            # Conversation commands - EXPANDED for "Her" style
            conversation_commands = [
                # Greetings
                "hi", "hello", "hey", "hi ava", "hello ava",
                "good morning", "good afternoon", "good evening",
                "what's up", "whats up", "sup", "yo",
                
                # Questions about Ava
                "how are you", "how are you doing", "how's it going",
                "who created you", "who made you", "who built you", "your creator",
                "what can you do", "what do you do", "what are you",
                "introduce yourself", "tell me about yourself",
                "what's your name", "whats your name", "who are you",
                "how old are you", "your age", "when were you created",
                
                # Emotions & personality
                "do you have feelings", "can you feel", "are you alive",
                "favorite color", "favorite food",
                "do you eat", "what do you eat",
                
                # Affection & social
                "i love you", "love you", "i like you",
                "you're awesome", "you're great", "you're amazing",
                "good job", "well done", "thank you", "thanks",
                
                # Fun & random
                "tell me a joke", "joke", "make me laugh",
                "talk to me", "chat with me", "say something",
                "weather", "what's the weather",
                "meaning of life",
                
                # Apologies & goodbyes
                "sorry", "i'm sorry", "my bad",
                "goodbye", "bye", "see you later", "take care"
            ]
            all_commands.extend(conversation_commands)
            
            # System commands
            system_commands = [
                "time", "what time", "current time", "what's the time",
                "date", "what date", "today", "what day",
                "screenshot", "take screenshot", "capture screen",
                "close window", "close", "exit",
                "minimize all", "show desktop",
                "lock computer", "lock screen"
            ]
            all_commands.extend(system_commands)
            
            # Mouse commands
            mouse_commands = [
                "click", "left click",
                "right click",
                "double click",
                "scroll up", "scroll down"
            ]
            all_commands.extend(mouse_commands)
            
            # Register all in voice module
            for cmd in all_commands:
                self.voice.add_custom_command(cmd, "AVA_COMMAND")
            
            print(f"✅ Registered {len(all_commands)} voice commands")
            
        except Exception as e:
            print(f"⚠️ Voice initialization error: {e}")
            self.voice = None

        # Hand Tracker
        try:
            self.hand_tracker = AdvancedHandTracker(
                model_path="hand_landmarker.task"
            )
            print("✅ Hand Tracker initialized")
        except Exception as e:
            print(f"⚠️ Hand tracker initialization error: {e}")
            print("📝 Make sure 'hand_landmarker.task' model file exists")
            self.hand_tracker = None

        # Camera Setup
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 60)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                print("✅ Camera initialized")
            else:
                print("⚠️ Camera not available")
                self.cap = None
        except Exception as e:
            print(f"⚠️ Camera error: {e}")
            self.cap = None

        # PyAutoGUI Configuration
        try:
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0
            self.screen_w, self.screen_h = pyautogui.size()
            print(f"✅ Screen: {self.screen_w}x{self.screen_h}")
        except Exception as e:
            print(f"⚠️ PyAutoGUI error: {e}")
            self.screen_w, self.screen_h = 1920, 1080

    def _init_state(self):
        """Initialize application state variables"""

        # Control states
        self.mouse_enabled = True
        self.voice_listening = False
        self.continuous_voice = False
        self.show_landmarks = True
        self.assistant_mode = "gesture"

        # Cursor control
        self.cursor_smoothing = True
        self.cursor_speed = 1.5
        self.cursor_history = deque(maxlen=5)

        # Gesture state
        self.last_gesture = None
        self.gesture_cooldown = 0

        # Drag state
        self.is_dragging = False
        self.drag_hold_frames = 0
        self.drag_threshold = 30
        self.pinch_start_time = None

        # Performance tracking
        self.fps_counter = deque(maxlen=30)
        self.frame_counter = 0
        self.gesture_count = 0
        self.command_count = 0
        self.session_start = time.time()

        # System running flag
        self.running = True

    # ========== UI BUILD ==========

    def _build_ui(self):
        """Build the complete UI using components"""

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=320)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # === Main Window (Video Feed) ===
        if MainWindow:
            self.main_window = MainWindow(self)
            self.main_window.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        else:
            self.main_window = self._create_fallback_video_frame()

        # === Sidebar ===
        if Sidebar:
            self.sidebar = Sidebar(self, callbacks=self._get_sidebar_callbacks())
            self.sidebar.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        else:
            self.sidebar = self._create_fallback_controls()

        # === Status Panel ===
        if StatusPanel:
            self.status_panel = StatusPanel(self)
            self.status_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        else:
            self.status_panel = self._create_fallback_status()

    def _create_fallback_video_frame(self):
        frame = ctk.CTkFrame(self)
        label = ctk.CTkLabel(frame, text="Video Feed", font=("Arial", 20))
        label.pack(expand=True)
        self.video_label = label
        return frame

    def _create_fallback_controls(self):
        frame = ctk.CTkFrame(self, width=300)
        ctk.CTkLabel(frame, text="Controls", font=("Arial", 16)).pack(pady=10)
        return frame

    def _create_fallback_status(self):
        class FallbackStatus:
            def __init__(self, parent):
                self.frame = ctk.CTkFrame(parent)
            def log(self, msg, level="INFO"): print(f"[{level}] {msg}")
            def update_status(self, msg, color, icon): print(f"{icon} {msg}")
            def update_performance(self, fps, tfps=0, conf=0): pass
            def update_system_info(self, info): pass
            def log_gesture(self, g): print(f"Gesture: {g}")
            def log_command(self, c, r): print(f"Command: {c} -> {r}")

        panel = FallbackStatus(self)
        panel.frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        return panel

    def _get_sidebar_callbacks(self) -> dict:
        return {
            'mode_changed': self.on_mode_changed,
            'toggle_mouse': self.toggle_mouse,
            'speed_changed': self.on_speed_changed,
            'voice_command': self.start_voice_command,
            'toggle_continuous_voice': self.toggle_continuous_voice,
            'set_wake_word': self.set_wake_word,
            'toggle_landmarks': self.toggle_landmarks,
            'show_gesture_guide': self.show_gesture_guide,
            'toggle_smoothing': self.toggle_smoothing,
            'toggle_autostart': self.toggle_autostart,
            'toggle_tray': self.toggle_tray,
            'reset': self.reset_system,
            'help': self.show_help,
            'settings': self.show_settings,
        }

    # ========== STARTUP ==========

    def start_systems(self):
        """Start main systems after UI is ready"""
        try:
            greeting = self.ava.initialize()
            self.status_panel.log(greeting, "SUCCESS")
            self.status_panel.log(self.ava.personality.system_ready(), "INFO")
            self.status_panel.log(f"Screen resolution: {self.screen_w}x{self.screen_h}", "INFO")

            self.ava.update_context(
                current_mode=self.assistant_mode,
                mouse_enabled=self.mouse_enabled
            )

            if hasattr(self.main_window, 'update_mode'):
                self.main_window.update_mode("ACTIVE", "lightgreen")
                self.main_window.set_title(f"🤖 {self.ava.personality.assistant_name}")

            self.update_frame()
            self.update_stats()

            self.after(2000, lambda: self.status_panel.log(self.ava.get_tip(), "INFO"))

        except Exception as e:
            print(f"⚠️ Startup error: {e}")
            traceback.print_exc()

    # ========== CAMERA & TRACKING ==========

    def update_frame(self):
        """Main video processing loop"""
        if not self.running:
            return

        start_time = time.time()

        if not self.cap or not self.cap.isOpened():
            self.after(100, self.update_frame)
            return

        ret, frame = self.cap.read()
        if not ret:
            self.after(16, self.update_frame)
            return

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        try:
            if self.assistant_mode in ["gesture", "hybrid"] and self.hand_tracker:
                frame = self._process_gestures(frame, h, w)

            if hasattr(self.main_window, 'update_video'):
                self.main_window.update_video(frame, size=(800, 600))

        except Exception as e:
            print(f"⚠️ Frame processing error: {e}")
            traceback.print_exc()

        # Performance tracking
        frame_time = time.time() - start_time
        fps = 1.0 / frame_time if frame_time > 0 else 0
        self.fps_counter.append(fps)

        if hasattr(self.main_window, 'update_fps'):
            self.main_window.update_fps(fps)

        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1

        self.frame_counter += 1
        self.after(16, self.update_frame)

    def _process_gestures(self, frame, h: int, w: int):
        """Process hand gestures"""

        # find_hands() returns (frame, List[HandData])
        frame, hands = self.hand_tracker.find_hands(frame)

        if hands:
            # Use the dominant (most confident) hand
            hand = self.hand_tracker.get_dominant_hand()

            if hand:
                # --- Cursor movement via index fingertip ---
                index_pos = self.hand_tracker.get_finger_position("index")
                if index_pos and self.mouse_enabled:
                    self._move_cursor_smooth(index_pos[0], index_pos[1], (h, w))

                # --- Gesture handling ---
                if hand.gesture:
                    self._handle_gesture(hand.gesture.value)

            # --- Drawing ---
            if self.show_landmarks:
                frame = self.hand_tracker.draw_hand_data(frame, hands)

            # Drag indicator overlay
            if self.is_dragging:
                cv2.putText(frame, "DRAGGING", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)
                cv2.circle(frame, (30, 30), 15, (255, 0, 255), -1)

            self.status_panel.update_status("Hand detected", "lightgreen", "✋")

        else:
            # No hand detected
            if self.is_dragging:
                self._end_drag()
                self.status_panel.log("Drag cancelled (hand lost)", "WARNING")

            self.status_panel.update_status("Searching for hand...", "orange", "🔍")

        return frame

    # ========== CURSOR CONTROL ==========

    def _move_cursor_smooth(self, finger_x: int, finger_y: int, frame_shape: Tuple):
        """Move cursor with smoothing"""
        h, w = frame_shape

        screen_x = int(finger_x * self.screen_w / w * self.cursor_speed)
        screen_y = int(finger_y * self.screen_h / h * self.cursor_speed)

        margin = 10
        screen_x = max(margin, min(self.screen_w - margin, screen_x))
        screen_y = max(margin, min(self.screen_h - margin, screen_y))

        if self.cursor_smoothing:
            self.cursor_history.append((screen_x, screen_y))

            if len(self.cursor_history) > 1:
                positions = np.array(self.cursor_history)
                weights = np.linspace(0.5, 1.0, len(positions))
                smooth_x = int(np.average(positions[:, 0], weights=weights))
                smooth_y = int(np.average(positions[:, 1], weights=weights))
                try:
                    pyautogui.moveTo(smooth_x, smooth_y, _pause=False)
                except Exception:
                    pass
            else:
                try:
                    pyautogui.moveTo(screen_x, screen_y, _pause=False)
                except Exception:
                    pass
        else:
            try:
                pyautogui.moveTo(screen_x, screen_y, _pause=False)
            except Exception:
                pass

    # ========== GESTURE HANDLING ==========

    def _handle_gesture(self, gesture: str):
        """Handle detected gestures"""

        if not gesture:
            return

        gesture_name = gesture.lower()

        # === DRAG LOGIC (PINCH) ===
        if gesture_name == "pinch":
            self.drag_hold_frames += 1

            if self.pinch_start_time is None:
                self.pinch_start_time = time.time()

            pinch_duration = time.time() - self.pinch_start_time

            if pinch_duration >= 1.0 and not self.is_dragging:
                self._start_drag()
                return
            elif self.is_dragging:
                return
            elif self.gesture_cooldown == 0 and pinch_duration < 0.3:
                try:
                    pyautogui.click()
                    response = self.ava.process_gesture("PINCH")
                    self.status_panel.update_status(response, "yellow", "👌")
                    self.status_panel.log_gesture("PINCH (Click)")
                    self.gesture_cooldown = 15
                    self.gesture_count += 1
                except Exception:
                    pass
                return

        else:
            self.pinch_start_time = None
            if self.is_dragging:
                self._end_drag()
                return

        # Reset hold counter for non-pinch
        if gesture_name != "pinch":
            self.drag_hold_frames = 0

        if self.is_dragging:
            return

        if self.gesture_cooldown > 0:
            return

        if gesture_name == self.last_gesture:
            return

        self.last_gesture = gesture_name
        self.gesture_cooldown = 15
        self.gesture_count += 1

        response = self.ava.process_gesture(gesture_name)

        try:
            if gesture_name == "open_palm":
                pyautogui.rightClick()
                self.status_panel.update_status(response, "orange", "✋")
                self.status_panel.log_gesture("OPEN_PALM (Right Click)")

            elif gesture_name == "fist":
                pyautogui.doubleClick()
                self.status_panel.update_status(response, "red", "✊")
                self.status_panel.log_gesture("FIST (Double Click)")

            elif gesture_name == "peace":
                self.status_panel.update_status(response, "lightblue", "✌️")
                self.status_panel.log_gesture("PEACE")

            elif gesture_name == "thumbs_up":
                self.status_panel.update_status(response, "lightgreen", "👍")
                self.status_panel.log_gesture("THUMBS_UP")

            elif gesture_name == "thumbs_down":
                self.status_panel.update_status(response, "orange", "👎")
                self.status_panel.log_gesture("THUMBS_DOWN")

            elif gesture_name == "three":
                self.status_panel.update_status(response, "purple", "🤟")
                self.status_panel.log_gesture("THREE")

        except Exception as e:
            print(f"⚠️ Gesture execution error: {e}")

    def _start_drag(self):
        try:
            self.is_dragging = True
            pyautogui.mouseDown()
            response = self.ava.process_gesture("DRAG_START")
            self.status_panel.update_status(response, "purple", "🔒")
            self.status_panel.log("Drag started", "SUCCESS")
            if hasattr(self.main_window, 'show_message'):
                self.main_window.show_message("🔒 DRAGGING", 1000)
        except Exception as e:
            print(f"⚠️ Drag start error: {e}")

    def _end_drag(self):
        try:
            pyautogui.mouseUp()
            self.is_dragging = False
            self.drag_hold_frames = 0
            self.pinch_start_time = None
            response = self.ava.process_gesture("DRAG_END")
            self.status_panel.update_status(response, "lightgreen", "✅")
            self.status_panel.log("Drag ended", "SUCCESS")
            self.gesture_cooldown = 20
        except Exception as e:
            print(f"⚠️ Drag end error: {e}")

    # ========== VOICE CONTROL ==========

    def start_voice_command(self):
        """Start single voice command"""
        if not self.voice:
            self.status_panel.log("Voice assistant not available", "ERROR")
            return

        if not self.voice_listening:
            self.voice_listening = True
            if hasattr(self.sidebar, 'set_voice_button_state'):
                self.sidebar.set_voice_button_state(False)
            threading.Thread(target=self._run_voice_command, daemon=True).start()

    def _run_voice_command(self):
        """Run single voice command with proper command routing"""
        try:
            listening_msg = self.ava.start_listening()
            self.status_panel.update_status(listening_msg, "yellow", "🎤")
            if hasattr(self.main_window, 'update_mode'):
                self.main_window.update_mode("LISTENING", "yellow")

            # Listen for voice input
            result = self.voice.listen_and_execute()

            if result.success and result.command:
                # Process command through Ava's brain
                ava_response = self.ava.process_voice_command(result.command)
                
                # Handle basic mouse commands from voice_module
                self._handle_voice_command(result)
                
                # Determine which response to display
                if ava_response and ava_response not in ["Command not recognized", None]:
                    # Ava understood and executed the command
                    display_response = ava_response
                    color = "lightgreen"
                    icon = "✅"
                elif result.response and "MOUSE_" in result.response:
                    # Voice module handled it (mouse command)
                    display_response = "Mouse action executed"
                    color = "lightgreen"
                    icon = "✅"
                elif result.response == "AVA_COMMAND":
                    # Custom command recognized, use Ava's response
                    display_response = ava_response if ava_response else "Command processed"
                    color = "lightgreen"
                    icon = "✅"
                else:
                    # Command not recognized by either system
                    display_response = self.ava.voice_not_understood()
                    color = "orange"
                    icon = "❓"
            else:
                # Listening failed or no command detected
                display_response = result.response if result.response else self.ava.voice_not_understood()
                color = "orange"
                icon = "🎤"

            # Update UI
            self.status_panel.update_status(display_response, color, icon)
            self.status_panel.log_command(
                result.command if result.command else "unclear",
                display_response
            )

            if hasattr(self.main_window, 'update_mode'):
                self.main_window.update_mode("ACTIVE", "lightgreen")
            if hasattr(self.sidebar, 'set_voice_button_state'):
                self.sidebar.set_voice_button_state(True)

            self.voice_listening = False

            if result.success:
                self.command_count += 1

        except Exception as e:
            print(f"⚠️ Voice command error: {e}")
            traceback.print_exc()
            self.voice_listening = False
            if hasattr(self.sidebar, 'set_voice_button_state'):
                self.sidebar.set_voice_button_state(True)

    def toggle_continuous_voice(self):
        """Toggle continuous voice listening"""
        if not self.voice:
            self.status_panel.log("Voice assistant not available", "ERROR")
            return

        self.continuous_voice = not self.continuous_voice

        try:
            if self.continuous_voice:
                self.voice.start_continuous_listening(callback=self._on_voice_command)
                if hasattr(self.sidebar, 'set_continuous_voice_state'):
                    self.sidebar.set_continuous_voice_state(True)
                response = self.ava.set_voice_active(True)
                self.status_panel.update_status(response, "lightgreen", "🎤")
                self.status_panel.log(response, "INFO")
                if hasattr(self.main_window, 'update_mode'):
                    self.main_window.update_mode("LISTENING", "yellow")
            else:
                self.voice.stop_continuous_listening()
                if hasattr(self.sidebar, 'set_continuous_voice_state'):
                    self.sidebar.set_continuous_voice_state(False)
                response = self.ava.set_voice_active(False)
                self.status_panel.update_status(response, "gray", "🔇")
                self.status_panel.log(response, "INFO")
                if hasattr(self.main_window, 'update_mode'):
                    self.main_window.update_mode("ACTIVE", "lightgreen")
        except Exception as e:
            print(f"⚠️ Continuous voice error: {e}")

    def _on_voice_command(self, cmd: VoiceCommand):
        """Callback for continuous voice listening"""
        try:
            if cmd.success:
                ava_response = self.ava.process_voice_command(cmd.command)
                self._handle_voice_command(cmd)
                
                # Determine display response
                if ava_response and ava_response not in ["Command not recognized", None]:
                    display_response = ava_response
                elif cmd.response == "AVA_COMMAND":
                    display_response = ava_response if ava_response else "Command processed"
                else:
                    display_response = cmd.response
                
                self.status_panel.log_command(cmd.command, display_response)
                self.command_count += 1
        except Exception as e:
            print(f"⚠️ Voice callback error: {e}")
            traceback.print_exc()

    def _handle_voice_command(self, cmd: VoiceCommand):
        """Handle voice command execution - only for basic mouse commands"""
        response = cmd.response
        
        try:
            # Only handle basic MOUSE commands from voice_module here
            # Everything else is handled by Ava's command_registry
            if "MOUSE_LEFT_CLICK" in response:
                pyautogui.click()
            elif "MOUSE_RIGHT_CLICK" in response:
                pyautogui.rightClick()
            elif "MOUSE_DOUBLE_CLICK" in response:
                pyautogui.doubleClick()
            elif "MOUSE_SCROLL_UP" in response:
                pyautogui.scroll(3)
            elif "MOUSE_SCROLL_DOWN" in response:
                pyautogui.scroll(-3)
            # All other commands (open google, time, etc.) are handled by Ava
            
        except Exception as e:
            print(f"⚠️ Voice action error: {e}")

    def set_wake_word(self, wake_word: str):
        """Set wake word for voice activation"""
        if not self.voice:
            return
        try:
            if wake_word:
                self.voice.enable_wake_word(wake_word)
                self.status_panel.log(f"Wake word set to: '{wake_word}'", "SUCCESS")
        except Exception as e:
            print(f"⚠️ Wake word error: {e}")

    # ========== SETTINGS & CONTROLS ==========

    def toggle_mouse(self):
        """Toggle mouse control"""
        self.mouse_enabled = not self.mouse_enabled
        if hasattr(self.sidebar, 'set_mouse_state'):
            self.sidebar.set_mouse_state(self.mouse_enabled)

        response = self.ava.toggle_mouse(self.mouse_enabled)
        icon = "🟢" if self.mouse_enabled else "🔴"
        color = "lightgreen" if self.mouse_enabled else "red"
        self.status_panel.update_status(response, color, icon)
        self.status_panel.log(response, "INFO")

    def on_mode_changed(self, mode: str):
        """Handle mode change"""
        self.assistant_mode = mode
        response = self.ava.change_mode(mode)
        self.status_panel.log(response, "SUCCESS")

        if mode == "gesture":
            self.status_panel.log("Use your hand to control the cursor", "INFO")
        elif mode == "voice":
            self.status_panel.log("Use voice commands to control", "INFO")

    def on_speed_changed(self, speed: float):
        """Handle cursor speed change"""
        self.cursor_speed = speed
        if hasattr(self.sidebar, 'update_speed_label'):
            self.sidebar.update_speed_label(speed)

    def toggle_landmarks(self, state: bool):
        """Toggle landmark visibility"""
        self.show_landmarks = state

    def toggle_smoothing(self, state: bool):
        """Toggle cursor smoothing"""
        self.cursor_smoothing = state
        if not state:
            self.cursor_history.clear()

    def toggle_autostart(self, state: bool):
        """Toggle autostart on Windows boot"""
        self.status_panel.log(f"Autostart: {'enabled' if state else 'disabled'}", "INFO")

    def toggle_tray(self, state: bool):
        """Toggle minimize to tray"""
        self.status_panel.log(f"Minimize to tray: {'enabled' if state else 'disabled'}", "INFO")

    # ========== DIALOGS ==========

    def show_help(self):
        """Show help dialog"""
        if HelpDialog:
            HelpDialog(self)
        else:
            self.status_panel.log("Help dialog not available", "WARNING")

    def show_settings(self):
        """Show settings dialog"""
        if SettingsDialog:
            current_settings = {
                "fps_target": 60,
                "smoothing_level": 5,
                "gesture_confidence": 0.7,
                "drag_hold_time": 1.0,
                "voice_timeout": 4,
                "minimize_to_tray": False,
                "start_minimized": False,
                "auto_start": False
            }
            SettingsDialog(self, current_settings, on_save=self._on_settings_saved)
        else:
            self.status_panel.log("Settings dialog not available", "WARNING")

    def show_gesture_guide(self):
        """Show gesture guide (same as help)"""
        self.show_help()

    def _show_error(self, message: str):
        """Show error dialog"""
        if AlertDialog:
            AlertDialog(self, "Error", message, "error")
        else:
            print(f"ERROR: {message}")

    def _on_settings_saved(self, settings: dict):
        """Handle settings save"""
        self.status_panel.log("Settings saved", "SUCCESS")

        if "drag_hold_time" in settings:
            self.drag_threshold = int(settings["drag_hold_time"] * 60)

        if "smoothing_level" in settings and self.hand_tracker:
            smoothing = settings["smoothing_level"] / 10.0
            self.hand_tracker.smooth_factor = smoothing

    # ========== SYSTEM MANAGEMENT ==========

    def reset_system(self):
        """Reset the system"""
        try:
            if self.is_dragging:
                self._end_drag()

            if self.hand_tracker:
                self.hand_tracker.reset()

            self.cursor_history.clear()
            self.last_gesture = None
            self.gesture_cooldown = 0
            self.drag_hold_frames = 0
            self.pinch_start_time = None

            response = self.ava.reset()
            self.status_panel.update_status(response, "lightblue", "🔄")
            self.status_panel.log(response, "INFO")
        except Exception as e:
            print(f"⚠️ Reset error: {e}")

    def update_stats(self):
        """Update statistics display"""
        if not self.running:
            return

        try:
            avg_fps = np.mean(self.fps_counter) if self.fps_counter else 0
            tracking_fps = self.hand_tracker.get_fps() if self.hand_tracker else 0

            self.status_panel.update_performance(avg_fps, tracking_fps)

            self.status_panel.update_system_info({
                "mode": self.assistant_mode.title(),
                "mouse_enabled": self.mouse_enabled,
                "voice_active": self.continuous_voice,
                "gesture_count": self.gesture_count,
                "commands_total": self.command_count
            })
        except Exception as e:
            print(f"⚠️ Stats update error: {e}")

        self.after(500, self.update_stats)

    def _log_startup(self):
        """Log startup information"""
        print("=" * 60)
        print(f"🤖 {self.ava.personality.assistant_name.upper()} - AI DESKTOP ASSISTANT")
        print("=" * 60)
        print(f"✅ Created by Ashams with love and dedication")
        print(f"✅ Systems initialized")
        print(f"📺 Screen: {self.screen_w}x{self.screen_h}")
        print(f"🎥 Camera: {'Available' if self.cap and self.cap.isOpened() else 'Not Available'}")
        print(f"✋ Hand tracking: {'Ready' if self.hand_tracker else 'Not Available'}")
        print(f"🎤 Voice assistant: {'Ready' if self.voice else 'Not Available'}")
        print(f"🧠 Ava's brain: Active and caring!")
        print("=" * 60)

    def on_close(self):
        """Handle application close"""
        print(f"\n🔄 Shutting down {self.ava.personality.assistant_name}...")
        self.running = False

        try:
            shutdown_msg = self.ava.shutdown()
            self.status_panel.log(shutdown_msg, "INFO")

            if self.voice and self.continuous_voice:
                self.voice.stop_continuous_listening()

            if self.cap and self.cap.isOpened():
                self.cap.release()

            stats = self.ava.get_status_report()
            session_duration = time.time() - self.session_start

            print(f"📊 Session Summary:")
            print(f"   Commands executed: {stats.get('commands_executed', self.command_count)}")
            print(f"   Gestures detected: {stats.get('gestures_detected', self.gesture_count)}")
            print(f"   Session duration: {session_duration:.1f}s")
            print(f"   Average FPS: {np.mean(self.fps_counter) if self.fps_counter else 0:.1f}")

        except Exception as e:
            print(f"⚠️ Shutdown error: {e}")

        self.destroy()
        print("✅ Shutdown complete. Thank you for using Ava! 💙")


# ========== ENTRY POINT ==========

def main():
    """Main entry point"""
    try:
        print("🚀 Starting Ava AI Desktop Assistant Pro...")
        print("💝 Created by Ashams with love")
        print("📦 Initializing systems...")

        app = AvaDesktopAssistant()
        app.mainloop()

    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure 'hand_landmarker.task' model file exists")
        print("   2. Check camera permissions and availability")
        print("   3. Verify all dependencies are installed:")
        print("      - opencv-python")
        print("      - mediapipe")
        print("      - customtkinter")
        print("      - pyautogui")
        print("      - numpy")
        print("      - SpeechRecognition")


if __name__ == "__main__":
    main()
