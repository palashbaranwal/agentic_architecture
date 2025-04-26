from mcp.types import TextContent
from typing import List, Dict, Any, Optional
import json
import os
import time

class Memory:
    """Component responsible for storing and retrieving information."""
    
    def __init__(self, storage_path: str = "agent_memory.json"):
        self.storage_path = storage_path
        self.calculation_history = []
        self.error_patterns = {}
        self.user_preferences = {}
        self.paint_state = None
        self.load_memory()
    
    def load_memory(self):
        """Load memory from storage if it exists."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.calculation_history = data.get('calculation_history', [])
                    self.error_patterns = data.get('error_patterns', {})
                    self.user_preferences = data.get('user_preferences', {})
            except Exception as e:
                print(f"Error loading memory: {e}")
    
    def save_memory(self):
        """Save memory to storage."""
        try:
            data = {
                'calculation_history': self.calculation_history,
                'error_patterns': self.error_patterns,
                'user_preferences': self.user_preferences
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_calculation(self, expression: str, result: Any, steps: List[str] = None):
        """Add a calculation to history."""
        self.calculation_history.append({
            'timestamp': time.time(),
            'expression': expression,
            'result': result,
            'steps': steps or []
        })
        self.save_memory()
    
    def get_calculation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent calculation history."""
        return self.calculation_history[-limit:] if self.calculation_history else []
    
    def add_error_pattern(self, error_type: str, error_message: str, resolution: str):
        """Add an error pattern and its resolution."""
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = []
        
        self.error_patterns[error_type].append({
            'message': error_message,
            'resolution': resolution,
            'timestamp': time.time()
        })
        self.save_memory()
    
    def get_error_resolution(self, error_type: str, error_message: str) -> Optional[str]:
        """Get resolution for a specific error if available."""
        if error_type in self.error_patterns:
            for pattern in self.error_patterns[error_type]:
                if pattern['message'] in error_message:
                    return pattern['resolution']
        return None
    
    def set_user_preference(self, key: str, value: Any):
        """Set a user preference."""
        self.user_preferences[key] = value
        self.save_memory()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self.user_preferences.get(key, default)
    
    def set_paint_state(self, state: Dict[str, Any]):
        """Set the current state of the Paint application."""
        self.paint_state = state
    
    def get_paint_state(self) -> Optional[Dict[str, Any]]:
        """Get the current state of the Paint application."""
        return self.paint_state
    
    def store_steps(self, steps: List[str]):
        """Store calculation steps for consistency checking."""
        self.current_steps = steps
    
    def get_steps(self) -> List[str]:
        """Get stored calculation steps."""
        return getattr(self, 'current_steps', [])
    
    def clear_steps(self):
        """Clear stored calculation steps."""
        if hasattr(self, 'current_steps'):
            delattr(self, 'current_steps') 