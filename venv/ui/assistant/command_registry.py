"""
Command Registry - Central Command Management System
Organizes all commands by category with intelligent routing
"""

import os
import webbrowser
import subprocess
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class CommandCategory(Enum):
    """Command categories for organization"""
    SYSTEM = "system"
    APPLICATION = "application"
    WEB = "web"
    MEDIA = "media"
    MOUSE = "mouse"
    ASSISTANT = "assistant"
    INFO = "info"


@dataclass
class Command:
    """Command data structure"""
    name: str
    aliases: List[str]
    category: CommandCategory
    handler: Callable
    description: str
    requires_confirmation: bool = False
    enabled: bool = True


class CommandRegistry:
    """
    Central command management system
    Handles registration, routing, and execution of all commands
    """
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.command_history: List[str] = []
        self.max_history = 100
        
        # Register all default commands
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register all built-in commands"""
        
        # ========== CONVERSATIONAL COMMANDS ==========
        
        self.register(Command(
            name="greet",
            aliases=["hi", "hello", "hey", "hi ava", "hello ava", "hey ava"],
            category=CommandCategory.ASSISTANT,
            handler=lambda: "CONVERSATION_GREETING",
            description="Greet Ava"
        ))
        
        self.register(Command(
            name="how_are_you",
            aliases=["how are you", "how are you doing", "how's it going", "what's up"],
            category=CommandCategory.ASSISTANT,
            handler=lambda: "CONVERSATION_HOW_ARE_YOU",
            description="Ask how Ava is doing"
        ))
        
        self.register(Command(
            name="thank_you",
            aliases=["thank you", "thanks", "thank you ava", "thanks ava"],
            category=CommandCategory.ASSISTANT,
            handler=lambda: "CONVERSATION_THANK_YOU",
            description="Thank Ava"
        ))
        
        self.register(Command(
            name="goodbye",
            aliases=["bye", "goodbye", "see you", "see you later"],
            category=CommandCategory.ASSISTANT,
            handler=lambda: "CONVERSATION_GOODBYE",
            description="Say goodbye"
        ))
        
        self.register(Command(
            name="your_name",
            aliases=["what's your name", "who are you", "your name"],
            category=CommandCategory.ASSISTANT,
            handler=lambda: "CONVERSATION_NAME",
            description="Ask Ava's name"
        ))
        
        self.register(Command(
            name="tell_joke",
            aliases=["tell me a joke", "joke", "tell joke", "make me laugh"],
            category=CommandCategory.ASSISTANT,
            handler=lambda: "CONVERSATION_JOKE",
            description="Tell a joke"
        ))
        
        # ========== WEB COMMANDS ==========
        
        self.register(Command(
            name="open_google",
            aliases=["google", "search google", "open google"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.google.com", "Google"),
            description="Open Google in browser"
        ))
        
        self.register(Command(
            name="open_youtube",
            aliases=["youtube", "open youtube"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.youtube.com", "YouTube"),
            description="Open YouTube"
        ))
        
        self.register(Command(
            name="open_gmail",
            aliases=["gmail", "email", "open gmail", "open email"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://mail.google.com", "Gmail"),
            description="Open Gmail"
        ))
        
        self.register(Command(
            name="open_github",
            aliases=["github", "open github"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://github.com", "GitHub"),
            description="Open GitHub"
        ))
        
        self.register(Command(
            name="open_facebook",
            aliases=["facebook", "open facebook", "fb"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.facebook.com", "Facebook"),
            description="Open Facebook"
        ))
        
        self.register(Command(
            name="open_twitter",
            aliases=["twitter", "open twitter", "x"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.twitter.com", "Twitter"),
            description="Open Twitter"
        ))
        
        self.register(Command(
            name="open_instagram",
            aliases=["instagram", "open instagram", "insta"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.instagram.com", "Instagram"),
            description="Open Instagram"
        ))
        
        self.register(Command(
            name="open_linkedin",
            aliases=["linkedin", "open linkedin"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.linkedin.com", "LinkedIn"),
            description="Open LinkedIn"
        ))
        
        self.register(Command(
            name="open_reddit",
            aliases=["reddit", "open reddit"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.reddit.com", "Reddit"),
            description="Open Reddit"
        ))
        
        self.register(Command(
            name="open_netflix",
            aliases=["netflix", "open netflix"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.netflix.com", "Netflix"),
            description="Open Netflix"
        ))
        
        # ========== APPLICATION COMMANDS ==========
        
        self.register(Command(
            name="open_notepad",
            aliases=["notepad", "open notepad", "text editor"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("notepad" if os.name == 'nt' else "gedit", "Notepad"),
            description="Open text editor"
        ))
        
        self.register(Command(
            name="open_calculator",
            aliases=["calculator", "calc", "open calculator"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("calc" if os.name == 'nt' else "gnome-calculator", "Calculator"),
            description="Open calculator"
        ))
        
        self.register(Command(
            name="open_file_explorer",
            aliases=["explorer", "file explorer", "open explorer", "files", "my computer"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("explorer" if os.name == 'nt' else "nautilus", "File Explorer"),
            description="Open file explorer"
        ))
        
        self.register(Command(
            name="open_browser",
            aliases=["browser", "open browser", "web browser", "chrome"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("start chrome" if os.name == 'nt' else "google-chrome", "Browser"),
            description="Open web browser"
        ))
        
        self.register(Command(
            name="open_paint",
            aliases=["paint", "open paint", "drawing"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("mspaint" if os.name == 'nt' else "drawing", "Paint"),
            description="Open Paint"
        ))
        
        self.register(Command(
            name="open_word",
            aliases=["word", "open word", "microsoft word"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("winword" if os.name == 'nt' else "libreoffice --writer", "Word"),
            description="Open Microsoft Word"
        ))
        
        self.register(Command(
            name="open_excel",
            aliases=["excel", "open excel", "spreadsheet"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("excel" if os.name == 'nt' else "libreoffice --calc", "Excel"),
            description="Open Excel"
        ))
        
        self.register(Command(
            name="open_powerpoint",
            aliases=["powerpoint", "open powerpoint", "presentation"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("powerpnt" if os.name == 'nt' else "libreoffice --impress", "PowerPoint"),
            description="Open PowerPoint"
        ))
        
        # ========== MEDIA COMMANDS ==========
        
        self.register(Command(
            name="play_music",
            aliases=["play music", "music", "play songs", "open spotify"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._open_app("spotify" if os.name == 'nt' else "spotify", "Spotify"),
            description="Play music (opens Spotify)"
        ))
        
        self.register(Command(
            name="pause_music",
            aliases=["pause", "pause music", "stop music"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._media_control("pause"),
            description="Pause media playback"
        ))
        
        self.register(Command(
            name="next_track",
            aliases=["next", "next song", "next track", "skip"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._media_control("next"),
            description="Next track"
        ))
        
        self.register(Command(
            name="previous_track",
            aliases=["previous", "previous song", "previous track", "back"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._media_control("previous"),
            description="Previous track"
        ))
        
        self.register(Command(
            name="volume_up",
            aliases=["volume up", "increase volume", "louder"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._volume_control("up"),
            description="Increase volume"
        ))
        
        self.register(Command(
            name="volume_down",
            aliases=["volume down", "decrease volume", "quieter", "lower volume"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._volume_control("down"),
            description="Decrease volume"
        ))
        
        self.register(Command(
            name="mute",
            aliases=["mute", "silence", "mute volume"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._volume_control("mute"),
            description="Mute volume"
        ))
        
        # ========== MOUSE COMMANDS ==========
        
        self.register(Command(
            name="left_click",
            aliases=["click", "left click"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_LEFT_CLICK",
            description="Perform left mouse click"
        ))
        
        self.register(Command(
            name="right_click",
            aliases=["right click"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_RIGHT_CLICK",
            description="Perform right mouse click"
        ))
        
        self.register(Command(
            name="double_click",
            aliases=["double click"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_DOUBLE_CLICK",
            description="Perform double click"
        ))
        
        self.register(Command(
            name="scroll_up",
            aliases=["scroll up"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_SCROLL_UP",
            description="Scroll up"
        ))
        
        self.register(Command(
            name="scroll_down",
            aliases=["scroll down"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_SCROLL_DOWN",
            description="Scroll down"
        ))
        
        # ========== INFO COMMANDS ==========
        
        self.register(Command(
            name="get_time",
            aliases=["time", "what time", "current time", "what's the time", "tell me the time"],
            category=CommandCategory.INFO,
            handler=lambda: self._get_time_info(),
            description="Get current time"
        ))
        
        self.register(Command(
            name="get_date",
            aliases=["date", "what date", "today's date", "what's the date", "tell me the date", "what day is it"],
            category=CommandCategory.INFO,
            handler=lambda: self._get_date_info(),
            description="Get current date"
        ))
        
        self.register(Command(
            name="get_day",
            aliases=["what day", "day of week", "what day is today"],
            category=CommandCategory.INFO,
            handler=lambda: self._get_day_info(),
            description="Get current day of week"
        ))
        
        # ========== SYSTEM COMMANDS ==========
        
        self.register(Command(
            name="lock_computer",
            aliases=["lock", "lock computer", "lock screen"],
            category=CommandCategory.SYSTEM,
            handler=lambda: self._lock_system(),
            description="Lock the computer",
            requires_confirmation=True
        ))
        
        self.register(Command(
            name="minimize_all",
            aliases=["minimize all", "show desktop", "hide all"],
            category=CommandCategory.SYSTEM,
            handler=lambda: self._minimize_all(),
            description="Minimize all windows"
        ))
        
        self.register(Command(
            name="screenshot",
            aliases=["screenshot", "take screenshot", "capture screen", "screen capture"],
            category=CommandCategory.SYSTEM,
            handler=lambda: self._take_screenshot(),
            description="Take a screenshot"
        ))
        
        self.register(Command(
            name="close_window",
            aliases=["close", "close window", "close this"],
            category=CommandCategory.SYSTEM,
            handler=lambda: self._close_window(),
            description="Close current window"
        ))
        
        # ========== ASSISTANT COMMANDS ==========
        
        self.register(Command(
            name="help",
            aliases=["help", "what can you do", "commands", "show commands"],
            category=CommandCategory.ASSISTANT,
            handler=lambda: self._list_commands(),
            description="Show available commands"
        ))
    
    # ========== COMMAND REGISTRATION ==========
    
    def register(self, command: Command):
        """Register a new command"""
        # Register by name
        self.commands[command.name] = command
        
        # Register all aliases
        for alias in command.aliases:
            self.commands[alias.lower()] = command
    
    def unregister(self, command_name: str):
        """Unregister a command"""
        if command_name in self.commands:
            command = self.commands[command_name]
            # Remove all aliases
            for alias in command.aliases:
                if alias in self.commands:
                    del self.commands[alias]
            del self.commands[command_name]
    
    # ========== COMMAND EXECUTION ==========
    
    def execute(self, command_input: str) -> Optional[str]:
        """
        Execute a command by name or alias
        
        Returns:
            Result string or None if command not found
        """
        command_input = command_input.lower().strip()
        
        # Add to history
        self.command_history.append(command_input)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        # Find command
        command = self._find_command(command_input)
        
        if command is None:
            return None
        
        if not command.enabled:
            return f"Command '{command.name}' is currently disabled"
        
        try:
            # Execute handler
            result = command.handler()
            return result if result else f"✅ {command.description}"
        except Exception as e:
            return f"❌ Error executing {command.name}: {str(e)}"
    
    def _find_command(self, input_text: str) -> Optional[Command]:
        """Find command by matching input text"""
        # Exact match
        if input_text in self.commands:
            return self.commands[input_text]
        
        # Partial match
        for alias, command in self.commands.items():
            if alias in input_text or input_text in alias:
                return command
        
        return None
    
    # ========== COMMAND HANDLERS ==========
    
    def _open_url(self, url: str, name: str) -> str:
        """Open URL in browser"""
        try:
            webbrowser.open(url)
            return f"✅ Opened {name}"
        except Exception as e:
            return f"❌ Could not open {name}: {e}"
    
    def _open_app(self, command: str, name: str) -> str:
        """Open application"""
        try:
            if os.name == 'nt':  # Windows
                os.system(f"start {command}")
            else:  # Linux/Mac
                subprocess.Popen(command.split())
            return f"✅ Opened {name}"
        except Exception as e:
            return f"❌ Could not open {name}: {e}"
    
    def _get_time_info(self) -> str:
        """Get current time"""
        from datetime import datetime
        now = datetime.now()
        return f"🕐 Current time: {now.strftime('%I:%M %p')}"
    
    def _get_date_info(self) -> str:
        """Get current date"""
        from datetime import datetime
        today = datetime.now()
        return f"📅 Today is {today.strftime('%A, %B %d, %Y')}"
    
    def _get_day_info(self) -> str:
        """Get current day of week"""
        from datetime import datetime
        today = datetime.now()
        return f"📅 Today is {today.strftime('%A')}"
    
    def _media_control(self, action: str) -> str:
        """Control media playback"""
        try:
            import pyautogui
            if action == "pause":
                pyautogui.press('playpause')
                return "⏸️ Media paused"
            elif action == "next":
                pyautogui.press('nexttrack')
                return "⏭️ Next track"
            elif action == "previous":
                pyautogui.press('prevtrack')
                return "⏮️ Previous track"
        except:
            return f"❌ Could not {action} media"
    
    def _volume_control(self, action: str) -> str:
        """Control system volume"""
        try:
            import pyautogui
            if action == "up":
                pyautogui.press('volumeup')
                return "🔊 Volume increased"
            elif action == "down":
                pyautogui.press('volumedown')
                return "🔉 Volume decreased"
            elif action == "mute":
                pyautogui.press('volumemute')
                return "🔇 Volume muted"
        except:
            return f"❌ Could not control volume"
    
    def _take_screenshot(self) -> str:
        """Take a screenshot"""
        try:
            import pyautogui
            from datetime import datetime
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(filename)
            return f"📸 Screenshot saved as {filename}"
        except:
            return "❌ Could not take screenshot"
    
    def _close_window(self) -> str:
        """Close current window"""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            return "✅ Window closed"
        except:
            return "❌ Could not close window"
    
    def _lock_system(self) -> str:
        """Lock the computer"""
        try:
            if os.name == 'nt':
                os.system("rundll32.exe user32.dll,LockWorkStation")
            else:
                os.system("gnome-screensaver-command -l")
            return "🔒 Computer locked"
        except:
            return "❌ Could not lock computer"
    
    def _minimize_all(self) -> str:
        """Minimize all windows"""
        try:
            if os.name == 'nt':
                # Windows: Win+D
                import pyautogui
                pyautogui.hotkey('win', 'd')
            return "✅ Minimized all windows"
        except:
            return "❌ Could not minimize windows"
    
    def _list_commands(self) -> str:
        """List all available commands"""
        categories = {}
        
        # Group by category
        for cmd_name, command in self.commands.items():
            if cmd_name == command.name:  # Only count primary name
                cat = command.category.value
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(command)
        
        # Format output
        output = ["Available Commands:\n"]
        for category, commands in categories.items():
            output.append(f"\n{category.upper()}:")
            for cmd in commands:
                output.append(f"  • {cmd.aliases[0]} - {cmd.description}")
        
        return "\n".join(output)
    
    # ========== QUERY METHODS ==========
    
    def get_all_commands(self) -> List[Command]:
        """Get all registered commands"""
        seen = set()
        result = []
        for command in self.commands.values():
            if command.name not in seen:
                seen.add(command.name)
                result.append(command)
        return result
    
    def get_commands_by_category(self, category: CommandCategory) -> List[Command]:
        """Get commands in a specific category"""
        return [cmd for cmd in self.get_all_commands() if cmd.category == category]
    
    def get_command_info(self, command_name: str) -> Optional[Command]:
        """Get information about a command"""
        return self.commands.get(command_name.lower())
    
    def search_commands(self, query: str) -> List[Command]:
        """Search commands by name or description"""
        query = query.lower()
        results = []
        
        for command in self.get_all_commands():
            if (query in command.name.lower() or 
                query in command.description.lower() or
                any(query in alias.lower() for alias in command.aliases)):
                results.append(command)
        
        return results
    
    # ========== STATISTICS ==========
    
    def get_command_history(self, limit: int = 10) -> List[str]:
        """Get recent command history"""
        return self.command_history[-limit:]
    
    def get_most_used_commands(self, limit: int = 5) -> List[tuple]:
        """Get most frequently used commands"""
        from collections import Counter
        counter = Counter(self.command_history)
        return counter.most_common(limit)
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()


# ========== FACTORY FUNCTION ==========

def create_registry() -> CommandRegistry:
    """Create command registry instance"""
    return CommandRegistry()