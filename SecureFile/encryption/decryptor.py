import os
import sys
import time
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from encryption.encryptor import derive_key, OperationCancelled

def decrypt_file(encrypted_path: str, dest_dir: str, password: str, progress_callback=None, stop_event=None) -> tuple[str, str, int]:
    """
    Decrypts a .secure file chunk-by-chunk using AES-256 GCM.
    Restores original filename, data, and permissions.
    
    Returns: (original_filename, restored_file_path, original_size)
    """
    enc_p = Path(encrypted_path)
    if not enc_p.exists():
        raise FileNotFoundError(f"Encrypted file {encrypted_path} does not exist.")
        
    dest_path = None
    original_size = 0
    original_filename = ""
    permissions = 0o644
    
    try:
        with open(enc_p, 'rb') as enc_file:
            # 1. Read and verify unencrypted header
            magic = enc_file.read(2)
            if magic != b'SF':
                raise ValueError("Invalid file format. Not a SecureFile container.")
                
            version = enc_file.read(1)
            if version != b'\x01':
                raise ValueError(f"Unsupported file format version: {version[0]}")
                
            salt = enc_file.read(16)
            base_nonce = enc_file.read(12)
            
            if len(salt) < 16 or len(base_nonce) < 12:
                raise ValueError("Corrupted file header.")
                
            if progress_callback:
                progress_callback(0.05, "Deriving decryption key...")
                
            # Derive key
            key = derive_key(password, salt)
            aesgcm = AESGCM(key)
            
            chunk_idx = 0
            dest_file = None
            bytes_written = 0
            
            while True:
                # Check for cancellation event
                if stop_event and stop_event.is_set():
                    raise OperationCancelled("Decryption cancelled by user.")
                    
                # Read ciphertext chunk length
                len_bytes = enc_file.read(4)
                if not len_bytes:
                    break # EOF
                    
                if len(len_bytes) < 4:
                    raise ValueError("Corrupted encrypted file chunk size.")
                    
                ciphertext_len = int.from_bytes(len_bytes, byteorder='big')
                ciphertext = enc_file.read(ciphertext_len)
                
                if len(ciphertext) < ciphertext_len:
                    raise ValueError("Corrupted encrypted file chunk data.")
                    
                # Construct chunk nonce
                chunk_nonce = base_nonce[:8] + chunk_idx.to_bytes(4, byteorder='big')
                
                # Decrypt chunk (throws InvalidTag on wrong password or modified file)
                try:
                    plaintext_chunk = aesgcm.decrypt(chunk_nonce, ciphertext, None)
                except Exception as e:
                    raise ValueError("Incorrect password or corrupted encrypted file.") from e
                    
                if chunk_idx == 0:
                    # Parse metadata block: [2 bytes filename len] + [filename] + [8 bytes size] + [2 bytes permissions]
                    filename_len = int.from_bytes(plaintext_chunk[0:2], byteorder='big')
                    
                    if len(plaintext_chunk) < 2 + filename_len + 8 + 2:
                        raise ValueError("Corrupted metadata block.")
                        
                    original_filename = plaintext_chunk[2 : 2 + filename_len].decode('utf-8')
                    
                    original_size = int.from_bytes(
                        plaintext_chunk[2 + filename_len : 10 + filename_len], 
                        byteorder='big'
                    )
                    
                    permissions = int.from_bytes(
                        plaintext_chunk[10 + filename_len : 12 + filename_len], 
                        byteorder='big'
                    )
                    
                    # File data starts after metadata
                    file_data_start = plaintext_chunk[12 + filename_len:]
                    
                    # Verify destination path
                    dest_p_dir = Path(dest_dir) if dest_dir else enc_p.parent
                    dest_path = dest_p_dir / original_filename
                    
                    # Check disk space
                    import shutil
                    total_space, used_space, free_space = shutil.disk_usage(dest_p_dir)
                    if free_space < original_size:
                        raise OSError("Insufficient disk space on destination drive.")
                        
                    # Open output file
                    dest_file = open(dest_path, 'wb')
                    dest_file.write(file_data_start)
                    bytes_written += len(file_data_start)
                else:
                    dest_file.write(plaintext_chunk)
                    bytes_written += len(plaintext_chunk)
                    
                chunk_idx += 1
                
                # Report progress
                if progress_callback and original_size > 0:
                    progress = min(bytes_written / original_size, 0.99)
                    progress_callback(progress, f"Decrypting chunk {chunk_idx}... ({int(progress * 100)}%)")
                    
            # Close file handles
            if dest_file:
                dest_file.close()
                dest_file = None
                
            # Restore permissions
            if dest_path and dest_path.exists():
                try:
                    os.chmod(dest_path, permissions)
                except Exception:
                    pass # Silently proceed if permission restoration fails on OS
                    
            if progress_callback:
                progress_callback(1.0, "Decryption completed successfully!")
                
            return original_filename, str(dest_path), original_size
            
    except Exception as e:
        # Cleanup incomplete output file on error or cancellation
        if 'dest_file' in locals() and dest_file:
            try:
                dest_file.close()
            except Exception:
                pass
        if dest_path and dest_path.exists():
            try:
                os.remove(dest_path)
            except Exception:
                pass
        raise e
