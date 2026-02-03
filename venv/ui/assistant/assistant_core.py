"""
Assistant Core - Ava's Brain
Central intelligence managing all assistant operations
"""

from typing import Optional, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .personality import AvaPersonality, create_personality
from .command_registry import CommandRegistry, create_registry, CommandCategory


class AssistantState(Enum):
    """Current state of the assistant"""
    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    LISTENING = "listening"
    PROCESSING = "processing"
    ERROR = "error"
    STANDBY = "standby"


@dataclass
class AssistantContext:
    """Context information for assistant operations"""
    current_mode: str = "gesture"
    mouse_enabled: bool = True
    voice_active: bool = False
    tracking_active: bool = False
    last_command: Optional[str] = None
    last_gesture: Optional[str] = None
    session_start: datetime = None


class AvaCore:
    """
    Ava's Central Intelligence
    Manages personality, commands, state, and decision-making
    """
    
    def __init__(self, assistant_name: str = "Ava"):
        # Core components
        self.personality = create_personality(assistant_name)
        self.command_registry = create_registry()
        
        # State management
        self.state = AssistantState.INITIALIZING
        self.context = AssistantContext(session_start=datetime.now())
        
        # Callbacks
        self.callbacks: Dict[str, Callable] = {}
        
        # Statistics
        self.commands_executed = 0
        self.gestures_detected = 0
        self.errors_count = 0
        
        # Configuration
        self.verbose = True
        self.auto_respond = True
        
    # ========== INITIALIZATION ==========
    
    def initialize(self) -> str:
        """Initialize the assistant"""
        self.state = AssistantState.READY
        return self.personality.get_greeting()
    
    def shutdown(self) -> str:
        """Shutdown the assistant"""
        self.state = AssistantState.STANDBY
        return self.personality.shutting_down()
    
    # ========== STATE MANAGEMENT ==========
    
    def set_state(self, new_state: AssistantState):
        """Change assistant state"""
        self.state = new_state
    
    def get_state(self) -> AssistantState:
        """Get current state"""
        return self.state
    
    def update_context(self, **kwargs):
        """Update context information"""
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
    
    # ========== COMMAND PROCESSING ==========
    
    def process_voice_command(self, command_text: str) -> str:
        """
        Process voice command and return response
        
        Args:
            command_text: Voice command text
            
        Returns:
            Response string from personality
        """
        self.state = AssistantState.PROCESSING
        self.context.last_command = command_text
        
        # Execute command
        result = self.command_registry.execute(command_text)
        
        self.commands_executed += 1
        self.state = AssistantState.ACTIVE
        
        if result:
            # Command found and executed
            return result
        else:
            # Command not found
            return self.personality.command_not_found(command_text)
    
    def process_gesture(self, gesture_name: str) -> str:
        """
        Process gesture detection
        
        Args:
            gesture_name: Detected gesture
            
        Returns:
            Response string
        """
        self.context.last_gesture = gesture_name
        self.gestures_detected += 1
        
        return self.personality.gesture_detected(gesture_name)
    
    # ========== MODE MANAGEMENT ==========
    
    def change_mode(self, mode: str) -> str:
        """
        Change assistant mode
        
        Args:
            mode: New mode ('gesture', 'voice')
            
        Returns:
            Response message
        """
        self.context.current_mode = mode
        return self.personality.mode_changed(mode)
    
    def toggle_mouse(self, enabled: bool) -> str:
        """Toggle mouse control"""
        self.context.mouse_enabled = enabled
        return self.personality.mouse_toggled(enabled)
    
    def set_voice_active(self, active: bool) -> str:
        """Set voice listening state"""
        self.context.voice_active = active
        
        if active:
            return self.personality.continuous_voice_activated()
        else:
            return self.personality.continuous_voice_deactivated()
    
    # ========== TRACKING STATUS ==========
    
    def update_tracking_status(self, is_tracking: bool) -> str:
        """Update hand tracking status"""
        self.context.tracking_active = is_tracking
        return self.personality.tracking_status(is_tracking)
    
    def report_tracking_lost(self) -> str:
        """Report tracking was lost"""
        return self.personality.tracking_lost_warning()
    
    # ========== ERROR HANDLING ==========
    
    def handle_error(self, error_type: str, error_msg: str = "") -> str:
        """
        Handle error and provide appropriate response
        
        Args:
            error_type: Type of error
            error_msg: Detailed error message
            
        Returns:
            User-friendly error message
        """
        self.errors_count += 1
        self.state = AssistantState.ERROR
        
        response = self.personality.system_error(error_type)
        
        # Log error if verbose
        if self.verbose and error_msg:
            print(f"[AVA ERROR] {error_type}: {error_msg}")
        
        # Return to active state
        self.state = AssistantState.ACTIVE
        
        return response
    
    # ========== INFORMATION REQUESTS ==========
    
    def get_time(self) -> str:
        """Get current time"""
        return self.personality.get_time_response()
    
    def get_date(self) -> str:
        """Get current date"""
        return self.personality.get_date_response()
    
    def get_tip(self) -> str:
        """Get a helpful tip"""
        return self.personality.tip_of_the_day()
    
    # ========== SYSTEM STATUS ==========
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        return {
            "assistant_name": self.personality.assistant_name,
            "state": self.state.value,
            "mode": self.context.current_mode,
            "mouse_enabled": self.context.mouse_enabled,
            "voice_active": self.context.voice_active,
            "tracking_active": self.context.tracking_active,
            "commands_executed": self.commands_executed,
            "gestures_detected": self.gestures_detected,
            "errors": self.errors_count,
            "session_duration": (datetime.now() - self.context.session_start).seconds,
            "last_command": self.context.last_command,
            "last_gesture": self.context.last_gesture
        }
    
    def get_statistics(self) -> str:
        """Get formatted statistics"""
        stats = self.get_status_report()
        
        return f"""
Ava Statistics:
• State: {stats['state']}
• Mode: {stats['mode']}
• Commands: {stats['commands_executed']}
• Gestures: {stats['gestures_detected']}
• Session: {stats['session_duration']}s
• Errors: {stats['errors']}
        """.strip()
    
    # ========== COMMAND MANAGEMENT ==========
    
    def register_custom_command(self, name: str, aliases: list, 
                                category: CommandCategory, handler: Callable, 
                                description: str):
        """Register a custom command"""
        from .command_registry import Command
        
        command = Command(
            name=name,
            aliases=aliases,
            category=category,
            handler=handler,
            description=description
        )
        
        self.command_registry.register(command)
    
    def list_available_commands(self) -> str:
        """List all available commands"""
        return self.command_registry._list_commands()
    
    def search_commands(self, query: str) -> list:
        """Search for commands"""
        return self.command_registry.search_commands(query)
    
    # ========== CALLBACK SYSTEM ==========
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for specific events"""
        self.callbacks[event] = callback
    
    def trigger_callback(self, event: str, *args, **kwargs):
        """Trigger registered callback"""
        if event in self.callbacks:
            self.callbacks[event](*args, **kwargs)
    
    # ========== VOICE INTERACTION ==========
    
    def start_listening(self) -> str:
        """Start voice listening"""
        self.state = AssistantState.LISTENING
        return self.personality.listening()
    
    def voice_not_understood(self) -> str:
        """Voice input not understood"""
        return self.personality.voice_not_understood()
    
    # ========== UTILITY METHODS ==========
    
    def reset(self) -> str:
        """Reset assistant to initial state"""
        self.commands_executed = 0
        self.gestures_detected = 0
        self.errors_count = 0
        self.context.last_command = None
        self.context.last_gesture = None
        
        return self.personality.system_reset()
    
    def get_personality_trait(self, trait: str) -> str:
        """Get personality trait"""
        traits = {
            "name": self.personality.assistant_name,
            "tone": self.personality.tone,
            "intro": self.personality.introduce_self()
        }
        return traits.get(trait, "")
    
    # ========== SMART RESPONSES ==========
    
    def generate_response(self, context: str, success: bool = True) -> str:
        """Generate contextual response"""
        return self.personality.custom_response(context, success)
    
    def respond_to_greeting(self) -> str:
        """Respond to user greeting"""
        greetings = [
            "Hello! How can I help you?",
            "Hi there! Ready to assist.",
            "Hey! What can I do for you?",
            "Greetings! Ava at your service."
        ]
        import random
        return random.choice(greetings)
    
    # ========== DECISION MAKING ==========
    
    def should_process_command(self, command: str) -> bool:
        """Decide if command should be processed"""
        # Check if in correct state
        if self.state not in [AssistantState.READY, AssistantState.ACTIVE]:
            return False
        
        # Check if voice is active when needed
        if not self.context.voice_active and self.context.current_mode == "voice":
            return False
        
        return True
    
    def get_recommended_action(self) -> Optional[str]:
        """Get recommended action based on context"""
        # If tracking lost for too long
        if not self.context.tracking_active and self.context.current_mode == "gesture":
            return "tracking_help"
        
        # If no recent activity
        if self.commands_executed == 0 and self.gestures_detected == 0:
            return "first_run_tutorial"
        
        return None


# ========== FACTORY FUNCTION ==========

def create_assistant(name: str = "Ava") -> AvaCore:
    """Create Ava assistant instance"""
    return AvaCore(assistant_name=name)