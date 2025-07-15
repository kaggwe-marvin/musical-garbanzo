import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .storage_utils import get_storage_type, get_all_drives

class PasteDetector(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.recent_copies = {}  # Changed to dict to store full paths
        self.lock = threading.Lock()
    
    def set_copied_files(self, files):
        """Set the list of recently copied files."""
        with self.lock:
            self.recent_copies = {os.path.basename(f): f for f in files}
            print(f"Tracking copied files: {list(self.recent_copies.keys())}")
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self._handle_file_event(event.src_path, 'paste')
    
    def on_moved(self, event):
        """Handle file move events (cut/paste)."""
        if not event.is_directory:
            self._handle_file_event(event.dest_path, 'move')
    
    def _handle_file_event(self, file_path, operation):
        """Handle file creation/move events."""
        with self.lock:
            filename = os.path.basename(file_path)
            if filename in self.recent_copies:
                original_path = self.recent_copies[filename]
                
                # Check if this is actually a paste (different location)
                if os.path.dirname(file_path) != os.path.dirname(original_path):
                    storage_type = get_storage_type(file_path)
                    print(f"Detected {operation}: {filename} -> {file_path} ({storage_type})")
                    self.callback(file_path, storage_type, operation)
                    
                    # Remove from tracking after successful paste
                    del self.recent_copies[filename]

class FileMonitor:
    def __init__(self, callback):
        self.observers = []
        self.paste_detector = PasteDetector(callback)
        self.monitored_drives = set()
    
    def start_monitoring(self):
        """Start monitoring all available drives."""
        print("Starting file system monitoring...")
        
        # Get all available drives with their types
        drives = get_all_drives()
        
        for drive_info in drives:
            drive = drive_info['drive']
            drive_type = drive_info['type']
            
            if drive not in self.monitored_drives:
                try:
                    observer = Observer()
                    observer.schedule(self.paste_detector, drive, recursive=True)
                    observer.start()
                    self.observers.append(observer)
                    self.monitored_drives.add(drive)
                    print(f"Monitoring {drive} ({drive_type})")
                except Exception as e:
                    print(f"Could not monitor {drive}: {e}")
        
        print(f"Monitoring {len(self.observers)} drives")
    
    def set_copied_files(self, files):
        """Update the list of copied files."""
        self.paste_detector.set_copied_files(files)
    
    def stop_monitoring(self):
        """Stop all file monitoring."""
        print("Stopping file system monitoring...")
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers.clear()
        self.monitored_drives.clear()