import time
import atexit
from utils.clipboard_utils import get_clipboard_content
from utils.logger import log_text_entry, log_files_entry, log_paste_entry
from utils.file_monitor import FileMonitor
from utils.input_monitor import InputMonitor


def handle_input_event(event_type, data):
    """Handle input events from mouse and keyboard."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if event_type == "KEYBOARD_SHORTCUT":
        print(f"[{timestamp}] SHORTCUT: {data}")
        # Log to file
        with open("clipboard_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] SHORTCUT: {data}\n")

    elif event_type == "DRAG_START":
        print(
            f"[{timestamp}] DRAG_START: from {data['start_path']} at {data['start_pos']} to {data['current_path']} at {data['current_pos']}"
        )
        if data["modifiers"]:
            print(f"  Modifiers: {', '.join(data['modifiers'])}")

        # Log to file
        with open("clipboard_log.txt", "a", encoding="utf-8") as f:
            f.write(
                f"[{timestamp}] DRAG_START: from {data['start_path']} at {data['start_pos']} to {data['current_path']} at {data['current_pos']}\n"
            )

    elif event_type == "DRAG_DROP":
        print(
            f"[{timestamp}] DRAG_DROP: from {data['start_path']} at {data['start_pos']} to {data['end_path']} at {data['end_pos']} (distance: {data['distance']:.1f}px)"
        )
        if data["modifiers"]:
            print(f"  Modifiers: {', '.join(data['modifiers'])}")

        # Log to file
        with open("clipboard_log.txt", "a", encoding="utf-8") as f:
            f.write(
                f"[{timestamp}] DRAG_DROP: from {data['start_path']} at {data['start_pos']} to {data['end_path']} at {data['end_pos']} (distance: {data['distance']:.1f}px)\n"
            )

    elif event_type == "MOUSE_CLICK_WITH_MODIFIERS":
        if data["pressed"]:  # Only log press events to avoid spam
            print(
                f"[{timestamp}] MOUSE_CLICK: {data['button']} at {data['position']} in {data['location']} with {', '.join(data['modifiers'])}"
            )
            # Log to file
            with open("clipboard_log.txt", "a", encoding="utf-8") as f:
                f.write(
                    f"[{timestamp}] MOUSE_CLICK: {data['button']} at {data['position']} in {data['location']} with {', '.join(data['modifiers'])}\n"
                )


def main():
    last_clipboard = None
    print("Clipboard logger with input monitoring started. Press Ctrl+C to stop.")

    # Initialize file monitor
    file_monitor = FileMonitor(log_paste_entry)
    file_monitor.start_monitoring()

    # Initialize input monitor
    input_monitor = InputMonitor(handle_input_event)
    input_monitor.start_monitoring()

    # Ensure cleanup on exit
    atexit.register(file_monitor.stop_monitoring)
    atexit.register(input_monitor.stop_monitoring)

    try:
        while True:
            ctype, content = get_clipboard_content()

            if content != last_clipboard:
                if ctype == "text":
                    log_text_entry(content)
                elif ctype == "files":
                    log_files_entry(content)
                    # Update file monitor with copied files
                    file_monitor.set_copied_files(content)

                last_clipboard = content

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nClipboard logger stopped.")
    finally:
        file_monitor.stop_monitoring()
        input_monitor.stop_monitoring()


if __name__ == "__main__":
    main()
