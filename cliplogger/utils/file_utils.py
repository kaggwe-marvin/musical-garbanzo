import os

def get_file_category(extension):
    """Categorize files based on their extension."""
    # Convert to lowercase for case-insensitive matching
    ext = extension.lower()
    
    # Define categories
    categories = {
        'document': ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt', '.pages'],
        'spreadsheet': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
        'presentation': ['.ppt', '.pptx', '.key', '.odp'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico'],
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
        'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.swift'],
        'executable': ['.exe', '.msi', '.app', '.deb', '.rpm', '.dmg'],
        'data': ['.json', '.xml', '.yaml', '.yml', '.sql', '.db', '.sqlite'],
        'font': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
        'config': ['.ini', '.cfg', '.conf', '.config', '.properties', '.env']
    }
    
    # Find the category for the extension
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    
    # Return 'other' if no category matches
    return 'other'

def get_file_info(file_path):
    """Get file information including extension, drive, and category."""
    ext = os.path.splitext(file_path)[1]
    drive = os.path.splitdrive(file_path)[0]
    
    if os.path.isdir(file_path):
        ftype = "FOLDER"
        category = "folder"
    else:
        ftype = "FILE"
        category = get_file_category(ext)
    
    return {
        'type': ftype,
        'extension': ext,
        'category': category,
        'drive': drive
    }