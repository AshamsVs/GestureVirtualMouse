
"""
Main Window - Premium Desktop App Interface with Animations
Features: Ava's animated avatar, listening effects, modern design
"""

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter
import cv2
from typing import Optional
import math
import time


class AvaAvatar(ctk.CTkCanvas):
    """
    Ava's animated avatar with breathing and listening effects
    """
    
    def __init__(self, parent, size=80, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, bg='#1a1a1a', **kwargs)
        
        self.size = size
        self.center = size // 2
        self.pulse_angle = 0
        self.is_listening = False
        self.is_speaking = False
        
        # Color scheme
        self.primary_color = "#00D9FF"  # Cyan
        self.secondary_color = "#8B5CF6"  # Purple
        self.accent_color = "#F472B6"  # Pink
        
        self._draw_avatar()
        self._start_animation()
    
    def _draw_avatar(self):
        """Draw Ava's avatar"""
        self.delete("all")
        
        # Outer glow ring (animated)
        if self.is_listening:
            glow_radius = self.center + 10 + math.sin(self.pulse_angle) * 5
            self.create_oval(
                self.center - glow_radius, self.center - glow_radius,
                self.center + glow_radius, self.center + glow_radius,
                outline=self.primary_color, width=2, tags="glow"
            )
        
        # Main circle (gradient effect with multiple circles)
        for i in range(5):
            radius = self.center - 5 - i * 2
            alpha = hex(255 - i * 50)[2:].zfill(2)
            color = f"{self.primary_color}{alpha}"
            self.create_oval(
                self.center - radius, self.center - radius,
                self.center + radius, self.center + radius,
                fill='', outline=self.primary_color, width=1
            )
        
        # Inner circle (solid)
        inner_radius = self.center - 15
        self.create_oval(
            self.center - inner_radius, self.center - inner_radius,
            self.center + inner_radius, self.center + inner_radius,
            fill=self.secondary_color, outline=self.primary_color, width=2
        )
        
        # A letter for Ava
        self.create_text(
            self.center, self.center,
            text="A", font=("Arial", 40, "bold"),
            fill="white"
        )
        
        # Listening wave effect
        if self.is_listening:
            for i in range(3):
                wave_offset = math.sin(self.pulse_angle + i * 1.5) * 8
                y_pos = self.center + wave_offset
                self.create_line(
                    15, y_pos, 25, y_pos,
                    fill=self.accent_color, width=3, capstyle="round"
                )
                self.create_line(
                    self.size - 25, y_pos, self.size - 15, y_pos,
                    fill=self.accent_color, width=3, capstyle="round"
                )
    
    def _start_animation(self):
        """Animate the avatar"""
        self.pulse_angle += 0.1
        if self.pulse_angle > 2 * math.pi:
            self.pulse_angle = 0
        
        self._draw_avatar()
        self.after(50, self._start_animation)
    
    def set_listening(self, listening: bool):
        """Set listening state"""
        self.is_listening = listening
    
    def set_speaking(self, speaking: bool):
        """Set speaking state"""
        self.is_speaking = speaking


class MainWindow(ctk.CTkFrame):
    """
    Premium main application window with animations and modern design
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#0a0a0a", corner_radius=0, **kwargs)
        
        self.parent = parent
        self.video_frame = None
        self.video_label = None
        self.title_label = None
        self.listening_animation_active = False
        
        self._build_interface()
    
    def _build_interface(self):
        """Build the stunning main window layout"""
        
        # Configure grid
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Video
        self.grid_columnconfigure(0, weight=1)
        
        # === Animated Header Bar ===
        header_frame = ctk.CTkFrame(
            self, 
            fg_color=("#1a1a1a", "#0f0f0f"),
            corner_radius=0,
            height=100
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)
        
        # Ava's Avatar (left side)
        self.avatar = AvaAvatar(header_frame, size=70)
        self.avatar.grid(row=0, column=0, padx=20, pady=15)
        
        # Title and subtitle
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.grid(row=0, column=1, sticky="w", padx=10)
        
        self.title_label = ctk.CTkLabel(
            title_container,
            text="🤖 Ava AI Assistant",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00D9FF"
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(
            title_container,
            text="Your intelligent desktop companion",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_label.pack(anchor="w")
        
        # Mode indicator (right side)
        self.mode_indicator = ctk.CTkFrame(
            header_frame,
            fg_color=("#2a2a2a", "#1a1a1a"),
            corner_radius=20,
            height=40
        )
        self.mode_indicator.grid(row=0, column=2, padx=20, pady=30, sticky="e")
        
        self.mode_label = ctk.CTkLabel(
            self.mode_indicator,
            text="● STANDBY",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        self.mode_label.pack(padx=20, pady=8)
        
        # === Premium Video Feed Container ===
        self.video_frame = ctk.CTkFrame(
            self, 
            fg_color=("#1a1a1a", "#0f0f0f"),
            corner_radius=15,
            border_width=2,
            border_color="#00D9FF"
        )
        self.video_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)
        
        # Video label with loading animation
        self.video_label = ctk.CTkLabel(
            self.video_frame,
            text="🎥 Initializing camera...",
            font=ctk.CTkFont(size=16),
            text_color="#00D9FF"
        )
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Overlay info frame (FPS, confidence, etc.)
        self.overlay_frame = ctk.CTkFrame(
            self.video_frame,
            fg_color="transparent"
        )
        self.overlay_frame.place(relx=0.02, rely=0.02, anchor="nw")
        
        # FPS counter with glow effect
        self.fps_frame = ctk.CTkFrame(
            self.overlay_frame,
            fg_color=("#1a1a1a", "#0f0f0f"),
            corner_radius=10,
            border_width=2,
            border_color="#00D9FF"
        )
        self.fps_frame.pack()
        
        self.fps_label = ctk.CTkLabel(
            self.fps_frame,
            text="FPS: --",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00D9FF"
        )
        self.fps_label.pack(padx=12, pady=6)
        
        # Listening indicator (animated)
        self.listening_indicator = ctk.CTkFrame(
            self.video_frame,
            fg_color=("#8B5CF6", "#7C3AED"),
            corner_radius=10,
            height=50
        )
        
        self.listening_label = ctk.CTkLabel(
            self.listening_indicator,
            text="🎤 Listening...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        self.listening_label.pack(padx=20, pady=12)
    
    def update_video(self, frame: cv2.Mat, size: tuple = (900, 675)):
        """Update video feed with enhanced frame"""
        try:
            # Add subtle vignette effect
            h, w = frame.shape[:2]
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            img = Image.fromarray(frame_rgb)
            
            # Update label
            ctk_image = ctk.CTkImage(img, size=size)
            self.video_label.configure(image=ctk_image, text="")
            self.video_label.image = ctk_image
            
        except Exception as e:
            print(f"Error updating video: {e}")
    
    def update_fps(self, fps: float):
        """Update FPS counter with color coding"""
        color = "#00FF00" if fps > 45 else "#FFA500" if fps > 25 else "#FF0000"
        self.fps_label.configure(
            text=f"FPS: {fps:.1f}",
            text_color=color
        )
    
    def update_mode(self, mode: str, color: str = "gray"):
        """Update mode indicator with animation"""
        self.mode_label.configure(
            text=f"● {mode.upper()}",
            text_color=color
        )
        
        # Update mode indicator background
        if mode.upper() == "LISTENING":
            self.mode_indicator.configure(fg_color="#8B5CF6")
            self.avatar.set_listening(True)
            self._show_listening_indicator()
        else:
            self.mode_indicator.configure(fg_color=("#2a2a2a", "#1a1a1a"))
            self.avatar.set_listening(False)
            self._hide_listening_indicator()
    
    def _show_listening_indicator(self):
        """Show animated listening indicator"""
        if not self.listening_animation_active:
            self.listening_animation_active = True
            self.listening_indicator.place(relx=0.5, rely=0.05, anchor="n")
            self._animate_listening()
    
    def _hide_listening_indicator(self):
        """Hide listening indicator"""
        self.listening_animation_active = False
        self.listening_indicator.place_forget()
    
    def _animate_listening(self):
        """Animate listening indicator"""
        if not self.listening_animation_active:
            return
        
        # Pulse effect
        current_time = time.time()
        pulse = (math.sin(current_time * 5) + 1) / 2
        
        # Change opacity (simulated with color brightness)
        alpha = int(155 + pulse * 100)
        
        self.after(50, self._animate_listening)
    
    def set_title(self, title: str):
        """Update window title with animation"""
        self.title_label.configure(text=title)
    
    def show_message(self, message: str, duration: int = 2000, message_type: str = "info"):
        """
        Show animated message overlay
        
        Args:
            message: Message text
            duration: Display duration in milliseconds
            message_type: "info", "success", "warning", "error"
        """
        # Color scheme based on type
        colors = {
            "info": ("#00D9FF", "#0891b2"),
            "success": ("#00FF00", "#059669"),
            "warning": ("#FFA500", "#d97706"),
            "error": ("#FF0000", "#dc2626")
        }
        
        bg_color, border_color = colors.get(message_type, colors["info"])
        
        # Create message frame
        msg_frame = ctk.CTkFrame(
            self.video_frame,
            fg_color=bg_color,
            corner_radius=15,
            border_width=2,
            border_color=border_color
        )
        
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=message,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        msg_label.pack(padx=30, pady=15)
        
        # Animate in
        msg_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Fade out after duration
        def fade_out():
            msg_frame.place_forget()
            msg_frame.destroy()
        
        self.after(duration, fade_out)
    
    def get_video_label(self):
        """Get video label widget"""
        return self.video_label