"""
Sound Service for notification sounds
"""

from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

class SoundService:
    
    # Available sound types
    SOUND_TYPES = {
        "chime": {
            "file": "/sounds/chime.mp3",
            "description": "Soft chime",
            "priority_levels": ["low", "medium"]
        },
        "bell": {
            "file": "/sounds/bell.mp3",
            "description": "Traditional bell",
            "priority_levels": ["medium", "high"]
        },
        "alert": {
            "file": "/sounds/alert.mp3",
            "description": "Attention-grabbing alert",
            "priority_levels": ["high", "urgent"]
        },
        "digital": {
            "file": "/sounds/digital.mp3",
            "description": "Digital notification sound",
            "priority_levels": ["low", "medium", "high"]
        },
        "none": {
            "file": None,
            "description": "No sound",
            "priority_levels": []
        }
    }
    
    def should_play_sound(self, settings, priority: str) -> bool:
        """Determine if a sound should play based on settings and DND"""
        if not settings.sound_enabled:
            return False
        
        # Check Do Not Disturb
        if settings.dnd_enabled:
            current_time = datetime.now().time()
            
            # Parse DND times
            start = datetime.strptime(settings.dnd_start, "%H:%M").time()
            end = datetime.strptime(settings.dnd_end, "%H:%M").time()
            
            # Handle overnight DND (e.g., 22:00 to 08:00)
            if start < end:
                # Same day range
                in_dnd = start <= current_time <= end
            else:
                # Overnight range
                in_dnd = current_time >= start or current_time <= end
            
            if in_dnd:
                # Check if this priority should still play
                priority_levels = ["low", "medium", "high", "urgent"]
                threshold_idx = priority_levels.index(settings.dnd_priority_threshold)
                current_idx = priority_levels.index(priority)
                
                return current_idx >= threshold_idx
        
        return True
    
    def get_sound_file(self, sound_type: str, priority: str) -> str:
        """Get the appropriate sound file for notification type and priority"""
        sound_config = self.SOUND_TYPES.get(sound_type, self.SOUND_TYPES["chime"])
        
        # Check if this priority is allowed for this sound type
        if priority not in sound_config["priority_levels"]:
            # Fallback to appropriate sound
            if priority in ["high", "urgent"]:
                return self.SOUND_TYPES["alert"]["file"]
            elif priority == "medium":
                return self.SOUND_TYPES["bell"]["file"]
            else:
                return self.SOUND_TYPES["chime"]["file"]
        
        return sound_config["file"]
    
    def format_time_for_display(self, time_str: str) -> str:
        """Format time string for display"""
        try:
            t = datetime.strptime(time_str, "%H:%M")
            return t.strftime("%I:%M %p")
        except:
            return time_str
