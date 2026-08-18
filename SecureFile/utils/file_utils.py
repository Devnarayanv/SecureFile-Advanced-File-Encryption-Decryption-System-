import os
import shutil
import stat
from pathlib import Path

def format_size(size_bytes: int) -> str:
    """
    Formats bytes into human-readable strings (B, KB, MB, GB, TB).
    """
    if size_bytes < 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            # Avoid decimal point for bytes
            if unit == 'B':
                return f"{int(size_bytes)} B"
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_file_permissions(file_path: str) -> tuple[str, str]:
    """
    Returns the file permissions.
    Returns: (octal_str, human_readable)
    Example: ("0644", "Read & Write")
    """
    try:
        p = Path(file_path)
        if not p.exists():
            return "N/A", "N/A"
            
        mode = p.stat().st_mode
        octal_str = oct(mode & 0o7777)[2:]
        # Pad octal string to 4 characters (e.g. 0644)
        octal_str = octal_str.zfill(4)
        
        # Determine read/write capabilities
        readable = bool(mode & stat.S_IREAD)
        writable = bool(mode & stat.S_IWRITE)
        
        if readable and writable:
            human = "Read & Write"
        elif readable:
            human = "Read-Only"
        elif writable:
            human = "Write-Only"
        else:
            human = "No Access"
            
        return octal_str, human
    except Exception:
        return "N/A", "Unknown"

def get_disk_info(path: str = ".") -> tuple[int, int, int]:
    """
    Gets storage metrics for the disk containing the specified path.
    Returns: (total_bytes, used_bytes, free_bytes)
    """
    try:
        total, used, free = shutil.disk_usage(path)
        return total, used, free
    except Exception:
        return 0, 0, 0
