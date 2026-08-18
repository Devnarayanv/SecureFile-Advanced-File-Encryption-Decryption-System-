import os
import sys
import psutil
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from utils.file_utils import format_size

def get_system_stats() -> dict:
    """
    Retrieves system resource metrics (CPU, RAM, Disk) and current process statistics.
    """
    stats = {
        "sys_cpu": 0.0,
        "sys_ram_percent": 0.0,
        "sys_ram_used": "0 B",
        "sys_ram_total": "0 B",
        "sys_disk_percent": 0.0,
        "sys_disk_free": "0 B",
        "sys_disk_total": "0 B",
        "proc_cpu": 0.0,
        "proc_ram": "0 B",
        "proc_threads": 1,
        "proc_handles": 0,
    }
    
    try:
        # Global CPU
        stats["sys_cpu"] = psutil.cpu_percent(interval=None)
        
        # Global RAM
        ram = psutil.virtual_memory()
        stats["sys_ram_percent"] = ram.percent
        stats["sys_ram_used"] = format_size(ram.used)
        stats["sys_ram_total"] = format_size(ram.total)
        
        # Global Disk (use drive letter where script is running)
        current_drive = Path(__file__).anchor
        disk = psutil.disk_usage(current_drive)
        stats["sys_disk_percent"] = disk.percent
        stats["sys_disk_free"] = format_size(disk.free)
        stats["sys_disk_total"] = format_size(disk.total)
        
        # Process specific metrics
        proc = psutil.Process(os.getpid())
        
        # On some OS, first call to process cpu_percent returns 0.0, which is normal
        stats["proc_cpu"] = proc.cpu_percent(interval=None)
        
        # Process RAM (Resident Set Size)
        proc_mem = proc.memory_info().rss
        stats["proc_ram"] = format_size(proc_mem)
        
        # Process threads
        stats["proc_threads"] = proc.num_threads()
        
        # Process OS handles (Windows specific, use num_fds on Unix)
        if os.name == 'nt':
            stats["proc_handles"] = proc.num_handles()
        else:
            stats["proc_handles"] = proc.num_fds()
            
    except Exception:
        pass # Return fallback values on permission or system errors
        
    return stats
