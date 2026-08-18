import time
import sys
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from database import database
from security.password_manager import verify_password

LOCKOUT_DURATION = 30  # seconds
MAX_FAILED_ATTEMPTS = 3

def authenticate(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticates a user against credentials stored in SQLite.
    Handles lockout timing and brute-force protection.
    Returns: (success_bool, message_str)
    """
    user = database.get_user(username)
    if not user:
        return False, "Invalid username or password"
        
    current_time = time.time()
    
    # Check if account is currently locked out
    lockout_until = user["lockout_until"]
    if lockout_until and lockout_until > current_time:
        remaining = int(lockout_until - current_time)
        return False, f"Account locked. Try again in {remaining} seconds."
        
    # Attempt password verification
    if verify_password(password, user["password_hash"]):
        # Success: reset failed attempts
        database.update_user_lockout(username, 0, 0.0)
        return True, "Login successful"
    else:
        # Failure: increment failed attempt counter
        failed_attempts = user["failed_logins"] + 1
        
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            lockout_time = current_time + LOCKOUT_DURATION
            database.update_user_lockout(username, failed_attempts, lockout_time)
            return False, f"Account locked for {LOCKOUT_DURATION} seconds due to excessive failed attempts."
        else:
            database.update_user_lockout(username, failed_attempts, 0.0)
            remaining_attempts = MAX_FAILED_ATTEMPTS - failed_attempts
            return False, f"Invalid username or password. {remaining_attempts} attempts remaining."
