"""
Context management for the test runner.

The context is a shared dictionary that tests use to pass data between them.
For example, create_matter saves the matter_id, and delete_matter reads it.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import copy


class ContextManager:
    """
    Manages the shared context dictionary for test runs.
    
    The context allows tests to share data:
    - create_matter saves: context["created_matter_id"] = "abc123"
    - delete_matter reads: matter_id = context["created_matter_id"]
    
    Context is:
    - Fresh for each category run (by default)
    - Optionally persisted to .context/current_run.json for debugging
    - Cleared between runs
    """
    
    def __init__(self, context_dir: Optional[Path] = None):
        """
        Initialize the context manager.
        
        Args:
            context_dir: Directory to store context files. 
                        Defaults to .context/ in current directory.
        """
        self.context_dir = context_dir or Path(".context")
        self._context: Dict[str, Any] = {}
        self._history: list = []  # Track context changes for debugging
    
    def create_fresh(self) -> Dict[str, Any]:
        """
        Create a fresh context dictionary.
        
        Returns:
            New empty context dict with metadata
        """
        self._context = {
            "_meta": {
                "created_at": datetime.now().isoformat(),
                "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            }
        }
        self._history = []
        return self._context
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current context dictionary.
        
        Returns:
            Current context dict (creates fresh if none exists)
        """
        if not self._context:
            return self.create_fresh()
        return self._context
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the context.
        
        Args:
            key: Context key
            value: Value to store
        """
        if not self._context:
            self.create_fresh()
        
        old_value = self._context.get(key)
        self._context[key] = value
        
        # Track change for debugging
        self._history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "set",
            "key": key,
            "old_value": old_value,
            "new_value": value,
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the context.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Value from context or default
        """
        return self._context.get(key, default)
    
    def delete(self, key: str) -> None:
        """
        Delete a key from the context.
        
        Args:
            key: Context key to delete
        """
        if key in self._context:
            old_value = self._context.pop(key)
            self._history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "delete",
                "key": key,
                "old_value": old_value,
            })
    
    def snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of the current context (deep copy).
        
        Returns:
            Deep copy of current context
        """
        return copy.deepcopy(self._context)
    
    def save_to_file(self, filename: str = "current_run.json") -> Path:
        """
        Save the current context to a JSON file.
        
        Args:
            filename: Name of the file to save to
            
        Returns:
            Path to the saved file
        """
        self.context_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.context_dir / filename
        
        data = {
            "context": self._context,
            "history": self._history,
            "saved_at": datetime.now().isoformat(),
        }
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        return file_path
    
    def load_from_file(self, filename: str = "current_run.json") -> Dict[str, Any]:
        """
        Load context from a JSON file.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Loaded context dict
        """
        file_path = self.context_dir / filename
        
        if not file_path.exists():
            return self.create_fresh()
        
        with open(file_path, "r") as f:
            data = json.load(f)
        
        self._context = data.get("context", {})
        self._history = data.get("history", [])
        
        return self._context
    
    def clear(self) -> None:
        """Clear the context and history."""
        self._context = {}
        self._history = []
    
    def get_history(self) -> list:
        """
        Get the history of context changes.
        
        Returns:
            List of context change records
        """
        return self._history.copy()
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the context."""
        return key in self._context
    
    def __getitem__(self, key: str) -> Any:
        """Get a value using dict-like access."""
        return self._context[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value using dict-like access."""
        self.set(key, value)
