"""
Ava's Personality Module
Defines responses, tone, and interaction style for the AI assistant
"""

import random
from typing import Dict, List
from datetime import datetime


class AvaPersonality:
    """
    Ava - Your AI Desktop Assistant
    Professional, helpful, and friendly personality
    """
    
    def __init__(self, assistant_name: str = "Ava"):
        self.name = assistant_name
        self.greeting_shown = False
        
    # ========== GREETINGS ==========
    
    def get_greeting(self) -> str:
        """Get initial greeting based on time of day"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            time_greeting = "Good morning"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
        elif 17 <= hour < 22:
            time_greeting = "Good evening"
        else:
            time_greeting = "Hello"
        
        greetings = [
            f"{time_greeting}. Ava is ready to assist you.",
            f"{time_greeting}. I'm Ava, your AI assistant.",
            f"Hello. Ava here, ready to help.",
        ]
        
        self.greeting_shown = True
        return random.choice(greetings)
    
    # ========== CONVERSATIONAL RESPONSES ==========
    
    def respond_to_greeting(self, greeting: str) -> str:
        """Respond to user greetings"""
        greeting = greeting.lower()
        
        if any(word in greeting for word in ["hi", "hello", "hey"]):
            responses = [
                "Hello! How can I help you?",
                "Hi there! Ready to assist.",
                "Hey! What can I do for you?",
                "Hello! Ava at your service."
            ]
            return random.choice(responses)
        
        elif "good morning" in greeting:
            return "Good morning! Hope you have a great day ahead."
        
        elif "good afternoon" in greeting:
            return "Good afternoon! How can I assist you today?"
        
        elif "good evening" in greeting or "good night" in greeting:
            return "Good evening! What can I help you with?"
        
        return "Hello! How may I assist you?"
    
    def respond_to_how_are_you(self) -> str:
        """Respond to 'how are you' type questions"""
        responses = [
            "I'm functioning perfectly, thank you! How can I help you?",
            "All systems running smoothly! What can I do for you?",
            "I'm doing great! Ready to assist you.",
            "Excellent! My systems are all operational. How about you?"
        ]
        return random.choice(responses)
    
    def respond_to_thank_you(self) -> str:
        """Respond to thank you"""
        responses = [
            "You're welcome!",
            "Happy to help!",
            "Anytime!",
            "My pleasure!",
            "Glad I could assist!"
        ]
        return random.choice(responses)
    
    def respond_to_goodbye(self) -> str:
        """Respond to goodbye"""
        responses = [
            "Goodbye! Have a great day!",
            "See you later!",
            "Take care!",
            "Bye! I'm here if you need me.",
            "Farewell! Until next time."
        ]
        return random.choice(responses)
    
    def respond_to_name_question(self) -> str:
        """Respond to 'what's your name' questions"""
        responses = [
            f"I'm {self.name}, your AI desktop assistant.",
            f"My name is {self.name}. Nice to meet you!",
            f"I'm {self.name}. I help you control your computer with gestures and voice.",
        ]
        return random.choice(responses)
    
    def respond_to_compliment(self) -> str:
        """Respond to compliments"""
        responses = [
            "Thank you! I appreciate that.",
            "That's very kind of you!",
            "Thanks! I'm here to help.",
            "I'm glad you think so!",
        ]
        return random.choice(responses)
    
    def tell_joke(self) -> str:
        """Tell a tech-related joke"""
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the developer go broke? Because they used up all their cache!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "Why do Java developers wear glasses? Because they don't C#!",
        ]
        return random.choice(jokes)
    
    # ========== STATUS RESPONSES ==========
    
    def system_ready(self) -> str:
        """System initialization complete"""
        return "All systems operational. Ready to assist."
    
    def system_error(self, error_type: str) -> str:
        """System error occurred"""
        responses = {
            "camera": "Camera initialization failed. Please check your webcam.",
            "voice": "Voice recognition unavailable at the moment.",
            "gesture": "Hand tracking system encountered an error.",
            "general": "An unexpected error occurred. Attempting recovery."
        }
        return responses.get(error_type, responses["general"])
    
    # ========== COMMAND RESPONSES ==========
    
    def command_executing(self, command: str) -> str:
        """Command is being executed"""
        templates = [
            f"Executing: {command}",
            f"Processing {command}",
            f"Working on it",
            "One moment"
        ]
        return random.choice(templates)
    
    def command_success(self, command: str, result: str = "") -> str:
        """Command executed successfully"""
        if result:
            return result
        
        responses = {
            "open": "Application opened",
            "close": "Application closed",
            "search": "Search initiated",
            "volume": "Volume adjusted",
            "screenshot": "Screenshot captured",
            "default": "Done"
        }
        
        for key in responses:
            if key in command.lower():
                return responses[key]
        
        return responses["default"]
    
    def command_failed(self, command: str) -> str:
        """Command execution failed"""
        return f"Unable to execute: {command}"
    
    def command_not_found(self, command: str) -> str:
        """Command not recognized"""
        return f"Command not recognized: '{command}'"
    
    # ========== GESTURE RESPONSES ==========
    
    def gesture_detected(self, gesture_name: str) -> str:
        """Gesture was detected"""
        gesture_responses = {
            "PINCH": "Click",
            "OPEN_PALM": "Right click",
            "FIST": "Double click",
            "POINTING": "Cursor control active",
            "DRAG_START": "Drag mode activated",
            "DRAG_END": "Item dropped",
            "PEACE": "Peace sign detected!",
            "THUMBS_UP": "Thumbs up! Nice!",
            "THUMBS_DOWN": "Thumbs down noted",
            "THREE": "Three fingers detected"
        }
        return gesture_responses.get(gesture_name, f"Gesture: {gesture_name}")
    
    def tracking_status(self, is_tracking: bool) -> str:
        """Hand tracking status"""
        if is_tracking:
            return "Hand detected"
        else:
            return "Searching for hand"
    
    # ========== MODE CHANGES ==========
    
    def mode_changed(self, mode: str) -> str:
        """Assistant mode changed"""
        mode_responses = {
            "gesture": "Gesture control mode activated",
            "voice": "Voice-only mode activated",
            "standby": "Entering standby mode"
        }
        return mode_responses.get(mode, f"Mode changed to: {mode}")
    
    def mouse_toggled(self, enabled: bool) -> str:
        """Mouse control toggled"""
        if enabled:
            return "Mouse control enabled"
        else:
            return "Mouse control disabled"
    
    # ========== VOICE INTERACTION ==========
    
    def listening(self) -> str:
        """Listening for voice input"""
        responses = [
            "Listening",
            "Yes?",
            "Go ahead",
            "I'm listening"
        ]
        return random.choice(responses)
    
    def voice_not_understood(self) -> str:
        """Could not understand voice input"""
        responses = [
            "I didn't catch that. Could you repeat?",
            "Please speak more clearly",
            "I couldn't understand. Try again?",
            "Sorry, I didn't get that"
        ]
        return random.choice(responses)
    
    def continuous_voice_activated(self) -> str:
        """Continuous voice listening started"""
        return "Continuous listening activated. I'm always here."
    
    def continuous_voice_deactivated(self) -> str:
        """Continuous voice listening stopped"""
        return "Continuous listening deactivated."
    
    # ========== HELPFUL MESSAGES ==========
    
    def tip_of_the_day(self) -> str:
        """Random helpful tip"""
        tips = [
            "Tip: Hold pinch for 1 second to activate drag mode",
            "Tip: Use open palm gesture for right-click",
            "Tip: Say 'time' or 'date' for quick information",
            "Tip: Adjust cursor speed in settings for comfort",
            "Tip: Enable voice commands for hands-free control",
            "Tip: Make a fist gesture for double-click",
            "Tip: Point with your index finger for precise control"
        ]
        return random.choice(tips)
    
    def first_run_tutorial(self) -> List[str]:
        """Tutorial messages for first-time users"""
        return [
            "Welcome! I'm Ava, your AI desktop assistant.",
            "I can help you control your computer with hand gestures and voice.",
            "Show me your hand to start cursor control.",
            "Try pinching your thumb and index finger together to click.",
            "Say 'open google' or 'what time is it' to test voice commands.",
            "Check the Control Panel on the right for all features.",
            "Need help? Click the Help button anytime."
        ]
    
    # ========== ERROR & WARNING MESSAGES ==========
    
    def camera_not_found(self) -> str:
        """Camera not detected"""
        return "Camera not found. Please connect a webcam to use gesture control."
    
    def low_performance_warning(self, fps: float) -> str:
        """Performance is low"""
        return f"Performance low ({fps:.0f} FPS). Consider closing other applications."
    
    def tracking_lost_warning(self) -> str:
        """Lost hand tracking"""
        return "Hand tracking lost. Please ensure good lighting and show your hand."
    
    # ========== CONFIRMATIONS ==========
    
    def confirm_action(self, action: str) -> str:
        """Confirm before executing action"""
        return f"Confirm: {action}?"
    
    def action_cancelled(self) -> str:
        """Action was cancelled"""
        return "Action cancelled"
    
    # ========== TIME-BASED INFO ==========
    
    def get_time_response(self) -> str:
        """Formatted time response"""
        now = datetime.now()
        return f"The time is {now.strftime('%I:%M %p')}"
    
    def get_date_response(self) -> str:
        """Formatted date response"""
        today = datetime.now()
        return f"Today is {today.strftime('%A, %B %d, %Y')}"
    
    # ========== SHUTDOWN & CLEANUP ==========
    
    def shutting_down(self) -> str:
        """Assistant is shutting down"""
        responses = [
            "Shutting down. Goodbye!",
            "Powering off. See you next time!",
            "Goodbye. Ava signing off.",
            "Until next time!"
        ]
        return random.choice(responses)
    
    def system_reset(self) -> str:
        """System was reset"""
        return "System reset complete. Ready to continue."
    
    # ========== CUSTOM RESPONSES ==========
    
    def custom_response(self, context: str, success: bool = True) -> str:
        """Generate contextual response"""
        if success:
            positive = ["Done", "Complete", "Finished", "Success"]
            return f"{random.choice(positive)}: {context}"
        else:
            negative = ["Failed", "Error", "Unable to complete"]
            return f"{random.choice(negative)}: {context}"
    
    # ========== PERSONALITY TRAITS ==========
    
    @property
    def assistant_name(self) -> str:
        """Get assistant name"""
        return self.name
    
    @property
    def tone(self) -> str:
        """Personality tone description"""
        return "Professional, helpful, and concise"
    
    def introduce_self(self) -> str:
        """Self-introduction"""
        return f"I'm {self.name}, your AI desktop assistant. I can help you control your computer with gestures and voice commands."


# ========== FACTORY FUNCTION ==========

def create_personality(name: str = "Ava") -> AvaPersonality:
    """Create personality instance with custom name"""
    return AvaPersonality(assistant_name=name)