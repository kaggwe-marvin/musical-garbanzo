import os
import psutil
import win32api
import win32file

def get_storage_type(path):
    """Determine if a path is on internal storage or external drive."""
    try:
        # Get the drive letter from the path
        drive = os.path.splitdrive(path)[0]
        if not drive:
            return 'unknown'
        
        # Ensure drive has backslash
        if not drive.endswith('\\'):
            drive += '\\'
        
        # Use Windows API to get drive type
        drive_type = win32file.GetDriveType(drive)
        
        if drive_type == win32file.DRIVE_REMOVABLE:
            return 'external'
        elif drive_type == win32file.DRIVE_FIXED:
            # Could be internal or external SSD/HDD
            # Check if it's a USB drive using additional methods
            if is_usb_drive(drive):
                return 'external'
            return 'internal'
        elif drive_type == win32file.DRIVE_REMOTE:
            return 'network'
        elif drive_type == win32file.DRIVE_CDROM:
            return 'optical'
        elif drive_type == win32file.DRIVE_RAMDISK:
            return 'ramdisk'
        else:
            return 'unknown'
            
    except Exception as e:
        print(f"Error detecting storage type for {path}: {e}")
        return 'unknown'

def is_usb_drive(drive):
    """Check if a drive is a USB drive using psutil."""
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if partition.device.upper() == drive.upper():
                # Check partition options for removable flag
                if 'removable' in partition.opts.lower():
                    return True
                # Additional check for USB drives that might not be marked as removable
                if partition.fstype in ['FAT32', 'exFAT', 'NTFS']:
                    # Use WMI to check if it's a USB device
                    return check_usb_via_wmi(drive)
        return False
    except Exception:
        return False

def check_usb_via_wmi(drive):
    """Use WMI to check if a drive is connected via USB."""
    try:
        import wmi
        c = wmi.WMI()
        
        # Remove backslash for WMI query
        drive_letter = drive.replace('\\', '')
        
        # Query logical disk
        for disk in c.Win32_LogicalDisk():
            if disk.DeviceID == drive_letter:
                # Get associated physical disk
                for partition in c.Win32_LogicalDiskToPartition():
                    if partition.Dependent.DeviceID == drive_letter:
                        disk_drive = partition.Antecedent
                        # Check if it's a USB device
                        for physical_disk in c.Win32_DiskDrive():
                            if physical_disk.DeviceID in disk_drive:
                                if 'usb' in physical_disk.InterfaceType.lower():
                                    return True
        return False
    except ImportError:
        # WMI not available, fallback to basic check
        return False
    except Exception:
        return False

def is_system_drive(path):
    """Check if the path is on the system drive (usually C:)."""
    try:
        drive = os.path.splitdrive(path)[0].upper()
        system_drive = os.path.splitdrive(os.environ.get('SystemRoot', 'C:'))[0].upper()
        return drive == system_drive
    except Exception:
        return False

def get_all_drives():
    """Get all available drives with their types."""
    drives = []
    try:
        # Get all logical drives
        drive_bits = win32api.GetLogicalDrives()
        for i in range(26):
            if drive_bits & (1 << i):
                drive = f"{chr(65 + i)}:\\"
                if os.path.exists(drive):
                    storage_type = get_storage_type(drive)
                    drives.append({
                        'drive': drive,
                        'type': storage_type
                    })
    except Exception as e:
        print(f"Error getting drives: {e}")
    
    return drives