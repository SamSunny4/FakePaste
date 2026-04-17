"""
FakePaste - Global Hotkey Manager
Handles system-wide hotkeys for emergency stop and other controls.
"""

import threading
from typing import Callable, Optional
from pynput import keyboard


class HotkeyManager:
    """Manages global hotkeys using pynput listener."""

    def __init__(self):
        self._listener: Optional[keyboard.Listener] = None
        self._callbacks = {}
        self._running = False

    def register(self, key_name: str, callback: Callable):
        """
        Register a callback for a key.
        key_name: 'esc', 'f1', 'f2', etc.
        """
        self._callbacks[key_name.lower()] = callback

    def unregister(self, key_name: str):
        """Unregister a hotkey callback."""
        self._callbacks.pop(key_name.lower(), None)

    def start(self):
        """Start listening for global hotkeys."""
        if self._running:
            return
        self._running = True
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        """Stop listening for global hotkeys."""
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key):
        """Handle key press events."""
        try:
            # Check for special keys
            if isinstance(key, keyboard.Key):
                key_name = key.name.lower()
            else:
                key_name = key.char.lower() if key.char else None

            if key_name and key_name in self._callbacks:
                # Run callback in separate thread to avoid blocking listener
                callback = self._callbacks[key_name]
                threading.Thread(target=callback, daemon=True).start()
        except (AttributeError, TypeError):
            pass

    def __del__(self):
        self.stop()
