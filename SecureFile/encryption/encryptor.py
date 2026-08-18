import os
import sys
import time
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

CHUNK_SIZE = 1024 * 1024  # 1MB Plaintext chunk
PBKDF2_ITERATIONS = 100000

class OperationCancelled(Exception):
    """Exception raised when user cancels the operation."""
    pass

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a 256-bit AES key from the password and salt using PBKDF2-HMAC-SHA256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS
    )
    return kdf.derive(password.encode('utf-8'))

def encrypt_file(source_path: str, dest_dir: str, password: str, progress_callback=None, stop_event=None) -> tuple[str, int]:
    """
    Encrypts a file chunk-by-chunk using AES-256 GCM.
    Prepend metadata (filename, size, permissions) inside the encrypted payload.
    
    Returns: (dest_path, encrypted_size)
    """
    source_p = Path(source_path)
    if not source_p.exists():
        raise FileNotFoundError(f"Source file {source_path} does not exist.")
        
    # Get metadata
    filename = source_p.name
    filename_bytes = filename.encode('utf-8')
    original_size = source_p.stat().st_size
    permissions = source_p.stat().st_mode & 0o7777 # keep permission bits
    
    # Check space
    import shutil
    total_space, used_space, free_space = shutil.disk_usage(dest_dir)
    if free_space < original_size * 1.1: # Allow extra buffer for encryption overhead
        raise OSError("Insufficient disk space on destination drive.")
        
    # Construct destination path
    dest_path = Path(dest_dir) / f"{filename}.secure"
    
    # Generate cryptographic parameters
    salt = os.urandom(16)
    base_nonce = os.urandom(12)
    
    if progress_callback:
        progress_callback(0.05, "Deriving encryption key...")
        
    # Derive key (runs on worker thread, so no GUI lag)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    
    # Construct metadata block to encrypt inside payload
    # Format: [2 bytes filename len] + [filename] + [8 bytes original size] + [2 bytes permissions]
    metadata_block = (
        len(filename_bytes).to_bytes(2, byteorder='big') +
        filename_bytes +
        original_size.to_bytes(8, byteorder='big') +
        permissions.to_bytes(2, byteorder='big')
    )
    
    # Total plaintext size to read is metadata block + original file content
    total_plaintext_bytes = len(metadata_block) + original_size
    bytes_read = 0
    
    try:
        # Open source file for reading and destination file for writing
        with open(source_p, 'rb') as src_file, open(dest_path, 'wb') as dest_file:
            # Write unencrypted Header: [2 bytes Magic 'SF'] + [1 byte Version \x01] + [16 bytes Salt] + [12 bytes Base Nonce]
            dest_file.write(b'SF')
            dest_file.write(b'\x01')
            dest_file.write(salt)
            dest_file.write(base_nonce)
            
            chunk_idx = 0
            metadata_sent = False
            
            while True:
                # Check for cancellation event
                if stop_event and stop_event.is_set():
                    raise OperationCancelled("Encryption cancelled by user.")
                    
                # Read plaintext chunk
                if not metadata_sent:
                    # In first chunk, we prepend the metadata block
                    meta_len = len(metadata_block)
                    file_chunk_len = CHUNK_SIZE - meta_len
                    file_data = src_file.read(file_chunk_len)
                    chunk_plaintext = metadata_block + file_data
                    metadata_sent = True
                else:
                    chunk_plaintext = src_file.read(CHUNK_SIZE)
                    
                if not chunk_plaintext:
                    break
                    
                bytes_read += len(chunk_plaintext)
                
                # Derive unique 12-byte nonce for this chunk
                # 8 bytes base nonce + 4 bytes chunk index (big-endian)
                chunk_nonce = base_nonce[:8] + chunk_idx.to_bytes(4, byteorder='big')
                
                # Encrypt chunk
                ciphertext = aesgcm.encrypt(chunk_nonce, chunk_plaintext, None)
                
                # Write to file: [4 bytes ciphertext length] + [ciphertext data]
                dest_file.write(len(ciphertext).to_bytes(4, byteorder='big'))
                dest_file.write(ciphertext)
                
                chunk_idx += 1
                
                # Report progress
                if progress_callback:
                    progress = bytes_read / total_plaintext_bytes
                    progress_callback(progress, f"Encrypting chunk {chunk_idx}... ({int(progress * 100)}%)")
                    
            if progress_callback:
                progress_callback(1.0, "Encryption completed successfully!")
                
        return str(dest_path), dest_path.stat().st_size
        
    except Exception as e:
        # Cleanup incomplete output file on error or cancellation
        if dest_path.exists():
            try:
                os.remove(dest_path)
            except Exception:
                pass
        raise e
