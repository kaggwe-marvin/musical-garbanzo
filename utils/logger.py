import time
import os
from .file_utils import get_file_info
from .storage_utils import get_storage_type, is_system_drive

def log_text_entry(content, log_file="clipboard_log.txt"):
    """Log text clipboard content."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] TEXT: {content}"
    print(log_entry)
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def log_file_entry(file_path, log_file="clipboard_log.txt"):
    """Log file clipboard content."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    file_info = get_file_info(file_path)
    storage_type = get_storage_type(file_path)
    
    log_entry = f"[{timestamp}] {file_info['type']}: {file_path} (ext: {file_info['extension']}) (category: {file_info['category']}) (from: {file_info['drive']} - {storage_type})"
    print(log_entry)
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def log_files_entry(files, log_file="clipboard_log.txt"):
    """Log multiple files clipboard content."""
    for file_path in files:
        log_file_entry(file_path, log_file)

def log_paste_entry(dest_path, storage_type, operation, log_file="clipboard_log.txt"):
    """Log file paste operations."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    file_info = get_file_info(dest_path)
    drive = os.path.splitdrive(dest_path)[0]
    
    operation_text = "PASTED" if operation == 'paste' else "MOVED"
    log_entry = f"[{timestamp}] {operation_text}: {dest_path} (ext: {file_info['extension']}) (category: {file_info['category']}) (to: {drive} - {storage_type})"
    print(log_entry)
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")