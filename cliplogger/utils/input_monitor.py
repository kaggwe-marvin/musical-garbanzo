import time
import threading
import os
import win32gui
import win32con
from pynput import mouse, keyboard
from pynput.mouse import Button
from .file_utils import get_file_info
from .storage_utils import get_storage_type
from .logger import log_paste_entry, log_drag_drop_entry


class InputMonitor:
    def __init__(self, callback=None):
        self.callback = callback or self._default_callback
        self.mouse_listener = None
        self.keyboard_listener = None
        self.is_running = False

        # State tracking
        self.mouse_pressed = False
        self.drag_start_pos = None
        self.drag_start_time = None
        self.drag_start_window = None
        self.drag_start_path = None
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False

        # Drag and drop detection
        self.drag_threshold = 10  # pixels
        self.drag_time_threshold = 0.5  # seconds
        self.potential_drag = False

    def _default_callback(self, event_type, data):
        """Default callback for input events."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {event_type}: {data}")

    def _get_window_path(self, x, y):
        """Get the file path or window title at the given coordinates."""
        try:
            hwnd = win32gui.WindowFromPoint((x, y))
            window_title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)

            # Check if it's a file explorer window
            if class_name in ["CabinetWClass", "ExploreWClass"]:
                # Try to get the current folder path from explorer
                return self._get_explorer_path(hwnd)

            # For other windows, return the window title
            return window_title if window_title else f"Window:{class_name}"

        except Exception as e:
            return f"Unknown location ({x}, {y})"

    def _get_explorer_path(self, hwnd):
        """Get the current folder path from Windows Explorer."""
        try:
            # This is a simplified approach - in practice you might need
            # to use Shell interfaces for more accurate path detection
            window_title = win32gui.GetWindowText(hwnd)

            # Parse common Explorer window title patterns
            if " - " in window_title:
                parts = window_title.split(" - ")
                if len(parts) > 1:
                    potential_path = parts[0]
                    # Check if it looks like a valid path
                    if os.path.exists(potential_path):
                        return potential_path

            # Fallback to window title
            return window_title

        except Exception:
            return "Explorer Window"

    def start_monitoring(self):
        """Start monitoring mouse and keyboard input."""
        if self.is_running:
            return

        self.is_running = True
        print("Starting input monitoring...")

        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move,
            on_scroll=self._on_mouse_scroll,
        )

        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press, on_release=self._on_key_release
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()

        print("Input monitoring started")

    def stop_monitoring(self):
        """Stop monitoring input."""
        if not self.is_running:
            return

        self.is_running = False
        print("Stopping input monitoring...")

        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        print("Input monitoring stopped")

    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if button == Button.left:
            if pressed:
                self.mouse_pressed = True
                self.drag_start_pos = (x, y)
                self.drag_start_time = time.time()
                self.drag_start_path = self._get_window_path(x, y)
                self.potential_drag = True
            else:
                self.mouse_pressed = False
                if self.potential_drag:
                    self._handle_potential_drop(x, y)
                self.potential_drag = False

        # Log mouse events with modifier keys
        modifiers = self._get_current_modifiers()
        event_data = {
            "position": (x, y),
            "button": button.name,
            "pressed": pressed,
            "modifiers": modifiers,
            "location": self._get_window_path(x, y),
        }

        if pressed and modifiers:
            self.callback("MOUSE_CLICK_WITH_MODIFIERS", event_data)

    def _on_mouse_move(self, x, y):
        """Handle mouse movement."""
        if self.mouse_pressed and self.potential_drag and self.drag_start_pos:
            # Calculate distance from drag start
            dx = x - self.drag_start_pos[0]
            dy = y - self.drag_start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5

            # Check if movement exceeds threshold
            if distance > self.drag_threshold:
                elapsed_time = time.time() - self.drag_start_time
                if elapsed_time > self.drag_time_threshold:
                    self._handle_drag_start(x, y)

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events."""
        modifiers = self._get_current_modifiers()
        if modifiers:
            event_data = {
                "position": (x, y),
                "scroll": (dx, dy),
                "modifiers": modifiers,
                "location": self._get_window_path(x, y),
            }
            self.callback("MOUSE_SCROLL_WITH_MODIFIERS", event_data)

    def _on_key_press(self, key):
        """Handle key press events."""
        try:
            # Track modifier keys
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self.shift_pressed = True
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = True

            # Detect common shortcuts
            if self.ctrl_pressed:
                if hasattr(key, "char"):
                    if key.char == "c":
                        self.callback("KEYBOARD_SHORTCUT", "Ctrl+C (Copy)")
                    elif key.char == "x":
                        self.callback("KEYBOARD_SHORTCUT", "Ctrl+X (Cut)")
                    elif key.char == "v":
                        self.callback("KEYBOARD_SHORTCUT", "Ctrl+V (Paste)")
                    elif key.char == "z":
                        self.callback("KEYBOARD_SHORTCUT", "Ctrl+Z (Undo)")
                    elif key.char == "y":
                        self.callback("KEYBOARD_SHORTCUT", "Ctrl+Y (Redo)")
                    elif key.char == "a":
                        self.callback("KEYBOARD_SHORTCUT", "Ctrl+A (Select All)")

            # Detect F5 (refresh)
            if key == keyboard.Key.f5:
                self.callback("KEYBOARD_SHORTCUT", "F5 (Refresh)")

            # Detect Delete key
            if key == keyboard.Key.delete:
                self.callback("KEYBOARD_SHORTCUT", "Delete")

        except AttributeError:
            pass

    def _on_key_release(self, key):
        """Handle key release events."""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self.shift_pressed = False
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = False
        except AttributeError:
            pass

    def _get_current_modifiers(self):
        """Get currently pressed modifier keys."""
        modifiers = []
        if self.ctrl_pressed:
            modifiers.append("Ctrl")
        if self.shift_pressed:
            modifiers.append("Shift")
        if self.alt_pressed:
            modifiers.append("Alt")
        return modifiers

    def _handle_drag_start(self, x, y):
        """Handle the start of a drag operation."""
        event_data = {
            "start_pos": self.drag_start_pos,
            "current_pos": (x, y),
            "start_path": self.drag_start_path,
            "current_path": self._get_window_path(x, y),
            "modifiers": self._get_current_modifiers(),
        }
        self.callback("DRAG_START", event_data)
        self.potential_drag = False  # Prevent multiple drag start events

    def _handle_potential_drop(self, x, y):
        """Handle potential drop operation."""
        if self.drag_start_pos:
            dx = x - self.drag_start_pos[0]
            dy = y - self.drag_start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5

            if distance > self.drag_threshold:
                drop_path = self._get_window_path(x, y)

                # Log the drag and drop operation
                log_drag_drop_entry(
                    source_path=self.drag_start_path,
                    dest_path=drop_path,
                    operation="DRAG_DROP",
                )

                event_data = {
                    "start_pos": self.drag_start_pos,
                    "end_pos": (x, y),
                    "distance": distance,
                    "start_path": self.drag_start_path,
                    "end_path": drop_path,
                    "modifiers": self._get_current_modifiers(),
                }
                self.callback("DRAG_DROP", event_data)
