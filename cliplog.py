import time
import atexit
from utils.clipboard_utils import get_clipboard_content
from utils.logger import log_text_entry, log_files_entry, log_paste_entry
from utils.file_monitor import FileMonitor

def main():
    last_clipboard = None
    print("Clipboard logger started. Press Ctrl+C to stop.")
    
    # Initialize file monitor
    file_monitor = FileMonitor(log_paste_entry)
    file_monitor.start_monitoring()
    
    # Ensure cleanup on exit
    atexit.register(file_monitor.stop_monitoring)
    
    try:
        while True:
            ctype, content = get_clipboard_content()
            
            if content != last_clipboard:
                if ctype == 'text':
                    log_text_entry(content)
                elif ctype == 'files':
                    log_files_entry(content)
                    # Update file monitor with copied files
                    file_monitor.set_copied_files(content)
                
                last_clipboard = content
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nClipboard logger stopped.")
    finally:
        file_monitor.stop_monitoring()

if __name__ == "__main__":
    main()