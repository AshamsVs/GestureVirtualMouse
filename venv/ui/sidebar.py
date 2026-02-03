"""
Sidebar - Modern Professional Control Panel
Fixed width, always visible, clean design
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict


# Modern Color Scheme
class Colors:
    BG_DARK = "#0F1419"
    BG_MEDIUM = "#1C2128"
    BG_LIGHT = "#262C36"
    PRIMARY = "#6366F1"
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    TEXT_PRIMARY = "#E6EDF3"
    TEXT_SECONDARY = "#8B949E"
    BORDER = "#30363D"


class Sidebar(ctk.CTkFrame):
    """
    Modern sidebar with fixed width - ALWAYS VISIBLE
    """
    
    def __init__(self, parent, callbacks: Optional[Dict[str, Callable]] = None, **kwargs):
        super().__init__(
            parent, 
            width=320,  # FIXED WIDTH
            fg_color=Colors.BG_MEDIUM,
            corner_radius=0,
            **kwargs
        )
        
        self.callbacks = callbacks or {}
        
        # CRITICAL: Prevent shrinking
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        self._build_interface()
    
    def _build_interface(self):
        """Build sidebar with scrollable content"""
        
        # Configure grid for scrollable frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Scrollable container
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_LIGHT,
            scrollbar_button_hover_color=Colors.BORDER
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        
        # Build content
        self._build_content(scroll_frame)
    
    def _build_content(self, parent):
        """Build all sidebar sections"""
        
        # Header
        ctk.CTkLabel(
            parent,
            text="⚙️ Control Center",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        ).pack(pady=(20, 15), padx=20, anchor="w")
        
        # Mode Section
        self._build_mode_section(parent)
        
        # Mouse Section
        self._build_mouse_section(parent)
        
        # Voice Section
        self._build_voice_section(parent)
        
        # Gesture Section
        self._build_gesture_section(parent)
        
        # Advanced Section
        self._build_advanced_section(parent)
        
        # Quick Actions
        self._build_actions(parent)
    
    def _build_mode_section(self, parent):
        """Assistant mode selection"""
        section = self._create_section(parent, "🎮 Assistant Mode")
        
        self.mode_var = ctk.StringVar(value="gesture")
        
        for text, value in [
            ("✋ Gesture Control", "gesture"),
            ("🎤 Voice Only", "voice")
        ]:
            ctk.CTkRadioButton(
                section,
                text=text,
                variable=self.mode_var,
                value=value,
                command=lambda: self._callback("mode_changed", self.mode_var.get()),
                font=ctk.CTkFont(size=12),
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY
            ).pack(anchor="w", padx=20, pady=4)
        
        section.pack(fill="x", padx=15, pady=8)
    
    def _build_mouse_section(self, parent):
        """Mouse controls"""
        section = self._create_section(parent, "🖱️ Mouse Control")
        
        # Toggle button
        self.mouse_toggle_btn = ctk.CTkButton(
            section,
            text="🟢 Mouse Enabled",
            command=lambda: self._callback("toggle_mouse"),
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=Colors.SUCCESS,
            hover_color="#059669",
            corner_radius=10
        )
        self.mouse_toggle_btn.pack(fill="x", padx=15, pady=10)
        
        # Speed control
        speed_frame = ctk.CTkFrame(section, fg_color="transparent")
        speed_frame.pack(fill="x", padx=15, pady=8)
        
        speed_header = ctk.CTkFrame(speed_frame, fg_color="transparent")
        speed_header.pack(fill="x")
        
        ctk.CTkLabel(
            speed_header,
            text="⚡ Cursor Speed",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Colors.TEXT_SECONDARY
        ).pack(side="left")
        
        self.speed_value = ctk.CTkLabel(
            speed_header,
            text="1.5x",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Colors.PRIMARY
        )
        self.speed_value.pack(side="right")
        
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0.5,
            to=3.0,
            number_of_steps=25,
            command=lambda v: self._on_speed_changed(v),
            button_color=Colors.PRIMARY,
            progress_color=Colors.PRIMARY
        )
        self.speed_slider.set(1.5)
        self.speed_slider.pack(fill="x", pady=6)
        
        section.pack(fill="x", padx=15, pady=8)
    
    def _build_voice_section(self, parent):
        """Voice controls"""
        section = self._create_section(parent, "🎤 Voice Assistant")
        
        # Single command
        self.voice_btn = ctk.CTkButton(
            section,
            text="🎙️ Voice Command",
            command=lambda: self._callback("voice_command"),
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=Colors.BG_LIGHT,
            hover_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=8
        )
        self.voice_btn.pack(fill="x", padx=15, pady=6)
        
        # Continuous listening
        self.continuous_voice_btn = ctk.CTkButton(
            section,
            text="🔄 Continuous: OFF",
            command=lambda: self._callback("toggle_continuous_voice"),
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=Colors.BG_LIGHT,
            hover_color=Colors.BORDER,
            text_color=Colors.TEXT_SECONDARY,
            corner_radius=8
        )
        self.continuous_voice_btn.pack(fill="x", padx=15, pady=6)
        
        # Wake word
        wake_frame = ctk.CTkFrame(section, fg_color="transparent")
        wake_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            wake_frame,
            text="💬 Wake Word",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))
        
        self.wake_word_entry = ctk.CTkEntry(
            wake_frame,
            placeholder_text="e.g., 'jarvis'",
            height=32,
            corner_radius=6,
            border_color=Colors.BORDER
        )
        self.wake_word_entry.pack(fill="x", pady=4)
        
        ctk.CTkButton(
            wake_frame,
            text="Set Wake Word",
            command=lambda: self._callback("set_wake_word", self.wake_word_entry.get()),
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=Colors.PRIMARY,
            hover_color="#5558E3",
            corner_radius=6
        ).pack(fill="x", pady=4)
        
        section.pack(fill="x", padx=15, pady=8)
    
    def _build_gesture_section(self, parent):
        """Gesture settings"""
        section = self._create_section(parent, "✋ Gesture Settings")
        
        # Show landmarks
        self.landmarks_switch = ctk.CTkSwitch(
            section,
            text="Show Hand Landmarks",
            command=lambda: self._callback("toggle_landmarks", self.landmarks_switch.get()),
            font=ctk.CTkFont(size=11),
            progress_color=Colors.PRIMARY
        )
        self.landmarks_switch.select()
        self.landmarks_switch.pack(anchor="w", padx=20, pady=6)
        
        # Gesture guide
        ctk.CTkButton(
            section,
            text="📖 Gesture Guide",
            command=lambda: self._callback("show_gesture_guide"),
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color=Colors.BG_LIGHT,
            hover_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=6
        ).pack(fill="x", padx=15, pady=6)
        
        section.pack(fill="x", padx=15, pady=8)
    
    def _build_advanced_section(self, parent):
        """Advanced settings"""
        section = self._create_section(parent, "⚙️ Advanced")
        
        # Smoothing
        self.smooth_switch = ctk.CTkSwitch(
            section,
            text="Cursor Smoothing",
            command=lambda: self._callback("toggle_smoothing", self.smooth_switch.get()),
            font=ctk.CTkFont(size=11),
            progress_color=Colors.PRIMARY
        )
        self.smooth_switch.select()
        self.smooth_switch.pack(anchor="w", padx=20, pady=5)
        
        # Auto-start
        self.autostart_switch = ctk.CTkSwitch(
            section,
            text="Start with Windows",
            command=lambda: self._callback("toggle_autostart", self.autostart_switch.get()),
            font=ctk.CTkFont(size=11),
            progress_color=Colors.PRIMARY
        )
        self.autostart_switch.pack(anchor="w", padx=20, pady=5)
        
        # Minimize to tray
        self.tray_switch = ctk.CTkSwitch(
            section,
            text="Minimize to Tray",
            command=lambda: self._callback("toggle_tray", self.tray_switch.get()),
            font=ctk.CTkFont(size=11),
            progress_color=Colors.PRIMARY
        )
        self.tray_switch.pack(anchor="w", padx=20, pady=5)
        
        section.pack(fill="x", padx=15, pady=8)
    
    def _build_actions(self, parent):
        """Quick actions"""
        section = self._create_section(parent, "⚡ Quick Actions")
        
        actions = [
            ("🔄 Reset", "reset", Colors.PRIMARY),
            ("ℹ️ Help", "help", Colors.SUCCESS),
            ("⚙️ Settings", "settings", Colors.WARNING)
        ]
        
        for text, action, color in actions:
            ctk.CTkButton(
                section,
                text=text,
                command=lambda a=action: self._callback(a),
                height=34,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=color,
                hover_color=color,
                corner_radius=8
            ).pack(fill="x", padx=15, pady=3)
        
        section.pack(fill="x", padx=15, pady=(8, 20))
    
    def _create_section(self, parent, title: str) -> ctk.CTkFrame:
        """Create section frame"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.BG_LIGHT,
            corner_radius=10,
            border_width=1,
            border_color=Colors.BORDER
        )
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        ).pack(pady=(10, 5), padx=15, anchor="w")
        
        return frame
    
    def _callback(self, event: str, *args):
        """Execute callback"""
        if event in self.callbacks:
            self.callbacks[event](*args)
    
    def _on_speed_changed(self, value):
        """Handle speed slider change"""
        self.speed_value.configure(text=f"{value:.1f}x")
        self._callback("speed_changed", value)
    
    # === Public API ===
    
    def set_mouse_state(self, enabled: bool):
        """Update mouse button"""
        self.mouse_toggle_btn.configure(
            text="🟢 Mouse Enabled" if enabled else "🔴 Mouse Disabled",
            fg_color=Colors.SUCCESS if enabled else Colors.ERROR,
            hover_color="#059669" if enabled else "#dc2626"
        )
    
    def set_continuous_voice_state(self, active: bool):
        """Update continuous voice button"""
        self.continuous_voice_btn.configure(
            text="🔄 Continuous: ON" if active else "🔄 Continuous: OFF",
            fg_color=Colors.SUCCESS if active else Colors.BG_LIGHT,
            text_color=Colors.TEXT_PRIMARY if active else Colors.TEXT_SECONDARY
        )
    
    def set_voice_button_state(self, enabled: bool):
        """Enable/disable voice button"""
        self.voice_btn.configure(state="normal" if enabled else "disabled")
    
    def update_speed_label(self, speed: float):
        """Update speed label"""
        self.speed_value.configure(text=f"{speed:.1f}x")
    
    def get_mode(self) -> str:
        """Get current mode"""
        return self.mode_var.get()
    
    def get_cursor_speed(self) -> float:
        """Get cursor speed"""
        return self.speed_slider.get()