import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .storage_utils import get_storage_type

class PasteDetector(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.recent_copies = set()
        self.lock = threading.Lock()
    
    def set_copied_files(self, files):
        """Set the list of recently copied files."""
        with self.lock:
            self.recent_copies = set(os.path.basename(f) for f in files)
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            with self.lock:
                filename = os.path.basename(event.src_path)
                if filename in self.recent_copies:
                    # This might be a paste operation
                    storage_type = get_storage_type(event.src_path)
                    self.callback(event.src_path, storage_type, 'paste')
    
    def on_moved(self, event):
        """Handle file move events (cut/paste)."""
        if not event.is_directory:
            with self.lock:
                filename = os.path.basename(event.dest_path)
                if filename in self.recent_copies:
                    storage_type = get_storage_type(event.dest_path)
                    self.callback(event.dest_path, storage_type, 'move')

class FileMonitor:
    def __init__(self, callback):
        self.observers = []
        self.paste_detector = PasteDetector(callback)
        self.monitored_drives = set()
    
    def start_monitoring(self):
        """Start monitoring all available drives."""
        # Get all available drives
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        
        for drive in drives:
            if drive not in self.monitored_drives:
                try:
                    observer = Observer()
                    observer.schedule(self.paste_detector, drive, recursive=True)
                    observer.start()
                    self.observers.append(observer)
                    self.monitored_drives.add(drive)
                except Exception as e:
                    print(f"Could not monitor {drive}: {e}")
    
    def set_copied_files(self, files):
        """Update the list of copied files."""
        self.paste_detector.set_copied_files(files)
    
    def stop_monitoring(self):
        """Stop all file monitoring."""
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers.clear()
        self.monitored_drives.clear()