import os
import psutil

def get_storage_type(path):
    """Determine if a path is on internal storage or external drive."""
    try:
        # Get the drive letter from the path
        drive = os.path.splitdrive(path)[0]
        if not drive:
            return 'unknown'
        
        # Get all disk partitions
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            if partition.device.startswith(drive):
                # Check if it's a removable drive
                if 'removable' in partition.opts:
                    return 'external'
                # Check if it's a network drive
                elif partition.fstype in ['cifs', 'nfs', 'smb']:
                    return 'network'
                # Check if it's a CD/DVD
                elif partition.fstype == 'cdfs':
                    return 'optical'
                else:
                    return 'internal'
        
        return 'unknown'
    except Exception:
        return 'unknown'

def is_system_drive(path):
    """Check if the path is on the system drive (usually C:)."""
    try:
        drive = os.path.splitdrive(path)[0].upper()
        system_drive = os.path.splitdrive(os.environ.get('SystemRoot', 'C:'))[0].upper()
        return drive == system_drive
    except Exception:
        return False