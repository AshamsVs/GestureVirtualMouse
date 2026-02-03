"""
Status Panel - Animated Real-time Feedback
Beautiful logs with smooth animations and color coding
"""

import customtkinter as ctk
from datetime import datetime
from collections import deque
from typing import Optional
import time


class AnimatedLogEntry(ctk.CTkFrame):
    """Single animated log entry"""
    
    def __init__(self, parent, message: str, level: str, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=8,
            **kwargs
        )
        
        # Color mapping
        colors = {
            "INFO": ("#00D9FF", "#0891b2"),
            "SUCCESS": ("#10B981", "#059669"),
            "WARNING": ("#F59E0B", "#d97706"),
            "ERROR": ("#EF4444", "#dc2626"),
            "COMMAND": ("#8B5CF6", "#7C3AED")
        }
        
        color, bg_color = colors.get(level, ("#00D9FF", "#0891b2"))
        
        # Entry frame with border
        entry_frame = ctk.CTkFrame(
            self,
            fg_color=("#2a2a2a", "#1a1a1a"),
            corner_radius=8,
            border_width=1,
            border_color=color
        )
        entry_frame.pack(fill="x", padx=5, pady=2)
        
        # Level indicator
        level_label = ctk.CTkLabel(
            entry_frame,
            text=level,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=color,
            width=80
        )
        level_label.pack(side="left", padx=8, pady=6)
        
        # Message
        msg_label = ctk.CTkLabel(
            entry_frame,
            text=message,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        msg_label.pack(side="left", fill="x", expand=True, padx=5)


class StatusPanel(ctk.CTkFrame):
    """
    Premium status panel with animated logs and real-time stats
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, 
            height=180,
            fg_color=("#1a1a1a", "#0f0f0f"),
            corner_radius=15,
            border_width=2,
            border_color="#00D9FF",
            **kwargs
        )
        
        self.parent = parent
        self.log_buffer = deque(maxlen=100)
        
        # Color scheme
        self.primary_color = "#00D9FF"
        self.success_color = "#10B981"
        self.warning_color = "#F59E0B"
        self.error_color = "#EF4444"
        
        # Prevent resize
        self.pack_propagate(False)
        
        self._build_interface()
    
    def _build_interface(self):
        """Build premium status panel layout"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # === Animated Status Header ===
        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=50
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_propagate(False)
        
        # Current status with glow effect
        status_container = ctk.CTkFrame(
            header_frame,
            fg_color=("#2a2a2a", "#1a1a1a"),
            corner_radius=12,
            border_width=2,
            border_color=self.primary_color
        )
        status_container.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            status_container,
            text="🟢 Ready",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="lightgreen"
        )
        self.status_label.pack(padx=15, pady=10)
        
        # Performance stats with gradient
        stats_container = ctk.CTkFrame(
            header_frame,
            fg_color=("#2a2a2a", "#1a1a1a"),
            corner_radius=12,
            border_width=2,
            border_color=self.success_color
        )
        stats_container.grid(row=0, column=1, sticky="e")
        
        self.perf_label = ctk.CTkLabel(
            stats_container,
            text="FPS: -- | Tracking: --",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.success_color
        )
        self.perf_label.pack(padx=15, pady=10)
        
        # === Scrollable Log Display ===
        log_container = ctk.CTkFrame(
            self,
            fg_color=("#2a2a2a", "#1a1a1a"),
            corner_radius=12
        )
        log_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 10))
        log_container.grid_rowconfigure(0, weight=1)
        log_container.grid_columnconfigure(0, weight=1)
        
        # Scrollable log frame
        self.log_frame = ctk.CTkScrollableFrame(
            log_container,
            fg_color="transparent"
        )
        self.log_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # === Compact System Info Panel ===
        info_frame = ctk.CTkFrame(
            self,
            width=220,
            fg_color=("#2a2a2a", "#1a1a1a"),
            corner_radius=12,
            border_width=2,
            border_color=self.primary_color
        )
        info_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 15), pady=(5, 10))
        info_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            info_frame,
            text="📊 System Info",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.primary_color
        ).pack(pady=(12, 8))
        
        self.info_text = ctk.CTkLabel(
            info_frame,
            text="Initializing...",
            font=ctk.CTkFont(size=10),
            justify="left",
            anchor="nw"
        )
        self.info_text.pack(fill="both", expand=True, padx=12, pady=5)
    
    def update_status(self, message: str, color: str = "gray", icon: str = "🔷"):
        """Update main status with animation"""
        self.status_label.configure(
            text=f"{icon} {message}",
            text_color=color
        )
        
        # Animate status container border
        if color == "lightgreen":
            border_color = self.success_color
        elif color == "orange":
            border_color = self.warning_color
        elif color == "red":
            border_color = self.error_color
        else:
            border_color = self.primary_color
        
        # Find status container and update border
        for widget in self.status_label.master.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(border_color=border_color)
    
    def update_performance(self, fps: float, tracking_fps: float = 0, 
                          confidence: float = 0):
        """Update performance statistics with color coding"""
        stats = f"FPS: {fps:.1f}"
        
        if tracking_fps > 0:
            stats += f" | Tracking: {tracking_fps:.1f}"
        
        if confidence > 0:
            stats += f" | Conf: {confidence:.0%}"
        
        # Color based on FPS
        if fps > 45:
            color = self.success_color
        elif fps > 25:
            color = self.warning_color
        else:
            color = self.error_color
        
        self.perf_label.configure(text=stats, text_color=color)
    
    def update_system_info(self, info: dict):
        """Update system information panel"""
        info_lines = []
        
        if "mode" in info:
            info_lines.append(f"🎮 Mode: {info['mode']}")
        
        if "mouse_enabled" in info:
            state = "ON" if info["mouse_enabled"] else "OFF"
            emoji = "🟢" if info["mouse_enabled"] else "🔴"
            info_lines.append(f"{emoji} Mouse: {state}")
        
        if "voice_active" in info:
            state = "ACTIVE" if info["voice_active"] else "OFF"
            emoji = "🎤" if info["voice_active"] else "🔇"
            info_lines.append(f"{emoji} Voice: {state}")
        
        if "gesture_count" in info:
            info_lines.append(f"✋ Gestures: {info['gesture_count']}")
        
        if "commands_total" in info:
            info_lines.append(f"🎯 Commands: {info['commands_total']}")
        
        self.info_text.configure(text="\n".join(info_lines))
    
    def log(self, message: str, level: str = "INFO", show_time: bool = True):
        """Add animated log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}" if show_time else message
        
        # Store in buffer
        self.log_buffer.append((log_message, level))
        
        # Create animated entry
        entry = AnimatedLogEntry(self.log_frame, log_message, level)
        entry.pack(fill="x", pady=1)
        
        # Auto-scroll to bottom
        self.after(50, lambda: self.log_frame._parent_canvas.yview_moveto(1.0))
        
        # Limit visible entries
        entries = self.log_frame.winfo_children()
        if len(entries) > 50:
            entries[0].destroy()
    
    def log_command(self, command: str, response: str = ""):
        """Log a voice/gesture command with style"""
        self.log(f"💬 Command: {command}", "COMMAND")
        if response:
            self.log(f"   ✓ {response}", "SUCCESS")
    
    def log_gesture(self, gesture: str):
        """Log a detected gesture"""
        self.log(f"✋ {gesture}", "SUCCESS")
    
    def log_error(self, error: str):
        """Log an error"""
        self.log(f"❌ {error}", "ERROR")
    
    def log_warning(self, warning: str):
        """Log a warning"""
        self.log(f"⚠️ {warning}", "WARNING")
    
    def clear_log(self):
        """Clear the log display with animation"""
        for widget in self.log_frame.winfo_children():
            widget.destroy()
        self.log_buffer.clear()
        self.log("📝 Log cleared", "INFO")
    
    def export_log(self, filename: str = "ava_log.txt"):
        """Export log to file"""
        try:
            with open(filename, 'w') as f:
                for entry, level in self.log_buffer:
                    f.write(f"{entry}\n")
            self.log(f"💾 Log exported to {filename}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Export failed: {e}", "ERROR")
            return False