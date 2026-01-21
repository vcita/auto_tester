"""
Event system for the test runner.

Provides an event-based architecture that allows consumers (CLI, GUI, API)
to subscribe to runner events for real-time updates.
"""

from enum import Enum
from typing import Callable, Dict, Any, List
import threading


class RunnerEvent(Enum):
    """Events emitted by the test runner."""
    
    # Run lifecycle
    RUN_STARTED = "run_started"
    """Emitted when a run starts. Data: {categories: List[str], total_tests: int}"""
    
    RUN_COMPLETED = "run_completed"
    """Emitted when a run completes. Data: {result: RunResult}"""
    
    # Category lifecycle
    CATEGORY_STARTED = "category_started"
    """Emitted when a category starts. Data: {category: str, tests: List[str], index: int, total: int}"""
    
    CATEGORY_COMPLETED = "category_completed"
    """Emitted when a category completes. Data: {category: str, result: CategoryResult}"""
    
    # Browser lifecycle
    BROWSER_STARTING = "browser_starting"
    """Emitted when browser is starting. Data: {category: str}"""
    
    BROWSER_STARTED = "browser_started"
    """Emitted when browser has started. Data: {category: str}"""
    
    BROWSER_CLOSING = "browser_closing"
    """Emitted when browser is closing. Data: {category: str}"""
    
    # Test lifecycle
    TEST_STARTED = "test_started"
    """Emitted when a test starts. Data: {test: str, test_type: str, index: int, total: int}"""
    
    TEST_PROGRESS = "test_progress"
    """Emitted during test execution. Data: {test: str, message: str}"""
    
    TEST_COMPLETED = "test_completed"
    """Emitted when a test completes. Data: {test: str, result: TestResult}"""
    
    # Errors and healing
    TEST_FAILED = "test_failed"
    """Emitted when a test fails. Data: {test: str, error: str, error_type: str}"""
    
    HEAL_REQUEST_CREATED = "heal_request_created"
    """Emitted when a heal request is created. Data: {test: str, path: str}"""
    
    # Context updates
    CONTEXT_UPDATED = "context_updated"
    """Emitted when context is modified. Data: {key: str, value: Any}"""


class EventEmitter:
    """
    Thread-safe event emitter for the test runner.
    
    Allows multiple consumers to subscribe to events and receive
    real-time updates during test execution.
    
    Usage:
        emitter = EventEmitter()
        
        # Subscribe to events
        emitter.on(RunnerEvent.TEST_STARTED, lambda data: print(f"Started: {data['test']}"))
        
        # Emit events
        emitter.emit(RunnerEvent.TEST_STARTED, {"test": "create_matter"})
    """
    
    def __init__(self):
        self._listeners: Dict[RunnerEvent, List[Callable[[Dict[str, Any]], None]]] = {}
        self._lock = threading.Lock()
    
    def on(self, event: RunnerEvent, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to an event.
        
        Args:
            event: The event type to subscribe to
            callback: Function to call when event is emitted. Receives event data dict.
        """
        with self._lock:
            if event not in self._listeners:
                self._listeners[event] = []
            self._listeners[event].append(callback)
    
    def off(self, event: RunnerEvent, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Unsubscribe from an event.
        
        Args:
            event: The event type to unsubscribe from
            callback: The callback function to remove
        """
        with self._lock:
            if event in self._listeners:
                try:
                    self._listeners[event].remove(callback)
                except ValueError:
                    pass  # Callback not found, ignore
    
    def emit(self, event: RunnerEvent, data: Dict[str, Any]) -> None:
        """
        Emit an event to all subscribers.
        
        Args:
            event: The event type to emit
            data: Event data to pass to subscribers
        """
        with self._lock:
            listeners = self._listeners.get(event, []).copy()
        
        # Call listeners outside the lock to prevent deadlocks
        for callback in listeners:
            try:
                callback(data)
            except Exception as e:
                # Don't let a failing listener break the runner
                print(f"Warning: Event listener error for {event.value}: {e}")
    
    def clear(self, event: RunnerEvent = None) -> None:
        """
        Clear event listeners.
        
        Args:
            event: Specific event to clear, or None to clear all
        """
        with self._lock:
            if event is None:
                self._listeners.clear()
            elif event in self._listeners:
                self._listeners[event].clear()
    
    def listener_count(self, event: RunnerEvent) -> int:
        """Get the number of listeners for an event."""
        with self._lock:
            return len(self._listeners.get(event, []))
