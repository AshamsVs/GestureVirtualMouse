"""
Command Registry - Central Command Management System
Organizes all commands by category with intelligent routing
COMPLETE EXPANDED VERSION - Created for Ava by Ashams
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
    CONVERSATION = "conversation"
    SEARCH = "search"


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
        
        # Import personality for conversation responses
        from .personality import AvaPersonality
        self.personality = AvaPersonality("Ava")
        
        # Register all default commands
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register all built-in commands"""
        
        # ========== CONVERSATIONAL COMMANDS ==========
        
        # === GREETINGS ===
        self.register(Command(
            name="greet",
            aliases=[
                "hi", "hello", "hey", "hi ava", "hello ava", "hey ava",
                "good morning", "good afternoon", "good evening",
                "morning", "afternoon", "evening",
                "what's up", "whats up", "sup", "yo",
                "greetings", "howdy", "hiya"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_greeting("hello"),
            description="Greet Ava"
        ))
        
        # === HOW ARE YOU ===
        self.register(Command(
            name="how_are_you",
            aliases=[
                "how are you", "how are you doing", "how's it going", "hows it going",
                "how do you do", "how are things", "how's everything",
                "how you doing", "you good", "you okay", "you alright"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_how_are_you(),
            description="Ask how Ava is doing"
        ))
        
        # === THANK YOU ===
        self.register(Command(
            name="thank_you",
            aliases=[
                "thank you", "thanks", "thank you ava", "thanks ava",
                "thx", "ty", "appreciate it", "much appreciated",
                "thanks a lot", "thank you so much", "cheers"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_thank_you(),
            description="Thank Ava"
        ))
        
        # === GOODBYE ===
        self.register(Command(
            name="goodbye",
            aliases=[
                "bye", "goodbye", "see you", "see you later", "see ya",
                "catch you later", "talk to you later", "ttyl",
                "gotta go", "i'm leaving", "im leaving", "take care",
                "farewell", "peace out", "later"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_goodbye(),
            description="Say goodbye"
        ))
        
        # === NAME & IDENTITY ===
        self.register(Command(
            name="your_name",
            aliases=[
                "what's your name", "whats your name", "your name",
                "who are you", "what are you", "introduce yourself",
                "tell me about yourself"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_name_question(),
            description="Ask Ava's name"
        ))
        
        # === CREATOR ===
        self.register(Command(
            name="who_created_you",
            aliases=[
                "who created you", "who made you", "who built you",
                "who's your creator", "whos your creator", "who developed you",
                "who designed you", "who programmed you", "who is your maker",
                "your creator"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_creator_question(),
            description="Ask about Ava's creator"
        ))
        
        # === CAPABILITIES ===
        self.register(Command(
            name="what_can_you_do",
            aliases=[
                "what can you do", "what do you do", "what are you capable of",
                "tell me what you can do", "show me what you can do",
                "your abilities", "your capabilities", "your features",
                "what are your skills", "what are you"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_capabilities_question(),
            description="Ask about Ava's capabilities"
        ))
        
        # === JOKES ===
        self.register(Command(
            name="tell_joke",
            aliases=[
                "tell me a joke", "joke", "tell joke", "make me laugh",
                "tell me something funny", "say something funny",
                "got any jokes", "know any jokes", "funny", "be funny"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.tell_joke(),
            description="Tell a joke"
        ))
        
        # === COMPLIMENTS ===
        self.register(Command(
            name="compliment",
            aliases=[
                "you're awesome", "youre awesome", "you're great", "youre great",
                "you're amazing", "youre amazing", "you're cool", "good job",
                "well done", "nice work", "you're smart", "youre smart",
                "you're the best", "you rock", "you're wonderful"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_compliment(),
            description="Compliment Ava"
        ))
        
        # === AGE ===
        self.register(Command(
            name="how_old",
            aliases=[
                "how old are you", "what's your age", "whats your age",
                "your age", "when were you born", "when were you created",
                "when were you made"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_age_question(),
            description="Ask Ava's age"
        ))
        
        # === FEELINGS ===
        self.register(Command(
            name="do_you_have_feelings",
            aliases=[
                "do you have feelings", "can you feel", "do you feel emotions",
                "are you alive", "are you sentient", "are you conscious",
                "do you think", "can you think"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_feelings_question(),
            description="Ask about feelings"
        ))
        
        # === FAVORITE THINGS ===
        self.register(Command(
            name="favorite_color",
            aliases=[
                "what's your favorite color", "whats your favorite color",
                "favorite color", "your favorite color", "what color do you like"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_favorite_color(),
            description="Ask favorite color"
        ))
        
        self.register(Command(
            name="favorite_food",
            aliases=[
                "what's your favorite food", "whats your favorite food",
                "favorite food", "what do you eat", "do you eat"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_favorite_food(),
            description="Ask favorite food"
        ))
        
        # === LOVE & RELATIONSHIPS ===
        self.register(Command(
            name="i_love_you",
            aliases=[
                "i love you", "love you", "i like you", "you're my favorite"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_love(),
            description="Express love"
        ))
        
        # === WEATHER ===
        self.register(Command(
            name="weather",
            aliases=[
                "what's the weather", "whats the weather", "weather",
                "how's the weather", "hows the weather", "is it raining"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_weather(),
            description="Ask about weather"
        ))
        
        # === MEANING OF LIFE ===
        self.register(Command(
            name="meaning_of_life",
            aliases=[
                "what's the meaning of life", "whats the meaning of life",
                "meaning of life", "what is life", "why are we here"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_meaning_of_life(),
            description="Ask meaning of life"
        ))
        
        # === SORRY ===
        self.register(Command(
            name="apology",
            aliases=[
                "sorry", "i'm sorry", "im sorry", "my bad", "apologize"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_apology(),
            description="User apologizes"
        ))
        
        # === RANDOM CHAT ===
        self.register(Command(
            name="random_chat",
            aliases=[
                "talk to me", "chat with me", "let's talk", "lets talk",
                "say something", "tell me something", "anything new"
            ],
            category=CommandCategory.CONVERSATION,
            handler=lambda: self.personality.respond_to_random_chat(),
            description="Random chat"
        ))
        
        # ========== WEB COMMANDS (EXPANDED) ==========
        
        # Social Media
        self.register(Command(
            name="open_google",
            aliases=["google", "search google", "open google"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.google.com", "Google"),
            description="Open Google"
        ))
        
        self.register(Command(
            name="open_youtube",
            aliases=["youtube", "open youtube", "yt"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.youtube.com", "YouTube"),
            description="Open YouTube"
        ))
        
        self.register(Command(
            name="open_gmail",
            aliases=["gmail", "email", "open gmail", "open email", "mail"],
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
            aliases=["twitter", "open twitter", "x", "open x"],
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
            name="open_tiktok",
            aliases=["tiktok", "open tiktok"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.tiktok.com", "TikTok"),
            description="Open TikTok"
        ))
        
        self.register(Command(
            name="open_pinterest",
            aliases=["pinterest", "open pinterest"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.pinterest.com", "Pinterest"),
            description="Open Pinterest"
        ))
        
        self.register(Command(
            name="open_snapchat",
            aliases=["snapchat", "open snapchat", "snap"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.snapchat.com", "Snapchat"),
            description="Open Snapchat"
        ))
        
        # Streaming Services
        self.register(Command(
            name="open_netflix",
            aliases=["netflix", "open netflix"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.netflix.com", "Netflix"),
            description="Open Netflix"
        ))
        
        self.register(Command(
            name="open_spotify",
            aliases=["spotify", "open spotify"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.spotify.com", "Spotify"),
            description="Open Spotify"
        ))
        
        self.register(Command(
            name="open_amazon_prime",
            aliases=["amazon prime", "prime video", "prime"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.primevideo.com", "Amazon Prime"),
            description="Open Amazon Prime"
        ))
        
        self.register(Command(
            name="open_disney_plus",
            aliases=["disney plus", "disney+", "disney"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.disneyplus.com", "Disney+"),
            description="Open Disney+"
        ))
        
        self.register(Command(
            name="open_hulu",
            aliases=["hulu", "open hulu"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.hulu.com", "Hulu"),
            description="Open Hulu"
        ))
        
        self.register(Command(
            name="open_twitch",
            aliases=["twitch", "open twitch"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.twitch.tv", "Twitch"),
            description="Open Twitch"
        ))
        
        # Shopping
        self.register(Command(
            name="open_amazon",
            aliases=["amazon", "open amazon"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.amazon.com", "Amazon"),
            description="Open Amazon"
        ))
        
        self.register(Command(
            name="open_ebay",
            aliases=["ebay", "open ebay"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.ebay.com", "eBay"),
            description="Open eBay"
        ))
        
        # Learning & Productivity
        self.register(Command(
            name="open_wikipedia",
            aliases=["wikipedia", "wiki", "open wiki"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.wikipedia.org", "Wikipedia"),
            description="Open Wikipedia"
        ))
        
        self.register(Command(
            name="open_stackoverflow",
            aliases=["stackoverflow", "stack overflow", "stack"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://stackoverflow.com", "Stack Overflow"),
            description="Open Stack Overflow"
        ))
        
        self.register(Command(
            name="open_coursera",
            aliases=["coursera", "open coursera"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.coursera.org", "Coursera"),
            description="Open Coursera"
        ))
        
        self.register(Command(
            name="open_udemy",
            aliases=["udemy", "open udemy"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.udemy.com", "Udemy"),
            description="Open Udemy"
        ))
        
        self.register(Command(
            name="open_chatgpt",
            aliases=["chatgpt", "chat gpt", "open chatgpt"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://chat.openai.com", "ChatGPT"),
            description="Open ChatGPT"
        ))
        
        # Cloud & Storage
        self.register(Command(
            name="open_google_drive",
            aliases=["google drive", "drive", "gdrive"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://drive.google.com", "Google Drive"),
            description="Open Google Drive"
        ))
        
        self.register(Command(
            name="open_dropbox",
            aliases=["dropbox", "open dropbox"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://www.dropbox.com", "Dropbox"),
            description="Open Dropbox"
        ))
        
        self.register(Command(
            name="open_onedrive",
            aliases=["onedrive", "one drive"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://onedrive.live.com", "OneDrive"),
            description="Open OneDrive"
        ))
        
        # Communication
        self.register(Command(
            name="open_whatsapp",
            aliases=["whatsapp", "open whatsapp"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://web.whatsapp.com", "WhatsApp"),
            description="Open WhatsApp Web"
        ))
        
        self.register(Command(
            name="open_discord",
            aliases=["discord", "open discord"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://discord.com/app", "Discord"),
            description="Open Discord"
        ))
        
        self.register(Command(
            name="open_slack",
            aliases=["slack", "open slack"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://slack.com", "Slack"),
            description="Open Slack"
        ))
        
        self.register(Command(
            name="open_zoom",
            aliases=["zoom", "open zoom"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://zoom.us", "Zoom"),
            description="Open Zoom"
        ))
        
        self.register(Command(
            name="open_teams",
            aliases=["teams", "microsoft teams", "ms teams"],
            category=CommandCategory.WEB,
            handler=lambda: self._open_url("https://teams.microsoft.com", "Microsoft Teams"),
            description="Open Microsoft Teams"
        ))
        
        # ========== APPLICATION COMMANDS (EXPANDED) ==========
        
        # Basic Apps
        self.register(Command(
            name="open_notepad",
            aliases=["notepad", "open notepad", "text editor", "note"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("notepad" if os.name == 'nt' else "gedit", "Notepad"),
            description="Open Notepad"
        ))
        
        self.register(Command(
            name="open_calculator",
            aliases=["calculator", "calc", "open calculator"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("calc" if os.name == 'nt' else "gnome-calculator", "Calculator"),
            description="Open Calculator"
        ))
        
        self.register(Command(
            name="open_file_explorer",
            aliases=["explorer", "file explorer", "open explorer", "files", "my computer", "this pc"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("explorer" if os.name == 'nt' else "nautilus", "File Explorer"),
            description="Open File Explorer"
        ))
        
        self.register(Command(
            name="open_browser",
            aliases=["browser", "open browser", "web browser", "chrome"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("start chrome" if os.name == 'nt' else "google-chrome", "Browser"),
            description="Open Browser"
        ))
        
        self.register(Command(
            name="open_paint",
            aliases=["paint", "open paint", "drawing", "draw"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("mspaint" if os.name == 'nt' else "drawing", "Paint"),
            description="Open Paint"
        ))
        
        # Microsoft Office
        self.register(Command(
            name="open_word",
            aliases=["word", "open word", "microsoft word", "ms word"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("winword" if os.name == 'nt' else "libreoffice --writer", "Word"),
            description="Open Microsoft Word"
        ))
        
        self.register(Command(
            name="open_excel",
            aliases=["excel", "open excel", "spreadsheet", "ms excel"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("excel" if os.name == 'nt' else "libreoffice --calc", "Excel"),
            description="Open Excel"
        ))
        
        self.register(Command(
            name="open_powerpoint",
            aliases=["powerpoint", "open powerpoint", "presentation", "ppt"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("powerpnt" if os.name == 'nt' else "libreoffice --impress", "PowerPoint"),
            description="Open PowerPoint"
        ))
        
        self.register(Command(
            name="open_outlook",
            aliases=["outlook", "open outlook", "microsoft outlook"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("outlook" if os.name == 'nt' else "thunderbird", "Outlook"),
            description="Open Outlook"
        ))
        
        # System Apps
        self.register(Command(
            name="open_task_manager",
            aliases=["task manager", "open task manager", "processes"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("taskmgr" if os.name == 'nt' else "gnome-system-monitor", "Task Manager"),
            description="Open Task Manager"
        ))
        
        self.register(Command(
            name="open_control_panel",
            aliases=["control panel", "settings", "system settings"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("control" if os.name == 'nt' else "gnome-control-center", "Control Panel"),
            description="Open Control Panel"
        ))
        
        self.register(Command(
            name="open_command_prompt",
            aliases=["command prompt", "cmd", "terminal"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("cmd" if os.name == 'nt' else "gnome-terminal", "Command Prompt"),
            description="Open Command Prompt"
        ))
        
        self.register(Command(
            name="open_powershell",
            aliases=["powershell", "power shell"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("powershell" if os.name == 'nt' else "gnome-terminal", "PowerShell"),
            description="Open PowerShell"
        ))
        
        # Media & Creative
        self.register(Command(
            name="open_photos",
            aliases=["photos", "photo viewer", "pictures"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("microsoft.windows.photos:" if os.name == 'nt' else "eog", "Photos"),
            description="Open Photos"
        ))
        
        self.register(Command(
            name="open_camera",
            aliases=["camera", "webcam", "open camera"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("microsoft.windows.camera:" if os.name == 'nt' else "cheese", "Camera"),
            description="Open Camera"
        ))
        
        self.register(Command(
            name="open_video_player",
            aliases=["video player", "media player", "vlc"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("vlc" if os.name == 'nt' else "vlc", "VLC"),
            description="Open Video Player"
        ))
        
        # Development
        self.register(Command(
            name="open_vscode",
            aliases=["vscode", "visual studio code", "vs code", "code"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("code", "VS Code"),
            description="Open Visual Studio Code"
        ))
        
        self.register(Command(
            name="open_pycharm",
            aliases=["pycharm", "open pycharm"],
            category=CommandCategory.APPLICATION,
            handler=lambda: self._open_app("pycharm", "PyCharm"),
            description="Open PyCharm"
        ))
        
        # ========== MEDIA COMMANDS (EXPANDED) ==========
        
        self.register(Command(
            name="play_music",
            aliases=["play music", "music", "play songs", "play song", "start music"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._open_url("https://www.spotify.com", "Spotify"),
            description="Play music"
        ))
        
        self.register(Command(
            name="pause_music",
            aliases=["pause", "pause music", "stop music", "stop"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._media_control("pause"),
            description="Pause media"
        ))
        
        self.register(Command(
            name="play_pause",
            aliases=["play pause", "toggle play"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._media_control("pause"),
            description="Play/Pause toggle"
        ))
        
        self.register(Command(
            name="next_track",
            aliases=["next", "next song", "next track", "skip", "skip song"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._media_control("next"),
            description="Next track"
        ))
        
        self.register(Command(
            name="previous_track",
            aliases=["previous", "previous song", "previous track", "back", "last song"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._media_control("previous"),
            description="Previous track"
        ))
        
        self.register(Command(
            name="volume_up",
            aliases=["volume up", "increase volume", "louder", "turn up"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._volume_control("up"),
            description="Increase volume"
        ))
        
        self.register(Command(
            name="volume_down",
            aliases=["volume down", "decrease volume", "quieter", "lower volume", "turn down"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._volume_control("down"),
            description="Decrease volume"
        ))
        
        self.register(Command(
            name="mute",
            aliases=["mute", "silence", "mute volume", "unmute"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._volume_control("mute"),
            description="Mute/Unmute volume"
        ))
        
        self.register(Command(
            name="volume_max",
            aliases=["volume max", "maximum volume", "full volume"],
            category=CommandCategory.MEDIA,
            handler=lambda: self._volume_control("max"),
            description="Set volume to maximum"
        ))
        
        # ========== MOUSE COMMANDS ==========
        
        self.register(Command(
            name="left_click",
            aliases=["click", "left click"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_LEFT_CLICK",
            description="Left click"
        ))
        
        self.register(Command(
            name="right_click",
            aliases=["right click"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_RIGHT_CLICK",
            description="Right click"
        ))
        
        self.register(Command(
            name="double_click",
            aliases=["double click"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_DOUBLE_CLICK",
            description="Double click"
        ))
        
        self.register(Command(
            name="scroll_up",
            aliases=["scroll up", "page up"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_SCROLL_UP",
            description="Scroll up"
        ))
        
        self.register(Command(
            name="scroll_down",
            aliases=["scroll down", "page down"],
            category=CommandCategory.MOUSE,
            handler=lambda: "MOUSE_SCROLL_DOWN",
            description="Scroll down"
        ))
        
        # ========== INFO COMMANDS ==========
        
        self.register(Command(
            name="get_time",
            aliases=["time", "what time", "current time", "what's the time", "tell me the time", "what time is it"],
            category=CommandCategory.INFO,
            handler=lambda: self._get_time_info(),
            description="Get current time"
        ))
        
        self.register(Command(
            name="get_date",
            aliases=["date", "what date", "today's date", "what's the date", "tell me the date", "what day is it", "today"],
            category=CommandCategory.INFO,
            handler=lambda: self._get_date_info(),
            description="Get current date"
        ))
        
        self.register(Command(
            name="get_day",
            aliases=["what day", "day of week", "what day is today"],
            category=CommandCategory.INFO,
            handler=lambda: self._get_day_info(),
            description="Get day of week"
        ))
        
        # ========== SYSTEM COMMANDS ==========
        
        self.register(Command(
            name="lock_computer",
            aliases=["lock", "lock computer", "lock screen", "lock pc"],
            category=CommandCategory.SYSTEM,
            handler=lambda: self._lock_system(),
            description="Lock computer",
            requires_confirmation=True
        ))
        
        self.register(Command(
            name="minimize_all",
            aliases=["minimize all", "show desktop", "hide all", "minimize everything"],
            category=CommandCategory.SYSTEM,
            handler=lambda: self._minimize_all(),
            description="Minimize all windows"
        ))
        
        self.register(Command(
            name="screenshot",
            aliases=["screenshot", "take screenshot", "capture screen", "screen capture", "print screen"],
            category=CommandCategory.SYSTEM,
            handler=lambda: self._take_screenshot(),
            description="Take screenshot"
        ))
        
        self.register(Command(
            name="close_window",
            aliases=["close", "close window", "close this", "exit"],
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
            description="Show commands"
        ))
    
    # ========== COMMAND REGISTRATION ==========
    
    def register(self, command: Command):
        """Register a new command"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias.lower()] = command
    
    def unregister(self, command_name: str):
        """Unregister a command"""
        if command_name in self.commands:
            command = self.commands[command_name]
            for alias in command.aliases:
                if alias in self.commands:
                    del self.commands[alias]
            del self.commands[command_name]
    
    # ========== COMMAND EXECUTION ==========
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute a command"""
        command_input = command_input.lower().strip()
        
        self.command_history.append(command_input)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        command = self._find_command(command_input)
        
        if command is None:
            return None
        
        if not command.enabled:
            return f"Command '{command.name}' is currently disabled"
        
        try:
            result = command.handler()
            return result if result else f"✅ {command.description}"
        except Exception as e:
            return f"❌ Error executing {command.name}: {str(e)}"
    
    def _find_command(self, input_text: str) -> Optional[Command]:
        """Find command by matching input text"""
        if input_text in self.commands:
            return self.commands[input_text]
        
        for alias, command in self.commands.items():
            if alias in input_text or input_text in alias:
                return command
        
        return None
    
    # ========== COMMAND HANDLERS ==========
    
    def _open_url(self, url: str, name: str) -> str:
        """Open URL in browser"""
        try:
            webbrowser.open(url)
            return f"Opening {name} for you!"
        except Exception as e:
            return f"Sorry, I couldn't open {name}"
    
    def _open_app(self, command: str, name: str) -> str:
        """Open application"""
        try:
            if os.name == 'nt':
                os.system(f"start {command}")
            else:
                subprocess.Popen(command.split())
            return f"Opening {name} now!"
        except Exception as e:
            return f"I couldn't open {name}, sorry!"
    
    def _get_time_info(self) -> str:
        """Get current time"""
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime('%I:%M %p')
        return f"It's {time_str} right now!"
    
    def _get_date_info(self) -> str:
        """Get current date"""
        from datetime import datetime
        today = datetime.now()
        date_str = today.strftime('%A, %B %d, %Y')
        return f"Today is {date_str}!"
    
    def _get_day_info(self) -> str:
        """Get current day of week"""
        from datetime import datetime
        today = datetime.now()
        day_str = today.strftime('%A')
        return f"Today is {day_str}!"
    
    def _media_control(self, action: str) -> str:
        """Control media playback"""
        try:
            import pyautogui
            if action == "pause":
                pyautogui.press('playpause')
                return "Done!"
            elif action == "next":
                pyautogui.press('nexttrack')
                return "Next track!"
            elif action == "previous":
                pyautogui.press('prevtrack')
                return "Previous track!"
        except:
            return f"I couldn't control media playback"
    
    def _volume_control(self, action: str) -> str:
        """Control system volume"""
        try:
            import pyautogui
            if action == "up":
                for _ in range(5):
                    pyautogui.press('volumeup')
                return "Volume increased!"
            elif action == "down":
                for _ in range(5):
                    pyautogui.press('volumedown')
                return "Volume decreased!"
            elif action == "mute":
                pyautogui.press('volumemute')
                return "Volume toggled!"
            elif action == "max":
                for _ in range(50):
                    pyautogui.press('volumeup')
                return "Volume at maximum!"
        except:
            return f"I couldn't control the volume"
    
    def _take_screenshot(self) -> str:
        """Take a screenshot"""
        try:
            import pyautogui
            from datetime import datetime
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(filename)
            return f"Screenshot saved as {filename}!"
        except:
            return "I couldn't take a screenshot"
    
    def _close_window(self) -> str:
        """Close current window"""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            return "Window closed!"
        except:
            return "I couldn't close the window"
    
    def _lock_system(self) -> str:
        """Lock the computer"""
        try:
            if os.name == 'nt':
                os.system("rundll32.exe user32.dll,LockWorkStation")
            else:
                os.system("gnome-screensaver-command -l")
            return "Computer locked!"
        except:
            return "I couldn't lock the computer"
    
    def _minimize_all(self) -> str:
        """Minimize all windows"""
        try:
            if os.name == 'nt':
                import pyautogui
                pyautogui.hotkey('win', 'd')
            return "Minimized all windows!"
        except:
            return "I couldn't minimize windows"
    
    def _list_commands(self) -> str:
        """List all available commands"""
        return self.personality.introduce_self()
    
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
        """Search commands"""
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