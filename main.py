import customtkinter as ctk
import cv2
from PIL import Image
import threading
import pyautogui
import numpy as np
from typing import Optional, Tuple
import time
from collections import deque

from voice_module import VoiceAssistant, VoiceCommand
from gestures import HandTracker


class VirtualMouseApp(ctk.CTk):
    """
    Gesture and Voice Controlled Virtual Mouse System
    Pure AI-based hand tracking - No color markers needed!
    """
    
    def __init__(self):
        super().__init__()
        
        # --- Window Configuration ---
        self.title("🖱️ AI Gesture Virtual Mouse")
        self.geometry("1280x800")
        self.minsize(1000, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # --- Core Components ---
        self.voice = VoiceAssistant()
        self.hand_tracker = HandTracker()
        
        # --- Camera Setup ---
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not self.cap.isOpened():
            self.show_error("Camera not found! Please connect a webcam.")
            return
        
        # --- PyAutoGUI Optimization ---
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # --- State Management ---
        self.mouse_enabled = True
        self.voice_listening = False
        self.continuous_voice = False
        self.show_landmarks = True
        
        # --- Cursor Control ---
        self.screen_w, self.screen_h = pyautogui.size()
        self.cursor_smoothing = True
        self.cursor_speed = 1.5  # Speed multiplier
        
        # Smoothing
        self.prev_cursor_pos = None
        self.cursor_history = deque(maxlen=5)
        
        # --- Gesture State ---
        self.last_gesture = None
        self.gesture_cooldown = 0
        
        # --- Drag State ---
        self.is_dragging = False
        self.drag_gesture = None  # Track which gesture initiated drag
        self.drag_hold_frames = 0  # Count frames gesture is held
        self.drag_threshold = 8  # Frames to hold before drag activates
        
        # --- Performance ---
        self.fps_counter = deque(maxlen=30)
        self.frame_counter = 0
        
        # --- Build UI ---
        self._create_ui()
        
        # --- Start Systems ---
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_frame()
        self.update_stats()
        
        print("✅ AI Gesture Mouse Initialized")
        print(f"📺 Screen: {self.screen_w}x{self.screen_h}")
        print("✋ Use your index finger to control the cursor")
        print("👌 Pinch to click, Open palm to right-click")
    
    def _create_ui(self):
        """Create simplified UI"""
        
        # Main Container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Left Panel - Video ===
        self.left_panel = ctk.CTkFrame(self.main_container)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        video_title = ctk.CTkLabel(
            self.left_panel,
            text="📹 AI Hand Tracking",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        video_title.pack(pady=(10, 5))
        
        self.video = ctk.CTkLabel(self.left_panel, text="")
        self.video.pack(expand=True, pady=10)
        
        self.status = ctk.CTkLabel(
            self.left_panel,
            text="🟢 Ready - Show your hand",
            font=ctk.CTkFont(size=14),
            text_color="lightgreen"
        )
        self.status.pack(pady=5)
        
        # === Right Panel - Controls ===
        self.right_panel = ctk.CTkFrame(self.main_container, width=300)
        self.right_panel.pack(side="right", fill="both", padx=(0, 0))
        self.right_panel.pack_propagate(False)
        
        controls_title = ctk.CTkLabel(
            self.right_panel,
            text="⚙️ Control Panel",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        controls_title.pack(pady=(15, 10))
        
        # --- Gesture Info ---
        info_frame = ctk.CTkFrame(self.right_panel)
        info_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="✋ Gesture Guide",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        gestures_info = """
👆 Point with Index
   → Move cursor

👌 Pinch (Thumb + Index)
   → Click
   → Hold to DRAG

✋ Open Palm (All fingers)
   → Right Click

✊ Fist (Closed hand)
   → Double Click

🔒 Hold Pinch + Move
   → Drag and Drop
        """
        
        ctk.CTkLabel(
            info_frame,
            text=gestures_info,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(padx=15, pady=10, anchor="w")
        
        # --- Mouse Control ---
        mouse_frame = ctk.CTkFrame(self.right_panel)
        mouse_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            mouse_frame,
            text="🖱️ Mouse Control",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.btn_toggle = ctk.CTkButton(
            mouse_frame,
            text="🔴 Disable Mouse",
            command=self.toggle_mouse,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_toggle.pack(fill="x", padx=15, pady=10)
        
        # --- Voice Control ---
        voice_frame = ctk.CTkFrame(self.right_panel)
        voice_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            voice_frame,
            text="🎤 Voice Commands",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.btn_voice = ctk.CTkButton(
            voice_frame,
            text="🎙️ Voice Command",
            command=self.start_voice,
            height=35
        )
        self.btn_voice.pack(fill="x", padx=15, pady=5)
        
        self.btn_continuous_voice = ctk.CTkButton(
            voice_frame,
            text="🔄 Continuous: OFF",
            command=self.toggle_continuous_voice,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.btn_continuous_voice.pack(fill="x", padx=15, pady=5)
        
        # --- Settings ---
        settings_frame = ctk.CTkFrame(self.right_panel)
        settings_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            settings_frame,
            text="⚡ Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.landmarks_switch = ctk.CTkSwitch(
            settings_frame,
            text="Show Hand Landmarks",
            command=self.toggle_landmarks
        )
        self.landmarks_switch.pack(anchor="w", padx=15, pady=5)
        self.landmarks_switch.select()
        
        self.smooth_switch = ctk.CTkSwitch(
            settings_frame,
            text="Cursor Smoothing",
            command=self.toggle_smoothing
        )
        self.smooth_switch.pack(anchor="w", padx=15, pady=5)
        self.smooth_switch.select()
        
        # Speed slider
        ctk.CTkLabel(
            settings_frame,
            text="Cursor Speed",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=(10, 0))
        
        self.speed_slider = ctk.CTkSlider(
            settings_frame,
            from_=0.5,
            to=3.0,
            number_of_steps=25,
            command=self.update_speed
        )
        self.speed_slider.set(1.5)
        self.speed_slider.pack(fill="x", padx=15, pady=5)
        
        self.speed_label = ctk.CTkLabel(
            settings_frame,
            text="Speed: 1.5x",
            font=ctk.CTkFont(size=11)
        )
        self.speed_label.pack(anchor="w", padx=15)
        
        # --- Stats ---
        stats_frame = ctk.CTkFrame(self.right_panel)
        stats_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 Performance",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="FPS: --\nTracking: --",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        self.stats_label.pack(padx=15, pady=10, anchor="w")
        
        # --- Quick Actions ---
        actions_frame = ctk.CTkFrame(self.right_panel)
        actions_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(
            actions_frame,
            text="🎯 Quick Actions",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Reset",
            command=self.reset_system,
            width=130,
            height=30
        ).pack(side="left", padx=5, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="ℹ️ Help",
            command=self.show_help,
            width=130,
            height=30
        ).pack(side="right", padx=5, pady=5)
    
    # === Settings ===
    
    def toggle_landmarks(self):
        self.show_landmarks = self.landmarks_switch.get()
    
    def toggle_smoothing(self):
        self.cursor_smoothing = self.smooth_switch.get()
        if not self.cursor_smoothing:
            self.cursor_history.clear()
    
    def update_speed(self, value):
        self.cursor_speed = value
        self.speed_label.configure(text=f"Speed: {value:.1f}x")
    
    def toggle_mouse(self):
        self.mouse_enabled = not self.mouse_enabled
        
        if self.mouse_enabled:
            self.btn_toggle.configure(
                text="🔴 Disable Mouse",
                fg_color="green",
                hover_color="darkgreen"
            )
            self.update_status("🟢 Mouse Enabled", "lightgreen")
        else:
            self.btn_toggle.configure(
                text="🟢 Enable Mouse",
                fg_color="red",
                hover_color="darkred"
            )
            self.update_status("🔴 Mouse Disabled", "red")
    
    # === Voice Control ===
    
    def start_voice(self):
        if not self.voice_listening:
            self.voice_listening = True
            threading.Thread(target=self.run_voice, daemon=True).start()
    
    def run_voice(self):
        self.update_status("🎤 Listening...", "yellow")
        self.btn_voice.configure(state="disabled")
        
        result = self.voice.listen_and_execute()
        self.handle_voice_command(result)
        
        color = "lightgreen" if result.success else "red"
        self.update_status(f"🎤 {result.response}", color)
        
        self.btn_voice.configure(state="normal")
        self.voice_listening = False
    
    def toggle_continuous_voice(self):
        self.continuous_voice = not self.continuous_voice
        
        if self.continuous_voice:
            self.btn_continuous_voice.configure(
                text="🔄 Continuous: ON",
                fg_color="green",
                hover_color="darkgreen"
            )
            self.voice.start_continuous_listening(callback=self.on_voice_command)
            self.update_status("🎤 Continuous listening ON", "lightgreen")
        else:
            self.btn_continuous_voice.configure(
                text="🔄 Continuous: OFF",
                fg_color="gray",
                hover_color="darkgray"
            )
            self.voice.stop_continuous_listening()
            self.update_status("🔇 Continuous listening OFF", "gray")
    
    def on_voice_command(self, cmd):
        if cmd.success:
            self.handle_voice_command(cmd)
            self.update_status(f"🎤 {cmd.response}", "lightgreen")
    
    def handle_voice_command(self, cmd):
        response = cmd.response
        
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
    
    # === Gesture Control ===
    
    def handle_gesture(self, gesture: str):
        """Handle gestures with drag support"""
        
        # === DRAG LOGIC ===
        if gesture == "PINCH":
            self.drag_hold_frames += 1
            
            # Start dragging after holding for threshold frames
            if self.drag_hold_frames >= self.drag_threshold and not self.is_dragging:
                self.is_dragging = True
                self.drag_gesture = "PINCH"
                pyautogui.mouseDown()  # Press and hold mouse button
                self.update_status("🔒 DRAGGING - Release to drop", "purple")
                print("🔒 Drag mode activated")
                return
            
            # Already dragging - just move cursor
            elif self.is_dragging:
                return  # Cursor continues moving in main loop
            
            # Quick pinch (not held long enough) = Click
            elif self.drag_hold_frames < self.drag_threshold:
                if self.gesture_cooldown == 0:
                    pyautogui.click()
                    self.update_status("👌 Click!", "yellow")
                    self.gesture_cooldown = 15
                return
        
        # Gesture released (no longer pinching)
        elif self.is_dragging and gesture != "PINCH":
            # End drag
            pyautogui.mouseUp()  # Release mouse button
            self.is_dragging = False
            self.drag_gesture = None
            self.drag_hold_frames = 0
            self.update_status("✅ Dropped!", "lightgreen")
            print("✅ Drag released")
            self.gesture_cooldown = 20
            return
        
        # Reset hold counter if not pinching
        if gesture != "PINCH":
            self.drag_hold_frames = 0
        
        # === REGULAR GESTURES (when not dragging) ===
        if self.is_dragging:
            return  # Don't process other gestures while dragging
        
        if gesture is None or gesture == self.last_gesture:
            return
        
        if self.gesture_cooldown > 0:
            return
        
        self.last_gesture = gesture
        self.gesture_cooldown = 15
        
        if gesture == "OPEN_PALM":
            pyautogui.rightClick()
            self.update_status("✋ Right Click!", "orange")
        elif gesture == "FIST":
            pyautogui.doubleClick()
            self.update_status("✊ Double Click!", "red")
    
    def move_cursor_smooth(self, finger_x: int, finger_y: int, frame_shape: Tuple):
        """Move cursor with smoothing"""
        h, w = frame_shape[:2]
        
        # Map to screen coordinates
        screen_x = int(finger_x * self.screen_w / w * self.cursor_speed)
        screen_y = int(finger_y * self.screen_h / h * self.cursor_speed)
        
        # Clamp to screen bounds
        screen_x = max(0, min(self.screen_w - 1, screen_x))
        screen_y = max(0, min(self.screen_h - 1, screen_y))
        
        if self.cursor_smoothing:
            # Add to history
            self.cursor_history.append((screen_x, screen_y))
            
            # Smooth using average
            if len(self.cursor_history) > 1:
                positions = np.array(self.cursor_history)
                smooth_x = int(np.mean(positions[:, 0]))
                smooth_y = int(np.mean(positions[:, 1]))
                
                pyautogui.moveTo(smooth_x, smooth_y, _pause=False)
            else:
                pyautogui.moveTo(screen_x, screen_y, _pause=False)
        else:
            pyautogui.moveTo(screen_x, screen_y, _pause=False)
    
    # === Main Loop ===
    
    def update_frame(self):
        start_time = time.time()
        
        ret, frame = self.cap.read()
        if not ret:
            self.after(16, self.update_frame)
            return
        
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Detect hand
        frame, landmarks = self.hand_tracker.find_hand_landmarks(frame)
        
        if landmarks:
            # Get index finger tip for cursor
            index_tip = self.hand_tracker.get_fingertip_position(landmarks, "index")
            
            if index_tip and self.mouse_enabled:
                self.move_cursor_smooth(index_tip[0], index_tip[1], (h, w))
            
            # Detect gestures (including drag detection)
            gesture = self.hand_tracker.detect_gesture(landmarks)
            self.handle_gesture(gesture)
            
            # Draw landmarks
            if self.show_landmarks:
                frame = self.hand_tracker.draw_landmarks(frame, landmarks, show_connections=True)
            
            # Show drag indicator
            if self.is_dragging:
                cv2.putText(frame, "DRAGGING", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)
                cv2.circle(frame, (30, 30), 15, (255, 0, 255), -1)
            
            self.update_status("✋ Hand detected", "lightgreen")
        else:
            # Hand lost - cancel drag if active
            if self.is_dragging:
                pyautogui.mouseUp()
                self.is_dragging = False
                self.drag_gesture = None
                self.drag_hold_frames = 0
                self.update_status("❌ Drag cancelled (hand lost)", "red")
            else:
                self.update_status("🔍 Searching for hand...", "orange")
        
        # Display frame
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.video.configure(image=ctk.CTkImage(img, size=(720, 480)))
        self.video.image = img
        
        # Performance
        frame_time = time.time() - start_time
        fps = 1.0 / frame_time if frame_time > 0 else 0
        self.fps_counter.append(fps)
        
        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
        
        self.frame_counter += 1
        self.after(16, self.update_frame)
    
    def update_stats(self):
        avg_fps = np.mean(self.fps_counter) if self.fps_counter else 0
        gesture_fps = self.hand_tracker.get_fps()
        
        stats_text = f"""FPS: {avg_fps:.1f}
Tracking: {gesture_fps:.1f} FPS
Mode: AI Gestures"""
        
        self.stats_label.configure(text=stats_text)
        self.after(500, self.update_stats)
    
    # === Utilities ===
    
    def update_status(self, message: str, color: str = "gray"):
        self.after(0, lambda: self.status.configure(
            text=f"🔷 {message}",
            text_color=color
        ))
    
    def show_error(self, message: str):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("400x150")
        
        ctk.CTkLabel(
            error_window,
            text="❌ Error",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(error_window, text=message, wraplength=350).pack(pady=10)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)
    
    def show_help(self):
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help")
        help_window.geometry("500x400")
        
        ctk.CTkLabel(
            help_window,
            text="ℹ️ How to Use",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        help_text = """
🖱️ CURSOR CONTROL:
• Point with your index finger
• Move your hand to control the cursor
• Adjust speed with the slider

✋ GESTURES:
• 👌 Pinch (quick) = Left Click
• 👌 Pinch + HOLD (1 sec) = START DRAG
  → Keep pinching and move to drag
  → Release pinch to DROP
• ✋ Open Palm = Right Click
• ✊ Fist = Double Click

🔒 DRAG & DROP:
1. Make pinch gesture (thumb + index)
2. HOLD pinch for 1 second
3. Purple "DRAGGING" appears
4. Move your hand while pinching
5. Release pinch to drop item

🎤 VOICE COMMANDS:
• "left click" - Click
• "right click" - Right click
• "open google" - Open Google
• "time" - Show time
• And more!

💡 TIPS:
• Keep hand visible in camera
• Use good lighting
• Adjust cursor speed for comfort
• Enable continuous voice for hands-free
• Hold pinch steady to activate drag
        """
        
        ctk.CTkLabel(
            help_window,
            text=help_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(padx=20, pady=10)
        
        ctk.CTkButton(
            help_window,
            text="Close",
            command=help_window.destroy
        ).pack(pady=10)
    
    def reset_system(self):
        # Cancel any active drag
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False
            self.drag_gesture = None
        
        self.hand_tracker.reset()
        self.cursor_history.clear()
        self.last_gesture = None
        self.gesture_cooldown = 0
        self.prev_cursor_pos = None
        self.drag_hold_frames = 0
        self.update_status("🔄 System Reset", "lightblue")
    
    def on_close(self):
        print("🔄 Shutting down...")
        
        if self.continuous_voice:
            self.voice.stop_continuous_listening()
        
        if self.cap.isOpened():
            self.cap.release()
        
        self.destroy()
        print("✅ Shutdown complete")


if __name__ == "__main__":
    try:
        app = VirtualMouseApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()