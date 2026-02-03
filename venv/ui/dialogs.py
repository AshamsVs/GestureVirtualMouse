"""
Dialogs - Help Windows, Settings, and Alerts
Professional dialog windows with animations and modern UI
"""

import customtkinter as ctk
from typing import Optional, Callable
import math


class AnimatedDialog(ctk.CTkToplevel):
    """Base class for animated dialogs"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._animation_running = False
        self._fade_alpha = 0.0
        
    def _center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _fade_in(self, duration_ms=200):
        """Smooth fade-in animation"""
        steps = 20
        increment = 1.0 / steps
        delay = duration_ms // steps
        
        def animate(step=0):
            if step <= steps:
                alpha = step * increment
                self.attributes('-alpha', alpha)
                self.after(delay, lambda: animate(step + 1))
        
        self.attributes('-alpha', 0.0)
        animate()
    
    def _slide_in_from_top(self, duration_ms=300):
        """Slide in from top animation"""
        self.update_idletasks()
        target_y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        start_y = -self.winfo_height()
        
        steps = 30
        delay = duration_ms // steps
        
        def animate(step=0):
            if step <= steps:
                progress = step / steps
                # Ease out cubic
                progress = 1 - pow(1 - progress, 3)
                current_y = int(start_y + (target_y - start_y) * progress)
                x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
                self.geometry(f'+{x}+{current_y}')
                self.after(delay, lambda: animate(step + 1))
        
        animate()
    
    def _bounce_in(self, duration_ms=400):
        """Bounce in animation"""
        self.update_idletasks()
        target_scale = 1.0
        
        steps = 30
        delay = duration_ms // steps
        
        def animate(step=0):
            if step <= steps:
                progress = step / steps
                # Bounce easing
                if progress < 0.5:
                    scale = 0.3 + progress * 1.4
                else:
                    overshoot = math.sin((progress - 0.5) * math.pi * 2) * 0.1
                    scale = 1.0 + overshoot
                
                # Simulate scale with alpha (limited scaling in tkinter)
                alpha = min(1.0, 0.3 + progress * 0.7)
                self.attributes('-alpha', alpha)
                
                if step < steps:
                    self.after(delay, lambda: animate(step + 1))
        
        self.attributes('-alpha', 0.3)
        animate()


class HelpDialog(AnimatedDialog):
    """
    Comprehensive help window with gesture guide and tutorials
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Help - AI Desktop Assistant")
        self.geometry("750x650")
        self.resizable(False, False)
        
        # Modern colors
        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        
        self._build_interface()
        self.after(100, self._center_window)
        self.after(150, lambda: self._fade_in(250))
    
    def _build_interface(self):
        """Build help dialog with modern styling"""
        
        # Gradient-style header frame
        header_frame = ctk.CTkFrame(
            self,
            fg_color=("#3b82f6", "#2563eb"),
            corner_radius=0
        )
        header_frame.pack(fill="x", pady=0)
        
        header = ctk.CTkLabel(
            header_frame,
            text="💡 AI Desktop Assistant - Help Center",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        header.pack(pady=25)
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Learn gestures, voice commands, and pro tips",
            font=ctk.CTkFont(size=13),
            text_color=("#e0e0e0", "#d0d0d0")
        )
        subtitle.pack(pady=(0, 20))
        
        # Tabview with custom styling
        tabview = ctk.CTkTabview(
            self,
            corner_radius=10,
            border_width=2,
            segmented_button_fg_color=("#3b82f6", "#2563eb"),
            segmented_button_selected_color=("#2563eb", "#1d4ed8"),
            segmented_button_selected_hover_color=("#1d4ed8", "#1e40af")
        )
        tabview.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Create tabs with emojis
        tab_gestures = tabview.add("✋ Gestures")
        tab_voice = tabview.add("🎤 Voice")
        tab_tips = tabview.add("💡 Pro Tips")
        
        # === Gestures Tab ===
        self._build_gestures_tab(tab_gestures)
        
        # === Voice Tab ===
        self._build_voice_tab(tab_voice)
        
        # === Tips Tab ===
        self._build_tips_tab(tab_tips)
        
        # Modern close button
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Got it!",
            command=self._close_with_fade,
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=25,
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8")
        )
        close_btn.pack(side="right")
        
        # Animate button on hover
        self._add_hover_effect(close_btn)
    
    def _build_gestures_tab(self, parent):
        """Build gestures tab with card layout"""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        gestures = [
            ("👌 Pinch Gesture", "Thumb + Index Touch", [
                "Quick pinch (< 1s) → Click",
                "Hold pinch (≥ 1s) → Start Drag",
                "Keep pinching & move → Drag item",
                "Release pinch → Drop item"
            ]),
            ("✋ Open Palm", "All 5 Fingers Extended", [
                "Action: Right Click",
                "Perfect for context menus",
                "Keep fingers clearly spread"
            ]),
            ("✊ Fist", "All Fingers Closed", [
                "Action: Double Click",
                "Opens files and folders",
                "Make a clear closed fist"
            ]),
            ("👆 Point", "Index Finger Only", [
                "Action: Cursor Control",
                "Most natural position",
                "Move hand to guide cursor"
            ])
        ]
        
        for title, subtitle, items in gestures:
            self._create_gesture_card(scroll, title, subtitle, items)
    
    def _create_gesture_card(self, parent, title, subtitle, items):
        """Create an animated gesture card"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=15,
            border_width=2,
            border_color=("#3b82f6", "#2563eb")
        )
        card.pack(fill="x", pady=8, padx=5)
        
        # Card header
        header_frame = ctk.CTkFrame(card, fg_color=("#e0f2fe", "#1e3a5f"), corner_radius=12)
        header_frame.pack(fill="x", padx=3, pady=3)
        
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(padx=15, pady=(10, 2), anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        ).pack(padx=15, pady=(0, 10), anchor="w")
        
        # Card content
        for item in items:
            item_frame = ctk.CTkFrame(card, fg_color="transparent")
            item_frame.pack(fill="x", padx=15, pady=3)
            
            ctk.CTkLabel(
                item_frame,
                text="•",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#3b82f6", "#60a5fa")
            ).pack(side="left", padx=(0, 8))
            
            ctk.CTkLabel(
                item_frame,
                text=item,
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).pack(side="left", fill="x", expand=True, pady=2)
        
        ctk.CTkLabel(card, text="").pack(pady=5)  # Spacer
        
        # Hover effect
        self._add_card_hover(card)
    
    def _build_voice_tab(self, parent):
        """Build voice commands tab"""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        sections = [
            ("🖱️ Mouse Control", [
                '"left click" → Click',
                '"right click" → Right click',
                '"double click" → Double click',
                '"scroll up/down" → Scroll page'
            ]),
            ("🌐 Web Browsers", [
                '"open google" → Google',
                '"open youtube" → YouTube',
                '"open gmail" → Gmail',
                '"search for [topic]" → Web search'
            ]),
            ("💻 Applications", [
                '"notepad" → Open Notepad',
                '"calculator" → Open Calculator'
            ]),
            ("📊 System Info", [
                '"time" / "what time" → Current time',
                '"date" / "what date" → Current date'
            ])
        ]
        
        for section_title, commands in sections:
            self._create_command_section(scroll, section_title, commands)
    
    def _create_command_section(self, parent, title, commands):
        """Create command section"""
        section = ctk.CTkFrame(parent, corner_radius=12, border_width=2,
                              border_color=("#10b981", "#059669"))
        section.pack(fill="x", pady=8, padx=5)
        
        ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        ).pack(padx=15, pady=(12, 8), anchor="w")
        
        for cmd in commands:
            cmd_frame = ctk.CTkFrame(section, fg_color="transparent")
            cmd_frame.pack(fill="x", padx=15, pady=2)
            
            ctk.CTkLabel(
                cmd_frame,
                text="▸",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#10b981", "#34d399")
            ).pack(side="left", padx=(5, 10))
            
            ctk.CTkLabel(
                cmd_frame,
                text=cmd,
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).pack(side="left", pady=3)
        
        ctk.CTkLabel(section, text="").pack(pady=5)
        self._add_card_hover(section)
    
    def _build_tips_tab(self, parent):
        """Build tips tab"""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        tips = [
            ("🎯 Best Performance", [
                "Use bright, even lighting",
                "Position camera at eye level",
                "Simple background",
                "Contrast-colored clothing"
            ]),
            ("⚡ Optimization", [
                "Close other camera apps",
                "Adjust cursor speed slider",
                "Use Hybrid mode for balance",
                "Monitor FPS (target: 30+)"
            ]),
            ("🔧 Troubleshooting", [
                "Gestures not working? → Check lighting & hand visibility",
                "Cursor too fast/slow? → Adjust speed slider",
                "Voice not working? → Check mic permissions & noise",
                "Drag not activating? → Hold pinch for full 1 second"
            ])
        ]
        
        for tip_title, tip_items in tips:
            self._create_tip_card(scroll, tip_title, tip_items)
    
    def _create_tip_card(self, parent, title, items):
        """Create tip card"""
        card = ctk.CTkFrame(parent, corner_radius=12, border_width=2,
                           border_color=("#f59e0b", "#d97706"))
        card.pack(fill="x", pady=8, padx=5)
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        ).pack(padx=15, pady=(12, 8), anchor="w")
        
        for item in items:
            item_frame = ctk.CTkFrame(card, fg_color="transparent")
            item_frame.pack(fill="x", padx=15, pady=2)
            
            ctk.CTkLabel(
                item_frame,
                text="💡",
                font=ctk.CTkFont(size=12)
            ).pack(side="left", padx=(0, 8))
            
            ctk.CTkLabel(
                item_frame,
                text=item,
                font=ctk.CTkFont(size=12),
                anchor="w",
                wraplength=600
            ).pack(side="left", fill="x", expand=True, pady=3)
        
        ctk.CTkLabel(card, text="").pack(pady=5)
        self._add_card_hover(card)
    
    def _add_hover_effect(self, widget):
        """Add hover animation to widget"""
        original_fg = widget.cget("fg_color")
        
        def on_enter(e):
            widget.configure(cursor="hand2")
        
        def on_leave(e):
            widget.configure(cursor="")
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _add_card_hover(self, card):
        """Add subtle hover effect to cards"""
        original_border = card.cget("border_color")
        
        def on_enter(e):
            card.configure(border_width=3)
        
        def on_leave(e):
            card.configure(border_width=2)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
    
    def _close_with_fade(self):
        """Close with fade out animation"""
        steps = 10
        delay = 20
        
        def animate(step=0):
            if step <= steps:
                alpha = 1.0 - (step / steps)
                self.attributes('-alpha', alpha)
                if step < steps:
                    self.after(delay, lambda: animate(step + 1))
                else:
                    self.destroy()
        
        animate()


class SettingsDialog(AnimatedDialog):
    """
    Advanced settings dialog with animations
    """
    
    def __init__(self, parent, current_settings: dict, 
                 on_save: Optional[Callable] = None):
        super().__init__(parent)
        
        self.current_settings = current_settings
        self.on_save_callback = on_save
        
        self.title("Settings - AI Desktop Assistant")
        self.geometry("650x550")
        self.resizable(False, False)
        
        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        
        self._build_interface()
        self.after(100, self._center_window)
        self.after(150, lambda: self._bounce_in(300))
    
    def _build_interface(self):
        """Build settings dialog"""
        
        # Header
        header_frame = ctk.CTkFrame(
            self,
            fg_color=("#8b5cf6", "#7c3aed"),
            corner_radius=0
        )
        header_frame.pack(fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="⚙️ Advanced Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=25)
        
        # Settings scroll frame
        settings_frame = ctk.CTkScrollableFrame(self, height=350, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # === Performance ===
        perf_section = self._create_section(settings_frame, "⚡ Performance", "#3b82f6")
        
        self.fps_target = self._create_animated_slider(
            perf_section, "Target FPS", 30, 120, 60,
            "Higher FPS = smoother but more CPU"
        )
        
        self.smoothing_level = self._create_animated_slider(
            perf_section, "Smoothing Level", 0, 10, 5,
            "Higher = smoother cursor"
        )
        
        # === Gestures ===
        gesture_section = self._create_section(settings_frame, "✋ Gestures", "#10b981")
        
        self.gesture_confidence = self._create_animated_slider(
            gesture_section, "Detection Confidence", 0.5, 1.0, 0.7,
            "Higher = fewer false positives"
        )
        
        self.drag_hold_time = self._create_animated_slider(
            gesture_section, "Drag Hold Time (sec)", 0.5, 2.0, 1.0,
            "Time to hold pinch before drag"
        )
        
        # === Voice ===
        voice_section = self._create_section(settings_frame, "🎤 Voice", "#f59e0b")
        
        self.voice_timeout = self._create_animated_slider(
            voice_section, "Listen Timeout (sec)", 2, 10, 4,
            "Max time to wait for input"
        )
        
        # === System ===
        system_section = self._create_section(settings_frame, "🖥️ System", "#8b5cf6")
        
        self.minimize_to_tray = self._create_animated_switch(
            system_section, "Minimize to system tray"
        )
        
        self.start_minimized = self._create_animated_switch(
            system_section, "Start minimized"
        )
        
        self.auto_start = self._create_animated_switch(
            system_section, "Start with Windows"
        )
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        reset_btn = ctk.CTkButton(
            button_frame,
            text="↺ Reset",
            command=self._reset_defaults,
            width=120,
            height=40,
            corner_radius=20,
            fg_color=("#f59e0b", "#d97706"),
            hover_color=("#d97706", "#b45309")
        )
        reset_btn.pack(side="left")
        self._add_hover_effect(reset_btn)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=120,
            height=40,
            corner_radius=20,
            fg_color=("#6b7280", "#4b5563"),
            hover_color=("#4b5563", "#374151")
        )
        cancel_btn.pack(side="right", padx=5)
        self._add_hover_effect(cancel_btn)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="✓ Save",
            command=self._save_settings,
            width=120,
            height=40,
            corner_radius=20,
            fg_color=("#10b981", "#059669"),
            hover_color=("#059669", "#047857")
        )
        save_btn.pack(side="right", padx=5)
        self._add_hover_effect(save_btn)
    
    def _create_section(self, parent, title: str, color: str) -> ctk.CTkFrame:
        """Create settings section with color"""
        frame = ctk.CTkFrame(parent, corner_radius=12, border_width=2,
                            border_color=color)
        frame.pack(fill="x", padx=5, pady=10)
        
        header = ctk.CTkFrame(frame, fg_color=color, corner_radius=10)
        header.pack(fill="x", padx=3, pady=3)
        
        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white"
        ).pack(pady=10, padx=15, anchor="w")
        
        return frame
    
    def _create_animated_slider(self, parent, label: str, from_: float, 
                               to: float, default: float, desc: str = ""):
        """Create slider with value label"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=15, pady=8)
        
        # Label and value
        label_frame = ctk.CTkFrame(container, fg_color="transparent")
        label_frame.pack(fill="x")
        
        ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(side="left")
        
        value_label = ctk.CTkLabel(
            label_frame,
            text=f"{default:.1f}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#3b82f6", "#60a5fa")
        )
        value_label.pack(side="right")
        
        # Slider
        slider = ctk.CTkSlider(
            container,
            from_=from_,
            to=to,
            corner_radius=10,
            button_corner_radius=10,
            progress_color=("#3b82f6", "#2563eb"),
            button_color=("#2563eb", "#1d4ed8"),
            button_hover_color=("#1d4ed8", "#1e40af")
        )
        slider.set(default)
        slider.pack(fill="x", pady=5)
        
        # Update value label
        def update_value(val):
            value_label.configure(text=f"{float(val):.1f}")
        
        slider.configure(command=update_value)
        
        if desc:
            ctk.CTkLabel(
                container,
                text=desc,
                font=ctk.CTkFont(size=10),
                text_color="gray",
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))
        
        return slider
    
    def _create_animated_switch(self, parent, label: str):
        """Create animated switch"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=15, pady=6)
        
        switch = ctk.CTkSwitch(
            container,
            text=label,
            font=ctk.CTkFont(size=13),
            progress_color=("#10b981", "#059669"),
            button_color=("#f0f0f0", "#2a2a2a"),
            button_hover_color=("#e0e0e0", "#3a3a3a")
        )
        switch.pack(anchor="w", pady=3)
        
        return switch
    
    def _save_settings(self):
        """Save settings"""
        settings = {
            "fps_target": int(self.fps_target.get()),
            "smoothing_level": int(self.smoothing_level.get()),
            "gesture_confidence": self.gesture_confidence.get(),
            "drag_hold_time": self.drag_hold_time.get(),
            "voice_timeout": int(self.voice_timeout.get()),
            "minimize_to_tray": self.minimize_to_tray.get(),
            "start_minimized": self.start_minimized.get(),
            "auto_start": self.auto_start.get()
        }
        
        if self.on_save_callback:
            self.on_save_callback(settings)
        
        self.destroy()
    
    def _reset_defaults(self):
        """Reset with animation"""
        widgets = [
            (self.fps_target, 60),
            (self.smoothing_level, 5),
            (self.gesture_confidence, 0.7),
            (self.drag_hold_time, 1.0),
            (self.voice_timeout, 4)
        ]
        
        for widget, value in widgets:
            self._animate_slider_to_value(widget, value)
        
        self.minimize_to_tray.deselect()
        self.start_minimized.deselect()
        self.auto_start.deselect()
    
    def _animate_slider_to_value(self, slider, target_value, duration_ms=300):
        """Animate slider to target value"""
        start_value = slider.get()
        steps = 20
        delay = duration_ms // steps
        
        def animate(step=0):
            if step <= steps:
                progress = step / steps
                # Ease out
                progress = 1 - pow(1 - progress, 3)
                current = start_value + (target_value - start_value) * progress
                slider.set(current)
                if step < steps:
                    self.after(delay, lambda: animate(step + 1))
        
        animate()
    
    def _add_hover_effect(self, widget):
        """Add hover effect"""
        def on_enter(e):
            widget.configure(cursor="hand2")
        def on_leave(e):
            widget.configure(cursor="")
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)


class AlertDialog(AnimatedDialog):
    """
    Animated alert/confirmation dialog
    """
    
    def __init__(self, parent, title: str, message: str, 
                 dialog_type: str = "info",
                 on_confirm: Optional[Callable] = None):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("450x250")
        self.resizable(False, False)
        
        self.on_confirm = on_confirm
        self.dialog_type = dialog_type
        
        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        
        self._build_interface(message, dialog_type)
        self.after(100, self._center_window)
        self.after(150, lambda: self._bounce_in(250))
    
    def _build_interface(self, message: str, dialog_type: str):
        """Build alert dialog"""
        
        # Color schemes
        colors = {
            "info": ("#3b82f6", "#2563eb"),
            "warning": ("#f59e0b", "#d97706"),
            "error": ("#ef4444", "#dc2626"),
            "success": ("#10b981", "#059669"),
            "question": ("#8b5cf6", "#7c3aed")
        }
        
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
            "question": "❓"
        }
        
        color = colors.get(dialog_type, colors["info"])
        icon = icons.get(dialog_type, "ℹ️")
        
        # Icon with animated background
        icon_frame = ctk.CTkFrame(
            self,
            fg_color=color,
            corner_radius=50,
            width=100,
            height=100
        )
        icon_frame.pack(pady=(40, 20))
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=50)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Animate icon
        self._pulse_animation(icon_frame, color)
        
        # Message
        ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=380
        ).pack(pady=15, padx=30)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(15, 30))
        
        if dialog_type == "question":
            yes_btn = ctk.CTkButton(
                button_frame,
                text="Yes",
                command=self._confirm,
                width=120,
                height=40,
                corner_radius=20,
                fg_color=color,
                hover_color=(color[1], color[0])
            )
            yes_btn.pack(side="left", padx=5)
            self._add_hover_effect(yes_btn)
            
            no_btn = ctk.CTkButton(
                button_frame,
                text="No",
                command=self.destroy,
                width=120,
                height=40,
                corner_radius=20,
                fg_color=("#6b7280", "#4b5563"),
                hover_color=("#4b5563", "#374151")
            )
            no_btn.pack(side="left", padx=5)
            self._add_hover_effect(no_btn)
        else:
            ok_btn = ctk.CTkButton(
                button_frame,
                text="OK",
                command=self.destroy,
                width=180,
                height=40,
                corner_radius=20,
                fg_color=color,
                hover_color=(color[1], color[0])
            )
            ok_btn.pack()
            self._add_hover_effect(ok_btn)
    
    def _pulse_animation(self, widget, color, step=0):
        """Pulse animation for icon"""
        if not widget.winfo_exists():
            return
        
        # Pulse effect using opacity simulation
        scale = 1.0 + 0.1 * math.sin(step * 0.1)
        
        # Continue animation
        self.after(50, lambda: self._pulse_animation(widget, color, step + 1))
    
    def _confirm(self):
        """Handle confirmation"""
        if self.on_confirm:
            self.on_confirm()
        self.destroy()
    
    def _add_hover_effect(self, widget):
        """Add hover effect"""
        def on_enter(e):
            widget.configure(cursor="hand2")
        def on_leave(e):
            widget.configure(cursor="")
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)