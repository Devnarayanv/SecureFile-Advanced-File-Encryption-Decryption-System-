import datetime
import sys
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from database import database

def log_action(username: str, filename: str, operation: str, original_size: int, result: str, duration: float = 0.0):
    """
    Utility wrapper to record system events and operations directly to SQLite.
    Operations include: ENCRYPT, DECRYPT, DELETE, LOGIN, LOGIN FAILED.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Write to database
    database.log_activity(
        timestamp=timestamp,
        username=username,
        filename=filename,
        operation=operation,
        original_size=original_size,
        result=result,
        duration=duration
    )
    
    # Print to console for server-style stdout logs
    size_str = f" ({original_size} bytes)" if original_size is not None else ""
    duration_str = f" in {duration:.2f}s" if duration > 0 else ""
    print(f"[{timestamp}] [{result}] USER: {username} | OP: {operation} | FILE: {filename}{size_str}{duration_str}")
