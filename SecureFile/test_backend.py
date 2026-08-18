import os
import sys
import time
import shutil
from pathlib import Path

# Add current folder to path
sys.path.append(str(Path(__file__).parent))

from database import database
from security import password_manager, authentication
from encryption import encryptor, decryptor
from utils import file_utils, system_monitor, logger

def run_tests():
    print("==================================================")
    print("          SECUREFILE BACKEND INTEGRATION TEST      ")
    print("==================================================")
    
    # 1. Initialize DB
    print("\n[1] Initializing SQLite database...")
    database.init_db()
    db_path = database.DB_PATH
    print(f"-> Database initialized at: {db_path} (Exists: {db_path.exists()})")
    assert db_path.exists(), "Database file should exist."
    
    # 2. Test User Authentication
    print("\n[2] Testing user authentication and hashing...")
    # Test default demo account
    success, msg = authentication.authenticate("admin", "Admin@123")
    print(f"-> Authenticating 'admin' / 'Admin@123': {success} ({msg})")
    assert success, "Default credentials authentication failed."
    
    # Test incorrect login
    success, msg = authentication.authenticate("admin", "WrongPassword")
    print(f"-> Authenticating with incorrect password: {success} ({msg})")
    assert not success, "Incorrect password should fail."
    
    # Verify failed logins count incremented
    user = database.get_user("admin")
    print(f"-> Failed login count in database: {user['failed_logins']}")
    assert user['failed_logins'] == 1, "Failed attempts count should be 1."
    
    # 3. Test File Encryption and Decryption
    print("\n[3] Testing AES-256 GCM chunked encryption...")
    # Create a dummy plaintext file (approx. 2.5 MB to test chunk boundary spanning)
    test_dir = Path(__file__).parent / "test_sandbox"
    test_dir.mkdir(exist_ok=True)
    
    src_file = test_dir / "plain.txt"
    with open(src_file, "wb") as f:
        f.write(b"SecureFile project test content. " * 100000) # ~ 3.3 MB
        
    print(f"-> Created dummy file: {src_file} (Size: {src_file.stat().st_size} bytes)")
    
    password = "MySecureKey@2026"
    dest_dir = str(test_dir)
    
    # Encrypt
    enc_path, enc_size = encryptor.encrypt_file(
        source_path=str(src_file),
        dest_dir=dest_dir,
        password=password
    )
    print(f"-> Encrypted file container: {enc_path} (Size: {enc_size} bytes)")
    assert Path(enc_path).exists(), "Encrypted container should be created."
    
    # Log to DB files table
    database.add_file(
        filename=src_file.name,
        encrypted_path=enc_path,
        original_size=src_file.stat().st_size,
        encrypted_size=enc_size,
        encryption_date=time.strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # 4. Decrypt - Correct Password
    print("\n[4] Testing decryption with correct password...")
    orig_name, dec_path, orig_size = decryptor.decrypt_file(
        encrypted_path=enc_path,
        dest_dir=dest_dir,
        password=password
    )
    print(f"-> Decrypted file output: {dec_path} (Restored size: {orig_size} bytes)")
    assert Path(dec_path).exists(), "Decrypted file should be restored."
    assert orig_size == src_file.stat().st_size, "Decrypted size should match original."
    
    # Check content identity
    with open(src_file, 'rb') as f1, open(dec_path, 'rb') as f2:
        assert f1.read() == f2.read(), "Content of restored file does not match original."
    print("-> Content verification: MATCH (100% Identical)")
    
    # Clean decrypted file
    if Path(dec_path).exists():
        os.remove(dec_path)
        
    # 5. Decrypt - Incorrect Password
    print("\n[5] Testing decryption with INCORRECT password...")
    try:
        decryptor.decrypt_file(
            encrypted_path=enc_path,
            dest_dir=dest_dir,
            password="WrongPassword"
        )
        raise AssertionError("Decryption with wrong password should have failed.")
    except ValueError as e:
        print(f"-> Decryption failed as expected: {str(e)}")
        assert not Path(dec_path).exists(), "Corrupted partial files should not be written to disk."
        print("-> Clean verification: NO residual fragments left on disk.")
        
    # 6. Decrypt - Corrupted Encrypted Container
    print("\n[6] Testing decryption with CORRUPTED file container...")
    # Corrupt the encrypted container
    with open(enc_path, "r+b") as f:
        f.seek(50) # Seek beyond header
        f.write(b"CORRUPTION_BYTES")
        
    try:
        decryptor.decrypt_file(
            encrypted_path=enc_path,
            dest_dir=dest_dir,
            password=password
        )
        raise AssertionError("Decryption of corrupted file should have failed.")
    except ValueError as e:
        print(f"-> Decryption failed as expected: {str(e)}")
        assert not Path(dec_path).exists(), "Corrupted files should be deleted."
        print("-> File integrity: SAFE (Integrity verification caught corruption)")
        
    # 7. Check Stats and System Diagnostics
    print("\n[7] Testing stats calculation and telemetry queries...")
    # Update user lockouts back to clean state
    database.update_user_lockout("admin", 0, 0.0)
    
    stats = database.get_stats()
    print(f"-> Database summary stats: {stats}")
    
    sys_stats = system_monitor.get_system_stats()
    print(f"-> Live resource telemetry: CPU={sys_stats['sys_cpu']}%, RAM={sys_stats['sys_ram_percent']}%, Handles={sys_stats['proc_handles']}")
    
    # 8. Clean Sandboxes
    print("\n[8] Cleaning sandbox temporary directory...")
    shutil.rmtree(test_dir)
    print("-> Sandbox cleaned successfully.")
    
    print("\n==================================================")
    print("          ALL BACKEND INTEGRATION TESTS PASSED     ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
