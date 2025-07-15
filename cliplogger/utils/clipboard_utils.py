import win32clipboard
import win32con

def get_clipboard_content():
    """Get clipboard content and determine its type."""
    win32clipboard.OpenClipboard()
    try:
        # Check for file list
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            return 'files', list(files)
        # Check for text
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            return 'text', text
        else:
            return 'unknown', None
    finally:
        win32clipboard.CloseClipboard()