import os
import hashlib
import hmac

ITERATIONS = 100000
KEY_LEN = 32
SALT_LEN = 16

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a unique salt.
    Returns: string in format 'pbkdf2_sha256$iterations$salt_hex$hash_hex'
    """
    salt = os.urandom(SALT_LEN)
    pwd_bytes = password.encode('utf-8')
    
    pwd_hash = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=pwd_bytes,
        salt=salt,
        iterations=ITERATIONS,
        dklen=KEY_LEN
    )
    
    salt_hex = salt.hex()
    hash_hex = pwd_hash.hex()
    return f"pbkdf2_sha256${ITERATIONS}${salt_hex}${hash_hex}"

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies a password against a stored PBKDF2-HMAC-SHA256 hash.
    """
    try:
        parts = stored_hash.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
            
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        original_hash = bytes.fromhex(parts[3])
        
        pwd_bytes = password.encode('utf-8')
        new_hash = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=pwd_bytes,
            salt=salt,
            iterations=iterations,
            dklen=len(original_hash)
        )
        
        return hmac.compare_digest(original_hash, new_hash)
    except Exception:
        return False
